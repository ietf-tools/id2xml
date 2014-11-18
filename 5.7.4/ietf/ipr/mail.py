import base64
import email
import datetime
from dateutil.tz import tzoffset
import os
import pytz
from django.conf import settings
from ietf.ipr.models import IprEvent
from ietf.message.models import Message
from ietf.person.models import Person
from ietf.utils.log import log

# ----------------------------------------------------------------
# Date Functions
# ----------------------------------------------------------------
def get_body(msg):
    """Returns the body of the message.  A Basic routine to walk parts of a MIME message
    concatenating text/plain parts"""
    body = ''
    for part in msg.walk():
        if part.get_content_type() == 'text/plain':
            body = body + part.get_payload() + '\n'
    return body
    
def is_aware(date):
    """Returns True if the date object passed in timezone aware, False if naive.
    See http://docs.python.org/2/library/datetime.html section 8.1.1
    """
    if not isinstance(date,datetime.datetime):
        return False
    if date.tzinfo and date.tzinfo.utcoffset(date) is not None:
        return True
    return False
    
def parsedate_to_datetime(date):
    """Returns a datetime object from string.  May return naive or aware datetime.

    This function is from email standard library v3.3, converted to 2.x
    http://python.readthedocs.org/en/latest/library/email.util.html
    """
    try:
        tuple = email.utils.parsedate_tz(date)
        if not tuple:
            return None
        tz = tuple[-1]
        if tz is None:
            return datetime.datetime(*tuple[:6])
        return datetime.datetime(*tuple[:6],tzinfo=tzoffset(None,tz))
    except ValueError:
        return None

def utc_from_string(s):
    date = parsedate_to_datetime(s)
    if is_aware(date):
        return date.astimezone(pytz.utc).replace(tzinfo=None)
    else:
        return date

# ----------------------------------------------------------------
# Email Functions
# ----------------------------------------------------------------
def get_reply_to():
    """Returns a new reply-to address for use with an outgoing message.  This is an
    address with "plus addressing" using a random string."""
    local,domain = settings.IPR_EMAIL_TO.split('@')
    while True:
        rand = base64.urlsafe_b64encode(os.urandom(12))
        address = "{}+{}@{}".format(local,rand,domain)
        q = Message.objects.filter(reply_to=address)
        if not q:
            break
    return address
    
def message_from_message(message,by=None):
    """Returns a ietf.message.models.Message.  msg=email.Message"""
    if not by:
        by = Person.objects.get(name="(System)")
    msg = Message.objects.create(
        by = by,
        subject = message.get('subject',''),
        frm = message.get('from',''),
        to = message.get('to',''),
        cc = message.get('cc',''),
        bcc = message.get('bcc',''),
        reply_to = message.get('reply_to',''),
        body = get_body(message),
        time = utc_from_string(message['date'])
    )
    return msg

def process_response_email(msg):
    """Saves an incoming message.  msg=string.  Message "To" field is expected to
    be in the format ietf-ipr+[identifier]@ietf.org.  Expect to find a message with
    a matching value in the reply_to field, associated to an IPR disclosure through
    IprEvent.  Create a Message object for the incoming message and associate it to
    the original message via new IprEvent"""
    message = email.message_from_string(msg)
    to = message.get('To')

    try:
        to_message = Message.objects.get(reply_to=to)
    except IprEvent.DoesNotExist:
        log('Error finding matching message ({})'.format(to))
        return

    try:
        disclosure = to_message.msgevents.first().disclosure
    except:
        log('Error processing message ({})'.format(to))
        return

    ietf_message = message_from_message(message)
    IprEvent.objects.create(
        type_id = 'msgin',
        by = Person.objects.get(name="(System)"),
        disclosure = disclosure,
        message = ietf_message,
        in_reply_to = to_message
    )
    
    return ietf_message