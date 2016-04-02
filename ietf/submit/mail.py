import sys, os, re, StringIO
import email, mimetypes
from datetime import datetime

from django.conf import settings
from django.core.urlresolvers import reverse as urlreverse
from django.contrib.sites.models import Site
from django.template.loader import render_to_string

from ietf.utils.log import log
from ietf.utils.mail import send_mail, send_mail_message
from ietf.doc.models import Document
from ietf.ipr.mail import utc_from_string
from ietf.mailtrigger.utils import gather_address_lists, \
    get_base_submission_message_address
from ietf.name.models import DraftSubmissionStateName
from ietf.person.models import Person
from ietf.message.models import Message
from ietf.utils.accesstoken import generate_access_token
from ietf.submit.models import SubmissionEmail, SubmissionEmailAttachment, \
    Submission


def send_submission_confirmation(request, submission):
    subject = 'Confirm submission of I-D %s' % submission.name
    from_email = settings.IDSUBMIT_FROM_EMAIL
    (to_email, cc) = gather_address_lists('sub_confirmation_requested',submission=submission)

    confirm_url = settings.IDTRACKER_BASE_URL + urlreverse('submit_confirm_submission', kwargs=dict(submission_id=submission.pk, auth_token=generate_access_token(submission.auth_key)))
    status_url = settings.IDTRACKER_BASE_URL + urlreverse('submit_submission_status_by_hash', kwargs=dict(submission_id=submission.pk, access_token=submission.access_token()))
        
    send_mail(request, to_email, from_email, subject, 'submit/confirm_submission.txt', 
              {
                'submission': submission,
                'confirm_url': confirm_url,
                'status_url': status_url,
              },
              cc=cc)

    all_addrs = to_email
    all_addrs.extend(cc)
    return all_addrs

def send_full_url(request, submission):
    subject = 'Full URL for managing submission of draft %s' % submission.name
    from_email = settings.IDSUBMIT_FROM_EMAIL
    (to_email, cc) = gather_address_lists('sub_management_url_requested',submission=submission)
    url = settings.IDTRACKER_BASE_URL + urlreverse('submit_submission_status_by_hash', kwargs=dict(submission_id=submission.pk, access_token=submission.access_token()))

    send_mail(request, to_email, from_email, subject, 'submit/full_url.txt', 
              {
                'submission': submission,
                'url': url,
              },
              cc=cc)

    all_addrs = to_email
    all_addrs.extend(cc)
    return all_addrs

def send_approval_request_to_group(request, submission):
    subject = 'New draft waiting for approval: %s' % submission.name
    from_email = settings.IDSUBMIT_FROM_EMAIL
    (to_email,cc) = gather_address_lists('sub_chair_approval_requested',submission=submission)
    if not to_email:
        return to_email

    send_mail(request, to_email, from_email, subject, 'submit/approval_request.txt', 
              {
                'submission': submission,
                'domain': Site.objects.get_current().domain,
              },
              cc=cc)
    all_addrs = to_email
    all_addrs.extend(cc)
    return all_addrs

def send_manual_post_request(request, submission, errors):
    subject = u'Manual Post Requested for %s' % submission.name
    from_email = settings.IDSUBMIT_FROM_EMAIL
    (to_email,cc) = gather_address_lists('sub_manual_post_requested',submission=submission)
    send_mail(request, to_email, from_email, subject, 'submit/manual_post_request.txt', {
        'submission': submission,
        'url': settings.IDTRACKER_BASE_URL + urlreverse('submit_submission_status', kwargs=dict(submission_id=submission.pk)),
        'errors': errors,
    }, cc=cc)


def announce_to_lists(request, submission):
    m = Message()
    m.by = Person.objects.get(name="(System)")
    if request.user.is_authenticated():
        try:
            m.by = request.user.person
        except Person.DoesNotExist:
            pass
    m.subject = 'I-D Action: %s-%s.txt' % (submission.name, submission.rev)
    m.frm = settings.IDSUBMIT_ANNOUNCE_FROM_EMAIL
    (m.to, m.cc) = gather_address_lists('sub_announced',submission=submission)
    m.body = render_to_string('submit/announce_to_lists.txt',
                              dict(submission=submission,
                                   settings=settings))
    m.save()
    m.related_docs.add(Document.objects.get(name=submission.name))

    send_mail_message(request, m)


def announce_new_version(request, submission, draft, state_change_msg):
    (to_email,cc) = gather_address_lists('sub_new_version',doc=draft,submission=submission)

    if to_email:
        subject = 'New Version Notification - %s-%s.txt' % (submission.name, submission.rev)
        from_email = settings.IDSUBMIT_ANNOUNCE_FROM_EMAIL
        send_mail(request, to_email, from_email, subject, 'submit/announce_new_version.txt',
                  {'submission': submission,
                   'msg': state_change_msg},
                  cc=cc)

def announce_to_authors(request, submission):
    (to_email, cc) = gather_address_lists('sub_announced_to_authors',submission=submission)
    from_email = settings.IDSUBMIT_ANNOUNCE_FROM_EMAIL
    subject = 'New Version Notification for %s-%s.txt' % (submission.name, submission.rev)
    if submission.group:
        group = submission.group.acronym
    elif submission.name.startswith('draft-iesg'):
        group = 'IESG'
    else:
        group = 'Individual Submission'
    send_mail(request, to_email, from_email, subject, 'submit/announce_to_authors.txt',
              {'submission': submission,
               'group': group},
              cc=cc)

# Following is from http://blog.magiksys.net/parsing-email-using-python-content
# Maybe we shoudl just use pyzmail


invalid_chars_in_filename='<>:"/\\|?*\%\''+reduce(lambda x,y:x+chr(y), range(32), '')
invalid_windows_name='CON PRN AUX NUL COM1 COM2 COM3 COM4 COM5 COM6 COM7 COM8 COM9 LPT1 LPT2 LPT3 LPT4 LPT5 LPT6 LPT7 LPT8 LPT9'.split()

# email address REGEX matching the RFC 2822 spec from perlfaq9
#    my $atom       = qr{[a-zA-Z0-9_!#\$\%&'*+/=?\^`{}~|\-]+};
#    my $dot_atom   = qr{$atom(?:\.$atom)*};
#    my $quoted     = qr{"(?:\\[^\r\n]|[^\\"])*"};
#    my $local      = qr{(?:$dot_atom|$quoted)};
#    my $domain_lit = qr{\[(?:\\\S|[\x21-\x5a\x5e-\x7e])*\]};
#    my $domain     = qr{(?:$dot_atom|$domain_lit)};
#    my $addr_spec  = qr{$local\@$domain};
# 
# Python's translation

atom_rfc2822=r"[a-zA-Z0-9_!#\$\%&'*+/=?\^`{}~|\-]+"
atom_posfix_restricted=r"[a-zA-Z0-9_#\$&'*+/=?\^`{}~|\-]+" # without '!' and '%'
atom=atom_rfc2822
dot_atom=atom  +  r"(?:\."  +  atom  +  ")*"
quoted=r'"(?:\\[^\r\n]|[^\\"])*"'
local="(?:"  +  dot_atom  +  "|"  +  quoted  +  ")"
domain_lit=r"\[(?:\\\S|[\x21-\x5a\x5e-\x7e])*\]"
domain="(?:"  +  dot_atom  +  "|"  +  domain_lit  +  ")"
addr_spec=local  +  "\@"  +  domain

email_address_re=re.compile('^'+addr_spec+'$')

class Attachment:
    def __init__(self, part, filename=None, type=None, payload=None, charset=None, content_id=None, description=None, disposition=None, sanitized_filename=None, is_body=None):
        self.part=part          # original python part
        self.filename=filename  # filename in unicode (if any) 
        self.type=type          # the mime-type
        self.payload=payload    # the MIME decoded content 
        self.charset=charset    # the charset (if any) 
        self.description=description    # if any 
        self.disposition=disposition    # 'inline', 'attachment' or None
        self.sanitized_filename=sanitized_filename # cleanup your filename here (TODO)  
        self.is_body=is_body        # usually in (None, 'text/plain' or 'text/html')
        self.content_id=content_id  # if any
        if self.content_id:
            # strip '<>' to ease searche and replace in "root" content (TODO) 
            if self.content_id.startswith('<') and self.content_id.endswith('>'):
                self.content_id=self.content_id[1:-1]

def getmailheader(header_text, default="ascii"):
    """Decode header_text if needed"""
    try:
        headers=email.Header.decode_header(header_text)
    except email.Errors.HeaderParseError:
        # This already append in email.base64mime.decode()
        # instead return a sanitized ascii string
        # this faile '=?UTF-8?B?15HXmdeh15jXqNeVINeY15DXpteUINeTJ9eV16jXlSDXkdeg15XXldeUINem15PXpywg15TXptei16bXldei15nXnSDXqdecINek15zXmdeZ?==?UTF-8?B?157XldeR15nXnCwg157Xldek16Ig157Xl9eV15wg15HXodeV15bXnyDXk9ec15DXnCDXldeh15gg157Xl9eR16rXldeqINep15wg15HXmdeQ?==?UTF-8?B?15zXmNeZ?='
        return header_text.encode('ascii', 'replace').decode('ascii')
    else:
        for i, (text, charset) in enumerate(headers):
            try:
                headers[i]=unicode(text, charset or default, errors='replace')
            except LookupError:
                # if the charset is unknown, force default 
                headers[i]=unicode(text, default, errors='replace')
        return u"".join(headers)

def getmailaddresses(msg, name):
    """retrieve addresses from header, 'name' supposed to be from, to,  ..."""
    addrs=email.utils.getaddresses(msg.get_all(name, []))
    for i, (name, addr) in enumerate(addrs):
        if not name and addr:
            # only one string! Is it the address or is it the name ?
            # use the same for both and see later
            name=addr

        try:
            # address must be ascii only
            addr=addr.encode('ascii')
        except UnicodeError:
            addr=''
        else:
            # address must match address regex
            if not email_address_re.match(addr):
                addr=''
        addrs[i]=(getmailheader(name), addr)
    return addrs

def get_filename(part):
    """Many mail user agents send attachments with the filename in 
    the 'name' parameter of the 'content-type' header instead 
    of in the 'filename' parameter of the 'content-disposition' header.
    """
    filename=part.get_param('filename', None, 'content-disposition')
    if not filename:
        filename=part.get_param('name', None) # default is 'content-type'

    if filename:
        # RFC 2231 must be used to encode parameters inside MIME header
        filename=email.Utils.collapse_rfc2231_value(filename).strip()

    if filename and isinstance(filename, str):
        # But a lot of MUA erroneously use RFC 2047 instead of RFC 2231
        # in fact anybody miss use RFC2047 here !!!
        filename=getmailheader(filename)

    return filename

def _search_message_bodies(bodies, part):
    """recursive search of the multiple version of the 'message' inside 
    the the message structure of the email, used by search_message_bodies()"""

    type=part.get_content_type()
    if type.startswith('multipart/'):
        # explore only True 'multipart/*' 
        # because 'messages/rfc822' are also python 'multipart' 
        if type=='multipart/related':
            # the first part or the one pointed by start 
            start=part.get_param('start', None)
            related_type=part.get_param('type', None)
            for i, subpart in enumerate(part.get_payload()):
                if (not start and i==0) or (start and start==subpart.get('Content-Id')):
                    _search_message_bodies(bodies, subpart)
                    return
        elif type=='multipart/alternative':
            # all parts are candidates and latest is best
            for subpart in part.get_payload():
                _search_message_bodies(bodies, subpart)
        elif type in ('multipart/report',  'multipart/signed'):
            # only the first part is candidate
            try:
                subpart=part.get_payload()[0]
            except IndexError:
                return
            else:
                _search_message_bodies(bodies, subpart)
                return

        elif type=='multipart/signed':
            # cannot handle this
            return

        else:
            # unknown types must be handled as 'multipart/mixed'
            # This is the peace of code could probably be improved, I use a heuristic : 
            # - if not already found, use first valid non 'attachment' parts found
            for subpart in part.get_payload():
                tmp_bodies=dict()
                _search_message_bodies(tmp_bodies, subpart)
                for k, v in tmp_bodies.iteritems():
                    if not subpart.get_param('attachment', None, 'content-disposition')=='':
                        # if not an attachment, initiate value if not already found
                        bodies.setdefault(k, v)
            return
    else:
        bodies[part.get_content_type().lower()]=part
        return

    return

def search_message_bodies(mail):
    """search message content into a mail"""
    bodies=dict()
    _search_message_bodies(bodies, mail)
    return bodies

def get_mail_contents(msg):
    """split an email in a list of attachments"""

    attachments=[]

    # retrieve messages of the email
    bodies=search_message_bodies(msg)
    # reverse bodies dict
    parts=dict((v,k) for k, v in bodies.iteritems())

    # organize the stack to handle deep first search
    stack=[ msg, ]
    while stack:
        part=stack.pop(0)
        type=part.get_content_type()
        if type.startswith('message/'):
            # ('message/delivery-status', 'message/rfc822', 'message/disposition-notification'):
            # I don't want to explore the tree deeper her and just save source using msg.as_string()
            # but I don't use msg.as_string() because I want to use mangle_from_=False 
            from email.Generator import Generator
            fp = StringIO.StringIO()
            g = Generator(fp, mangle_from_=False)
            g.flatten(part, unixfrom=False)
            payload=fp.getvalue()
            filename='mail.eml'
            attachments.append(Attachment(part, filename=filename, type=type, payload=payload, charset=part.get_param('charset'), description=part.get('Content-Description')))
        elif part.is_multipart():
            # insert new parts at the beginning of the stack (deep first search)
            stack[:0]=part.get_payload()
        else:
            payload=part.get_payload(decode=True)
            charset=part.get_param('charset')
            filename=get_filename(part)

            disposition=None
            if part.get_param('inline', None, 'content-disposition')=='':
                disposition='inline'
            elif part.get_param('attachment', None, 'content-disposition')=='':
                disposition='attachment'

            attachments.append(Attachment(part, filename=filename, type=type, payload=payload, charset=charset, content_id=part.get('Content-Id'), description=part.get('Content-Description'), disposition=disposition, is_body=parts.get(part)))

    return attachments

def decode_text(payload, charset, default_charset):
    if charset:
        try:
            return payload.decode(charset), charset
        except UnicodeError:
            pass

    if default_charset and default_charset!='auto':
        try:
            return payload.decode(default_charset), default_charset
        except UnicodeError:
            pass

    for chset in [ 'ascii', 'utf-8', 'utf-16', 'windows-1252', 'cp850' ]:
        try:
            return payload.decode(chset), chset
        except UnicodeError:
            pass

    return payload, None


def process_response_email(msg):
    """Saves an incoming message.  msg=string.  Message "To" field is expected to
    be in the format ietf-submit+[identifier]@ietf.org.  Expect to find a message with
    a matching value in the reply_to field, associated to a submission.
    Create a Message object for the incoming message and associate it to
    the original message via new SubmissionEvent"""
    message = email.message_from_string(msg)
    to = message.get('To')

    # exit if this isn't a response we're interested in (with plus addressing)
    local,domain = get_base_submission_message_address().split('@')
    if not re.match(r'^{}\+[a-zA-Z0-9_\-]{}@{}'.format(local,'{16}',domain),to):
        return None

    try:
        to_message = Message.objects.get(reply_to=to)
    except Message.DoesNotExist:
        log('Error finding matching message ({})'.format(to))
        return None

    try:
        submission = to_message.manualevents.first().submission
    except:
        log('Error processing message ({})'.format(to))
        return None

    if not submission:
        log('Error processing message - no submission ({})'.format(to))
        return None

    attachments = get_mail_contents(message)
    body=''
    for attach in attachments:
        if attach.is_body == 'text/plain' and attach.disposition == None:
            payload, used_charset=decode_text(attach.payload, attach.charset, 'auto')
            body = body + payload + '\n'

    by = Person.objects.get(name="(System)")
    msg = submit_message_from_message(message, body, by)

    submission_email_event = SubmissionEmail.objects.create(
            submission = submission,
            msgtype = 'msgin',
            by = by,
            message = msg,
            in_reply_to = to_message
    )

    save_submission_email_attachments(submission_email_event, attachments)

    log(u"Received submission email from %s" % msg.frm)
    return msg


def add_submission_email(remote_ip, name, message, by, msgtype):
    """Add email to submission history"""

    #in_reply_to = form.cleaned_data['in_reply_to']
    # create Message
    attachments = get_mail_contents(message)
    body=''
    for attach in attachments:
        if attach.is_body == 'text/plain' and attach.disposition == None:
            payload, used_charset=decode_text(attach.payload, attach.charset, 'auto')
            body = body + payload + '\n'

    msg = submit_message_from_message(message, body, by)

    try:
        submission = Submission.objects.get(name=name)
    except Submission.DoesNotExist:
        # create Submission using the name
        try:
            submission = Submission.objects.create(
                    state=DraftSubmissionStateName.objects.get(slug="secr-submit"),
                    remote_ip=remote_ip,
                    name=name,
                    title=name,
                    note="",
                    submission_date=datetime.date.today(),
                    replaces="",
            )
        except Exception as e:
            log("Exception: %s\n" % e)
            raise

    submission_email_event = SubmissionEmail.objects.create(
            submission = submission,
            msgtype = msgtype,
            by = by,
            message = msg)
    #in_reply_to = in_reply_to

    save_submission_email_attachments(submission_email_event, attachments)
        
        
def submit_message_from_message(message,body,by=None):
    """Returns a ietf.message.models.Message.  msg=email.Message
        A copy of mail.message_from_message with different body handling
    """
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
            body = body,
            time = utc_from_string(message['date'])
    )
    return msg

def save_submission_email_attachments(submission_email_event, attachments):
    for attach in attachments:
        if attach.disposition != 'attachment':
            continue

        payload, used_charset=decode_text(attach.payload, attach.charset, 'auto')

        name = submission_email_event.submission.name

        SubmissionEmailAttachment.objects.create(submission_email = submission_email_event,
                                                 filename=attach.filename,
                                                 body=payload)
