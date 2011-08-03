from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from sec.core.models import Acronym, AreaDirector, AreaGroup, IESGLogin, IETFWG, IRTF, InterimMeeting, LegacyWgPassword, Meeting, WGChair, WGSecretary
#from sec.groups.models import WGSecretary

import itertools

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

def get_meeting_or_404(id):
    '''
    This function takes an id (integer or string) and returns a GenericMeeting object which 
    is a wrapper for Meeting and InterimMeeting types
    '''
    id = int(id)
    if id < 200:
        meeting = get_object_or_404(Meeting, meeting_num=id)
    else:
        meeting = get_object_or_404(InterimMeeting, meeting_num=id)
    
    return meeting
    
def get_my_groups(request):
    '''
    This function takes a request object, for user info, and returns a list of group objects
    the user has access to.  A secretariat user has access to all groups, other users have
    access to groups they chair or are secretaries of.  ADs have access to all groups in their
    area.
    '''
    # if user is secretariat grant full access
    if request.user_is_secretariat:
        groups = IETFWG.objects.filter(status=1)
    # get groups for AD user
    elif request.user_is_ad:
        iesg = IESGLogin.objects.get(login_name=request.META['REMOTE_USER'])
        area_director = AreaDirector.objects.get(person=iesg.person)
        ags = AreaGroup.objects.filter(area=area_director.area)
        groups = [ x.group for x in ags if x.group.status.status_id==1 ]
    # otherwise user is chair or secretariat
    else:
        try:
            # restrict to active groups only
            legacy = LegacyWgPassword.objects.get(login_name=request.META['REMOTE_USER'])
            chairs = WGChair.objects.filter(person=legacy,group_acronym__status=1)
            secretaries = WGSecretary.objects.filter(person=legacy,group_acronym__status=1)
            groups = [ c.group_acronym for c in itertools.chain(chairs,secretaries) ]
        except ObjectDoesNotExist:
            groups = []

        # make sure the groups list contains no dupes in the off chance someone is
        # both a chair and secretary of the same group
        s = set(groups)
        groups = list(s)

    # sort the groups list by group acronym
    groups = sorted(groups, key=lambda a: a.group_acronym.acronym)
    
    return groups
