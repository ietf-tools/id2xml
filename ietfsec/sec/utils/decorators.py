from django.utils.functional import wraps
from django.shortcuts import render_to_response, get_object_or_404

from sec.core.models import AreaDirector, AreaGroup, IETFWG, WgMeetingSession, IRTFChair, WGChair, WGSecretary
#from sec.groups.models import WGSecretary
#from sec.utils.shortcuts import get_group_or_404

def get_group_or_404(id):
    '''
    This function takes an id (integer or string) and returns the appropriate IETFWG, IRTF or 
    Acronym object representing a group, raising 404 if it is not found
    '''
    id = int(id)
    if id > 100:
        group = get_object_or_404(IETFWG, group_acronym=id)
    elif 0 < id < 100:
        group = get_object_or_404(IRTF, irtf_id=id)
    elif id < 0:
        group = get_object_or_404(Acronym, acronym_id=id)
    return group

def check_permissions(func):
    """
    This decorator checks that the user making the request has access to the
    object being requested.  Expects one of the following four keyword
    arguments: group_id, meeting_id, slide_id, session_id.  
    
    Also expects the following custom attributes on the request object:
    user_is_secretariat
    user_is_ad
    person
    """
    def wrapper(request, *args, **kwargs):
        # short circuit.  secretariat user has full access
        if request.user_is_secretariat:
            return func(request, *args, **kwargs)

        # get the parent group
        if 'group_id' in kwargs:
            group_id = kwargs['group_id']
        elif 'meeting_id' in kwargs:
            meeting = InterimMeeting.objects.get(id=kwargs['meeting_id'])
            group_id = meeting.group_acronym_id
        elif 'slide_id' in kwargs:
            slide = InterimFile.objects.get(id=kwargs['slide_id'])
            group_id = slide.meeting.group_acronym_id
        elif 'session_id' in kwargs:
            session = get_object_or_404(WgMeetingSession, session_id=kwargs['session_id'])
            group_id = session.group_acronym_id
            
        if request.user_is_ad:
            ad = AreaDirector.objects.get(person=request.person)
            ags = AreaGroup.objects.filter(area=ad.area)
            if ags.filter(group=group_id):
                return func(request, *args, **kwargs)
        else:
            if ( WGChair.objects.filter(group_acronym=group_id,person=request.person) or
            WGSecretary.objects.filter(group_acronym=group_id,person=request.person) or
            IRTFChair.objects.filter(irtf=group_id,person=request.person)):
                return func(request, *args, **kwargs)
 
        # if we get here access is denied
        group = get_group_or_404(group_id)
        return render_to_response('unauthorized.html',{
            'user_name':request.person,
            'group_name':str(group)}
        )

    return wraps(func)(wrapper)

def sec_only(func):
    """
    This decorator checks that the user making the request is a secretariat user.
    (Based on the cusotm user_is_secretariat request attribute)
    """
    def wrapper(request, *args, **kwargs):
        # short circuit.  secretariat user has full access
        if request.user_is_secretariat:
            return func(request, *args, **kwargs)
        
        return render_to_response('unauthorized.html',{
            'user_name':request.person}
        )

    return wraps(func)(wrapper)
