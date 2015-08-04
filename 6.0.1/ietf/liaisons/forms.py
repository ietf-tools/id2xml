import datetime, os
import operator
from email.utils import parseaddr
from form_utils.forms import BetterModelForm

from django import forms
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.forms.util import ErrorList
from django.db.models import Q
from django.forms.widgets import RadioFieldRenderer
from django.forms.models import BaseInlineFormSet
from django.core.validators import validate_email, ValidationError
from django.template.loader import render_to_string
from django.utils.html import format_html
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe

import debug                            # pyflakes:ignore

from ietf.ietfauth.utils import has_role
from ietf.name.models import DocRelationshipName
from ietf.liaisons.utils import (can_add_outgoing_liaison,can_add_incoming_liaison,
    get_person_for_user,is_authorized_individual)
#from ietf.liaisons.utils import IETFHM
from ietf.liaisons.widgets import (FromWidget,ReadOnlyWidget,ButtonWidget,
    ShowAttachmentsWidget, RelatedLiaisonWidget)
from ietf.liaisons.models import (LiaisonStatement,LiaisonStatementPurposeName, 
    LiaisonStatementEvent,RelatedLiaisonStatement,LiaisonStatementAttachment)
from ietf.liaisons.fields import SearchableLiaisonStatementsField
from ietf.group.models import Group, Role
from ietf.person.models import Person, Email
from ietf.person.fields import SearchableEmailField
from ietf.doc.models import Document
from ietf.utils.fields import DatepickerDateField

# -------------------------------------------------
# Helper Functions
# -------------------------------------------------

def liaison_form_factory(request, **kwargs):
    user = request.user
    force_incoming = 'incoming' in request.GET.keys()
    liaison = kwargs.pop('liaison', None)
    if liaison:
        return EditLiaisonForm(user, instance=liaison, **kwargs)
    if not force_incoming and can_add_outgoing_liaison(user):
        return OutgoingLiaisonForm(user, **kwargs)
    elif can_add_incoming_liaison(user):
        return IncomingLiaisonForm(user, **kwargs)
    return None

def validate_emails(value):
    '''Custom validator for emails'''
    value = value.strip()           # strip whitespace
    if '\r\n' in value:             # cc_contacts has newlines
        value = value.replace('\r\n',',')
    emails = value.split(',')
    for email in emails:
        name, addr = parseaddr(email)
        try:
            validate_email(addr)
        except ValidationError:
            raise forms.ValidationError('Invalid email address: %s' % addr)
        try:
            addr.encode('ascii')
        except UnicodeEncodeError as e:
            raise forms.ValidationError('Invalid email address: %s (check character %d)' % (addr,e.start))

# -------------------------------------------------
# Form Classes
# -------------------------------------------------
def liaison_manager_sdos(person):
    return Group.objects.filter(type="sdo", state="active", role__person=person, role__name="liaiman").distinct()


"""
class EditLiaisonForm(LiaisonForm):

    #from_field = forms.CharField(widget=forms.TextInput, label=u'From')
    #response_contacts = forms.CharField(label=u'Reply to', widget=forms.TextInput)
    organization = forms.CharField(widget=forms.TextInput)
    to_poc = forms.CharField(widget=forms.TextInput, label="POC", required=False)
    cc1 = forms.CharField(widget=forms.TextInput, label="CC", required=False)

    class Meta:
        fields = ('from_raw_body', 'to_body', 'to_poc', 'cc1', 'last_modified_date', 'title',
                  'technical_contacts', 'body',
                  'deadline_date', 'purpose', 'response_contacts', 'related_to')

    def __init__(self, *args, **kwargs):
        super(EditLiaisonForm, self).__init__(*args, **kwargs)
        self.edit = True

    def set_from_field(self):
        self.fields['from_field'].initial = self.instance.from_name

    def set_response_contacts_field(self):
        self.fields['response_contacts'].initial = self.instance.response_contacts

    def set_organization_field(self):
        self.fields['organization'].initial = self.instance.to_name

    def save_extra_fields(self, liaison):
        liaison.from_name = self.cleaned_data.get('from_field')
        liaison.to_name = self.cleaned_data.get('organization')
        liaison.cc_contacts = self.cleaned_data['cc1']
"""

class RadioRenderer(RadioFieldRenderer):

    def render(self):
        output = []
        for widget in self:
            output.append(format_html(force_text(widget)))
        return mark_safe('\n'.join(output))


class SearchLiaisonForm(forms.Form):

    text = forms.CharField(required=False)
    scope = forms.ChoiceField(choices=(("all", "All text fields"), ("title", "Title field")), required=False, initial='title', widget=forms.RadioSelect(renderer=RadioRenderer))
    source = forms.CharField(required=False)
    destination = forms.CharField(required=False)
    start_date = forms.DateField(required=False, help_text="Format: YYYY-MM-DD")
    end_date = forms.DateField(required=False, help_text="Format: YYYY-MM-DD")

    def get_results(self):
        results = LiaisonStatement.objects.filter(state__slug='approved').extra(
            select={
                '_submitted': 'SELECT time FROM liaisons_liaisonstatementevent WHERE liaisons_liaisonstatement.id = liaisons_liaisonstatementevent.statement_id AND liaisons_liaisonstatementevent.type_id = "submitted"',
                '_awaiting_action': 'SELECT count(*) FROM liaisons_liaisonstatement_tags WHERE liaisons_liaisonstatement.id = liaisons_liaisonstatement_tags.liaisonstatement_id AND liaisons_liaisonstatement_tags.liaisonstatementtagname_id = "required"',
                'from_concat': 'SELECT GROUP_CONCAT(name SEPARATOR ", ") FROM group_group JOIN liaisons_liaisonstatement_from_groups WHERE liaisons_liaisonstatement.id = liaisons_liaisonstatement_from_groups.liaisonstatement_id AND liaisons_liaisonstatement_from_groups.group_id = group_group.id',
                'to_concat': 'SELECT GROUP_CONCAT(name SEPARATOR ", ") FROM group_group JOIN liaisons_liaisonstatement_to_groups WHERE liaisons_liaisonstatement.id = liaisons_liaisonstatement_to_groups.liaisonstatement_id AND liaisons_liaisonstatement_to_groups.group_id = group_group.id',
            })
        if self.is_bound:
            query = self.cleaned_data.get('text')
            if query:
                if self.cleaned_data.get('scope') == 'title':
                    q = Q(title__icontains=query)
                else:
                    q = (Q(title__icontains=query) | Q(other_identifiers__icontains=query) | Q(body__icontains=query) | Q(attachments__title__icontains=query) |
                         Q(response_contacts__icontains=query) | Q(technical_contacts__icontains=query) | Q(action_holder_contacts__icontains=query) |
                         Q(cc_contacts=query))
                results = results.filter(q)
            source = self.cleaned_data.get('source')
            if source:
                results = results.filter(Q(from_groups__name__icontains=source) | Q(from_groups__acronym__iexact=source) | Q(from_name__icontains=source))
            destination = self.cleaned_data.get('destination')
            if destination:
                results = results.filter(Q(to_groups__name__icontains=destination) | Q(to_groups__acronym__iexact=destination) | Q(to_name__icontains=destination))
            start_date = self.cleaned_data.get('start_date')
            end_date = self.cleaned_data.get('end_date')
            events = None
            if start_date:
                events = LiaisonStatementEvent.objects.filter(type='submitted', time__gte=start_date)
                if end_date:
                    events = events.filter(time__lte=end_date)
            elif end_date:
                events = LiaisonStatementEvent.objects.filter(type='submitted', time__lte=end_date)
            if events:
                results = results.filter(liaisonstatementevent__in=events)

                
            destination = self.cleaned_data.get('destination')
            if destination:
                results = results.filter(Q(to_groups__name__icontains=destination) | Q(to_groups__acronym__iexact=destination) | Q(to_name__icontains=destination))
        results = results.distinct().order_by('title')
        return results

# -------------------------------------------------
# New Classes
# -------------------------------------------------

class LiaisonModelForm(BetterModelForm):
    '''Specify fields which require a custom widget or that are not part of the model'''
    from_groups = forms.ModelMultipleChoiceField(queryset=Group.objects.all(),label=u'Groups')
    from_contact = forms.EmailField(label=u'Response Contact')
    to_groups = forms.ModelMultipleChoiceField(queryset=Group.objects,label=u'Groups')
    deadline = DatepickerDateField(date_format="yyyy-mm-dd", picker_settings={"autoclose": "1" }, label='Deadline', required=True)
    related_to = SearchableLiaisonStatementsField(label=u'Related Liaison Statement', required=False)
    submitted_date = DatepickerDateField(date_format="yyyy-mm-dd", picker_settings={"autoclose": "1" }, label='Submission date', required=True, initial=datetime.date.today())
    attachments = forms.CharField(label='Attachments', widget=ShowAttachmentsWidget, required=False)
    attach_title = forms.CharField(label='Title', required=False)
    attach_file = forms.FileField(label='File', required=False)
    attach_button = forms.CharField(label='',
                                    widget=ButtonWidget(label='Attach', show_on='id_attachments',
                                                        require=['id_attach_title', 'id_attach_file'],
                                                        required_label='title and file'),
                                    required=False)
    class Meta:
        model = LiaisonStatement
        exclude = ('attachments','state','from_name','to_name')
        fieldsets = [('From', {'fields': ['from_groups','from_contact'], 'legend': ''}),
                     ('To', {'fields': ['to_groups','to_contacts'], 'legend': ''}),
                     ('Other email addresses', {'fields': ['technical_contacts','action_holder_contacts','cc_contacts'], 'legend': ''}),
                     ('Purpose', {'fields':['purpose', 'deadline'], 'legend': ''}),
                     ('Reference', {'fields': ['other_identifiers','related_to'], 'legend': ''}),
                     ('Liaison Statement', {'fields': ['title', 'submitted_date', 'body', 'attachments'], 'legend': ''}),
                     ('Add attachment', {'fields': ['attach_title', 'attach_file', 'attach_button'], 'legend': ''})]
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        self.person = get_person_for_user(user)
        
        super(LiaisonModelForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.event_type = 'modified'
        else:
            self.event_type = 'submitted'
        self.fields["from_groups"].widget.attrs["placeholder"] = "Type in name to search for group"
        self.fields["to_groups"].widget.attrs["placeholder"] = "Type in name to search for group"
        self.fields["to_contacts"].label = 'Contacts'
        
        # add email validators
        for field in ['from_contact','to_contacts','technical_contacts','action_holder_contacts','cc_contacts']:
            if field in self.fields:
                self.fields[field].validators.append(validate_emails)
        
        self.set_from_fields()
        self.set_to_fields()

    def clean_from_contact(self):
        contact = self.cleaned_data.get('from_contact')
        try:
            email = Email.objects.get(address=contact)
        except ObjectDoesNotExist:
            raise forms.ValidationError('Email address does not exist')
        return email
        
    def clean(self):
        if not self.cleaned_data.get('body', None) and not self.has_attachments():
            self._errors['body'] = ErrorList([u'You must provide a body or attachment files'])
            self._errors['attachments'] = ErrorList([u'You must provide a body or attachment files'])
        return self.cleaned_data
        
    def full_clean(self):
        self.set_required_fields()
        super(LiaisonModelForm, self).full_clean()
        self.reset_required_fields()
        
    def has_attachments(self):
        for key in self.files.keys():
            if key.startswith('attach_file_') and key.replace('file', 'title') in self.data.keys():
                return True
        return False
        
    def is_approved(self):
        assert NotImplemented
        
    def save(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        
        self.is_new = not self.instance.pk
        super(LiaisonModelForm, self).save(*args,**kwargs)
        
        # set state for new statements
        if self.is_new:
            if self.is_approved():
                self.instance.state_id = 'approved'
            else:
                self.instance.state_id = 'pending'
        self.instance.save()
        
        # create submitted / modified event
        event = LiaisonStatementEvent.objects.create(
            type_id=self.event_type,
            by=get_person_for_user(self.request.user),
            statement=self.instance,
            desc='Statement {}'.format(self.event_type.capitalize())
        )
        
        self.save_related_liaisons()
        self.save_attachments()

        return self.instance
    
    def save_attachments(self):
        # TODO: handle deletes, create event on delete
        written = self.instance.attachments.all().count()
        for key in self.files.keys():
            title_key = key.replace('file', 'title')
            if not key.startswith('attach_file_') or not title_key in self.data.keys():
                continue
            attached_file = self.files.get(key)
            extension=attached_file.name.rsplit('.', 1)
            if len(extension) > 1:
                extension = '.' + extension[1]
            else:
                extension = ''
            written += 1
            name = self.instance.name() + ("-attachment-%s" % written)
            attach, _ = Document.objects.get_or_create(
                name = name,
                defaults=dict(
                    title = self.data.get(title_key),
                    type_id = "liai-att",
                    external_url = name + extension, # strictly speaking not necessary, but just for the time being ...
                    )
                )
            LiaisonStatementAttachment.objects.create(statement=self.instance,document=attach)
            attach_file = open(os.path.join(settings.LIAISON_ATTACH_PATH, attach.name + extension), 'w')
            attach_file.write(attached_file.read())
            attach_file.close()
            
    def save_related_liaisons(self):
        rel = DocRelationshipName.objects.get(slug='refold')
        new_related = self.cleaned_data.get('related_to', [])
        # add new ones
        for stmt in new_related:
            self.instance.source_of_set.get_or_create(target=stmt,relationship=rel)
        # delete removed ones
        for related in self.instance.source_of_set.all():
            if related.target not in new_related:
                related.delete()

    def set_from_fields(self):
        assert NotImplemented
    
    def set_required_fields(self):
        purpose = self.data.get('purpose', None)
        if purpose in ['action', 'comment']:
            self.fields['deadline'].required = True
        else:
            self.fields['deadline'].required = False
            
    def reset_required_fields(self):
        self.fields['deadline'].required = True
        
    def set_to_fields(self):
        assert NotImplemented
    
class IncomingLiaisonForm(LiaisonModelForm):
    def clean(self):
        if 'send' in self.data.keys() and self.get_post_only():
            raise forms.ValidationError('As an IETF Liaison Manager you can not send incoming liaison statements, you only can post them')
            #self._errors['from_groups'] = ErrorList([u'As an IETF Liaison Manager you can not send an incoming liaison statements, you only can post them'])
        return super(IncomingLiaisonForm, self).clean()
        
    def is_approved(self):
        return True

    def get_post_only(self):
        from_groups = self.cleaned_data.get('from_groups')
        if has_role(self.user, "Secretariat") or is_authorized_individual(self.user,from_groups):
            return False
        return True
        
    def set_from_fields(self):
        '''Set from_groups and from_contact options and initial value based on user
        accessing the form.'''
        if has_role(self.user, "Secretariat"):
            queryset = Group.objects.filter(type="sdo", state="active").order_by('name')
        else:
            queryset = Group.objects.filter(type="sdo", state="active", role__person=self.person, role__name__in=("liaiman", "auth")).distinct().order_by('name')
            self.fields['from_contact'].initial = self.person.role_set.filter(group=queryset[0]).first().email.address
        self.fields['from_groups'].queryset = queryset
        self.fields['from_groups'].widget.submitter = unicode(self.person)
        
        # if there's only one possibility make it the default
        if len(queryset) == 1:
            self.fields['from_groups'].initial = queryset

    def set_to_fields(self):
        '''Set to_groups and to_contacts options and initial value based on user
        accessing the form'''
        self.fields['to_groups'].choices = get_internal_choices(None)


class OutgoingLiaisonForm(LiaisonModelForm):
    from_contact = SearchableEmailField(label="Contact", required=False, only_users=True)
    approved = forms.BooleanField(label="Obtained prior approval", required=False)
    
    class Meta:
        model = LiaisonStatement
        exclude = ('attachments','state','from_name','to_name','action_holder_contacts')
        # add approved field, no action_holder_contacts
        fieldsets = [('From', {'fields': ['from_groups','from_contact','approved'], 'legend': ''}),
                     ('To', {'fields': ['to_groups','to_contacts'], 'legend': ''}),
                     ('Other email addresses', {'fields': ['technical_contacts','cc_contacts'], 'legend': ''}),
                     ('Purpose', {'fields':['purpose', 'deadline'], 'legend': ''}),
                     ('Reference', {'fields': ['other_identifiers','related_to'], 'legend': ''}),
                     ('Liaison Statement', {'fields': ['title', 'submitted_date', 'body', 'attachments'], 'legend': ''}),
                     ('Add attachment', {'fields': ['attach_title', 'attach_file', 'attach_button'], 'legend': ''})]
                     
    def is_approved(self):
        return self.cleaned_data['approved']

    def set_from_fields(self):
        '''Set from_groups and from_contact options and initial value based on user
        accessing the form'''
        self.fields['from_groups'].choices = get_internal_choices(self.user)
        roles = self.person.role_set.filter(name__in=('ad','chair'),group__state='active')
        if roles:
            email = roles.first().email.address
        else:
            email = self.person.email_address()
        self.fields['from_contact'].initial = email
    
    def set_to_fields(self):
        '''Set to_groups and to_contacts options and initial value based on user
        accessing the form'''
        # if the user is a Liaison Manager and nothing more, reduce to set to his SDOs
        if has_role(self.user, "Liaison Manager") and not get_groups_for_person(self.user.person):
            queryset = Group.objects.filter(type="sdo", state="active", role__person=self.person, role__name="liaiman").distinct().order_by('name')
        else:
            # get all outgoing entities
            queryset = Group.objects.filter(type="sdo", state="active").order_by('name')
        
        self.fields['to_groups'].queryset = queryset
        
        if len(queryset) == 1:
            self.fields['to_groups'].initial = queryset
            
class EditLiaisonForm(LiaisonModelForm):
    pass

def get_internal_choices(user):
    '''Returns the set of internal IETF groups the user has permissions for, as a list
    of choices suitable for use in a select widget.  If user == None, all active internal
    groups are included.'''
    choices = []
    groups = get_groups_for_person(user.person if user else None)
    main = [ (g.pk, 'The {}'.format(g.acronym.upper())) for g in groups.filter(acronym__in=('ietf','iesg','iab')) ]
    areas = [ (g.pk, '{} - {}'.format(g.acronym,g.name)) for g in groups.filter(type='area') ]
    wgs = [ (g.pk, '{} - {}'.format(g.acronym,g.name)) for g in groups.filter(type='wg') ]
    choices.append(('Main IETF Entities', main))
    choices.append(('IETF Areas', areas))
    choices.append(('IETF Working Groups', wgs ))
    return choices


def get_groups_for_person(person):
    '''Returns queryset of Groups the person has interesting roles in.
    This is a refactor of IETFHierarchyManager.get_entities_for_person().  If Person
    is None or Secretariat or Liaison Manager all internal IETF groups are returned.
    '''
    if person == None or has_role(person.user, "Secretariat") or has_role(person.user, "Liaison Manager"):
        # collect all internal IETF groups
        queries = [Q(acronym__in=('ietf','iesg','iab')),
                   Q(type='area',state='active'),
                   Q(type='wg',state='active')]
    else:
        # Interesting roles, as Group queries
        queries = [Q(role__person=person,role__name='chair',acronym='ietf'),
                   Q(role__person=person,role__name__in=('chair','execdir'),acronym='iab'),
                   Q(role__person=person,role__name='ad',type='area',state='active'),
                   Q(role__person=person,role__name__in=('chair','secretary'),type='wg',state='active')]
    return Group.objects.filter(reduce(operator.or_,queries)).order_by('acronym').distinct()
    