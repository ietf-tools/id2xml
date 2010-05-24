from ietf.idtracker.models import DocumentComment, BallotInfo, IESGLogin
from ietf.idrfc.mails import *

def add_document_comment(request, doc, text, include_by=True, ballot=None):
    login = IESGLogin.objects.get(login_name=request.user.username)
    if include_by:
        text += " by %s" % login

    c = DocumentComment()
    c.document = doc.idinternal
    c.public_flag = True
    c.version = doc.revision_display()
    c.comment_text = text
    c.created_by = login
    if ballot:
        c.ballot = ballot
    c.rfc_flag = doc.idinternal.rfc_flag
    c.save()

def make_last_call(request, doc):
    try:
        ballot = doc.idinternal.ballot
    except BallotInfo.DoesNotExist:
        ballot = BallotInfo()
        ballot.ballot = doc.idinternal.ballot_id
        ballot.active = False
        ballot.last_call_text = generate_last_call_announcement(request, doc)
        ballot.approval_text = generate_approval_mail(request, doc)
        ballot.ballot_writeup = render_to_string("idrfc/ballot_writeup.txt")
        ballot.save()

    send_last_call_request(request, doc, ballot)
    add_document_comment(request, doc, "Last Call was requested")

def log_state_changed(request, doc, by):
    change = u"State changed to <b>%s</b> from <b>%s</b> by <b>%s</b>" % (
        doc.idinternal.docstate(),
        format_document_state(doc.idinternal.prev_state, doc.
                              idinternal.prev_sub_state),
        by)

    c = DocumentComment()
    c.document = doc.idinternal
    c.public_flag = True
    c.version = doc.revision_display()
    c.comment_text = change
    c.created_by = by
    c.result_state = doc.idinternal.cur_state
    c.origin_state = doc.idinternal.prev_state
    c.rfc_flag = doc.idinternal.rfc_flag
    c.save()

    email_state_changed(request, doc, strip_tags(change))

    return change
