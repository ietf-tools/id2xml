# Copyright The IETF Trust 2007, All Rights Reserved

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from ietf.announcements.forms import SendForm
from ietf.utils.mail import send_smtp

def send(request):
    if request.method == 'POST':
        form = SendForm(request, request.POST)

        if form.is_valid() and request.POST['op'] == 'Send':
            from email.MIMEText import MIMEText

            msg = MIMEText(form.clean_data['body'])
            msg['From'] = form.clean_data['sender']
            msg['To'] = form.clean_data['recipient']
            msg['Cc'] = form.clean_data['cc']
            msg['Bcc'] = form.clean_data['bcc']
            msg['Reply-to'] = form.clean_data['reply_to']

            send_smtp(msg)

            return HttpResponseRedirect(reverse('ietf.announcements.views.send_confirm'))

    else:
        form = SendForm(request)

    return render_to_response('announcements/send.html', { 'form': form, 'request': request })

def send_confirm(request):
    return render_to_response('announcements/send_confirm.html')
