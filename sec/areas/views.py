from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.urlresolvers import reverse
from django.forms.formsets import formset_factory
from django.forms.models import inlineformset_factory, modelformset_factory
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils import simplejson
from session_messages import create_message
from models import *
from forms import *
import re
 
# --------------------------------------------------
# AJAX FUNCTIONS
# --------------------------------------------------
def getpeople(request):
    """
    Ajax function to find people.  Takes one or two terms (ignores rest) and
    returns JSON format response: first name, last name, primary email, tag
    """
    result = []
    term = request.GET.get('term','')
    terms = term.split(' ')
    # if just one term provided search first or last
    if len(terms) == 1:
	qs = PersonOrOrgInfo.objects.filter(first_name__istartswith=term) | PersonOrOrgInfo.objects.filter(last_name__istartswith=term)
    # if two terms provided search first and last
    else:
	qs = PersonOrOrgInfo.objects.filter(first_name__istartswith=terms[0]) & PersonOrOrgInfo.objects.filter(last_name__istartswith=terms[1])
    for item in qs:
	full = '%s %s - %s (%s)' % (item.first_name,item.last_name,item.email(),item.person_or_org_tag)
	result.append(full)
        
    return HttpResponse(simplejson.dumps(result), mimetype='application/javascript')

# --------------------------------------------------
# STANDARD VIEW FUNCTIONS
# --------------------------------------------------
def add(request):
    """ 
    Add a new IETF Area

    **Templates:**

    * ``areas/add.html``

    **Template Variables:**

    * area_form

    """
    AWPFormSet = formset_factory(AWPAddForm, extra=2)
    if request.method == 'POST':
        area_form = AddAreaForm(request.POST)
        awp_formset = AWPFormSet(request.POST, prefix='awp')
        if area_form.is_valid() and awp_formset.is_valid():
            # get form data
            acronym = area_form.cleaned_data['acronym']
            name = area_form.cleaned_data['name']
            status = area_form.cleaned_data['status']
            start = area_form.cleaned_data['start_date']
            comments = area_form.cleaned_data['comments']
            # save new Acronym 
            acronym_obj = Acronym(acronym=acronym,name=name)
            acronym_obj.save()
            # save new Area
            status_obj = AreaStatus.objects.get(status_id=status)
            area_obj = Area(area_acronym=acronym_obj,start_date=start,status=status_obj,comments=comments)
            area_obj.save()
            # save AWPs
            for item in awp_formset.cleaned_data:
                if item.get('url', 0):
                    awp_obj = AreaWGAWP(name=acronym_obj,url=item['url'],description=item['description'])
                    awp_obj.save()
            
            create_message(request, 'The Area was created successfully!')
            url = reverse('sec.areas.views.list_areas')
            return HttpResponseRedirect(url)
    else:
        # display initial forms
        area_form = AddAreaForm()
        awp_formset = AWPFormSet(prefix='awp')

    return render_to_response('areas/add.html', {
        'area_form': area_form,
        'awp_formset': awp_formset},
        RequestContext(request, {}),
    )

def edit(request, id):
    """ 
    Edit IETF Areas 

    **Templates:**

    * ``areas/edit.html``

    **Template Variables:**

    * acronym, area_formset, awp_formset, acronym_form 

    """
    # get acronym or return HTTP 404 if record not found
    acronym = get_object_or_404(Acronym, acronym_id=id)

    AreaFormSet = inlineformset_factory(Acronym, Area, form=AreaForm, can_delete=False, extra=0)
    AWPFormSet = inlineformset_factory(Acronym, AreaWGAWP, form=AWPForm, max_num=2)
    if request.method == 'POST':
        button_text = request.POST.get('submit', '')
        if button_text == 'Save':
	    acronym_form = AcronymForm(request.POST, instance=acronym)
	    area_formset = AreaFormSet(request.POST, instance=acronym)
	    awp_formset = AWPFormSet(request.POST, instance=acronym)
	    if acronym_form.is_valid() and area_formset.is_valid() and awp_formset.is_valid():
		acronym_form.save()
		area_formset.save()
		awp_formset.save()
		create_message(request, 'The Area entry was changed successfully')
                url = reverse('sec.areas.views.view', kwargs={'id':id})
		return HttpResponseRedirect(url)

	else:
                url = reverse('sec.areas.views.view', kwargs={'id':id})
		return HttpResponseRedirect(url)
    else:
        acronym_form = AcronymForm(instance=acronym)
        area_formset = AreaFormSet(instance=acronym)
        awp_formset = AWPFormSet(instance=acronym)

    return render_to_response('areas/edit.html', {
        'acronym': acronym,
        'area_formset': area_formset,
        'awp_formset': awp_formset, 
        'acronym_form': acronym_form, },
        RequestContext(request,{}),
    )
    
    
def list_areas(request):
    """ 
    List IETF Areas 

    **Templates:**

    * ``areas/list.html``

    **Template Variables:**

    * results 

    """

    # get all acronyms that are areas
    results = Acronym.objects.filter(area__status__lte=99)
    return render_to_response('areas/list.html', {
        'results': results},
        RequestContext(request, {}),
    )

def people(request, id):
    """ 
    Edit People associated with Areas, Area Directors 

    **Templates:**

    * ``areas/people.html``

    **Template Variables:**

    * directors, area

    """

    # get area or return HTTP 404 if record not found
    area = get_object_or_404(Area, area_acronym=id)

    if request.method == 'POST':
	# handle adding a new director 
	if request.POST.get('submit', '') == "Add":
            form = AreaDirectorForm(request.POST)
            if form.is_valid():
		name = request.POST.get('ad_name', '')
		login = request.POST.get('login', '')
		m = re.search(r'\((\d+)\)', name)
		tag = m.group(1)
		person = PersonOrOrgInfo.objects.get(person_or_org_tag=tag)
		# make sure ad entry doesn't already exist

		# create iesg_login entry.  If a row for the person already exists in the table, ie. for
		# a returning IESG member, just change the user_level to 1
		login_obj, created = IESGLogin.objects.get_or_create(
		    person=person,
		    defaults={
			'login_name': person.email(),
			'password': '',
			'user_level': 1,
			'first_name': person.first_name,
			'last_name': person.last_name})
		if not created:
		    login_obj.user_level = 1
		    login_obj.save()
		# create area director entry
		ad_obj = AreaDirector(area=area,person=person)
		ad_obj.save()
		create_message(request, 'New Area Director added successfully!')
                url = reverse('sec.areas.views.view', kwargs={'id':str(area.area_acronym.acronym_id)})
                return HttpResponseRedirect(url)
    else:
        form = AreaDirectorForm()

    directors = area.areadirector_set.all()
    return render_to_response('areas/people.html', {
        'area': area,
        'form': form,
        'directors': directors},
        RequestContext(request, {}),
    )

def modify(request, id):
    """ 
    Handle state changes of Area Directors (enable voting, retire)
    Per requirements, the Retire button shall perform the following DB updates
    - update iesg_login row, user_level = 4
    - remove telechat_user row (to revoke voting rights)
    - update IETFWG(groups) set area_director = TBD 
    - remove area_director row


    **Templates:**

    * none

    Redirects to view page on success.
    """

    # get area or return HTTP 404 if record not found
    area = get_object_or_404(Area, area_acronym=id)

    # should only get here with POST method
    if request.method == 'POST':
	# setup common request variables
	tag = request.POST.get('tag', '')
	person = PersonOrOrgInfo.objects.get(person_or_org_tag=tag)
	name = person.first_name + " " + person.last_name
	# handle retire request
	if request.POST.get('submit', '') == "Retire":
            # --------------------------------------------------
            # get necessary db objects, returning an error if records not found (ie database is corrupted)
	    try:
	        area_director = AreaDirector.objects.get(person=tag,area=area)
	        tbd_area_director = AreaDirector.objects.get(id=130)
	        login = IESGLogin.objects.get(person=tag)
	        telechat_user = TelechatUser.objects.get(person_or_org_tag=tag)
	    except (ObjectDoesNotExist, MultipleObjectsReturned), e: 
	        return render_to_response('areas/error.html', { 'error': e},)

            # if this AD is primary AD for working groups need to change to TBD
            working_groups = IETFWG.objects.filter(area_director=area_director.id)
  
            # --------------------------------------------------
            # perform database updates
	    login.user_level = 4
	    login.save()
	    telechat_user.delete()
            for group in working_groups:
                group.area_director=tbd_area_director
                group.save()
	    area_director.delete()

            create_message(request, 'The Area Director has been retired successfully!')

	# handle voting request
        # per requirements, affiliated_org field shall be the person's name
	if request.POST.get('submit', '') == "Enable Voting":
	    telechat_user_obj = TelechatUser(person_or_org_tag=tag,is_iesg=1,affiliated_org=name)
	    telechat_user_obj.save()
	    create_message(request, 'Voting rights have been granted successfully!')

        url = reverse('sec.areas.views.view', kwargs={'id':str(area.area_acronym.acronym_id)})
        return HttpResponseRedirect(url)

def view(request, id):
    """ 
    View Area information.

    **Templates:**

    * ``areas/view.html``

    **Template Variables:**

    * acronym, area, awps, directors

    """
    # get area or return HTTP 404 if record not found
    area = get_object_or_404(Area, area_acronym=id)
    acronym = get_object_or_404(Acronym, acronym_id=id)
    awps = AreaWGAWP.objects.filter(name=acronym.name)
    directors = area.areadirector_set.all()

    return render_to_response('areas/view.html', {
        'acronym': acronym,
        'area': area,
        'awps': awps,
        'directors': directors},
	RequestContext(request, {}),
    )
