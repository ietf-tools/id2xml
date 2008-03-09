# Create your views here.
import logging
import datetime
import tempfile, os

from ietf.wgcharter.models import WGCharterInfo, CharterVersion
from ietf.idtracker.models import IETFWG,Area

from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django import oldforms as forms
from django import newforms as forms

from django.newforms import form_for_model,form_for_instance

from django.contrib.auth.decorators import login_required

from ietf.wgcharter.models import  CharterVersion
from django.core.exceptions import ObjectDoesNotExist


# define to be the diff command
diff_command = "htmlwdiff"
#diff_command="diff"


def get_role(user, wgname):
    """Get the role that this person is in"""

    person_id = user.get_profile().person.person_or_org_tag

    try:
        group = IETFWG.objects.get(group_acronym__acronym=wgname)
    except IETFWG.DoesNotExist:
        return 'other'
    
    grs = [gr.name for gr in user.groups.all()]
    for grn in grs:
        if grn=="Secretariat":
            return 'sec'

    ads = [ad.person_id for ad in group.area.area.areadirector_set.all()]
    if person_id in ads:
        return 'ad'

    wgchairs = [ch.person_id for ch in group.wgchair_set.all()]
    if person_id in wgchairs:
        return 'chair'

    return 'other'


def add_charter_version(wg, state, charter_text, submitter) :
    charter=CharterVersion(state=state, text=charter_text, wg_charter_info=wg, 
                           creation_date = datetime.datetime.now(tz=None),
                           submitter=submitter)
    charter.save()
    return charter
    

def find_wgcharter_info (wgname):
    wgci_list = WGCharterInfo.objects.filter(wg_acronym=wgname)

    # TODO: Add error handling
    # for now just flip out
    if (len(wgci_list)!=1):
        raise Exception("No WG with this name")

    return wgci_list[0]


def find_charter_version (wgname, version):
    wgci = find_wgcharter_info(wgname)
    charter_list = wgci.charterversion_set.filter(version_id=version)

    if(len(charter_list)!=1):
        raise Exception("No such version found")

    return charter_list[0]
    


def current(request, wgname):
    wgci = find_wgcharter_info(wgname)
    charter_list = wgci.charterversion_set.order_by('-version_id')

    # Need to fix state once states work    
    approved_list=charter_list.filter(state='approved')
    charter=None
    if (len(approved_list)>0):
        charter=approved_list[0]
        
    return render_to_response('wgcharter/current.html',
                              {'wgname':wgname,'charter':charter,'lastdraft':charter_list[0]})
    


class AddForm(forms.Form):
    text = forms.CharField(required=True)


@login_required
def add(request, wgname):
    wgci=find_wgcharter_info(wgname)
    
    if request.method == 'POST':
	form = AddForm(request.POST)
	if form.is_valid():
	    data = form.clean_data
	    text = data['text']
            charter_version = add_charter_version(wgci, state='draft', charter_text=text, 
                                                  submitter=request.user.get_profile().person)
            id = charter_version.version_id
	    return HttpResponseRedirect('/wgcharter/%s/%d/'%(wgname,id))
    else:
	form = AddForm()
    return render_to_response('wgcharter/add.html', {'form': form,'wgname':wgname})


def list_groups(request):
    #groups = IETFWG.objects.all().select_related()
    areas = Area.objects.all().select_related()
    
    argroups={}
    for ar in areas:
         if ar.status.status == "Active":
             grlist=[]

             groups=ar.areagroup.all().select_related()
             for gr in groups:
                 grlist.append(gr.group.group_acronym.acronym)
                 
             argroups[ar.area_acronym.acronym]=grlist
    
    return render_to_response('wgcharter/groups.html', {'argroups':argroups})


def all(request, wgname):
    wgci = find_wgcharter_info(wgname)
    charters = wgci.charterversion_set.all()
    
    return render_to_response('wgcharter/all.html', {'wgname':wgname,'charterList': charters})




def diff(request, wgname, version1, version2):
    v1 = find_charter_version(wgname, version1)
    v2 = find_charter_version(wgname, version2)

    fd1, path1 = tempfile.mkstemp(suffix='.txt', text=True)
    fd2, path2 = tempfile.mkstemp(suffix='.txt', text=True)
    
    try:
        os.write(fd1,v1.text)
        os.close(fd1)
        os.write(fd2,v2.text)
        os.close(fd2)
        dc = "%s %s %s" % (diff_command,path1, path2)
        fd3 = os.popen(dc, "r")
        #diff=dc;
        diff=diff = fd3.read()
        fd3.close()
        
    finally:
        os.unlink(path1)
        os.unlink(path2)

    return render_to_response('wgcharter/diff.html',{'wgname':wgname,
                                                     'version1':v1,
                                                     'version2':v2,
                                                     'diff':diff})






class DiffForm(forms.Form):
    diffWidget = forms.ChoiceField(required=False)
    def __init__(self,wgci=None,*args,**kwargs):
	super(DiffForm, self).__init__(*args, **kwargs)
        charters = wgci.charterversion_set.all()
        choices=[]
        for i in charters:
            choices.append(("%d"%i.version_id,"%s"%i.creation_date))
        self.fields['diffWidget'].choices = choices


@login_required
def charter(request, wgname, version):
    test = ''
    wgci = find_wgcharter_info(wgname)
    diffForm = DiffForm(wgci=wgci)
    charters = wgci.charterversion_set.all().order_by('-version_id')
    default_diff=int(version)-1

    role = get_role(request.user, wgname);
    # Use this for testing
    # role='sec'   

    charter = find_charter_version(wgname, version)
    if (charter.version_id != charters[0].version_id):
        role='other'
        
    if request.method == 'POST':
	try:
	    profile = request.user.get_profile()
	    person = profile.person
	    #test += person
	except ObjectDoesNotExist:
	    role = 'other'
	    test += 'person-not-found'
	data = request.POST

        if ( data.has_key('diffWidget') ):
            data = request.POST
            diff_from = int(data['diffWidget'])
            return HttpResponseRedirect('/wgcharter/%s/%d/%s/'%(wgname,diff_from,version))

	if ( data.has_key('adReview')  and ( role=='sec' or role=='ad' or role=='chair' )):
	    test += 'adReview'
	    charter.state='ad'
            charter.save()
	if ( data.has_key('iesgProposedReview')  and ( role=='sec' or role=='ad')):
	    test += 'iesgProposedReview'
	    charter.state='internal'
            charter.save()
	if ( data.has_key('lastCall')  and ( role=='sec' or role=='ad')):
	    test += 'lastCall'
	    charter.state='external'
            charter.save()
	if ( data.has_key('iesgApprovalReview') and ( role=='sec' or role=='ad') ):
	    test = 'iesgApprovalReview'
	if ( data.has_key('approve') and (role == 'sec') ):
	    test += 'approve'
            charter.state='approved'
            charter.save()
	if ( data.has_key('dead') and (role == 'sec' or role=='ad') ):
	    test += 'dead'
            charter.state='dead'
            charter.save()
    return render_to_response('wgcharter/charter.html', 
                              {'diffForm':diffForm,
                               'wgname':wgname,'charter': charter,
                               'role':role,
                               'log':test})


# Test code
def fake_wg(request, wgname):
    wgci_list = WGCharterInfo.objects.filter(wg_acronym=wgname)
    if len(wgci_list)!=0 :
        raise Exception("Object already exists")
    
    wgci = WGCharterInfo(approved_charter_version_id=1,
                         recent_charter_version_id=2,
                         wg_acronym=wgname)
    wgci.save()
    for i in range(0,5):
        charter_text = "This is fake charter text, wg=%s version=%d" % (wgname, i)
        add_charter_version(wgci, 'draft', charter_text, "test_submitter")
    wgci.save()
    html = "<html><body>Faking up WG, WG=%s</body></html>" % wgname
    return HttpResponse(html)
