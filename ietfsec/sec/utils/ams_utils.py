from django.conf import settings
from sec.core.models import PersonOrOrgInfo
import glob
import os
import re

def get_base(name):
    """
    Takes a draft filename and returns the basename, with file extension
    and revision number stripped
    """
    #m = re.match(r'(.*)(-\d{2}\.(txt|pdf|ps|xml))$',name)
    m = re.match(r'(.*)(-\d{2})(.*)$',name)
    return m.group(1) 

def get_revision(name):
    """
    Takes a draft filename and returns the revision, as a string.
    """
    #return name[-6:-4]
    base,ext = os.path.splitext(name)
    return base[-2:]
    
def get_last_revision(filename):
    """
    This function takes a filename, in the same form it appears in the InternetDraft record,
    no revision or extension (ie. draft-ietf-alto-reqs) and returns a string which is the 
    reivision number of the last active version of the document, the highest revision 
    txt document in the archive directory.  If no matching file is found raise exception.
    """
    files = glob.glob(os.path.join(settings.INTERNET_DRAFT_ARCHIVE_DIR,filename) + '-??.txt')
    if files:
	sorted_files = sorted(files)
	return get_revision(sorted_files[-1])
    else:
        raise Exception('last revision not found in archive')

def get_person(name):
    '''
    This function takes a string which is in the name autocomplete format "name - email (tag)" 
    and returns a person object
    '''

    match = re.search(r'\((\d+)\)', name)
    if not match:
        return None
    tag = match.group(1)
    try:
       person = PersonOrOrgInfo.objects.get(person_or_org_tag=tag)
    except (PersonOrOrgInfo.ObjectDoesNoExist, PersonOrOrgInfo.MultipleObjectsReturned):
        return None
    return person
