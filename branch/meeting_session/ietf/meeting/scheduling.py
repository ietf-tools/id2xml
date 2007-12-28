# Copyright The IETF Trust 2007, All Rights Reserved

from ietf.proceedings.models import WgMeetingSession, SessionConflict, Meeting
from ietf.idtracker.models import NotMeetingGroups, SessionRequestActivities
from ietf.utils.mail import send_mail
import datetime,time
from ietf import settings

# Cancel a meeting request 
def cancel_meeting(group, request, meeting_num, person):
    group.meeting_scheduled = 'NO'
    group.save()

    WgMeetingSession.objects.filter(group_acronym_id=group.group_acronym_id, meeting=meeting_num).delete()
    SessionConflict.objects.filter(conflict_gid=group.group_acronym_id, meeting_num=meeting_num).delete()
    SessionRequestActivities(group_acronym_id=group.group_acronym_id, activity="Session was cancelled for IETF meeting", meeting_num=meeting_num, person=person).save()

    people = [person]

    # Only email others if not in debug mode
    if settings.DEBUG == False:
        people += group.get_chairs() + group.get_directors()

    cc = [ person_or_org.email() for person_or_org in people if person_or_org.email() != '' ]

    if cc:
        # Notify everyone by email that the group is cancelled
        send_mail(request, ["session-request@ietf.org"], \
                "IETF Meeting Session Request Tool <session_request_developers@ietf.org>", \
                "%s-Cancelling a session at IETF %s" % (group.group_acronym.name, meeting_num), \
                "meeting/meeting_cancel_email.txt", {'meeting_num': meeting_num, 'group': group}, cc)

# Mark group as not meeting
def not_meeting(group, request, meeting_num, person):

    # Make entry that group is not meeting
    NoMeeting = NotMeetingGroups(group=group.group_acronym_id, meeting=meeting_num)
    NoMeeting.save()

    # Log activity
    SessionRequestActivities(group_acronym_id=group.group_acronym_id, activity="A message was sent to notify not having a session at IETF %s" % meeting_num, meeting_num=meeting_num, person=person).save()

    people = [person]

    # Only email others if not in debug mode
    if settings.DEBUG == False:
        people += group.get_chairs() + group.get_directors()

    cc = [ person_or_org.email() for person_or_org in people if person_or_org.email() != '' ]

    if cc:
        # Notify everyone by email that the group is not meeting
        send_mail(request, ["session-request@ietf.org"], \
                "IETF Meeting Session Request Tool <session_request_developers@ietf.org>", \
                "%s-Not having a session at IETF %s" % (group.group_acronym.name, meeting_num), \
                "meeting/not_meeting_email.txt", {'meeting_num': meeting_num, 'group': group}, cc)

def get_meeting_num():
    meeting = Meeting.objects.order_by('-meeting_num')[0]
    return meeting.meeting_num

def last_group_session(meeting_num, group_id):
    try:
        return WgMeetingSession.objects.filter(meeting__meeting_num__lt=meeting_num, group_acronym_id=group_id).order_by('-meeting')[0]
    except IndexError:
        return False
