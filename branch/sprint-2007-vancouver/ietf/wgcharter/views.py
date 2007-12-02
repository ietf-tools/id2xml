# Create your views here.
from django.http import HttpResponse
import datetime

def current(request, wgname):
    html = "<html><body>Current Draft View, WG=%s</body></html>" % wgname
    return HttpResponse(html)

def list(request, wgname):
    html = "<html><body>List Drafts View, WG=%s</body></html>"  % wgname
    return HttpResponse(html)

def diff(request, wgname, version1, version2):
    html = "<html><body>Diff Drafts View, WG=%s, first=%s, second=%s</body></html>" % (wgname, version1, version2)
    return HttpResponse(html)

def draft(request, wgname, version):
    html = "<html><body>Draft Drafts View, WG=%s, version=%s</body></html>" % (wgname, version)
    return HttpResponse(html)

def draft_status(request, wgname, version):
    html = "<html><body>Status Drafts View, WG=%s, version=%s</body></html>" % (wgname, version)
    return HttpResponse(html)
