# Create your views here.

from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django import oldforms as forms
from django import newforms as forms
from django.newforms import form_for_model,form_for_instance

from ietf.wgcharter.models import  CharterVersion


def current(request, wgname):
    html = "<html><body>Current Draft View, WG=%s</body></html>" % wgname
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
    charters = CharterVersion.objects.all()
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
