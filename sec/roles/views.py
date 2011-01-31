from django.core.urlresolvers import reverse
from django.db.models import Max
from django.forms.formsets import formset_factory
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils import simplejson
from session_messages import create_message
from models import *
from forms import *
import re
import datetime

def iesg(request):
    """ 
    View IESG members, and save the list to iesg_history. 

    **Templates:**

    * ``roles/iesg.html``

    **Template Variables:**

    * area_directors, current_meeting, next_meeting

    """

    area_directors = AreaDirector.objects.filter(area__status=1).order_by('person')
    current_meeting = IESGHistory.objects.aggregate(Max('meeting'))['meeting__max']
    next_meeting = current_meeting + 1
    
    if request.method == 'POST':
	# handle adding a new director 
	button_text = request.POST.get('submit', '')
        if button_text.startswith('Update'):
            # remove previous entries
            IESGHistory.objects.filter(meeting=current_meeting).delete()
            # save new entries
            for ad in area_directors:
                history_obj = IESGHistory(meeting=current_meeting,area=ad.area,person=ad.person)
                history_obj.save()
            create_message(request, 'The IESG List for IETF %s was updated successfully!' % current_meeting ) 
                
        if button_text.startswith('Save'):
            # save new entries
            for ad in area_directors:
                history_obj = IESGHistory(meeting=next_meeting,area=ad.area,person=ad.person)
                history_obj.save()
            create_message(request, 'The IESG List for IETF %s was updated successfully!' % next_meeting )

    return render_to_response('roles/iesg.html', {
        'current_meeting': current_meeting,
        'next_meeting': next_meeting,
        'area_directors': area_directors},
        RequestContext(request, {}),
    )

def chair(request, type):
    """ 
    View IETF/IAB/NOMCOM Chair history.  Assign a new Chair. 

    **Templates:**

    * ``roles/ietf.html``

    **Template Variables:**

    * chairs, type

    """

    type = type.upper() 
    chair_type = getattr(Role, type + '_CHAIR')    
    chairs = ChairsHistory.objects.filter(chair_type=chair_type).order_by('present_chair','end_year').reverse()
    role = Role.objects.get(id=chair_type)
    
    if request.method == 'POST':
        # handle adding a new director 
        if request.POST.get('submit', '') == "Add":
            form = ChairForm(request.POST)
            if form.is_valid():
		# get person record
		text = request.POST.get('chair_name', '')
		m = re.search(r'\((.*)\)', text)
		tag = m.group(1)
		person = PersonOrOrgInfo.objects.get(person_or_org_tag=tag)
		year = datetime.date.today().year
		# update last
		try:
		    current_chair = ChairsHistory.objects.get(chair_type=chair_type,present_chair=1)
		except:
                    # use ERROR message level once upgraded to Django 1.2
		    create_message(request, 'ERROR: operation failed trying to get current chair.')
                    url = reverse('role_chair', kwargs={'type':type.lower()})
		    return HttpResponseRedirect(url)
		    
		current_chair.present_chair = 0
		current_chair.end_year = year
		current_chair.save()
		# save new chair 
		new_chair = ChairsHistory(chair_type=role,present_chair=1,person=person,start_year=year,end_year=0)
		new_chair.save()
		role.person = person
		role.save()
     
		create_message(request, 'The Chair was added successfully!')
                url = reverse('roles_chair', kwargs={'type':type.lower()})
		return HttpResponseRedirect(url)
    else:
        form = ChairForm()

    return render_to_response('roles/chairs.html', {
        'form': form,
        'type': type,
        'chairs': chairs},
        RequestContext(request, {}),
    )

def liaisons(request):
    """ 
    View Liaison members, add or delete a member 

    **Templates:**

    * ``roles/liaisons.html``

    **Template Variables:**

    * liaisons 

    """

    if request.method == 'POST':
        # handle adding a new Liaison 
        if request.POST.get('submit', '') == "Add":
            form = LiaisonForm(request.POST)
            if form.is_valid():
		affiliation = request.POST.get('affiliation', '')
		name = request.POST.get('liaison_name', '')
		# get person record
		m = re.search(r'\((\d+)\)', name)
		tag = m.group(1)
		person = PersonOrOrgInfo.objects.get(person_or_org_tag=tag)
		liaison = LiaisonsMembers(person=person,affiliation=affiliation)
		liaison.save()
		create_message(request, 'The Liaison was added successfully!')
                url = reverse('sec.roles.views.liaisons')
		return HttpResponseRedirect(url)

        # handle deleting a Liaison 
        if request.POST.get('submit', '') == "Delete":
            tag = request.POST.get('liaison-tag', '')
            try:
                liaison = LiaisonsMembers.objects.get(person=tag)
            except:
                # use ERROR message level once upgraded to Django 1.2
                create_message(request, 'Error locating liaisons record.')
                url = reverse('sec.roles.views.liaisons')
                return HttpResponseRedirect(url)

            liaison.delete()
            create_message(request, 'The liaison was deleted successfully')
            form = LiaisonForm()
    else:
        form = LiaisonForm()

    liaisons = LiaisonsMembers.objects.all()
    return render_to_response('roles/liaisons.html', {
        'form': form,
        'liaisons': liaisons},
        RequestContext(request, {}),
    )
