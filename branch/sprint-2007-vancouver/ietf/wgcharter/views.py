# Create your views here.
import logging

from ietf.wgcharter.models import WGCharterInfo, CharterVersion

from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django import oldforms as forms
from django import newforms as forms

from django.newforms import form_for_model,form_for_instance

from ietf.wgcharter.models import  CharterVersion

def find_wgcharter_info (wgname):
    wgci_list = WGCharterInfo.objects.filter(wg_acronym=wgname)

    # TODO: Add error handling
    # for now just flip out
    if (len(wgci_list)!=1):
        raise Exception("No WG with this name")

    return wgci_list[0]


def current(request, wgname):
    wgci_list = WGCharterInfo.objects.filter(wg_acronym=wgname)
    html = "<html><body>Current Draft View, WG=%s, %d wgs" % (wgname, len(wgci_list))
    wgci = wgci_list[0]  # better not be more than one
    return HttpResponse(html)

class AddForm(forms.Form):
    text = forms.CharField(required=True)

def add(request, wgname):
    if request.method == 'POST':
	form = AddForm(request.POST)
	if form.is_valid():
	    data = form.clean_data
	    text = data['text']
	    #TODO create new charter here with the text=text, wg-wgname, and get the id 
	    id =22
	    return HttpResponseRedirect('/wgcharter/%s/%d/status'%(wgname,id))
    else:
	form = AddForm()
    return render_to_response('wgcharter/add.html', {'form': form})

def list(request, wgname):
    wgci = find_wgcharter_info(wgname)
    charters = wgci.charterversion_set.all()

    logging.error("WG %s, num charters %d",wgname,len(charters))
    
    return render_to_response('wgcharter/all.html', {'wgname':wgname,'charterList': charters})

def diff(request, wgname, version1, version2):
    html = "<html><body>Diff Drafts View, WG=%s, first=%s, second=%s</body></html>" % (wgname, version1, version2)
    return HttpResponse(html)

def draft(request, wgname, version):
    html = "<html><body>Draft Drafts View, WG=%s, version=%s</body></html>" % (wgname, version)
    return HttpResponse(html)

def draft_status(request, wgname, version):
    html = "<html><body>Status Drafts View, WG=%s, version=%s</body></html>" % (wgname, version)
    return HttpResponse(html)


def add_charter_version(wg, state, charter_text, submitter) :
    charter=CharterVersion(state=state, text=charter_text, wg_charter_info=wg)
    charter.save()
    charters = wg.charterversion_set.all()
    
    
# Test code
def fake_wg(request, wgname):
    wgci_list = WGCharterInfo.objects.filter(wg_acronym=wgname)
    if len(wgci_list)!=0 :
        raise Exception("Object already exists")
    
    wgci = WGCharterInfo(approved_charter_version_id=1,recent_charter_version_id=2,wg_acronym=wgname)
    wgci.save()
    for i in range(0,5):
        charter_text = "This is fake charter text, wg=%s version=%d" % (wgname, i)
        add_charter_version(wgci, 'draft', charter_text, "test_submitter")
    wgci.save()
    html = "<html><body>Faking up WG, WG=%s</body></html>" % wgname
    return HttpResponse(html)
