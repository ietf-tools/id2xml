# Copyright The IETF Trust 2007, All Rights Reserved

# Create your views here.
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect
from django import newforms as forms
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.list_detail import object_detail, object_list
from ietf.idtracker.models import InternetDraft, IDInternal, IDState, IDSubState, Rfc, DocumentWrapper, IESGLogin, TelechatDates, IDNextState, BallotInfo, Position, DocumentComment,IDAuthor, Area, AreaGroup, IESGComment, IESGDiscuss
from ietf.idtracker.forms import IDSearch, EmailFeedback, IDDetail, BallotSearch
from ietf.utils.mail import send_mail_text, send_mail
from ietf.utils import normalize_draftname
import re, datetime

LoginObj = None
def get_tracker_mode(request):
    global LoginObj
    mode = "IETF"
    if request.user.is_authenticated():
        try:
            mode = request.user.groups.all()[0].name
            person = request.user.get_profile().person
            LoginObj = IESGLogin.objects.get(person=person)
        except IndexError:
            mode = "IETF"
    return mode

# Override default form field mappings
# group_acronym: CharField(max_length=10)
# note: CharField(max_length=100)
def myfields(f):
    if f.name == "group":
	return forms.CharField(max_length=10,
			widget=forms.TextInput(attrs={'size': 5}))
    if f.name == "note":
	return forms.CharField(max_length=100,
			widget=forms.TextInput(attrs={'size': 100}))
    return f.formfield()

def search(request):
    mode = get_tracker_mode(request)
    if mode == 'IETF':
        default_search = False
    else:
        global LoginObj 
        default_search = LoginObj.default_search
    # for compatability with old tracker form, which has
    #  "all substates" = 6.
    args = request.GET.copy()
    # For Non-Public mode, display menu button on top of the first screen
    if args.get('display_menu',''):
        menu = [key for key in args.keys()]
        menu_item = menu[1]
        return render_to_response('idtracker/%s.html' % menu_item,{'menu':menu_item},
            context_instance=RequestContext(request))
    # Switch Default Search option for IESG
    if args.get('switch_default_search'):
        if default_search:
            default_search = 0
        else:
            default_search = 1
        LoginObj.default_search=default_search
        LoginObj.save()
    if args.get('sub_state_id', '') == '6':
	args['sub_state_id'] = ''
    # "job_owner" of "0" means "All/Any"
    if args.get('search_job_owner', '') == '0':
	args['search_job_owner'] = ''
    if args.has_key('search_filename'):
	args['search_filename'] = normalize_draftname(args['search_filename'])
    form = IDSearch(args)
    # if there's a post, do the search and supply results to the template
    searching = False
    # filename, rfc_number, group searches are seperate because
    # they can't be represented as simple searches in the data model.
    qdict = { 
	      'search_job_owner': 'job_owner',
	      'search_cur_state': 'cur_state',
	      'sub_state_id': 'cur_sub_state',
	      'search_area_acronym': 'area_acronym',
	    }
    q_objs = []
    for k in qdict.keys() + ['search_group_acronym', 'search_rfcnumber', 'search_filename', 'search_status_id']:
	if args.has_key(k):
	    searching = True
	    if args[k] != '' and qdict.has_key(k):
		q_objs.append(Q(**{qdict[k]: args[k]}))
    if form.is_valid() == False:
	searching = False
    #print searching
    if searching:
        group = args.get('search_group_acronym', '')
	if group != '':
	    rfclist = [rfc['rfc_number'] for rfc in Rfc.objects.all().filter(group_acronym=group).values('rfc_number')]
	    draftlist = [draft['id_document_tag'] for draft in InternetDraft.objects.all().filter(group__acronym=group).values('id_document_tag')]
	    if rfclist or draftlist:
		q_objs.append(Q(draft__in=draftlist)&Q(rfc_flag=0)|Q(draft__in=rfclist)&Q(rfc_flag=1))
	    else:
		q_objs.append(Q(draft__isnull=True)) # no matches
        rfc_number = args.get('search_rfcnumber', '')
	if rfc_number != '':
	    draftlist = [draft['id_document_tag'] for draft in InternetDraft.objects.all().filter(rfc_number=rfc_number).values('id_document_tag')]
	    q_objs.append(Q(draft__in=draftlist)&Q(rfc_flag=0)|Q(draft=rfc_number)&Q(rfc_flag=1))
        filename = args.get('search_filename', '')
        if args.has_key('add_button'): # redirecting to add id
            if filename:
                draftObj =  InternetDraft.objects.all().filter(filename__icontains=filename).order_by('filename')
                rfc_flag=0
            elif rfc_number:
                draftObj =  Rfc.objects.all().filter(rfc_number=rfc_number)
                rfc_flag=1
            if draftObj:
                if args.has_key('ballot_id'):
                    ballot_id = args.get('ballot_id')
                else:
                    ballot_id = None
                return add_id(request,draftObj,ballot_id,rfc_flag)

	if filename != '':
	    q_objs.append(Q(draft__filename__icontains=filename,rfc_flag=0))
	status = args.get('search_status_id', '')
	if status != '':
	    q_objs.append(Q(draft__status=status,rfc_flag=0))
	matches = IDInternal.objects.all().filter(*q_objs)
	matches = matches.order_by('cur_state', 'cur_sub_state', '-primary_flag')
	#
	# Now search by I-D exists, if there could be any results.
	# If searching by job owner, current state or substate, there
	# can't be any "I-D exists" matches.
	if not(args.get('search_job_owner', 0) or args.get('search_cur_state', 0) or args.get('sub_state_id', 0)):
	    if not(args.get('search_rfcnumber', 0)):
		in_tracker=[i['draft'] for i in IDInternal.objects.filter(rfc_flag=0).values('draft')]
		qdict = {
		    'search_area_acronym': 'group__ietfwg__areagroup__area',
		    'search_group_acronym': 'group__acronym',
		    'search_filename': 'filename__icontains',
		    #'search_status_id': 'status',
		}
		q_objs = [Q(**{qdict[k]: args[k]}) for k in qdict.keys() if args.get(k, '') != '']
		idmatches = InternetDraft.objects.filter(*q_objs).exclude(id_document_tag__in=in_tracker).filter(status__status='Active').order_by('filename')
		# resolve the queryset, append wrapper objects.
		matches = list(matches) + [DocumentWrapper(id) for id in idmatches]
	    if not(args.get('search_filename', '') or args.get('search_status_id', 0)) and args.get('search_rfcnumber', 0):
		# the existing area acronym support in this function
		# in pidtracker.cgi is broken, since it compares an
		# area acronym string in the database against an
		# area acronym number in the form.  We just ignore
		# the area (resulting in a different search, but
		# given that this search is only performed when there's
		# an explicit rfc number, it seems more or less silly
		# to filter it further anyway.)
		in_tracker=[i['draft'] for i in IDInternal.objects.filter(rfc_flag=1).values('draft')]
		qdict = {
		    'search_group_acronym': 'group_acronym',
		    'search_rfcnumber': 'rfc_number',
		    'search_status_id': 'status',
		}
		q_objs = [Q(**{qdict[k]: args[k]}) for k in qdict.keys() if args.get(k, '') != '']
		rfcmatches = Rfc.objects.filter(*q_objs).exclude(rfc_number__in=in_tracker)
		matches = list(matches) + [DocumentWrapper(rfc) for rfc in rfcmatches]
    elif default_search:
        matches = IDInternal.objects.all().filter(job_owner=LoginObj.id)
        matches = matches.order_by('cur_state', 'cur_sub_state', '-primary_flag')
    else:
	matches = None
    if  args.has_key('ballot_id') and mode in ['IESG','Secretariat']:
        adding_ballot_to = IDInternal.objects.get(ballot=args.get('ballot_id'), primary_flag=1)
    else:
        adding_ballot_to = False
    ballot_search_form = BallotSearch()
    return render_to_response('idtracker/idtracker_search.html', {
	'form': form,
        'ballot_search_form': ballot_search_form,
	'matches': matches,
	'searching': searching,
        'mode': mode,
        'adding_ballot_to': adding_ballot_to,
        'default_search': default_search,
      }, context_instance=RequestContext(request))

def edit_idinternal(request, idinternal=None,adding=False,ballot_id=None,separate_ballot=False,rfc_flag=0):
    mode = get_tracker_mode(request)
    global LoginObj
    if idinternal:
        if adding==False and ballot_id: #Merging documents
            ballotObj, crated = BallotInfo.objects.get_or_create(ballot = ballot_id, active = False, an_sent = False)
            idinternal.ballot = ballotObj
            idinternal.primary_flag = 0
            idinternal.job_owner = ballotObj.get_primary_draft().job_owner
            idinternal.prev_state = idinternal.cur_state
            idinternal.cur_state = ballotObj.get_primary_draft().cur_state
            idinternal.cur_sub_state = ballotObj.get_primary_draft().cur_sub_state
            idinternal.save()
            idinternal.add_comment("Merged with %s by %s" % (ballotObj.get_primary_draft(),LoginObj.person),False,LoginObj)
            return HttpResponseRedirect(idinternal.get_absolute_url())
        if separate_ballot: # Separate Ballot
            old_ballotObj = idinternal.ballot
            new_ballot_id = BallotInfo.objects.all().order_by("-ballot")[0].ballot + 1
            new_ballotObj = BallotInfo.objects.create(
                ballot = new_ballot_id,
                active = old_ballotObj.active,
                an_sent = old_ballotObj.an_sent,
                an_sent_date = old_ballotObj.an_sent_date,
                an_sent_by = old_ballotObj.an_sent_by,
                defer = old_ballotObj.defer,
                defer_date = old_ballotObj.defer_date,
                approval_text = old_ballotObj.approval_text, # need to be regen
                last_call_text = old_ballotObj.last_call_text, # need to be regen
                ballot_writeup = old_ballotObj.ballot_writeup,
                ballot_issued = old_ballotObj.ballot_issued
            ) 
            idinternal.ballot = new_ballotObj
            idinternal.primary_flag=1
            idinternal.save()
            #to be moved to a function
            #copy_ballot(old_ballotObj,idinternal.ballot)
            #copying positions
            for position in Position.objects.filter(ballot=old_ballotObj):
                print new_ballotObj.ballot
                new_position = Position.objects.create(
                    ballot=new_ballotObj,
                    ad = position.ad,
                    yes = position.yes,
                    noobj = position.noobj,
                    abstain = position.abstain,
                    approve = position.approve,
                    discuss = position.discuss,
                    recuse = position.recuse
                )
            #copying ballot comments
            for iesg_comment in IESGComment.objects.filter(ballot=old_ballotObj):
                new_iesg_comment = IESGComment.objects.create(
                    ballot = new_ballotObj,
                    ad = iesg_comment.ad,
                    date = iesg_comment.date,
                    revision = iesg_comment.revision,
                    active = iesg_comment.active,
                    text = iesg_comment.text
                )
            #copying ballot comments
            for iesg_comment in IESGDiscuss.objects.filter(ballot=old_ballotObj):
                new_iesg_comment = IESGDiscuss.objects.create(
                    ballot = new_ballotObj,
                    ad = iesg_comment.ad,
                    date = iesg_comment.date,
                    revision = iesg_comment.revision,
                    active = iesg_comment.active,
                    text = iesg_comment.text
                )
            return HttpResponseRedirect(idinternal.get_absolute_url()) 
        try:
            next_state_object = IDNextState.objects.filter(cur_state=idinternal.cur_state)
	except IDNextState.DoesNotExist:
            next_state_object = []
        if request.method == 'POST':
	    idform = IDDetail(request.POST)
            if "next_state_button" in request.POST:
                next_state_id = IDState.objects.get(state= request.POST['next_state_button']).document_state_id
	    if idform.is_valid():
		(update_notify_to, comment_text) = idform.save(idinternal,request,LoginObj,adding=adding,ballot_id=ballot_id)
                if update_notify_to:
                    email_text = """Please DO NOT reply to this email

I-D: %s
ID Tracker URL: https://datatracker.ietf.org%s
%s
""" % (idinternal.draft,idinternal.get_absolute_url(),comment_text)
             # following line is commented for dev. Need to uncomment when deployed 
                    #send_mail_text(request,update_notify_to,("DraftTracker Mail System","iesg-secretary@ietf.org"),"%s updated by %s" % (idinternal.draft,LoginObj), email_text)
		return HttpResponseRedirect(".")
            else:
                print idform.error()
	else:
            idinternal_dict = {
                'intended_status':idinternal.draft.intended_status.intended_status_id,
                'agenda': idinternal.agenda,
                'telechat_date': idinternal.telechat_date,
                'job_owner': idinternal.job_owner.id,
                'status_date': idinternal.status_date,
                'note': idinternal.note,
                'public_flag': True,
                'state_change_notice_to': idinternal.state_change_notice_to,
                 }
            if idinternal.draft.group.acronym_id == 1027 and idinternal.primary_flag:
                idinternal_dict['area'] = idinternal.area_acronym_id
            if adding:
                idinternal_dict['next_state'] = idinternal.cur_state_id
                if rfc_flag:
                    docObj = Rfc.objects.get(pk=idinternal.draft.id_document_tag)
                else:
                    docObj = idinternal.draft
            else: 
                docObj = idinternal.document()
            idform = IDDetail(idinternal_dict)
    else:
	idform = None
    if mode == 'IETF':
        fontsize = 3
    else:
        fontsize = 4
    if idinternal.cur_state_id < 15:
        ballot_writeup = False
    else:
        ballot_writeup = True
    if mode != 'IETF' and rfc_flag==0 and idinternal.draft.is_expired():
        resurrection_needed = True
    else:
        resurrection_needed = False
    return render_to_response('idtracker/idinternal_detail.html', {
        'object': idinternal,
        'next_state_object': next_state_object,
	'idform': idform,
        'mode': mode,
        'fontsize':fontsize,
        'ballot_writeup': ballot_writeup,
        'adding': adding,
        'docObj': docObj,
        'ballot_id': ballot_id,
        'resurrection_needed': resurrection_needed 
      }, context_instance=RequestContext(request))

def state_desc(request, state, is_substate=0):
    if int(state) == 100:
	object = {
		'state': 'I-D Exists',
		'description': """
Initial (default) state for all internet drafts. Such documents are
not being tracked by the IESG as no request has been made of the
IESG to do anything with the document.
"""
		}
    elif is_substate:
	sub = get_object_or_404(IDSubState, pk=state)
	object = { 'state': sub.sub_state, 'description': sub.description }
    else:
	object = get_object_or_404(IDState, pk=state)
    return render_to_response('idtracker/state_desc.html', {'state': object},
	context_instance=RequestContext(request))

def comment(request, slug, object_id, queryset):
    rfcnum = re.match(r'^rfc(\d+)$', slug)
    if rfcnum:
	queryset = queryset.filter(document=rfcnum.groups()[0])
    else:
	draft = get_object_or_404(InternetDraft, filename=slug)
	queryset = queryset.filter(document=draft.id_document_tag)
    return object_detail(request, queryset=queryset, object_id=object_id)

def send_email(request):
    if request.method == 'POST':
	form = EmailFeedback(request.POST)
	cat = request.POST.get('category', 'bugs')
	if form.is_valid():
	    send_mail_text(request, "idtracker-%s@ietf.org" % form.clean_data['category'], (form.clean_data['name'], form.clean_data['email']), '[ID TRACKER %s] %s' % (form.clean_data['category'].upper(), form.clean_data['subject']), form.clean_data['message'])
	    return render_to_response('idtracker/email_sent.html', {},
		context_instance=RequestContext(request))
    else:
	cat = request.REQUEST.get('cat', 'bugs')
	form = EmailFeedback(initial={'category': cat})
    return render_to_response('idtracker/email_form.html', {'category': cat, 'form': form},
	context_instance=RequestContext(request))

def status(request):
    queryset = IDInternal.objects.filter(primary_flag=1).exclude(cur_state__state__in=('RFC Ed Queue', 'RFC Published', 'AD is watching', 'Dead')).order_by('cur_state', 'status_date', 'ballot_id')
    return object_list(request, template_name="idtracker/status_of_items.html", queryset=queryset, extra_context={'title': 'IESG Status of Items'})

def last_call(request):
    queryset = IDInternal.objects.filter(primary_flag=1).filter(cur_state__state__in=('In Last Call', 'Waiting for Writeup', 'Waiting for AD Go-Ahead')).order_by('cur_state', 'status_date', 'ballot_id')
    return object_list(request, template_name="idtracker/status_of_items.html", queryset=queryset, extra_context={'title': 'Documents in Last Call', 'lastcall': 1})

def redirect_id(request, object_id):
    '''Redirect from historical document ID to preferred filename url.'''
    doc = get_object_or_404(InternetDraft, id_document_tag=object_id)
    return HttpResponsePermanentRedirect(reverse(view_id, args=[doc.filename]))

def resurrect_id(request, queryset=None, slug=None, slug_field=None):
    mode = get_tracker_mode(request)
    global LoginObj
    draft = get_object_or_404(InternetDraft, filename=slug)
    if draft.idinternal:
        draft.idinternal.resurrect_requested_by = LoginObj
        draft.idinternal.save()
    #print render_to_string('idtracker/request_resurrect_email.txt', {'draft': draft, 'requested_by':LoginObj},  context_instance=RequestContext(request))
    # following line is commented for dev. Need to uncomment when deployed
    #send_mail(request, ('I-D Administrator', 'internet-drafts@ietf.org'), LoginObj.person.email(), 'I-D Resurrection Request', 'idtracker/request_resurrect_email.txt', {'draft': draft, 'requested_by': LoginObj})

    return render_to_response('idtracker/resurrect_id_result.html', {'draft': draft}, context_instance=RequestContext(request))

# calling sequence similar to object_detail, but we have different
# 404 handling: if the draft exists, render a not-found template.
def view_id(request, queryset=None, slug=None, slug_field=None, rfc_flag=0):
    mode = get_tracker_mode(request)
    global LoginObj
    if 'ballot_id' in request.GET:
        ballot_id = request.GET['ballot_id']
        primary_flag = 0
    elif 'ballot_id' in request.POST:
        ballot_id = request.POST['ballot_id']
        primary_flag = 0
    else:
        ballot_id = None
        primary_flag = 1
    if 'separate_ballot' in request.GET:
        separate_ballot=True
    else:
        separate_ballot=False
    try:
        if rfc_flag:
	    object = IDInternal.objects.get(pk=slug, rfc_flag=rfc_flag)
	else:
            object = IDInternal.objects.get(draft__filename=slug, rfc_flag=rfc_flag)
    except IDInternal.DoesNotExist: 
        if rfc_flag:
	    docObj = get_object_or_404(Rfc, rfc_number=slug)
        else:
	    docObj = get_object_or_404(InternetDraft, filename=slug)
        if mode == 'IESG' or mode == 'Secretariat':
            if 'ballot_id' in request.GET:
                ballot_id = request.GET['ballot_id']
                primary_flag = 0
            elif 'ballot_id' in request.POST:
                ballot_id = request.POST['ballot_id']
                primary_flag = 0
            else:
                ballot_id = None
                primary_flag = 1
            notice_list = []
            if docObj.group_acronym_id_display() == 1027:
                notice_list = [person.email() for person in IDAuthor.objects.filter(document=docObj)]
                #area_acronym = Area.objects.get(area_acronym=1008)
            else:
               notice_list.append("%s-chairs@tools.ietf.org" % docObj.group_acronym_display()) 
               notice_list.append("%s@tools.ietf.org" % docObj.filename) 
               #area_acronym = AreaGroup.objects.get(group=docObj.group).area
            new_object = IDInternal(
                draft = docObj.get_draft(),
                rfc_flag = rfc_flag, 
                primary_flag = primary_flag,
                group_flag = docObj.group_acronym_id_display(),
                job_owner =  LoginObj,
                mark_by =  LoginObj,
                area_acronym = docObj.get_area(),
                cur_state = IDState.objects.get(document_state_id=10),
                prev_state = IDState.objects.get(document_state_id=10),
                state_change_notice_to = ','.join(notice_list)
            )
            return edit_idinternal(request,new_object,adding=True,ballot_id=ballot_id,rfc_flag=rfc_flag)
        else:
	    return render_to_response('idtracker/idinternal_notfound.html', {'draft': docObj}, context_instance=RequestContext(request))
    args = request.GET.copy()
    if args.get('toggle_public_flag'):
        id = args.get('objectid')
        comment = DocumentComment.objects.get(id=id)
        comment.toggle_public_flag()
        comment.save()
        return HttpResponseRedirect(".") 
    return edit_idinternal(request,object,ballot_id=ballot_id,separate_ballot=separate_ballot,rfc_flag=rfc_flag)

def add_id (request, draftObj, ballot_id=None,rfc_flag=0):
    mode = get_tracker_mode(request)
    global LoginObj
    if draftObj.count() == 1: # Go directly to ADD ID page
        if rfc_flag:
            matching_slug = draftObj[0].rfc_number
        else:
            matching_slug = draftObj[0].filename
        return view_id (request,slug=matching_slug,rfc_flag=rfc_flag)
    else: #Display document list
        return render_to_response('idtracker/adding_doc_list.html', {'object': draftObj,'ballot_id':ballot_id}, context_instance=RequestContext(request))
    return HttpResponseRedirect("/idtracker/") 
def view_rfc(request, object_id):
    '''A replacement for the object_detail generic view for this
    specific case to work around the following problem:
    The object_detail generic view looks up the value of the
    primary key in order to hand it to populate_xheaders.
    In the IDInternal table, the primary key is a foreign key
    to InternetDraft.  object_detail assumes that the PK is not
    an FK so doesn't do the foo_id trick, so the lookup is
    attempted and an exception raised if there is no match.
    This view gets the appropriate row from IDInternal and
    calls the template with the necessary context.'''
    return view_id(request, queryset=None, slug=object_id, rfc_flag=1)
    #object = get_object_or_404(IDInternal, pk=object_id, rfc_flag=1)
    #return render_to_response('idtracker/idinternal_detail.html', {'object': object}, context_instance=RequestContext(request))

# Wrappers around object_detail to give permalink a handle.
# The named-URLs feature in django 0.97 will eliminate the
# need for these.
def view_comment(*args, **kwargs):
    return object_detail(*args, **kwargs)

def view_ballot(*args, **kwargs):
    request = args[0]
    mode = get_tracker_mode(request)
    object_id = kwargs['object_id']
    if mode == 'IETF':
        return object_detail(*args, **kwargs)
    else:
        return ballot(request,object_id) 

def view_ballot_writeup(*args, **kwargs):
    return object_detail(*args, **kwargs)

def ballot_comment (request, object_id, **kwargs) :
    method = None
    if kwargs.has_key("method") :
        method = kwargs.get("method", None)
        if method not in ("POST", "GET", "DELETE", "PUT", ) :
            method = "GET"
    else :
        method = request.method

    if kwargs.has_key("data") :
        argument = kwargs["data"]
    else :
        if method != "GET" :
            argument = request.POST.copy()
        else :
            argument = request.GET.copy()

    try :
        ad_id = int(argument.get("ad_id", "").strip())
    except :
        raise Http404
    else :
        LoginObj = IESGLogin.objects.get(id=ad_id)

    # get ballot
    ballot = get_object_or_404(BallotInfo.objects, pk=object_id)
    draft = ballot.get_primary_draft()
    if not draft :
        raise Http404

    if method == "GET" :
        if argument.has_key("edit_discuss") and argument.get("edit_discuss", "no") == "yes" :
            is_discuss_or_comment = "discuss"
        else :
            is_discuss_or_comment = "comment"

        if is_discuss_or_comment == "discuss" :
            discuss_comment0 = getattr(ballot, "discusses")
        else :
            discuss_comment0 = getattr(ballot, "comments")

        try :
            discuss_comment = discuss_comment0.get(ad=LoginObj)
        except :
            discuss_comment = {
                "date" : datetime.datetime.now().strftime("%Y-%m-%d"),
                "revision" : draft.document().revision,
            }

        return render_to_response(
            "idtracker/ballot_comment_edit.html",
            {
                "argument": argument,
                "draft": draft,
                "LoginObj": LoginObj,
                "ballot": ballot,
                "discuss_comment" : discuss_comment,
                "is_discuss_or_comment" : is_discuss_or_comment,
            }, context_instance=RequestContext(request)
        )
    elif method == "POST" :
        comment_text = argument.get("comment_text")
        result_list = argument.get("result_list")
        ad_id = argument.get("ad_id")
        category = argument.get("category")
        rfc_flag = argument.get("rfc_flag")

        if draft.rfc_flag == 1 :
            revision = "RFC %s" % draft.draft.id_document_tag
        else :
            revision = draft.draft.revision

        if category == "comment" :
            comment_type = 2
        else :
            comment_type = 1

        if category == "discuss" :
            discuss_comment0 = getattr(ballot, "discusses")
        else :
            discuss_comment0 = getattr(ballot, "comments")

        try :
            discuss_comment = discuss_comment0.get(ad=LoginObj)
        except : # insert new
            ballot.discusses.create(
                ad=LoginObj,
                date=datetime.datetime.now(),
                revision=revision,
                active=1,
                text=comment_text,
            )
        else : # update
            discuss_comment.date = datetime.datetime.now()
            discuss_comment.revision = revision
            discuss_comment.text = comment_text
            discuss_comment.active = 1
            discuss_comment.save()

        # add comment
        draft.add_comment(
            comment_text,
            False,
            LoginObj=LoginObj,
            public_flag=True,
            ballot=ballot.ballot,
        )

        # update event_date of IDInternal.
        draft.event_date = datetime.datetime.now()
        draft.save()

        # open ballot
        return view_ballot_iesg(request, object_id)
# this function needs to be rewritten not to use any legacy method
def ballot (request, object_id) :
    if request.method == "POST" :
        """
        To follow up the previous legacy perl script, idtracker.cgi,
        every internel command was implemented as 'do_XXX' function.

        If request method is 'POST' and there is 'comment' query exists,
        run it 'do_XX' command.
        """
        command = request.POST.copy().get("command", "").strip()
        func = globals().get("do_ballot_%s" % command, None)
        if func :
            return func(request, object_id)

    return view_ballot_iesg(request, object_id)

def view_ballot_iesg(request, object_id, extra_context=dict()) :
    # get ballot
    ballot = get_object_or_404(BallotInfo.objects, pk=object_id)

    if request.GET.copy().get("txt", "") :
        return render_to_response(
            "idtracker/ballotinfo_detail.html",
            {
                "object": ballot,
            }, context_instance=RequestContext(request)
        )

    # get primary draft
    draft = ballot.get_primary_draft()
    if not draft :
        raise Http404

    mode = get_tracker_mode(request)
    global LoginObj

    # is deferred?
    if ballot.defer is True : # check defer date
        if ballot.defer_date >= datetime.datetime.now() :
            # set ballot.defer to False
            ballot.defer = False
            ballot.save()

    context = {
        "LoginObj" : LoginObj,
        "ballot" : ballot,
        "draft" : draft,
    }
    context.update(extra_context)

    return render_to_response(
        "idtracker/ballotinfo_detail_form.html",
        context, context_instance=RequestContext(request)
    )

def get_position_label (selected_value) :
    if selected_value == "yes_col" :
        return "Yes"
    elif selected_value == "no_col" :
        return "No Objection"
    elif selected_value == "abstain" :
        return "Abstain"
    elif selected_value == "discuss" :
        return "Discuss"
    elif selected_value == "recuse" :
        return "Recuse"

    return "Undefined"

def do_ballot_update_single_ballot (request, object_id) :
    argument = request.POST.copy()

    try :
        loginid = int(argument.get("loginid", "").strip())
    except :
        raise Http404
    else :
        LoginObj = IESGLogin.objects.get(id=loginid)

    selected_position = argument.get("yes_no_abstain_col", None)

    # get position of this loginid
    ballot = get_object_or_404(BallotInfo.objects, pk=object_id)
    try :
        position = ballot.positions.get(ad=42)
    except ObjectDoesNotExist :
        position = None

    discuss = False
    try :
        discuss = ballot.positions.get(ad=42).discuss
    except :
        pass
    else :
        if discuss == 1 :
            discuss = -1

    if selected_position == "discuss" :
        discuss = 1

    # update single ballot
    # if in discuss, set it discuss
    new_position = get_position_label(selected_position)

    if position : # set it 'undefined'
        old_position = get_position_label(position.get_active_position())

        position.yes=(selected_position == "yes_col") and 1 or 0
        position.noobj=(selected_position == "no_col") and 1 or 0
        position.abstain=(selected_position == "abstain") and 1 or 0
        position.discuss=discuss
        position.recuse=(selected_position == "recuse") and 1 or 0

        position.save()

        comment_text = "[Ballot Position Update] Position for %(ad)s has been changed to %(new_position)s from %(old_position)s" % {
            "ad": position.ad,
            "new_position" : new_position,
            "old_position" : old_position,
        }
    elif new_position != "Undefined" : # insert new position
        position = Position(
            ballot=ballot,
            ad=LoginObj,
            yes=(selected_position == "yes_col") and 1 or 0,
            noobj=(selected_position == "no_col") and 1 or 0,
            abstain=(selected_position == "abstain") and 1 or 0,
            approve=0,
            discuss=discuss,
            recuse=(selected_position == "recuse") and 1 or 0,
        )
        position.save()

        comment_text = """Ballot Position Update] New position, %(new_position)s, has been recorded""" % {"new_position" : new_position, }

    for draft in ballot.drafts.all() :
        if draft.rfc_flag == 1 :
            version = "RFC"
        else :
            version = draft.draft.revision

        draft.add_comment(
            comment_text, 
            False,
            LoginObj=LoginObj,
            public_flag=True,
            ballot=ballot.ballot,
        )
    # update ballot discuss
    ballot_discuss = ballot.discusses.get(ad=LoginObj)
    ballot_discuss.active = 0

    # update event date in IdInternal
    for draft in ballot.drafts.all() :
        draft.event_date = datetime.datetime.now()
        draft.save()

    return True

do_ballot_update_ballot_comment_db = ballot_comment

def do_ballot_update_ballot (request, object_id) :
    argument = request.POST.copy()

    try :
        loginid = int(argument.get("loginid", "").strip())
    except :
        raise Http404
    else :
        LoginObj = IESGLogin.objects.get(id=loginid)

    context = dict()
    try :
        do_ballot_update_single_ballot(request, object_id)
    except :
        context["error_message"] = """<h2>There is a fatal error occured while processing your request</h2>"""

    ballot = get_object_or_404(BallotInfo.objects, pk=object_id)

    discuss = 0
    try :
        discuss = ballot.positions.get(ad=LoginObj).discuss
    except :
        pass

    # if in discuss,
    if discuss :
        if (discuss == 1 and argument.has_key("vote")) or argument.has_key("edit_discuss") or argument.has_key("edit_comment") :
            # get primary draft.

            draft = ballot.get_primary_draft()
            if not draft :
                raise Http404

            kwargs = {
                "filename" : draft.document().filename,
                "ad_id" : str(loginid),
            }

            if argument.get("edit_discuss", None) :
                kwargs.update(
                    (
                        ("edit_discuss", "yes"),
                    )
                )

            return ballot_comment(
                request,
                object_id,
                method="GET",
                data=kwargs,
            )
    else : # if not in discuss,
        if argument.has_key("edit_discuss") :
            context["error_message"] = """
<font color="red"><h2>Please mark 'Discuss' first to Add/Edit your discuss note</h2></font>"""

    return view_ballot_iesg(request, object_id, extra_context=context)

def do_ballot_send_ballot_comment_to_iesg (request, object_id) :
    argument = request.POST.copy()

    try :
        loginid = int(argument.get("loginid", "").strip())
    except :
        raise Http404
    else :
        LoginObj = IESGLogin.objects.get(id=loginid)

    ballot = get_object_or_404(BallotInfo.objects, pk=object_id)

    discuss = ballot.positions.get(ad=LoginObj).discuss
    try :
        ballot_discuss = ballot.discusses.get(ad=LoginObj)
    except :
        ballot_discuss = None

    try :
        ballot_comment = ballot.comments.get(ad=LoginObj)
    except :
        ballot_comment = None

    is_discuss_or_comment = None
    if discuss and ballot_discuss and ballot_discuss.text :
        is_discuss_or_comment = "discuss"
    elif ballot_comment and ballot_comment.text :
        is_discuss_or_comment = "comment"

    if is_discuss_or_comment == "discuss" :
        subject = ""
        text = ballot_discuss.text
    else :
        subject = ""
        text = ballot_comment.text

    draft = ballot.get_primary_draft()
    if not draft :
        raise Http404

    if is_discuss_or_comment == "comment" :
        if ballot_discuss.text :
            subject += "DISCUSS and "
        subject += "COMMENT: "
    else :
        subject += "DISCUSS: "

    subject += draft.document().filename

    return render_to_response(
        "idtracker/ballot_comment_send_to_iesg.html",
        {
            "argument" : argument,
            "LoginObj": LoginObj,
            "is_discuss_or_comment": is_discuss_or_comment,
            "draft": draft,
            "ballot": ballot,

            "subject" : subject,
            "discuss": ballot_discuss,
            "text": text,
        }, context_instance=RequestContext(request)
    )

def do_ballot_do_send_ballot_comment (request, object_id) :
    argument = request.POST.copy()

    try :
        loginid = int(argument.get("loginid", "").strip())
    except :
        raise Http404
    else :
        LoginObj = IESGLogin.objects.get(id=loginid)

    cc_val = argument.get("cc_val", "").strip()
    extra_cc = argument.get("extra_cc", "").strip()
    filename=argument.get("filename", "").strip()
    subject = argument.get("subject", "").strip()

    ballot = get_object_or_404(BallotInfo.objects, pk=object_id)
    draft = ballot.get_primary_draft()
    if not draft :
        raise Http404

    cc_val = [i.strip() for i in cc_val.split(",") if i.strip()]
    if extra_cc == "on" : # get 'state_change_notice_to' address list.
        cc_val.extend([i.strip() for i in draft.state_change_notice_to.split(",") if i.strip()])

    discuss = ballot.positions.get(ad=LoginObj).discuss
    try :
        ballot_discuss = ballot.discusses.get(ad=LoginObj)
    except :
        ballot_discuss = None

    try :
        ballot_comment = ballot.comments.get(ad=LoginObj)
    except :
        ballot_comment = None

    message = str()
    if discuss and ballot_discuss and ballot_discuss.text :
        message += """Discuss:
%s

""" % ballot_discuss.text

    if ballot_comment and ballot_comment.text :
        message += """Comment:
%s

""" % ballot_comment.text

    send_mail_text(
        request,
        "iesg@ietf.org",
        LoginObj.person.email(),
        subject,
        message,
        cc=cc_val,
    )

    return render_to_response(
       "idtracker/ballot_send_ballot_comment_done.html",
       {
           "argument" : argument,
           "LoginObj": LoginObj,
           "draft": draft,
           "ballot": ballot,
       }, context_instance=RequestContext(request)
    )

