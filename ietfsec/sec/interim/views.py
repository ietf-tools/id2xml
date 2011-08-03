from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db.models import Max
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect

from sec.groups.models import *
from sec.drafts.models import *
from sec.utils.decorators import check_permissions
from sec.utils.shortcuts import get_my_groups

from models import *
from forms import *

import os
import datetime
import itertools

# -------------------------------------------------
# Helper Functions
# -------------------------------------------------
def create_proceedings(meeting_id):
    """
    This function creates the proceedings.html document.  It gets called anytime there is an
    update to the meeting or the slides for the meeting.
    """
    # get all the objects we need for the template
    meeting = get_object_or_404(InterimMeeting, id=meeting_id)
    year,month,day = parsedate(meeting.meeting_date)
    group_name = meeting.get_group_acronym()
    group = IETFWG.objects.get(group_acronym=meeting.group_acronym_id)
    area_group = AreaGroup.objects.get(group=group.group_acronym)
    area_name = area_group.area.area_acronym.name
    # drafts and rfcs are available from methods on group, but they aren't sorted
    drafts = InternetDraft.objects.filter(group=meeting.group_acronym_id,
                                                    status=1).order_by('start_date')
    rfcs = Rfc.objects.filter(group_acronym=meeting.get_group_acronym()).order_by('rfc_number')
    
    # the simplest way to display the charter is to place it in a <pre> block
    # however, because this forces a fixed-width font, different than the rest of
    # the document we modify the charter by adding replacing linefeeds with <br>'s
    charter = group.charter_text().replace('\n','<br>')
    
    #assert False, charter
    # rather than return the response as in a typical view function we save it as the snapshot
    # proceedings.html
    response = render_to_response('interim/proceedings.html',{
        'meeting':meeting,
        'area_name': area_name,
        'group': group,
        'charter': charter,
        'drafts': drafts,
        'rfcs': rfcs}
    )
    
    # save proceedings
    proceedings_path = os.path.join(settings.MEDIA_ROOT,
                                    'proceedings/interim',
                                    year,
                                    month,
                                    day,
                                    group_name,
                                    'proceedings.html')
    f = open(proceedings_path,'w')
    f.write(response.content)
    f.close()
    
    # save the meeting object, which will cause "updated" field to be current
    meeting.save()
    
def find_index(slide_id, qs):
    """
    This function looks up a slide in a queryset of slides,
    returning the index.
    """
    for i in range(0,qs.count()):
        if str(qs[i].id) == slide_id:
            return i
            
def makedirectories(date, group_name):
    year,month,day = parsedate(date)
    path = os.path.join(settings.MEDIA_ROOT,'proceedings/interim',year,month,day,group_name)
    if not os.path.exists(path):
        os.makedirs(path)

def parsedate(d):
    """
    This function takes a date object and returns a tuple of year,month,day
    """
    return (d.strftime('%Y'),d.strftime('%m'),d.strftime('%d'))

# -------------------------------------------------
# View Functions
# -------------------------------------------------
@check_permissions
def delete_meeting(request, meeting_id):
    meeting = get_object_or_404(InterimMeeting, id=meeting_id)
    
    # delete proceedings.html if exists
    if os.path.isfile(meeting.proceedings_path()):
        os.remove(meeting.proceedings_path())
        
    meeting.delete()

    url = reverse('interim_group', kwargs={'group_id':meeting.group_acronym_id})
    return HttpResponseRedirect(url)

@check_permissions
def delete_slide(request, slide_id):
    slide = get_object_or_404(InterimFile, id=slide_id)
    meeting_id = slide.meeting.id
    
    slide.delete()
    
    # rebuild proceedings.html
    create_proceedings(meeting_id)
            
    url = reverse('interim_meeting', kwargs={'meeting_id':meeting_id})
    return HttpResponseRedirect(url)

@check_permissions
def group(request, group_id):
    group_acronym = get_object_or_404(Acronym, acronym_id=group_id)
    group_name = group_acronym.acronym
    if request.method == 'POST': # If the form has been submitted...
        button_text = request.POST.get('submit', '')
        if button_text == 'Back':
            url = reverse('interim_manage')
            return HttpResponseRedirect(url)
            
        form = MeetingForm(request.POST) # A form bound to the POST data
        if form.is_valid():
            meetingdate = form.cleaned_data['date']
            interim=InterimMeeting()
            interim.group_acronym_id = group_id
            interim.meeting_date = meetingdate
            interim.created = datetime.date.today().isoformat()
            interim.save()
            makedirectories(meetingdate, group_name)
            messages.success(request, 'Meeting created')
            url = reverse('sec.interim.views.group', kwargs={'group_id':group_id})
            return HttpResponseRedirect(url)
    else:
        form = MeetingForm(initial={'group_acronym_id':group_id}) # An unbound form
        
    interim_list = InterimMeeting.objects.filter(group_acronym_id=group_id).order_by('meeting_date')
    return render_to_response('interim/group.html',{
        'group_name':group_name,
        'meeting_list':interim_list,
        'form':form},
        RequestContext(request, {}),
    )

def manage(request):
    """
    Display list of groups this user has access to.
    """
    groups = get_my_groups(request)

    return render_to_response('interim/manage.html', {
        'groups': groups},
        RequestContext(request, {}),
    )

@check_permissions
def meeting(request, meeting_id):
    meeting = get_object_or_404(InterimMeeting, id=meeting_id)
    group_name = meeting.get_group_acronym()
    proceedings_link = ''
    year,month,day = parsedate(meeting.meeting_date)
    
    if request.method == 'POST': # If the form has been submitted...
        button_text = request.POST.get('submit', '')
        if button_text == 'Back':
            url = reverse('interim_group', kwargs={'group_id':meeting.group_acronym_id})
            return HttpResponseRedirect(url)

        # if submitted file type is "minutes" or "agenda" and one already exists, provide instance
        # to the form to update the existing record instead of creating a new one.
        instance = None
        file_type = int(request.POST['file_type_id'])
        if file_type in (InterimFile.AGENDA_FILE_TYPE, InterimFile.MINUTES_FILE_TYPE):
            try:
                instance = InterimFile.objects.get(meeting=meeting_id,file_type_id=file_type)
            except InterimFile.DoesNotExist:
                pass
        
        form = SlideModelForm(request.POST, request.FILES, instance=instance)
        
        if form.is_valid():
            slide = form.save()
            create_proceedings(meeting_id)
            
            messages.success(request, 'File %s Received' % slide.get_short_filename())
            url = reverse('sec.interim.views.meeting', kwargs={'meeting_id':meeting_id})
            return HttpResponseRedirect(url)

    else:
       form = SlideModelForm(initial={'meeting':meeting.id,
                                       'order_num':meeting.max_slide_order_num() + 1,
                                       'file_type_id':InterimFile.SLIDE_FILE_TYPE})
        
    if os.path.exists(meeting.proceedings_path()):
        proceedings_link = "%s/proceedings/interim/%s/%s/%s/%s/proceedings.html" % (settings.MEDIA_URL, year, month, day, group_name)

    return render_to_response('interim/meeting.html',{
        'meeting':meeting,
        'form':form,
        'proceedings_link':proceedings_link},
        RequestContext(request, {}),
    )

@check_permissions
def move_slide(request, slide_id, direction):
    slide = get_object_or_404(InterimFile, id=slide_id)
    
    qs = InterimFile.objects.filter(meeting=slide.meeting.id).order_by('order_num')
    # if direction is up and we aren't already the first slide
    if direction == 'up' and slide_id != str(qs[0].id):
        index = find_index(slide_id, qs)
        slide_before = qs[index-1]
        slide_before.order_num, slide.order_num = slide.order_num, slide_before.order_num
        slide.save()
        slide_before.save()
        # rebuild proceedings.html
        create_proceedings(slide.meeting.id)
    
    # if direction is down, more than one slide and we aren't already the last slide
    if direction == 'down' and qs.count() > 1 and slide_id != str(qs[qs.count()-1].id):
        index = find_index(slide_id, qs)
        slide_after = qs[index+1]
        slide_after.order_num, slide.order_num = slide.order_num, slide_after.order_num
        slide.save()
        slide_after.save()
        # rebuild proceedings.html
        create_proceedings(slide.meeting.id)
        
    url = reverse('interim_meeting', kwargs={'meeting_id':slide.meeting.id})
    return HttpResponseRedirect(url)

def view(request,order_by):
    """
    Displays list of all Interim Meetings, sortable by date or Working Group,
    with links to the meeting proceedings
    2011-03-16: this view was deployed as python script on public site
    """
    
    if order_by == 'date':
        meetings = InterimMeeting.objects.all().order_by('meeting_date')
    else:
        meetings = sorted(InterimMeeting.objects.all(), key=lambda a: a.group_acronym)
    
    return render_to_response('interim/list.html',{
        'meetings':meetings},
        RequestContext(request, {}),
    )
    
@check_permissions
def slide(request, slide_id):
    slide = get_object_or_404(InterimFile, id=slide_id)

    if request.method == 'POST': # If the form has been submitted...
        button_text = request.POST.get('submit', '')
        if button_text == 'Cancel':
            url = reverse('interim_meeting', kwargs={'meeting_id':slide.meeting.id})
            return HttpResponseRedirect(url)
            
        form = EditSlideForm(request.POST, instance=slide) # A form bound to the POST data
        if form.is_valid(): 
            form.save()
            # rebuild proceedings.html
            create_proceedings(slide.meeting.id)
            url = reverse('interim_meeting', kwargs={'meeting_id':slide.meeting.id})
            return HttpResponseRedirect(url)
    else:
        form = EditSlideForm(instance=slide)
    
    return render_to_response('interim/slide.html',{
        'meeting':slide.meeting,
        'slide':slide,
        'form':form},
        RequestContext(request, {}),
    )
