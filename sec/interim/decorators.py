from django.utils.functional import wraps
from django.shortcuts import render_to_response

from sec.interim.models import *

def wgchair_required(func):
    """
    This decorator checks that the user making the request has access to the
    object being requested.  Expects one of the following three keyword
    arguments: group_id, meeting_id, slide_id.  For access to be granted
    the REMOTE_USER must be found in LegacyWgPassword and the user must 
    be a chair of the group owning the object. 
    """
    def wrapper(request, *args, **kwargs):
        user = request.META.get('REMOTE_USER','')
        try:
            userid = LegacyWgPassword.objects.get(login_name=user)
        except LegacyWgPassword.DoesNotExist:
            return render_to_response('interim/unauthorized.html',{
                'user_name':userid,
                'group_name':group_id}
            )

        if 'group_id' in kwargs:
            group_id = kwargs['group_id']
        elif 'meeting_id' in kwargs:
            meeting = InterimMeeting.objects.using('interim').get(id=kwargs['meeting_id'])
            group_id = meeting.group_acronym_id
        elif 'slide_id' in kwargs:
            slide = Slides.objects.using('interim').get(id=kwargs['slide_id'])
            group_id = slide.meeting.group_acronym_id

        if WGChair.objects.filter(group_acronym=group_id,person=userid): 
            return func(request, *args, **kwargs)
        else:
            return render_to_response('interim/unauthorized.html',{
                'user_name':userid,
                'group_name':group_id}
            )

    return wraps(func)(wrapper)
