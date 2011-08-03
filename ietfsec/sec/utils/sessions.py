from django.db import models
from sec.core.models import SessionRequestActivity

def add_session_activity(group,text,meeting,userid):
    '''
    Add a record to session_request_activites.  Based on legacy function
    input: group can be any model with the primary key as group_id or string,int
    '''
    if isinstance(group,models.Model):
        gid = group.pk
    else:
	gid = int(group)
    record = SessionRequestActivity(group_acronym_id=gid,meeting=meeting,activity=text,act_by=userid)
    record.save()
