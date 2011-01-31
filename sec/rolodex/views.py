from django.core.urlresolvers import reverse
from django.db.models import Q
from django.forms.formsets import formset_factory
from django.forms.models import inlineformset_factory, modelformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from session_messages import create_message
from models import *
from sec.groups.models import IETFWG
from forms import *

# Special case rolodex record.  Seems like a bad idea to hardcode this record id but we need to do
# this because this record is treated special, it is used specifically in the AreaDirector table
# for TBD records.
TBD_TAG='106956'

# ---------------------------------------
# Functions
# ---------------------------------------
def get_roles(tag):
    """ Takes a PersonOrOrgInfo Tag as input and looks up roles the person has, returning
    a list of dictionaries.  The dictionaries consist of the keys 'label' which is the name of a leadership
    role (ie. Area Director) and 'html' which is a link to the area/group object view.
    """
    roles = []
    person = PersonOrOrgInfo.objects.get(person_or_org_tag=tag)
    # Special case for "TBD" person record, we'll show all active groups with area_director = TBD
    if tag == TBD_TAG:
        qs = IETFWG.objects.filter(area_director__person=person,status=1)
        for item in qs:
	    d = {} 
	    d['label'] = 'Group - Area Director'
	    d['html'] = '<a href="../../groups/%s/">%s</a>' % (item.group_acronym.acronym_id, item.group_acronym.name)
	    roles.append(d)
    else:
	# check Area Directors
	qs = AreaDirector.objects.filter(person=tag)
	for item in qs:
	    d = {} 
	    d['label'] = 'Area Director'
	    d['html'] = '<a href="../../areas/%s/">%s</a>' % (item.area.area_acronym.acronym_id, item.area.area_acronym.name)
	    roles.append(d)
    # check Working Groups Chairs
    qs = person.wgchair_set.all()
    for item in qs:
        d = {} 
        d['label'] = 'Chairperson'
        d['html'] = '<a href="../../groups/%s/">%s</a>' % (item.group_acronym_id, item.group_acronym)
        roles.append(d)
    qs = person.wgeditor_set.all()
    for item in qs:
        d = {} 
        d['label'] = 'Editor'
        d['html'] = '<a href="../../groups/%s/">%s</a>' % (item.group_acronym_id, item.group_acronym)
        roles.append(d)
    qs = person.wgtechadvisor_set.all()
    for item in qs:
        d = {} 
        d['label'] = 'Technical Advisor'
        d['html'] = '<a href="../../groups/%s/">%s</a>' % (item.group_acronym_id, item.group_acronym)
        roles.append(d)
    qs = person.wgsecretary_set.all()
    for item in qs:
        d = {} 
        d['label'] = 'Secretary'
        d['html'] = '<a href="../../groups/%s/">%s</a>' % (item.group_acronym_id, item.group_acronym)
        roles.append(d)
    return roles

# ---------------------------------------
# Views 
# ---------------------------------------
def add(request):
    """ 
    Add contact information.

    **Templates:**

    * ``rolodex/add.html``

    **Template Variables:**

    * personform
    * results: the list of similar names to allow user to check for dupes

    """
    results = []
    first_name = last_name = ''
    if request.method == 'POST':
        form = NewPersonForm(request.POST)
        if form.is_valid():
            # save form in session
            request.session['post_data'] = request.POST
            # search by last name to see if contact already exists
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            results = PersonOrOrgInfo.custom.multi_search(last_name=last_name)
            if not results:
                return HttpResponseRedirect('../add-proceed/')

    else:
        # display initial form
        form = NewPersonForm()

    return render_to_response('rolodex/add.html', {
        'form': form,
        'results': results,
        'first_name': first_name,
        'last_name': last_name},
        RequestContext(request, {}),
    )

def add_proceed(request):
    """ 
    Add contact information. (2nd page, allows entry of address, phone and email records)

    **Templates:**

    * ``rolodex/add_proceeed.html``

    **Template Variables:**

    * post_data: contact name fields, stored in session  
    * address_form, email_form, phone_form

    """
    # if we get to this page from the add page, as expected, the session will have post_data.
    if request.session['post_data']:
        post_data = request.session['post_data']
    else:
        return render_to_response('rolodex/no_data.html',)

    if request.method =='POST':
        name_form = NewPersonForm(request.session['post_data'])
        # set name from header or use "INTERNAL" (from legacy app)
        if request.META['REMOTE_USER']:
            name = request.META['REMOTE_USER']
        else:
            name = 'INTERNAL'
        phone_form = NewPhoneForm(request.POST)
        email_form = NewEmailForm(request.POST)
        address_form = NewAddressForm(request.POST)
        if ( phone_form.is_valid() and email_form.is_valid() and address_form.is_valid() ):
            # save person here
            new_person = name_form.save(commit=False)
            new_person.modified_by = name
            new_person.created_by = name
            new_person.save()
            # save phone
            if phone_form.cleaned_data['phone_number']:
	      new_phone = phone_form.save(commit=False)
	      new_phone.person_or_org = new_person
	      new_phone.save()
            # save email
            if email_form.cleaned_data['address']:
	      new_email = email_form.save(commit=False)
	      new_email.person_or_org = new_person
	      new_email.save()
            # save postal address
            if address_form.cleaned_data['affiliated_company'] or address_form.cleaned_data['city']:
	      new_address = address_form.save(commit=False)
	      new_address.person_or_org = new_person
	      new_address.save()
            create_message(request, 'The Rolodex entry was added successfully')
            url = reverse('sec.rolodex.views.view', kwargs={'tag': new_person.person_or_org_tag})
            return HttpResponseRedirect(url)
    else:
        phone_form = NewPhoneForm()
        email_form = NewEmailForm()
        address_form = NewAddressForm()

    return render_to_response('rolodex/add_proceed.html', {
        'post_data': post_data,
        'phone_form': phone_form,
        'email_form': email_form,
        'address_form': address_form},
        RequestContext(request, {}),
    )

def bulk_update(request, tag):
    """ 
    Bulk update email addresses.

    **Templates:**

    * ``rolodex/bulk_update.html``

    **Template Variables:**

    * person, emails

    """
    # get person or return HTTP 404 if record not found
    person = get_object_or_404(PersonOrOrgInfo, person_or_org_tag=tag)


    if request.method == 'POST':
        email_form = BulkUpdateForm(request.POST)
        email_forms = [email_form]
        if email_form.is_valid():
            new_email = email_form.cleaned_data['new_email']
            old_email = email_form.cleaned_data['old_email']
            # use update method on the queryset
            EmailAddress.objects.filter(person_or_org=tag,address=old_email).update(address=new_email)
            create_message(request, 'The Bulk Update was successful')
            url = reverse('sec.rolodex.views.view', kwargs={'tag': tag})
            return HttpResponseRedirect(url)
                
    else:
	# get unique emaill addresses
	emails = EmailAddress.objects.filter(person_or_org=tag)
	emails.query.group_by = ['email_address']
        email_forms = []
        for email in emails:
            email_forms.append(BulkUpdateForm( initial={'old_email':email, 'tag':tag} ))

    return render_to_response('rolodex/bulk_update.html', {
        'person': person,
        'email_forms': email_forms},
        RequestContext(request, {}),
    )

def delete(request, tag):
    """ 
    Delete contact information.
    Note: access to this view was disabled per Glen 3-16-10.

    **Templates:**

    * ``rolodex/delete.html``

    **Template Variables:**

    * person

    """
    # get person or return HTTP 404 if record not found
    person = get_object_or_404(PersonOrOrgInfo, person_or_org_tag=tag)

    if request.method == 'POST':
	if request.POST.get('post', '') == "yes":
            # by default django will delete all related objects so we 
            # don't need to do this explicitly
	    person.delete()
            create_message(request, 'The Rolodex entry was deleted successfully')
            url = reverse('sec.rolodex.views.search')
            return HttpResponseRedirect(url)

    return render_to_response('rolodex/delete.html', {
        'person': person},
        RequestContext(request, {}),
    )

def edit(request, tag):
    """ 
    Edit contact information.  Address, Email and Phone records are provided as inlineformsets.

    **Templates:**

    * ``rolodex/edit.html``

    **Template Variables:**

    * person, person_form, address_formset, email_formset, phone_formset

    """
    # get person or return HTTP 404 if record not found
    person = get_object_or_404(PersonOrOrgInfo, person_or_org_tag=tag)

    AddressFormset = inlineformset_factory(PersonOrOrgInfo, PostalAddress, form=AddressForm, can_delete=True, extra=0)
    EmailFormset = inlineformset_factory(PersonOrOrgInfo, EmailAddress, form=EmailForm, can_delete=False, extra=1)
    PhoneFormset = inlineformset_factory(PersonOrOrgInfo, PhoneNumber, form=PhoneForm, can_delete=True, extra=0)
    if request.method == 'POST':
        button_text = request.POST.get('submit', '')
        if button_text == 'Cancel':
            url = reverse('sec.rolodex.views.view', kwargs={'tag':tag})
            return HttpResponseRedirect(url)

        person_form = PersonForm(request.POST, instance=person)
        address_formset = AddressFormset(request.POST, instance=person, prefix='address')
        email_formset = EmailFormset(request.POST, instance=person, prefix='email')
        phone_formset = PhoneFormset(request.POST, instance=person, prefix='phone')
        if person_form.is_valid() and phone_formset.is_valid() and address_formset.is_valid() and email_formset.is_valid():
            person_form.save()
            # only save forms that have changed
            # uncomment for debugging
            #assert False, address_formset.forms[0].has_changed()
            #assert False, address_formset.forms[0].changed_data
            #for form in address_formset.forms:
            #    if form.has_changed:
            #        form.save()
            address_formset.save()
            phone_formset.save()
            email_formset.save()
            create_message(request, 'The Rolodex entry was changed successfully')
            url = reverse('sec.rolodex.views.view', kwargs={'tag': tag})
            return HttpResponseRedirect(url)
        else:
            # uncomment for debugging
            #for form in address_formset.forms:
            #    x = form.changed_data
            #assert False, phone_formset.errors
            pass
    else:
        # display initial edit form
        person_form = PersonForm(instance=person)
        # if any inlineformsets will be empty, need to initialize with extra=1
        # this is because the javascript for adding new forms requires a first one to copy
        if not PhoneNumber.objects.filter(person_or_org=tag):
            PhoneFormset.extra = 1
        if not EmailAddress.objects.filter(person_or_org=tag):
            EmailFormset.extra = 1
        if not PostalAddress.objects.filter(person_or_org=tag):
            AddressFormset.extra = 1
        # initialize formsets
        address_formset = AddressFormset(instance=person, prefix='address')
        email_formset = EmailFormset(instance=person, prefix='email')
        phone_formset = PhoneFormset(instance=person, prefix='phone')
            
    return render_to_response('rolodex/edit.html', {
        'person': person,
        'person_form': person_form, 
        'address_formset': address_formset,
        'email_formset': email_formset,
        'phone_formset': phone_formset, },
        RequestContext(request, {}),
    )
 
def search(request):
    """ 
    Search person_or_org_info by any combination of first_name, last_name, email or tag.  first_name
    last_name searches match the beginning of field, email matches any substring, if tag is provided
    only exact tag matches are returned.

    **Templates:**

    * ``rolodex/search.html``

    **Template Variables:**

    * results: list of dictionaries of search results (first_name, last_name, tag, email, company
    * form: the search form
    * not_found: contains text "No record found" if search results are empty

    """
    results = []
    not_found = ''
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            results = PersonOrOrgInfo.custom.multi_search(**form.cleaned_data)
            if not results:
                not_found = 'No record found' 
    else:
        form = SearchForm()
    return render_to_response('rolodex/search.html', {
        'results' : results,
        'form': form,
        'not_found': not_found},
        RequestContext(request, {}),
    )

def view(request, tag):
    """ 
    View contact information.

    **Templates:**

    * ``rolodex/view.html``

    **Template Variables:**

    * person, addresses, numbers, emails  

    """
    # type mappings
    phone_map = {'W':'Work Phone',
           'H':'Home Phone',
           'WF':'Work Fax',
           'HF':'Home Fax',
           'WT':'Work TDD',
           'HT':'Work TDD',
           'MP':'Mobile',
           'PG':'Pager'}
    address_map = {'W':'Work Address', 'H':'Home Address'}

    # get person or return HTTP 404 if record not found
    person = get_object_or_404(PersonOrOrgInfo, person_or_org_tag=tag)

    addresses = PostalAddress.objects.filter(person_or_org=tag)
    numbers = PhoneNumber.objects.filter(person_or_org=tag)
    emails = EmailAddress.objects.filter(person_or_org=tag)
    roles = get_roles(tag)

    # pre-process data before sending to template
    for number in numbers:
      if phone_map.has_key(number.phone_type):
	number.phone_type = phone_map[number.phone_type]
      else:
	number.phone_type = "Unknown"
    for address in addresses:
      if address_map.has_key(address.address_type):
	address.address_type = address_map[address.address_type]
      else:
	address.address_type = "Extra Address"
   
    return render_to_response('rolodex/view.html', {
	'addresses': addresses,
	'emails': emails,
	'numbers': numbers,
	'person': person,
        'roles': roles},
	RequestContext(request, {}),
    )
