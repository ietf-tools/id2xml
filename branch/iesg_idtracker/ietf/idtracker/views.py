# Copyright The IETF Trust 2007, All Rights Reserved

# Create your views here.
from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect
from django import newforms as forms
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.list_detail import object_detail, object_list
from ietf.idtracker.models import InternetDraft, IDInternal, IDState, IDSubState, Rfc, DocumentWrapper, IESGLogin, TelechatDates, IDNextState, BallotInfo, Position
from ietf.idtracker.forms import IDSearch, EmailFeedback, IDDetail, BallotSearch
from ietf.utils.mail import send_mail_text
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
    ballot_search_form = BallotSearch()
    return render_to_response('idtracker/idtracker_search.html', {
	'form': form,
        'ballot_search_form': ballot_search_form,
	'matches': matches,
	'searching': searching,
        'mode': mode,
        'default_search': default_search,
      }, context_instance=RequestContext(request))

# proof of concept, orphaned for now
def edit_idinternal(request, idinternal=None):
    mode = get_tracker_mode(request)
    global LoginObj
    ##draft = InternetDraft.objects.get(pk=id)
    #draft = get_object_or_404(InternetDraft.objects, pk=id)
    #IDEntryForm = forms.models.form_for_instance(object.draft)
    ## todo: POST handling for idform
    if idinternal:
	#EntryForm = forms.models.form_for_instance(idinternal)
        try:
            next_state_object = IDNextState.objects.filter(cur_state=idinternal.cur_state)
	except IDNextState.DoesNotExist:
            next_state_object = []
        if request.method == 'POST':
	    #form = EntryForm(request.POST)
	    idform = IDDetail(request.POST)
            if "next_state_button" in request.POST:
                next_state_id = IDState.objects.get(state= request.POST['next_state_button']).document_state_id
                print next_state_id
	    if idform.is_valid():
		idform.save(idinternal,request,LoginObj)
		return HttpResponseRedirect(".")	# really want here
	else:
            idform = IDDetail({
                'intended_status':idinternal.draft.intended_status.intended_status_id,
                'agenda': idinternal.agenda,
                'telechat_date': idinternal.telechat_date,
                'job_owner': idinternal.job_owner.id,
                'status_date': idinternal.status_date,
                'note': idinternal.note,
                'public_flag': True,
                'state_change_notice_to': idinternal.state_change_notice_to,
                 })
	    #form = EntryForm()
    else:
	idform = None
    if mode == 'IETF':
        fontsize = 3
    else:
        fontsize = 4
    return render_to_response('idtracker/idinternal_detail.html', {
        'object': idinternal,
        'next_state_object': next_state_object,
	'idform': idform,
        'mode': mode,
        'fontsize':fontsize,
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

# calling sequence similar to object_detail, but we have different
# 404 handling: if the draft exists, render a not-found template.
def view_id(request, queryset, slug, slug_field):
    mode = get_tracker_mode(request)
    try:
	object = IDInternal.objects.get(draft__filename=slug, rfc_flag=0)
    except IDInternal.DoesNotExist:
	draft = get_object_or_404(InternetDraft, filename=slug)
	return render_to_response('idtracker/idinternal_notfound.html', {'draft': draft}, context_instance=RequestContext(request))
    return edit_idinternal(request,object)
    return render_to_response('idtracker/idinternal_detail.html', {'object': object}, context_instance=RequestContext(request))

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
    object = get_object_or_404(IDInternal, pk=object_id, rfc_flag=1)
    return render_to_response('idtracker/idinternal_detail.html', {'object': object}, context_instance=RequestContext(request))

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

