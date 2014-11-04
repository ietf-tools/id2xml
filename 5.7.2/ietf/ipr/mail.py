import email
import datetime
from dateutil.tz import tzoffset
import pytz
import re
from ietf.utils.log import log
from ietf.message.models import Message
from ietf.person.models import Person

# ----------------------------------------------------------------
# Globals
# ----------------------------------------------------------------
response_pattern = re.compile(r'ietf-ipr\+([^@]+)@ietf.org')
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

def message_from_message(message,by=None,save=True):
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
    if save:
        msg.save()
    return msg
    
def message_from_string(s,save=True):
    """Returns ietf.message.models.Message. s=string"""
    message = email.message_from_string(s)
    return message_from_message(message,save=save)
    
def create_response_email(msg):
    """Saves an incoming message.  msg=string"""
    message = email.message.from_string(msg)
    to = message.get('To')
    match = response_pattern.match(to)
    if not match:
        log('Error parsing response digest ({})'.format(to))
        return
    else:
        digest = match.groups()[0]
        
    try:
        event = IprEvent.objects.get(response_digest=digest)
    except IprEvent.DoesNotExist:
        log('Error finding referenced message ({})'.format(to))
        return
    
    messasge = message_from_string(msg)
    IprEvent.objects.create(
        type_id = 'incoming',
        by = Person.objects.get(name="(System)"),
        disclosure = event.disclosure,
        message = event.message,
        in_reply_to = message
    )
    
    return message