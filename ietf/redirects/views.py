from django.http import HttpResponseRedirect,Http404
import re

from ietf.redirects.models import Redirect

def redirect(request, path="", script=""):
    if path:
	script = path + "/" + script
    try:
	redir = Redirect.objects.get(cgi=script)
    except Redirect.DoesNotExist:
	raise Http404
    url = redir.url + "/"
    try:
	url += redir.rest % request.REQUEST
    except:
	# rest had something in it that request didn't have, so just
	# redirect to the root of the tool.
	pass
    if redir.remove:
	url = re.sub(re.escape(redir.remove) + "/?$", "", url)
    return HttpResponseRedirect(url)
