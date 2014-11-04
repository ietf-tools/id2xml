#!/usr/bin/python

'''
This script migrates data from the old IPR models to the new models
'''

# Set PYTHONPATH and Django environment variable for standalone script -----------------
# for file living in project/app/
import os
import sys
path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if not path in sys.path:
    sys.path.insert(0, path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'ietf.settings'
# -------------------------------------------------------------------------------------

import email
import re
import urllib2
from time import mktime, strptime
from collections import namedtuple
from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from ietf.ipr.models import *
from ietf.message.models import Message
from ietf.name.models import DocRelationshipName
from ietf.name.utils import name
from ietf.person.models import Email

# ---------------------------
# Globals
# ---------------------------
DEFAULT_CHARSET = 'latin1'
UPDATES = DocRelationshipName.objects.get(slug='updates')
URL_PATTERN = re.compile(r'https?://datatracker.ietf.org/ipr/(\d{1,4})/')
DRAFT_PATTERN = re.compile(r'draft-[a-zA-Z0-9\-]+')
DRAFT_HAS_REVISION_PATTERN = re.compile(r'.*-[0-9]{2}')

ContactFields = namedtuple('ContactFields',['name','info','email'])
system = Person.objects.get(name="(System)")

# ---------------------------
# Setup States
# ---------------------------
pending_disclosure_state = name(IprDisclosureStateName, "pending", "Pending",order=0)
parked_disclosure_state = name(IprDisclosureStateName, "parked", "Parked",order=1)
posted_disclosure_state = name(IprDisclosureStateName, "posted", "Posted",order=2)
rejected_disclosure_state = name(IprDisclosureStateName, "rejected", "Rejected",order=3)
removed_disclosure_state = name(IprDisclosureStateName, "removed", "Removed",order=4)
#unknown_disclosure_state = name(IprDisclosureStateName, "unknown", "Unknown")

no_license_license_info = name(IprLicenseTypeName, "no-licns", "No License", desc="a) No License Required for Implementers", order=1)
royalty_free_license_info = name(IprLicenseTypeName,"royalty", "Royalty Free", desc="b) Royalty-Free, Reasonable and Non-Discriminatory License to All Implementers", order=2)
reasonable_license_info = name(IprLicenseTypeName,"reason", "Reasonable", desc="c) Reasonable and Non-Discriminatory License to All Implementers with Possible Royalty/Fee", order=3)
provided_later_license_info = name(IprLicenseTypeName,"later", "Provided Later", desc="d) Licensing Declaration to be Provided Later (implies a willingness to commit to the provisions of a), b), or c) above to all implementers; otherwise, the next option 'Unwilling to Commit to the Provisions of a), b), or c) Above'. - must be selected)", order=4)
unwilling_to_commit_license_info = name(IprLicenseTypeName,"unwill", "Unwilling to Commit", desc="e) Unwilling to Commit to the Provisions of a), b), or c) Above", order=5)
see_below_license_info = name(IprLicenseTypeName,"seebelow", "See Below", desc="f) See Text Below for Licensing Declaration", order=6)
none_selected_license_info = name(IprLicenseTypeName,"noselect", "None Selected")

submitted_event = name(IprEventTypeName, "submitted", "Submitted")
posted_event = name(IprEventTypeName, "posted", "Posted")
removed_event = name(IprEventTypeName, "removed", "Removed")
rejected_event = name(IprEventTypeName, "rejected", "Rejected")
pending_event = name(IprEventTypeName, "pending","Pending")
parked_event = name(IprEventTypeName, "parked", "Parked")
msgin_event = name(IprEventTypeName, "msgin", "MsgIn")
msgout_event = name(IprEventTypeName, "msgout", "MsgOut")
comment_event = name(IprEventTypeName, "comment", "Comment")
private_comment_event = name(IprEventTypeName, 'private_comment', "Private Comment")
legacy_event = name(IprEventTypeName, "legacy", "Legacy")
update_notify = name(IprEventTypeName, "update_notify", "Update Notify")
changed_disclosure = name(IprEventTypeName,"changed_disclosure", "Changed disclosure metadata")

# ---------------------------
# Mappings
# ---------------------------
contact_type_mapping = { 1:('holder_contact_name','holder_contact_info','holder_contact_email'),
                         2:('ietfer_name','ietfer_contact_info','ietfer_contact_email'),
                         3:('submitter_name','submitter_info','submitter_email') }

contact_type_name_mapping = { 1:'holder',2:'ietfer',3:'submitter' }

field_mapping = {'telephone':'T','fax':'F','notes':'\nNotes'}

licensing_mapping = { 0:none_selected_license_info,
                      1:no_license_license_info,
                      2:royalty_free_license_info,
                      3:reasonable_license_info,
                      4:provided_later_license_info,
                      5:unwilling_to_commit_license_info,
                      6:see_below_license_info,
                      None:none_selected_license_info }

states_mapping = { 0:pending_disclosure_state,
                   1:posted_disclosure_state,
                   2:rejected_disclosure_state,
                   3:removed_disclosure_state }

# ----------------------------
# Helpers
# ----------------------------

def clear():
    """Clear existing objects to allow rerun"""
    IprDisclosureBase.objects.all().delete()
    IprEvent.objects.all().delete()
    RelatedIpr.objects.all().delete()
    IprDocRel.objects.all().delete()
    
def combine_fields(obj,fields):
    """Returns fields combined into one string.  Uses field_mapping to apply
    extra formatting for some fields."""
    data = u""
    for field in fields:
        val = getattr(obj,field)
        if val:
            if field in field_mapping:
                data += u"{}: {}\n".format(field_mapping[field],val)
            else:
                data += u"{}\n".format(val)
    return data

def create_comment(old, new, url_field, title_field=None):
    """Create an IprEvent Comment given the legacy info.
    If called with legacy_url_0 field created use LegacyMigrationIprEvent type"""
    url = getattr(old,url_field)
    if title_field:
        title_text = u"{}: {}\n".format(title_field,getattr(old,title_field))
    else:
        title_text = u""

    if url.endswith('pdf'):
        # TODO: check for file ending in txt
        data = ''
    else:
        data = get_url(url)

    # create event objects
    #desc = title_text + u"{}: {}\n\n{}".format(url_field,url,data)
    desc = title_text + u"From: {}\n\n{}".format(url,data)
    if url_field == 'legacy_url_0':
        klass = LegacyMigrationIprEvent
    else:
        klass = IprEvent
    klass.objects.create(type=legacy_event,
                            by=system,
                            disclosure=new,
                            desc=desc)

def decode_safely(data, charset=DEFAULT_CHARSET):
    """Return data decoded according to charset, but do so safely."""
    try:
        return unicode(data,charset or DEFAULT_CHARSET)
    except (UnicodeDecodeError, LookupError) as error:
        return unicode(data,DEFAULT_CHARSET,errors='replace')

def get_url(url):
    """Returns contents of URL as unicode"""
    try:
        fp = urllib2.urlopen(url)
        data = fp.read()
        fp.close()
    except Exception:
        return ''
    return decode_safely(data)

def handle_contacts(old,new):
    """
    In some cases, due to bug?, one declaration may have multiple contacts of the same
    type (see pk=2185), only process once.
    """
    seen = []
    for contact in old.contact.all():
        if contact.contact_type in seen:
            continue
        seen.append(contact.contact_type)
        fields = contact_type_mapping[contact.contact_type]
        info = combine_fields(contact,['title',
                                       'department',
                                       'address1',
                                       'address2',
                                       'telephone',
                                       'fax'])

        fields = ContactFields(*fields)
        if hasattr(new,fields.name):
            setattr(new,fields.name,contact.name)
        if hasattr(new,fields.info):
            setattr(new,fields.info,info)
        if hasattr(new,fields.email):
            setattr(new,fields.email,contact.email)

def handle_docs(old,new):
    """Create IprDocRel relationships"""
    iprdocaliases = old.iprdocalias_set.all()
    for iprdocalias in iprdocaliases:
        IprDocRel.objects.create(disclosure=new.iprdisclosurebase_ptr,
                                 document=iprdocalias.doc_alias,
                                 sections=old.document_sections,
                                 revisions=iprdocalias.rev)

    # check other_designations for related documents
    matches = DRAFT_PATTERN.findall(old.other_designations)
    for name,rev in map(split_revision,matches):
        try:
            draft = Document.objects.get(type='draft',name=name)
        except Document.DoesNotExist:
            print "WARN: couldn't find other_designation: {}".format(name)
            continue
        if not IprDocRel.objects.filter(disclosure=new.iprdisclosurebase_ptr,document__in=draft.docalias_set.all()):
            IprDocRel.objects.create(disclosure=new.iprdisclosurebase_ptr,
                                     document=draft.canonical_docalias(),
                                     sections=old.document_sections,
                                     revisions=rev)

def handle_legacy_fields(old,new):
    """Get contents of URLs in legacy fields and save in an IprEvent"""
    # legacy_url_0
    if old.legacy_url_0:
        create_comment(old,new,'legacy_url_0')

    # legacy_url_1
    # Titles that start with "update" will be converted to RelatedIpr later
    if old.legacy_title_1 and not old.legacy_title_1.startswith('Update'):
        create_comment(old,new,'legacy_url_1','legacy_title_1')

    # legacy_url_2

def handle_licensing(old,new):
    """Map licensing information into new object.  ThirdParty disclosures
    do not have any."""
    if isinstance(new, (GenericIprDisclosure,NonDocSpecificIprDisclosure)):
        context = {'option':old.licensing_option,'info':old.comments}
        new.statement = render_to_string("ipr/migration_licensing.txt",context)
    elif isinstance(new, HolderIprDisclosure):
        new.licensing = licensing_mapping[old.licensing_option]
        new.licensing_comments = old.comments
        new.submitter_claims_all_terms_disclosed = old.lic_checkbox

def handle_notification(rec):
    """Map IprNotification to IprEvent and Message objects.
    
    NOTE: some IprNotifications contain non-ascii text causing
    email.message_from_string() to fail, hence the workaround
    """
    parts = rec.notification.split('\r\n\r\n',1)
    msg = email.message_from_string(parts[0])
    msg.set_payload(parts[1])
    disclosure = IprDisclosureBase.objects.get(pk=rec.ipr.pk)
    type = IprEventTypeName.objects.get(slug='msgout')
    subject = msg['subject']
    subject = (subject[:252] + '...') if len(subject) > 255 else subject
    message = Message.objects.create(
        by = system,
        subject = subject,
        frm = msg.get('from'),
        to = msg.get('to'),
        cc = msg.get('cc'),
        body = msg.get_payload()
    )
    event = IprEvent.objects.create(
        type = type,
        by = system,
        disclosure = disclosure,
        desc = 'Sent Message',
        message = message
    )
    # go back fix IprEvent.time
    time_string = rec.date_sent.strftime('%Y-%m-%d ') + rec.time_sent
    struct = strptime(time_string,'%Y-%m-%d %H:%M:%S')
    event.time = datetime.date.fromtimestamp(mktime(struct))
    event.save()
    
def handle_patent_info(old,new):
    """Map patent info.  patent_info and applies_to_all are mutually exclusive"""
    if old.applies_to_all and hasattr(new, 'applies_to_all'):
        new.applies_to_all = True
        return None
    if not hasattr(new, 'patent_info'):
        return None
    data = combine_fields(old,['patents','date_applied','country','notes'])
    new.patent_info = data
    if old.is_pending == 1:
        new.has_patent_pending = True

def handle_rel(iprdetail):
    """Create RelatedIpr relationships based on legacy data"""
    new = IprDisclosureBase.objects.get(pk=iprdetail.pk)

    # build relationships from IprUpdates
    # print iprdetail.id, iprdetail.updates.count()
    for iprupdate in iprdetail.updates.all():
        target = IprDisclosureBase.objects.get(pk=iprupdate.updated.pk)
        obj = RelatedIpr.objects.create(source=new,
                                        target=target,
                                        relationship=UPDATES)
        print "Created relationship: {} {} {}".format(obj.source.pk,
                                                      obj.relationship.name.lower(),
                                                      obj.target.pk)

    # build relationships from legacy_url_1
    url = iprdetail.legacy_url_1
    title = iprdetail.legacy_title_1
    if title and title.startswith('Updated by'):
        # get object id from URL
        match = URL_PATTERN.match(url)
        if match:
            id = match.groups()[0]
            try:
                source = IprDisclosureBase.objects.get(pk=id)
            except:
                print "No record for {}".format(url)
                return
            obj,created = RelatedIpr.objects.get_or_create(source=source,
                                                           target=new,
                                                           relationship=UPDATES)
            if created:
                print "Created legacy_1 relationship: {} {} {}".format(
                    obj.source.pk,
                    obj.relationship.name.lower(),
                    obj.target.pk)

def is_contact_empty(contact):
    return not any([contact.name,
                   contact.title,
                   contact.department,
                   contact.address1,
                   contact.address2,
                   contact.telephone,
                   contact.fax,
                   contact.email])

def split_revision(text):
    if DRAFT_HAS_REVISION_PATTERN.match(text):
        return text[:-3],text[-2:]
    else:
        return text,None

# ----------------------------
# Main Migration
# ----------------------------
# pass one, create new IPR Disclosure records
def main():
    clear()
    all = IprDetail.objects.all().order_by('ipr_id')
    # all = IprDetail.objects.filter(pk=104)
    for rec in all:
        print "IprDetail", rec.pk
        # print rec.status, states_mapping[rec.status]
        
        # Defaults
        kwargs = { #'by':(rec.get_submitter() or system),
                   'by':system,
                   'holder_legal_name':(rec.legal_name or "").strip(),
                   'id':rec.pk,
                   'notes':rec.other_notes,
                   'other_designations':rec.other_designations,
                   'state':states_mapping[rec.status],
                   'title':rec.title }

        # Determine Type.
        if rec.third_party:
            klass = ThirdPartyIprDisclosure
        elif rec.generic:
            #if rec.patents and not rec.applies_to_all:
            if rec.patents:
                klass = NonDocSpecificIprDisclosure
            else:
                klass = GenericIprDisclosure
        else:
            klass = HolderIprDisclosure
            kwargs['licensing'] = licensing_mapping[rec.licensing_option]

        new = klass.objects.create(**kwargs)
        new.time = rec.submitted_date
        handle_licensing(rec,new)
        handle_legacy_fields(rec,new)
        handle_patent_info(rec,new)
        handle_contacts(rec,new)
        handle_docs(rec,new)
        # save changes to disclosure object
        new.save()

        # create IprEvent:submitted
        event = IprEvent.objects.create(type_id='submitted',
                                        by=system,
                                        disclosure=new,
                                        desc='IPR Disclosure Submitted')
        # need to set time after object creation to override auto_now_add
        event.time = rec.submitted_date
        event.save()
        
        if rec.status == 1:
            # create IprEvent:posted
            event = IprEvent.objects.create(type_id='posted',
                                            by=system,
                                            disclosure=new,
                                            desc='IPR Disclosure Posted')
            # need to set time after object creation to override auto_now_add
            event.time = rec.submitted_date
            event.save()

    # pass two, create relationships
    for rec in all:
        handle_rel(rec)

    # migrate IprNotifications
    for rec in IprNotification.objects.all():
        print 'notification: {}'.format(rec.pk)
        handle_notification(rec)
        
    # print stats
    for klass in (HolderIprDisclosure,
                  ThirdPartyIprDisclosure,
                  NonDocSpecificIprDisclosure,
                  GenericIprDisclosure):
        print "{}: {}".format(klass.__name__,klass.objects.count())
    print "Total records: {}".format(IprDisclosureBase.objects.count())


if __name__ == "__main__":
    main()