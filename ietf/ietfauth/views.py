# Copyright The IETF Trust 2007, All Rights Reserved
from django.conf import settings
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.http import HttpResponseRedirect
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from ietf.idtracker.models import PersonOrOrgInfo
from ietf.ietfauth.models import UserMap
from ietf.ietfauth.forms import EmailForm, ChallengeForm, PWForm, email_hash
from ietf.utils.mail import send_mail
from ietf.utils.users import create_user
from ietf.utils.log import log
import time

def password_request(request):
    if request.method == 'POST':
	form = EmailForm(request.POST)
	if form.is_valid():
	    timestamp = int(time.time())
	    email = form.clean_data['email']
	    hash = email_hash(email, timestamp)
	    site = Site.objects.get_current()
	    context = {'timestamp': timestamp, 'email': email, 'hash': hash, 'days': settings.PASSWORD_DAYS, 'site': site}
	    send_mail(request, email, None, 'IETF Datatracker Password',
			'registration/password_email.txt', context)
	    return render_to_response('registration/challenge_sent.html', context,
			context_instance=RequestContext(request))
    else:
	form = EmailForm()
    return render_to_response('registration/password_request.html', {'form': form},
		context_instance=RequestContext(request))

def password_return(request):
    form = ChallengeForm(request.REQUEST)
    if form.is_valid():
	email = form.clean_data['email']
	try:
	    user = User.objects.get(email__iexact=email)
	    person = None
	except User.DoesNotExist:
	    user = None
	    try:
		person = PersonOrOrgInfo.objects.distinct().get(emailaddress__address__iexact=email)
		try:
		    usermap = UserMap.objects.get(person=person)
		    user = usermap.user
		except UserMap.DoesNotExist:
		    pass
	    except PersonOrOrgInfo.DoesNotExist:
		person = None
	if user or person:
	    # form to get a password, either for reset or new user
	    if request.method == 'POST':
		pwform = PWForm(request.POST)
		if pwform.is_valid():
		    pw = pwform.clean_data['password']
		    if user:
			user.set_password(pw)
			user.save()
			return HttpResponseRedirect('changed/')
		    else:
			create_user(None, email, person, pw=pw)
			return HttpResponseRedirect('created/')
	    else:
		pwform = PWForm()
	    return render_to_response('registration/password_form.html', {'u': user, 'person': person, 'form': form, 'pwform': pwform},
		    context_instance=RequestContext(request))
	else:
	    # hand off for manual handling.
	    # TO DO: See if there is anything to automate here.
	    # What does I-D Submission Tool do when it needs to
	    # create a new person?
	    return render_to_response('registration/manual_handling.html', {},
		    context_instance=RequestContext(request))
    else:
	log("bad challenge for %s: %s" % (form.data.get('email', '<None>'), form.errors.as_text().replace('\n', ' ').replace('   *', ':')))
	return render_to_response('registration/bad_challenge.html', {'form': form, 'days': settings.PASSWORD_DAYS},
		context_instance=RequestContext(request))
