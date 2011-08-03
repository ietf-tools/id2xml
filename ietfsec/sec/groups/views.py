from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.models import get_model
from django.core.exceptions import ObjectDoesNotExist
from django.forms.formsets import formset_factory
from django.forms.models import inlineformset_factory
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils import simplejson
from models import *
from forms import *
from sec.areas.forms import AWPAddForm
import os
import datetime

# -------------------------------------------------
# AJAX Functions
# -------------------------------------------------

def get_ads(request):
    """ AJAX function which takes a URL parameter, "area" and returns the area directors
    in the form of a list of dictionaries with "id" and "value" keys(in json format).  
    Used to populate select options. 
    """

    results=[]
    area = request.GET.get('area','')
    qs = AreaDirector.objects.filter(area=area)
    for item in qs:
        d = {'id': item.id, 'value': item.person.first_name + ' ' + item.person.last_name}
        results.append(d)

    return HttpResponse(simplejson.dumps(results), mimetype='application/javascript')

# -------------------------------------------------
# Standard View Functions
# -------------------------------------------------
def add(request):
    """ 
    Add a new IETF Group..

    **Templates:**

    * ``groups/add.html``

    **Template Variables:**

    * form, awp_formset

    """
    AWPFormSet = formset_factory(AWPAddForm, extra=2)
    if request.method == 'POST':
        button_text = request.POST.get('submit', '')
        if button_text == 'Cancel':
            url = reverse('sec.groups.views.search')
            return HttpResponseRedirect(url)

        form = NewGroupForm(request.POST)
        awp_formset = AWPFormSet(request.POST, prefix='awp')
        if form.is_valid():
            # get form data
            acronym = form.cleaned_data['group_acronym']
            name = form.cleaned_data['group_name']
            type = form.cleaned_data['group_type']
            status = form.cleaned_data['status']
            area = form.cleaned_data['primary_area']
            area_director = form.cleaned_data['primary_area_director']
            # convert IDs to objects
            status_obj = WGStatus.objects.get(status_id=status)
            type_obj = WGType.objects.get(group_type_id=type)
            area_director_obj = AreaDirector.objects.get(id=area_director)
            area_obj = Area.objects.get(area_acronym=area)
            # save new Acronym 
            acronym_obj = Acronym(acronym=acronym,name=name)
            acronym_obj.save()
            # save new Group 
            pdate = form.cleaned_data['proposed_date']
            if type == '2' and not pdate:
                pdate = datetime.date.today().isoformat() 
            group_obj = IETFWG(
                group_acronym = acronym_obj,
                group_type = type_obj,
                status = status_obj,
		proposed_date = pdate,
		area_director = area_director_obj,
		meeting_scheduled = form.cleaned_data['meeting_scheduled'],
		email_address = form.cleaned_data['email_address'],
		email_subscribe = form.cleaned_data['email_subscribe'],
		email_keyword = form.cleaned_data['email_keyword'],
		email_archive = form.cleaned_data['email_archive'],
		comments = form.cleaned_data['comments'])
            group_obj.save()
            # create AreaGroup record
            area_group_obj = AreaGroup(group=group_obj,area=area_obj)
            area_group_obj.save()
            # save Additional Web Pages
            for item in awp_formset.cleaned_data:
                if item.get('url', 0):
                    awp_obj = WGAWP(name=acronym_obj,url=item['url'],description=item['description'])
                    awp_obj.save()

            messages.success(request, 'The Group was created successfully!')
            url = reverse('sec.groups.views.view', kwargs={'id':group_obj.group_acronym.acronym_id})
            return HttpResponseRedirect(url)

        else:
            # if primary area director was selected we need special logic to retain when displaying errors
            # we first need to check that 'primary_area_director' is in the posted data, if nothing was
            # selected it won't be there
            if 'primary_area_director' in request.POST:
		ad = request.POST['primary_area_director']
		area = request.POST['primary_area']
		ad_choices = [(ad.id, ad.person.first_name + ' ' + ad.person.last_name) for ad in AreaDirector.objects.filter(area=area)]
		form.fields['primary_area_director'].widget.choices = ad_choices
		form.fields['primary_area_director'].initial = ad
                
    else:
        # display initial form, default to 'PWG' type
        form = NewGroupForm(initial={'group_type': 2})
        awp_formset = AWPFormSet(prefix='awp')

    return render_to_response('groups/add.html', {
        'form': form,
        'awp_formset': awp_formset},
        RequestContext(request, {}),
    )

def delete(request, id):
    """ 
    Handle deleting roles for groups (chair, editor, advisor, secretary)

    **Templates:**

    * none

    Redirects to people page on success.

    """

    group = get_object_or_404(IETFWG, group_acronym=id)

    if request.method == 'POST':
        # delete a role
        if request.POST.get('submit', '') == "Delete":
            table = request.POST.get('table', '')
            tag = request.POST.get('tag', '')
            obj = get_model('core',table)
            instance = obj.objects.get(person=tag,group_acronym=group.group_acronym)
            instance.delete()
            messages.success(request, 'The entry was deleted successfully')

    url = reverse('sec.groups.views.people', kwargs={'id':id})
    return HttpResponseRedirect(url)

def description(request, id):
    """ 
    Edit IETF Group description

    **Templates:**

    * ``groups/description.html``

    **Template Variables:**

    * group, form 

    """

    group = get_object_or_404(IETFWG, group_acronym=id)
    filename = os.path.join(settings.GROUP_DESCRIPTION_DIR,group.group_acronym.acronym + '.desc.txt')

    if request.method == 'POST':
        form = DescriptionForm(request.POST) 
        if request.POST['submit'] == "Cancel":
            url = reverse('sec.groups.views.view', kwargs={'id':id})
            return HttpResponseRedirect(url)
     
        if form.is_valid():
            description = form.cleaned_data['description'] 
            try:
                f = open(filename,'w')
                f.write(description)
                f.close()
            except IOError, e:
                return render_to_response('groups/error.html', { 'error': e},) 

            messages.success(request, 'The Group Description was changed successfully')
            url = reverse('sec.groups.views.view', kwargs={'id':id})
            return HttpResponseRedirect(url)
    else:
	if os.path.isfile(filename):
	    f = open(filename,'r')
	    value = f.read()
	    f.close()
	else:
	    value = 'Description file not found: %s.\nType new description here.' % filename 

	data = { 'description': value }
	form = DescriptionForm(data)

    return render_to_response('groups/description.html', {
        'group': group,
        'form': form},
        RequestContext(request, {}),
    )

def edit(request, id):
    """ 
    Edit IETF Group details

    **Templates:**

    * ``groups/edit.html``

    **Template Variables:**

    * acronym, acronym_form, group_formset, awp_formset

    """

    group = get_object_or_404(IETFWG, group_acronym=id)
    acronym = get_object_or_404(Acronym,acronym_id=id)

    GroupFormset = inlineformset_factory(Acronym, IETFWG, form=EditForm, can_delete=False, extra=0)
    AWPFormSet = inlineformset_factory(Acronym, WGAWP, form=AWPForm, max_num=2)

    if request.method == 'POST':
        button_text = request.POST.get('submit', '')
        if button_text == 'Cancel':
            url = reverse('sec.groups.views.view', kwargs={'id':id})
            return HttpResponseRedirect(url)

        acronym_form = AcronymForm(request.POST, instance=acronym)
        group_formset = GroupFormset(request.POST, instance=acronym)
        awp_formset = AWPFormSet(request.POST, instance=acronym)
        if acronym_form.is_valid() and group_formset.is_valid() and awp_formset.is_valid():
            acronym_form.save()
            group_formset.save()
            awp_formset.save()
            # if the area was changed we need to change the AreaGroup record
            if 'primary_area' in group_formset.forms[0].changed_data:
                area = Area.objects.get(area_acronym=group_formset.forms[0].cleaned_data.get('primary_area'))
                obj, created = AreaGroup.objects.get_or_create(group=group,defaults={'area':area})
                if not created:
                    obj.area = area
                    obj.save()
            messages.success(request, 'The Group was changed successfully')
            url = reverse('sec.groups.views.view', kwargs={'id':id})
            return HttpResponseRedirect(url)
        else:
            # reset ad options based on submitted primary area
            primary_area = request.POST.get('ietfwg-0-primary_area','')
            if primary_area:
                group_formset.forms[0].fields['area_director'].choices = [(ad.id, "%s %s" % (ad.person.first_name, ad.person.last_name)) for ad in AreaDirector.objects.filter(area=primary_area)]
            
    else:
        acronym_form = AcronymForm(instance=acronym)
        group_formset = GroupFormset(instance=acronym)
        awp_formset = AWPFormSet(instance=acronym)
        # preset extra field primary_area 
        '''
        # need to catch AttributeError because AD entry for "TBD" has NULL area_acronym
        # need to catch ObjectDoesNotExist because many groups reference non-existent AD record
        try:
            group_formset.forms[0].initial['primary_area']=group.area_director.area.area_acronym.acronym_id
        except (AttributeError, ObjectDoesNotExist):
            pass
        #group_formset.forms[0].fields['area_director'].choices = [(ad.id, "%s %s" % (ad.person.first_name, ad.person.last_name)) for ad in AreaDirector.objects.filter(area=group.area_director.area)]
        '''
        
        # some groups, mostly concluded ones, are not associated with an area via the areagroup
        # table.  In this case add blank option to primary area
        area = group.get_area()
        if area == None:
            group_formset.forms[0].fields['primary_area'].widget.choices = SEARCH_AREA_CHOICES
            #assert False, group_formset.forms[0].fields['primary_area'].choices 
        else:
            group_formset.forms[0].initial['primary_area']=group.get_area()
            group_formset.forms[0].fields['area_director'].choices = [(ad.id, "%s %s" % (ad.person.first_name, ad.person.last_name)) for ad in AreaDirector.objects.filter(area=area)]

    return render_to_response('groups/edit.html', {
        'group': group,
        'awp_formset': awp_formset,
        'acronym_form': acronym_form,
        'group_formset': group_formset},
        RequestContext(request, {}),
    )
    
def edit_gm(request, id):
    """ 
    Edit IETF Group Goal and Milestone details

    **Templates:**

    * ``groups/edit_gm.html``

    **Template Variables:**

    * group, formset 

    """

    group = get_object_or_404(IETFWG, group_acronym=id)
    GMFormset = inlineformset_factory(IETFWG, GoalMilestone, form=GoalMilestoneForm, can_delete=True, extra=5)

    if request.method == 'POST':
        button_text = request.POST.get('submit', '')
        if button_text == 'Cancel':
            url = reverse('sec.groups.views.view', kwargs={'id':id})
            return HttpResponseRedirect(url)

        formset = GMFormset(request.POST, instance=group, prefix='goalmilestone')
        if formset.is_valid():
            formset.save()
            messages.success(request, 'The Goals Milestones were changed successfully')
            url = reverse('sec.groups.views.view', kwargs={'id':id})
            return HttpResponseRedirect(url)
    else:
        formset = GMFormset(instance=group, prefix='goalmilestone')

    return render_to_response('groups/edit_gm.html', {
        'group': group,
        'formset': formset},
        RequestContext(request, {}),
    )

def grouplist(request, id):
    """ 
    List IETF Groups, id=group acronym 

    **Templates:**

    * ``groups/list.html``

    **Template Variables:**

    * groups 

    """

    groups = IETFWG.objects.filter(group_acronym__acronym_id=id)

    return render_to_response('groups/list.html', {
        'groups': groups},
        RequestContext(request, {}),
    )

def people(request, id):
    """ 
    Edit People associated with Groups, Chairs

    **Templates:**

    * ``groups/people.html``

    **Template Variables:**

    * driver, form, group

    """

    group = get_object_or_404(IETFWG, group_acronym=id)
    # dictionaries to produce template forms
    driver = [
        {'title':'Chairperson(s)','data':group.wgchair_set.all(),'table':'WGChair'},
        {'title':'Document Editor(s)','data':group.wgeditor_set.all(),'table':'WGEditor'},
        {'title':'Technical Advisor(s)','data':group.wgtechadvisor_set.all(),'table':'WGTechAdvisor'},
        {'title':'Secretary(ies)','data':group.wgsecretary_set.all(),'table':'WGSecretary'}]

    if request.method == 'POST':
        # handle adding a new role 
        if request.POST.get('submit', '') == "Add":
            form = GroupRoleForm(request.POST)
            if form.is_valid():
                name = request.POST.get('role_name', '')
                type = request.POST.get('role_type', '')
                person = get_person(name)
                # make sure ad entry doesn't already exist

                # because the various roles all have the same fields to initialize
                # we can use a generic object create call here
                role_model = get_model('core', type)
                obj = role_model(person=person, group_acronym=group)
                obj.save()

                messages.success(request, 'New %s added successfully!' % type)
                url = reverse('sec.groups.views.people', kwargs={'id':str(group.group_acronym.acronym_id)})
                return HttpResponseRedirect(url)
    else:
        # set hidden group field so we have this info for form validations
        form = GroupRoleForm(initial={'group':id})

    return render_to_response('groups/people.html', {
        'driver': driver,
        'group': group,
        'form': form},
        RequestContext(request, {}),
    )

def search(request):
    """ 
    Search IETF Groups

    **Templates:**

    * ``groups/search.html``

    **Template Variables:**

    * form, results

    """
    results = []
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if request.POST['submit'] == 'Add':
            url = reverse('sec.groups.views.add')
            return HttpResponseRedirect(url)
        
        if form.is_valid():
            kwargs = {} 
            group_acronym = form.cleaned_data['group_acronym']
            group_name = form.cleaned_data['group_name']
            primary_area = form.cleaned_data['primary_area']
            meeting_scheduled = form.cleaned_data['meeting_scheduled']
            status = form.cleaned_data['status']
            type = form.cleaned_data['type'] 
            # construct seach query
            if group_acronym:
                kwargs['group_acronym__acronym__istartswith'] = group_acronym
            if group_name:
                kwargs['group_acronym__name__istartswith'] = group_name
            if primary_area:
                kwargs['areagroup__area__area_acronym'] = primary_area
            if status:
                kwargs['status'] = status
            if type:
                kwargs['group_type'] = type
            if meeting_scheduled:
                kwargs['meeting_scheduled'] = meeting_scheduled
            # perform query
            if kwargs:
                qs = IETFWG.objects.filter(**kwargs)
            else:
                qs = IETFWG.objects.all()
            results = qs.order_by('group_acronym__name')
    # define GET argument to support link from area app 
    elif 'primary_area' in request.GET:
        area = request.GET.get('primary_area','')
        results = IETFWG.objects.filter(areagroup__area__area_acronym=area,status=1).order_by('group_acronym__name')
        form = SearchForm({'primary_area':area})
    else:
        # have status default to active
        form = SearchForm(initial={'status':'1'})

    return render_to_response('groups/search.html', {
        'results': results,
        'form': form},
        RequestContext(request, {}),
    )

def view(request, id):
    """ 
    View IETF Group details

    **Templates:**

    * ``groups/view.html``

    **Template Variables:**

    * group, awps

    """

    group = get_object_or_404(IETFWG, group_acronym=id)
    acronym = get_object_or_404(Acronym,acronym_id=id)
    awps = WGAWP.objects.filter(name=acronym.acronym)

    return render_to_response('groups/view.html', {
        'awps': awps,
        'group': group},
        RequestContext(request, {}),
    )

def view_gm(request, id):
    """ 
    View IETF Group Goals and Milestones details

    **Templates:**

    * ``groups/view_gm.html``

    **Template Variables:**

    * group

    """

    group = get_object_or_404(IETFWG, group_acronym=id)

    return render_to_response('groups/view_gm.html', {
        'group': group},
        RequestContext(request, {}),
    )
