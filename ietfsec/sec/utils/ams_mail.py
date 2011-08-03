from sec.core.models import IETFWG, IRTFChair
from sec.roles.models import Role

def get_ad_email_list(group):
    '''
    This function takes a group (either IETFWG or IRTF) and returns the Area Director email.
    '''
    emails = []
    if isinstance(group, IETFWG):    
        acronym = group.group_acronym.acronym
        emails.append('%s-ads@tools.ietf.org' % acronym)
    else:
        emails.append(Role.objects.get(role_name='IRTF').person.email())
    return emails

def get_cc_list(group, user):
    '''
    Per Pete Resnick, at IETF 80 meeting, session request notifications
    should go to chairs,ads lists not individuals.
    input:  group: is either a IETFWG or IRTF
            user: the logged in user
    '''
    emails = []
    emails.extend(get_ad_email_list(group))
    emails.extend(get_chair_email_list(group))
    if user.email() not in emails:
        emails.append(user.email())
    return emails
    
def get_chair_email_list(group):
    '''
    This function takes a group (either IETFWG or IRTF) and returns chair email(s).
    '''
    emails = []
    if isinstance(group, IETFWG):    
        acronym = group.group_acronym.acronym
        emails.append('%s-chairs@tools.ietf.org' % acronym)
    else:
        for chair in IRTFChair.objects.filter(irtf=group):
            emails.append(chair.person.email())
    return emails
