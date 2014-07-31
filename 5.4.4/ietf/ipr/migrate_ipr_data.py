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

import re
import urllib2
from collections import namedtuple
from django.template.loader import render_to_string
from ietf.ipr.models import *
from ietf.name.models import DocRelationshipName
from ietf.name.utils import name

# ---------------------------
# Globals
# ---------------------------
DEFAULT_CHARSET = 'latin1'
UPDATES = DocRelationshipName.objects.get(slug='updates')
URL_PATTERN = re.compile(r'https?://datatracker.ietf.org/ipr/(\d{1,4})/')
DRAFT_PATTERN = re.compile(r'draft-[a-zA-Z0-9\-]+')
DRAFT_HAS_REVISION_PATTERN = re.compile(r'.*-[0-9]{2}')

ContactFields = namedtuple('ContactFields',['name','info'])

# ---------------------------
# Setup States
# ---------------------------
pending_disclosure_state = name(IprDisclosureStateName, "pending", "Pending")
parked_disclosure_state = name(IprDisclosureStateName, "parked", "Parked")
posted_disclosure_state = name(IprDisclosureStateName, "posted", "Posted")
rejected_disclosure_state = name(IprDisclosureStateName, "rejected", "Rejected")
removed_disclosure_state = name(IprDisclosureStateName, "removed", "Removed")
unknown_disclosure_state = name(IprDisclosureStateName, "unknown", "Unknown")

no_license_license_info = name(IprLicenseTypeName, "no-licns", "No License", desc="a) No License Required for Implementers", order=1)
royalty_free_license_info = name(IprLicenseTypeName,"royalty", "Royalty Free", desc="b) Royalty-Free, Reasonable and Non-Discriminatory License to All Implementers", order=2)
reasonable_license_info = name(IprLicenseTypeName,"reason", "Reasonable", desc="c) Reasonable and Non-Discriminatory License to All Implementers with Possible Royalty/Fee", order=3)
provided_later_license_info = name(IprLicenseTypeName,"later", "Provided Later", desc="d) Licensing Declaration to be Provided Later (implies a willingness to commit to the provisions of a), b), or c) above to all implementers; otherwise, the next option 'Unwilling to Commit to the Provisions of a), b), or c) Above'. - must be selected)", order=4)
unwilling_to_commit_license_info = name(IprLicenseTypeName,"unwill", "Unwilling to Commit", desc="e) Unwilling to Commit to the Provisions of a), b), or c) Above", order=5)
see_below_license_info = name(IprLicenseTypeName,"seebelow", "See Below", desc="f) See Text Below for Licensing Declaration", order=6)
none_selected_license_info = name(IprLicenseTypeName,"noselect", "None Selected")

disclosure_event = name(IprEventTypeName, "disclose", "Disclosure")
msgin_event = name(IprEventTypeName, "msgin", "MsgIn")
msgout_event = name(IprEventTypeName, "msgout", "MsgOut")
comment_event = name(IprEventTypeName, "comment", "Comment")
legacy_event = name(IprEventTypeName, "legacy", "Legacy")

system = Person.objects.get(name="(System)")

# ---------------------------
# Mappings
# ---------------------------
contact_type_mapping = { 1:('holder_contact_name','holder_contact_info'),
                         2:('ietfer_name','ietfer_contact_info'),
                         3:None }   # submitter contact in legacy schema

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
    desc = title_text + u"{}: {}\n\n{}".format(url_field,url,data)
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
                                       'fax',
                                       'email'])

        # if no place to migrate contact save as comment
        if not fields:
            if not is_contact_empty(contact):
                desc = u'Legacy Contact.  Type={} ({})\n{}'.format(contact_type_name_mapping[contact.contact_type],contact.contact_type,info)
                IprEvent.objects.create(type=comment_event,
                                        by=system,
                                        disclosure=new,
                                        desc=desc)
            continue

        fields = ContactFields(*fields)
        if hasattr(new,fields.name):
            setattr(new,fields.name,contact.name)
        if hasattr(new,fields.info):
            setattr(new,fields.info,info)

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
    for rec in IprDetail.objects.all().order_by('ipr_id').iterator():
        print "IprDetail", rec.pk

        # Defaults
        kwargs = { #'by':(rec.get_submitter() or system),
                   'by':system,
                   'holder_legal_name':(rec.legal_name or "").strip(),
                   'id':rec.pk,
                   'notes':rec.other_notes,
                   'other_designations':rec.other_designations,
                   'state':states_mapping[rec.status],
                   'time':rec.submitted_date,
                   'title':rec.title }

        # Determine Type.
        if rec.third_party:
            klass = ThirdPartyIprDisclosure
        elif rec.generic:
            if rec.patents and not rec.applies_to_all:
                klass = NonDocSpecificIprDisclosure
            else:
                klass = GenericIprDisclosure
        else:
            klass = HolderIprDisclosure
            kwargs['licensing'] = licensing_mapping[rec.licensing_option]

        new,created = klass.objects.get_or_create(**kwargs)

        handle_licensing(rec,new)
        handle_legacy_fields(rec,new)
        handle_patent_info(rec,new)
        handle_contacts(rec,new)
        handle_docs(rec,new)
        # some handle routines modify new object
        new.save()

        # create DisclosureEvent (=submitted)
        event = IprEvent.objects.create(type=disclosure_event,
                                        by=system,
                                        disclosure=new,
                                        desc='IPR Disclosure Submitted')
        # need to set time after object creation to override auto_now_add
        event.time = rec.submitted_date
        event.save()

    # pass two, create relationships
    for rec in IprDetail.objects.all().order_by('ipr_id').iterator():
        handle_rel(rec)

    # print stats
    for klass in (HolderIprDisclosure,
                  ThirdPartyIprDisclosure,
                  NonDocSpecificIprDisclosure,
                  GenericIprDisclosure):
        print "{}: {}".format(klass.__name__,klass.objects.count())
    print "Total records: {}".format(IprDisclosureBase.objects.count())


if __name__ == "__main__":
    main()