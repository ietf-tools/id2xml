# Copyright The IETF Trust 2008, All Rights Reserved

from django.template import Context, RequestContext
from django.contrib.sites.models import Site
from django.shortcuts import render_to_response

def MaybeRequestContext( request=None ):
    if request is None:
	return Context( { "site": Site.objects.get_current() } )
    else:
	return RequestContext( request )

def render( request, template, context ):
    return render_to_response(template, context, context_instance=RequestContext( request ) )
