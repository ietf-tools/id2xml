from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db.models import Max
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from session_messages import create_message
from sec.groups.models import *
from sec.drafts.models import *
from models import *
from forms import *
from decorators import wgchair_required
import os
import datetime

# -------------------------------------------------
# Helper Functions
# -------------------------------------------------
def create_proceedings(meeting_id):
    """
    This function creates the proceedings.html document.  It gets called anytime there is an
    update to the meeting or the slides for the meeting.
    """
    # get all the objects we need for the template
    meeting = get_object_or_404(InterimMeeting.objects.using('interim'), id=meeting_id)
    year,month,day = parsedate(meeting.meeting_date)
    group_name = meeting.get_group_acronym()
    group = IETFWG.objects.get(group_acronym=meeting.group_acronym_id)
    mail_list_url = group.email_archive
    chairs = WGChair.objects.filter(group_acronym=meeting.group_acronym_id)
    secretaries = WGSecretary.objects.filter(group_acronym=meeting.group_acronym_id)
    area_group = AreaGroup.objects.get(group=group.group_acronym)
    area_name = area_group.area.area_acronym.name
    ads = AreaDirector.objects.filter(area=area_group.area.area_acronym)
    advisors = WGTechAdvisor.objects.filter(group_acronym=meeting.group_acronym_id)
    goals = GoalMilestone.objects.filter(group_acronym=meeting.group_acronym_id)
    drafts = InternetDraft.objects.filter(group=meeting.group_acronym_id,
                                                    status=1).order_by('start_date')
    rfcs = Rfc.objects.filter(group_acronym=meeting.get_group_acronym()).order_by('rfc_number')
    slides = Slides.objects.using('interim').filter(meeting=meeting_id).order_by('order_num')
    
    # get group description
    filename = os.path.join(settings.GROUP_DESCRIPTION_DIR,group.group_acronym.acronym + '.desc.txt')
    if os.path.isfile(filename):
        f = open(filename,'r')
        description = f.read()
        f.close()
    else:
        description = 'Description file not found: %s.' % filename
    
    # set minutes_url
    minutes_path = os.path.join(settings.MEDIA_ROOT,'interim',year,month,day,group_name,'minutes/minutes.html')
    minutes_url = "%s/interim/%s/%s/%s/%s/minutes/minutes.html" % (settings.MEDIA_URL, year, month, day, group_name)
    if not os.path.exists(minutes_path):
        minutes_url = ''
    
    # rather than return the response as in a typical view function we save it as the snapshot
    # proceedings.html
    response = render_to_response('interim/proceedings.html',{
        'meeting':meeting,
        'minutes_url': minutes_url,
        'mail_list_url': mail_list_url,
        'chairs': chairs,
        'secretaries': secretaries,
        'area_name': area_name,
        'ads': ads,
        'advisors': advisors,
        'group': group,
        'description': description,
        'goals': goals,
        'drafts': drafts,
        'rfcs': rfcs,
        'slides': slides}
    )
    
    # save proceedings
    proceedings_path = os.path.join(settings.MEDIA_ROOT,'interim',year,month,day,group_name,'proceedings.html')
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
    path = os.path.join(settings.MEDIA_ROOT,'interim',year,month,day,group_name)
    os.makedirs(path)

def parsedate(d):
    """
    This function takes a date object and returns a tuple of year,month,day
    """
    return (d.strftime('%Y'),d.strftime('%m'),d.strftime('%d'))
# -------------------------------------------------
# View Functions
# -------------------------------------------------
def index(request):
    interim_list = InterimMeeting.objects.using('interim').all().order_by('-id','group_acronym_id')
    return render_to_response('interim/index.html', {'interim_list': interim_list})
    
def dashboard(request):
    """
    This application is designed to be accessed by Group Chairs.  Lookup login name
    (from REMOTE_USER) and display any groups the user is chair of.
    """
    try:
        legacy = LegacyWgPassword.objects.get(login_name=request.META['REMOTE_USER'])
        wgchairs = WGChair.objects.filter(person=legacy.person.person_or_org_tag)
    except ObjectDoesNotExist:
        wgchairs = ''
    
    return render_to_response('interim/dashboard.html', {
        'wgchairs': wgchairs},
        RequestContext(request, {}),
    )

@wgchair_required
def group(request, group_id):
    group_acronym = get_object_or_404(Acronym, acronym_id=group_id)
    group_name = group_acronym.acronym
    if request.method == 'POST': # If the form has been submitted...
        form = MeetingForm(request.POST) # A form bound to the POST data
        if form.is_valid():
            meetingdate = form.cleaned_data['date']
            interim=InterimMeeting()
            interim.group_acronym_id = group_id
            interim.meeting_date = meetingdate
            interim.created = datetime.date.today().isoformat()
            interim.save(using='interim')
            makedirectories(meetingdate, group_name)
            create_message(request, 'Meeting created')
            url = reverse('sec.interim.views.group', kwargs={'group_id':group_id})
            return HttpResponseRedirect(url)
    else:
        form = MeetingForm(initial={'group_acronym_id':group_id}) # An unbound form
        
    interim_list = InterimMeeting.objects.using('interim').filter(group_acronym_id=group_id).order_by('-meeting_date')
    return render_to_response('interim/group.html',{
        'group_name':group_name,
        'meeting_list':interim_list,
        'form':form},
        RequestContext(request, {}),
    )

@wgchair_required
def meeting(request, meeting_id):
    meeting = InterimMeeting.objects.using('interim').get(id=meeting_id)
    group_name = meeting.get_group_acronym()
    proceedings_link = ''
    year,month,day = parsedate(meeting.meeting_date)
    
    if request.method == 'POST': # If the form has been submitted...
        form = SlideModelForm(request.POST, request.FILES) # A form bound to the POST data
        if form.is_valid():
            slide = form.save(commit=False)
            slide.meeting = meeting
            slide.save(using='interim')  
            create_proceedings(meeting_id)
            
            create_message(request, 'File %s Received' % slide.filename)
            url = reverse('sec.interim.views.meeting', kwargs={'meeting_id':meeting_id})
            return HttpResponseRedirect(url)

    else:
        # set default slide order_num to next max order_num + 1
        max_order_num = Slides.objects.using('interim').filter(meeting=meeting_id).aggregate(Max('order_num'))['order_num__max']
        if max_order_num:
            next_order_num = max_order_num + 1
        else:
            next_order_num = 1

        form = SlideModelForm(initial={'meeting':meeting.id,'order_num':next_order_num})
        
    procpath = os.path.join(settings.MEDIA_ROOT,'interim',year,month,day,group_name,'proceedings.html')
    if os.path.exists(procpath):
        proceedings_link = "%s/interim/%s/%s/%s/%s/proceedings.html" % (settings.MEDIA_URL, year, month, day, group_name)

    slides = Slides.objects.using('interim').filter(meeting=meeting_id).order_by('order_num')
    return render_to_response('interim/meeting.html',{
        'slides':slides,
        'meeting':meeting,
        'form':form,
        'proceedings_link':proceedings_link},
        RequestContext(request, {}),
    )

@wgchair_required
def slide(request, slide_id):
    slide = get_object_or_404(Slides.objects.using('interim'), id=slide_id)
    meeting = InterimMeeting.objects.using('interim').get(id=slide.meeting.id)

    if request.method == 'POST': # If the form has been submitted...
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
        'meeting':meeting,
        'slide':slide,
        'form':form},
        RequestContext(request, {}),
    )

@wgchair_required
def move_slide(request, slide_id, direction):
    slide = Slides.objects.using('interim').get(id=slide_id)
    meeting_id = slide.meeting.id
    meeting = InterimMeeting.objects.using('interim').get(id=meeting_id)
    
    qs = Slides.objects.using('interim').filter(meeting=meeting).order_by('order_num')
    # if direction is up and we aren't already the first slide
    if direction == 'up' and slide_id != str(qs[0].id):
        index = find_index(slide_id, qs)
        slide_before = qs[index-1]
        slide_before.order_num, slide.order_num = slide.order_num, slide_before.order_num
        slide.save(using='interim')
        slide_before.save(using='interim')
        # rebuild proceedings.html
        create_proceedings(meeting.id)
    
    # if direction is down, more than one slide and we aren't already the last slide
    if direction == 'down' and qs.count() > 1 and slide_id != str(qs[qs.count()-1].id):
        index = find_index(slide_id, qs)
        slide_after = qs[index+1]
        slide_after.order_num, slide.order_num = slide.order_num, slide_after.order_num
        slide.save(using='interim')
        slide_after.save(using='interim')
        # rebuild proceedings.html
        create_proceedings(meeting.id)
        
    url = reverse('interim_meeting', kwargs={'meeting_id':meeting.id})
    return HttpResponseRedirect(url)

