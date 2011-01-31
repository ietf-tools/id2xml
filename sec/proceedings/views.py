from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.urlresolvers import reverse
from django.forms.formsets import formset_factory
from django.forms.models import inlineformset_factory, modelformset_factory
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.template import Context
from django.template.loader import get_template
from django.utils import simplejson
from django.db.models import Max,Count
from session_messages import create_message
from models import *
from sec.core.models import Acronym
from sec.groups.models import IETFWG
from sec.proceedings.models import *
from forms import *
import os
import re
import glob
import shutil
import zipfile

# -------------------------------------------------
# Helper Functions
# -------------------------------------------------
def handle_uploaded_file(f,local_dir,meeting_num,filename):

    """
    Save uploaded (Agenda, Minutes, Slides ) files to location determined by settings variable
    """

    dest_dirname = os.path.join(settings.PROCEEDINGS_DIR + '/'+ str(meeting_num) + '/'+ local_dir + '/'+ filename) 
    destination = open(dest_dirname, 'wb+')

    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()

#---------------------------------------------------------
def handle_presentation_upload(file,filename,group_dirname,meeting_num): 

    """
    1. Save the zipped file in slides folder
    2. For every slide create new directory with group_name + slide_num  in the slide dirfectory
    3. Move the zipped file from slides folder to particular group folder  
    """

    filename = filename.lower()

    dest_dirnamefile = os.path.join(settings.PROCEEDINGS_DIR + '/'+ str(meeting_num) + '/' + 'slides' + '/' + filename)
    destination = open(dest_dirnamefile, 'wb+')
    for chunk in file.chunks():
        destination.write(chunk)
    destination.close()

#Make the directory to store the zip file
    dest_dirname = os.path.join(settings.PROCEEDINGS_DIR + '/'+ str(meeting_num) + '/' + 'slides')
    os.chdir(dest_dirname)
    os.mkdir(group_dirname)

#Copy the zip file to proper location 
    source_filename = os.path.join(settings.PROCEEDINGS_DIR + '/'+ str(meeting_num) + '/' + 'slides' + '/' + filename)
    dest_filename = os.path.join(settings.PROCEEDINGS_DIR + '/'+ str(meeting_num) + '/' + 'slides' + '/' + group_dirname + '/' + filename)
    shutil.move(source_filename,dest_filename)
    
#To handle the zipfile logic
#1. Change directory to group directory and make the folder for unzipping the file   
    zipped_slide_dir = os.path.join(settings.PROCEEDINGS_DIR + '/'+ str(meeting_num) + '/' + 'slides' + '/' + group_dirname)
    os.chdir(zipped_slide_dir)
    
#2. Read the zipfile and extract the zipped file contents 
    cmd_unzip = "unzip" + " " + filename
    os.system(cmd_unzip)

#Copy the Uploaded PPT with proper name (This upload is done by WG)
    os.chdir(dest_dirname)
    ppt_name_low = group_dirname.lower()
    ppt_name = ppt_name_low + ".ppt"
    gr_name = group_dirname + ".ppt"

    ppt_file =  os.path.join(settings.PROCEEDINGS_DIR + '/'+ str(meeting_num) + '/' + 'slides' + '/' + gr_name)

#    if os.path.exists(ppt_file):
#       shutil.copy(gr_name,ppt_name)

#---------------------------------------------------------
def handle_delete_file(meeting_num,local_dir,filename):
    """
    Deletes the (Agenda, Minutes, Slides ) files specified in the input data
    """
    
    dest_dirname = os.path.join(settings.PROCEEDINGS_DIR + '/'+ str(meeting_num) + '/'+ local_dir + '/' + filename)

    if local_dir == 'slides':
        if os.path.exists(dest_dirname):
           shutil.rmtree(dest_dirname)
    else:
        if os.path.exists(dest_dirname):
            os.remove(dest_dirname)
 
   
# --------------------------------------------------
# STANDARD VIEW FUNCTIONS
# --------------------------------------------------

def add(request):
    """
    Add a new IETF Meeting

    **Templates:**

    * ``proceedings/add.html``

    **Template Variables:**

    * proceedingform

    """
    if request.method == 'POST':
        proceedingform = AddProceedingForm(request.POST)
        if proceedingform.is_valid():
            # get form data - for Meeting Object
            meeting_num = proceedingform.cleaned_data['meeting_num']
            start_date = proceedingform.cleaned_data['start_date']
            end_date = proceedingform.cleaned_data['end_date']
            city = proceedingform.cleaned_data['city']
            state = proceedingform.cleaned_data['state']
            country = proceedingform.cleaned_data['country']

            # get form data - for Proceeding Object
            dir_name = proceedingform.cleaned_data['dir_name']
            sub_begin_date = proceedingform.cleaned_data['sub_begin_date']
            sub_cut_off_date = proceedingform.cleaned_data['sub_cut_off_date']
            c_sub_cut_off_date = proceedingform.cleaned_data['c_sub_cut_off_date']
            pr_from_date= proceedingform.cleaned_data['pr_from_date']
            pr_to_date= proceedingform.cleaned_data['pr_to_date']

            # We will need 2 objects over here Proceedings and Meetings
            # save new Meeting

            meeting_obj = Meeting(meeting_num=meeting_num,start_date=start_date,end_date=end_date,city=city,state=state,country=country)
            meeting_obj.save()

            # save new Proceeding
            # Using the meeting object to save in the Proceeding(As Meeting and Proceeding models are link together)
            proceeding_obj = Proceeding(meeting_num=meeting_obj,dir_name=dir_name,sub_begin_date=sub_begin_date,sub_cut_off_date=sub_cut_off_date,frozen=0,c_sub_cut_off_date=c_sub_cut_off_date,pr_from_date=pr_from_date,pr_to_date=pr_to_date)
            proceeding_obj.save()

           #Create Physical new meeting directory and subdirectories

            dest_dirname = os.path.join(settings.PROCEEDINGS_DIR + '/'+ str(meeting_num))
            os.mkdir(dest_dirname)
            os.chdir(dest_dirname)
            os.mkdir('slides')
            os.mkdir('agenda')
            os.mkdir('minutes')
            os.mkdir('id')
            os.mkdir('rfc')

            create_message(request, 'The Meeting was created successfully!')
            url = reverse('sec.proceedings.views.list')


            return HttpResponseRedirect(url)
    else:
        # display initial forms
        proceedingform = AddProceedingForm()


    return render_to_response('proceedings/add.html', {
        'proceedingform': proceedingform},
        RequestContext(request, {}),
    )


def list(request):
    """
    List IETF Meetings

    **Templates:**

    * ``proceedings/list.html``

    **Template Variables:**

    * proceeding_list

    """

    proceeding_list = Proceeding.objects.order_by('meeting_num')
    return render_to_response('proceedings/list.html',{
           'proceeding_list': proceeding_list},
          RequestContext(request,{}), 
    )



def view(request, id):
    """
    View Meeting information.

    **Templates:**

    * ``proceedings/view.html``

    **Template Variables:**

    * meeting , proceeding

    """
    # get meeting or return HTTP 404 if record not found

    meeting = get_object_or_404(Meeting, meeting_num=id)
    proceeding = get_object_or_404(Proceeding, meeting_num=id)


    return render_to_response('proceedings/view.html', {
        'meeting': meeting,
        'proceeding': proceeding},
        RequestContext(request, {}),
    )


def edit(request, id):

    """
    Edit Meeting information.

    **Templates:**

    * ``proceedings/edit.html``

    **Template Variables:**

    * meeting, meeting_formset, meeting_form

    """
    # get meeting or return HTTP 404 if record not found
    meeting = get_object_or_404(Meeting, meeting_num=id)
    proceeding = get_object_or_404(Proceeding, meeting_num=id)

    ProceedingFormSet = inlineformset_factory(Meeting, Proceeding, form=MeetingForm, can_delete=False, extra=0)
#    ProceedingFormSet = inlineformset_factory(Meeting, Proceeding, form=MeetingForm, can_delete=False, extra=0,fields='frozen')

    if request.method == 'POST':
       button_text = request.POST.get('submit','')
       if button_text == 'Save':
            proceeding_formset = ProceedingFormSet(request.POST, instance=meeting)
#            proceeding_formset = ProceedingFormSet(request.POST, instance=proceeding)

            meeting_form = MeetingForm(request.POST, instance=meeting)

            if proceeding_formset.is_valid() and meeting_form.is_valid():
               proceeding_formset.save()
               meeting_form.save()
               create_message(request,'The meeting entry was changed successfully')
               url = reverse('sec.proceedings.views.view', kwargs={'id':id})
               return HttpResponseRedirect(url)

       else:
              url = reverse('sec.proceedings.views.view', kwargs={'id':id})
              return HttpResponseRedirect(url)
    else:
#        meeting_form = MeetingForm(instance=meeting)
         proceeding_formset = ProceedingFormSet(instance=meeting)
         meeting_form = MeetingForm(instance=meeting)

    return render_to_response('proceedings/edit.html', {
         'meeting': meeting,
         'proceeding_formset': proceeding_formset,
         'meeting_form' : meeting_form, },
        RequestContext(request,{}),
    )



def status(request,id):
    """
    Edits the status associated with proceedings: Freeze/Unfreeze proceeding status.

    **Templates:**

    * ``proceedings/view.html``

    **Template Variables:**

    * meeting , proceeding

    """
    # get meeting or return HTTP 404 if record not found

    meeting = get_object_or_404(Meeting, meeting_num=id)
    proceeding = get_object_or_404(Proceeding, meeting_num=id)


    #Call the respected page using data passed.   
    return render_to_response('proceedings/status.html', {
           'meeting':meeting,
	   'proceeding':proceeding},
          RequestContext(request,{}), 
    )



def modify(request,id):
    """
    Handle status changes of Proceedings (Activate, Freeze)

    **Templates:**

    * none

    Redirects to view page on success.

    """

    if request.method == 'POST':
	

        meeting = get_object_or_404(Meeting, meeting_num=id)
        proceeding = get_object_or_404(Proceeding, meeting_num=id)

        #Handles the freeze request
	if request.POST.get('submit', '') == "Freeze":  

           new_proceeding_obj = Proceeding(meeting_num=meeting,dir_name=proceeding.dir_name,sub_begin_date=proceeding.sub_begin_date,sub_cut_off_date=proceeding.sub_cut_off_date,frozen=1,c_sub_cut_off_date=proceeding.c_sub_cut_off_date,pr_from_date=proceeding.pr_from_date,pr_to_date=proceeding.pr_to_date)

           new_proceeding_obj.save()
           create_message(request, 'Proceedings have been freezed successfully!')


        if request.POST.get('submit','') == "Activate":

           new_proceeding_obj = Proceeding(meeting_num=meeting,dir_name=proceeding.dir_name,sub_begin_date=proceeding.sub_begin_date,sub_cut_off_date=proceeding.sub_cut_off_date,frozen=0,c_sub_cut_off_date=proceeding.c_sub_cut_off_date,pr_from_date=proceeding.pr_from_date,pr_to_date=proceeding.pr_to_date)

           new_proceeding_obj.save()
           create_message(request, 'Proceedings have been activated successfully!')


        url = reverse('sec.proceedings.views.view', kwargs={'id':str(id)})
        return HttpResponseRedirect(url)





def upload_group(request,id,menu):
    """
    Handles the upload material process for the various categories.
      
    The main categories are
    
    - Groups/BOF/Plenary
    
    - Training
    
    - IRTF Group
    
    - Interim Meeting Groups 

    Shows the Groups under each category, each group detemines the current material

    related to that group

    **Templates:**

    * ``proceedings/view.html``

    **Template Variables:**

    * meeting , proceeding,upload_form,group_list,menu,upload_form

    """


    # get meeting  and proceeding or return HTTP 404 if record not found

    meeting = get_object_or_404(Meeting, meeting_num=id)
    proceeding = get_object_or_404(Proceeding, meeting_num=id)

    menu = menu
    
    group_list = []     
   # Get the maximum meeting number(Object) from Meeting model
    max_meeting_number = Proceeding.objects.aggregate(Max('meeting_num'))

    # Get Max meetig number from the Meeting object
    max_meeting_num = max_meeting_number['meeting_num__max']

    # Now check the passed meeting number to set value of meeting_scheduled_field
    # 1. Is same as the maximum meeting number from meetings table assign meeting_scheduled value
    # 2. Is different than the maximum meeting number from meetings table assign meeting_scheduled value

    # Initialize the meeting_scheduled field value
    meeting_scheduled_field = ''
    irtf = 0
    interim = 0 
    wg_exist = 0
    min_exist = 0

    if request.method == 'POST':
       button_text = request.POST.get('submit','')

       if button_text == 'Cancel':
          url = reverse('sec.proceedings.views.view', kwargs={'id':str(id)})
          return HttpResponseRedirect(url)

   # Group Selection dropdown criteria
   # If the passed meeting number is the latest meeting number then based on meeting scheduled filed
   # If the passed meeting number is not the latest meeting number then based on meeting scheduled old filed

       if menu == 'group':
          if str(max_meeting_num) == str(id):
             upload_form = GroupSelectionForm(request.POST,request.FILES,menu='group',meeting_scheduled_field='meeting_scheduled')
             group_list = Acronym.objects.filter(ietfwg__meeting_scheduled__exact='YES').order_by('acronym')            
             menu = "group"
          else:
             meeting_scheduled_field = 'meeting_scheduled_old'
             upload_form = GroupSelectionForm(request.POST,request.FILES,menu='group',meeting_scheduled_field='meeting_scheduled_old')
             group_list = Acronym.objects.filter(ietfwg__meeting_scheduled_old__exact='YES').order_by('acronym')            
             menu = "group"
       elif menu == 'training':
             upload_form = GroupSelectionForm(request.POST,request.FILES,menu='training',meeting_num=id)
             group_list = []
             q = WgMeetingSession.objects.filter(meeting=id,group_acronym_id__lt=-2)
             for item in q:
                 ts_choices = Acronym.objects.filter(acronym_id=item.group_acronym_id)
#----------------------------------------------------------------------------------
#Since Negative indices are not allowed in the django templates this arrangement
#is made. The "Training Session" has acronym ID in the negative range. So here 
#making it positive before passing to template. 
#----------------------------------------------------------------------------------
                 for e in ts_choices:
                       if e.acronym_id < 0:
                          tmp_acronym_id = e.acronym_id
                          e.acronym_id = 0 - (tmp_acronym_id)
                 group_list.append(e)                       
             menu = "training"
       elif menu == 'irtf':
             upload_form = GroupSelectionForm(request.POST,request.FILES,menu='irtf')
             group_list = IRTF.objects.all().order_by('acronym')
             menu = "irtf"
       elif menu == 'interim':
          if str(max_meeting_num) == str(id):
             upload_form = GroupSelectionForm(request.POST,request.FILES,menu='interim',meeting_scheduled_field='meeting_scheduled')
             group_list = Acronym.objects.filter(ietfwg__meeting_scheduled__exact='YES').order_by('acronym')            
             menu= "interim"
          else:
             meeting_scheduled_field = 'meeting_scheduled_old'
             upload_form = GroupSelectionForm(request.POST,request.FILES,menu='interim',meeting_scheduled_field='meeting_scheduled_old')
             group_list = Acronym.objects.filter(ietfwg__meeting_scheduled_old__exact='YES').order_by('acronym')            
             menu = "interim"
   #If the form is valid get the values of fields
       if upload_form.is_valid():
          group_acronym_id = upload_form.cleaned_data['group_name']
          material_type = upload_form.cleaned_data['material_type']
          slide_name =  upload_form.cleaned_data['slide_name']
          slide_type_id = upload_form.cleaned_data['file_format']

   #Get the acronym name for the selected group_acronym_id (acronym_id)
          if group_acronym_id == 0:
             group_name = "Ermsg"
   #Need to handle the group message
          if group_acronym_id == -1:
             group_name = "plenaryw"
          elif group_acronym_id == -2:
             group_name = "plenaryt"
          else:
             if menu == 'irtf':
            #Get from group_name from irtf_acronym #
                irtf = 1
                q = IRTF.objects.filter(irtf_id=group_acronym_id)
                for item in q:
                   group_name = item.acronym
             else:
                q = Acronym.objects.filter(acronym_id=group_acronym_id)
                for item in q:
                   group_name = item.acronym

                if menu == 'interim':
                   interim = 1
                   group_name = "i" + group_name
 
    #Get the file name and file type based on the slide_type_id
          filename = group_name

          if slide_type_id == 1:
             slide_type = 'html'
          elif slide_type_id == 2:
             slide_type = 'pdf'
          elif slide_type_id == 3:
             slide_type = 'txt'


          file = request.FILES[request.FILES.keys()[0]]


    #Depending upon the material  type(ie Presentation/Agenda/Minute) perform relevant actions
    #If Uploaded material is slide-presentation#
    #------------------------------------------
          if material_type == 1:

    #Get the current slides 
               local_dir = 'slides'
               if slide_type_id == 1: 
                   dict_slide = Slide.objects.filter(meeting__exact=id,group_acronym_id__exact=group_acronym_id).aggregate(Max('slide_num'))
                   slide_num = dict_slide['slide_num__max']

                   if slide_num is None:
                      slide_num = '0'
                   else:
                      slide_num = slide_num + 1;
                  
                   filename = group_name + "-" + str(slide_num)  
                   group_dirname = filename
                   filename = filename + ".zip" 

	    	   handle_presentation_upload(file,filename,group_dirname,id) 
                   slide_obj = Slide(meeting=meeting,group_acronym_id=group_acronym_id,slide_num=slide_num,slide_type_id=slide_type_id,slide_name=slide_name,irtf=irtf,interim=interim,in_q=0)
                   slide_obj.save()

    #If Uploaded material is agenda/minute#
    #------------------------------------------
	  elif material_type == 2 :
               filename = group_name + "." + slide_type
	       local_dir = 'minutes'
               min_exist = Minute.objects.filter(meeting=id,group_acronym_id=group_acronym_id,irtf=irtf,interim=interim)

               for file in request.FILES.values():
                      handle_uploaded_file(file,local_dir,id,filename)

               if min_exist:
                      for item in min_exist:
		          Minute_obj = Minute(id=item.id,meeting=item.meeting,group_acronym_id=item.group_acronym_id,filename=filename,irtf=item.irtf,interim=item.interim)
        	          Minute_obj.save()
               else : 
      	              Minute_obj = Minute(meeting=meeting,group_acronym_id=group_acronym_id,filename=filename,irtf=irtf,interim=interim)
        	      Minute_obj.save()
          elif material_type == 3 :
               filename = group_name + "." + slide_type
               local_dir = 'agenda'
               wg_exist =  WgAgenda.objects.filter(meeting=id,group_acronym_id=group_acronym_id,irtf=irtf,interim=interim)
               
               for file in request.FILES.values():
                      handle_uploaded_file(file,local_dir,id,filename)

               if wg_exist:
                      for item in wg_exist:
		          WgAgenda_obj = WgAgenda(id=item.id,meeting=item.meeting,group_acronym_id=item.group_acronym_id,filename=filename,irtf=item.irtf,interim=item.interim)
        	          WgAgenda_obj.save()
               else: 
	              WgAgenda_obj = WgAgenda(meeting=meeting,group_acronym_id=group_acronym_id,filename=filename,irtf=irtf,interim=interim)
        	      WgAgenda_obj.save()
          
    #Now store the actual file at the correct location using the handle_uploaded_file

          create_message(request,'The material was uploaded successfully')
          url = reverse('sec.proceedings.views.upload_group', args=(id,menu))
          return HttpResponseRedirect(url)
    #If the Material uploaded is not in proper format
       else:
          create_message(request,'MATERIAL NOT IN PROPER FORMAT')
          url = reverse('sec.proceedings.views.upload_group', args=(id,menu))
          return HttpResponseRedirect(url)

    else: 
         if menu == 'group':
            if str(max_meeting_num) == str(id):
               upload_form = GroupSelectionForm(menu='group',meeting_scheduled_field='meeting_scheduled')
               group_list = Acronym.objects.filter(ietfwg__meeting_scheduled__exact='YES').order_by('acronym')            
               menu = "group"
            else:
               meeting_scheduled_field = 'meeting_scheduled_old'
               upload_form = GroupSelectionForm(menu='group',meeting_scheduled_field='meeting_scheduled_old')
               group_list = Acronym.objects.filter(ietfwg__meeting_scheduled_old__exact='YES').order_by('acronym')            
               menu = "group"
         elif menu == 'training':
               upload_form = GroupSelectionForm(menu='training',meeting_num=id)
               group_list = []
               q = WgMeetingSession.objects.filter(meeting=id,group_acronym_id__lt=-2)
               for item in q:
                   ts_choices = Acronym.objects.filter(acronym_id=item.group_acronym_id)
#----------------------------------------------------------------------------------
#Since Negative indices are not allowed in the django templates this arrangement
#is made. The "Training Session" has acronym ID in the negative range. So here 
#making it positive before passing to template. 
#----------------------------------------------------------------------------------
                   for e in ts_choices:
                       if e.acronym_id < 0:
                          tmp_acronym_id = e.acronym_id
                          e.acronym_id = 0 - (tmp_acronym_id)
                   group_list.append(e)                       
               menu = "training"
         elif menu == 'irtf':
               upload_form = GroupSelectionForm(menu='irtf')
               group_list = IRTF.objects.all().order_by('acronym')
               menu = "irtf"
         elif menu == 'interim':
            if str(max_meeting_num) == str(id):
               upload_form = GroupSelectionForm(menu='interim',meeting_scheduled_field='meeting_scheduled')
               group_list = Acronym.objects.filter(ietfwg__meeting_scheduled__exact='YES').order_by('acronym')            
               menu= "interim"
            else:
               meeting_scheduled_field = 'meeting_scheduled_old'
               upload_form = GroupSelectionForm(menu='interim',meeting_scheduled_field='meeting_scheduled_old')
               group_list = Acronym.objects.filter(ietfwg__meeting_scheduled_old__exact='YES').order_by('acronym')            
               menu = "interim"
              
         return render_to_response('proceedings/upload_group.html', {
            'meeting':meeting,
            'proceeding':proceeding,
            'group_list':group_list,
            'menu':menu,
            'upload_form': upload_form},
             RequestContext(request,{}),
            )




def convert(request, id):
    """
    Handles the PPT to HTML conversion download/upload process.

    Slides waiting in a list for conversion are listed and manual Upload/Download is

    performed
 

    **Templates:**

    * ``proceedings/convert.html``

    **Template Variables:**

    * meeting , proceeding, slide_info

    """

    # get meeting or return HTTP 404 if record not found

    meeting = get_object_or_404(Meeting, meeting_num=id)
    proceeding = get_object_or_404(Proceeding, meeting_num=id)

   # Get the directory name for the passed meeting
    q = Proceeding.objects.filter(meeting_num=id)
    for item in q:
        dir_name = item.dir_name

   #Get the file names in queue waiting for the conversion

    slide_list = Slide.objects.filter(meeting=id,in_q='1')

  #Store the slide related details n the slide_info 
    ind_slide = []
    slide_info = []


  #Get the correct group name for individual groups/plenaries/irtf depending upon the group_acronym_id
    for slide_item in slide_list:
       if (slide_item.group_acronym_id == -1):
            ind_slide =  [{'slide_name':slide_item.slide_name,'group_name':'plenaryw','interim':slide_item.interim,'id':slide_item.id,'slide_num':slide_item.slide_num,'slide_type_id':slide_item.slide_type_id}]
       elif (slide_item.group_acronym_id == -2):
            ind_slide =  [{'slide_name':slide_item.slide_name,'group_name':'plenaryt','interim':slide_item.interim,'id':slide_item.id,'slide_num':slide_item.slide_num,'slide_type_id':slide_item.slide_type_id}]
       else:
            if slide_item.irtf == 0:
               group_name = Acronym.objects.filter(acronym_id=slide_item.group_acronym_id)
            else:
               group_name = IRTF.objects.filter(irtf_id=slide_item.group_acronym_id)
            for x in group_name:
               ind_slide =  [{'slide_name':slide_item.slide_name,'group_name':x.acronym,'interim':slide_item.interim,'id':slide_item.id,'slide_num':slide_item.slide_num,'slide_type_id':slide_item.slide_type_id}]
       slide_info.append(ind_slide)


    return render_to_response('proceedings/convert.html', {
        'meeting': meeting,
        'proceeding': proceeding,
        'slide_info':slide_info},
        RequestContext(request, {}),
    )



def upload_presentation(request,id,slide_id):
    """
    Handles the upload process for the zipped slide files.
      
    The files are in PPT/PPTX format. Manual downlaod and conversion to HTML is performed. 

    A zip file is consists of HTML file , plus related files.
    

    **Templates:**

    * ``proceedings/view.html``

    **Template Variables:**

    * meeting , proceeding,upload_presentation,slide_name,group_name,slide_id

    """

    meeting = get_object_or_404(Meeting, meeting_num=id)
    proceeding = get_object_or_404(Proceeding, meeting_num=id)

    #material_type = ''  

#Get All the details of the files to upload:
    slide_info = Slide.objects.filter(meeting=id,id=slide_id)
   
    for i in slide_info:
        if (i.group_acronym_id == -1):
            group_name = 'plenaryw'
        elif (i.group_acronym_id == -2):
            group_name = 'plenaryt'
        else:
            if i.irtf == 0:
               group = Acronym.objects.filter(acronym_id=i.group_acronym_id)
            else:
               group = IRTF.objects.filter(irtf_id=i.group_acronym_id)
            for x in group:
               group_name = x.acronym  


        if i.interim == 1:
             group_name = "i".group_name
 
        slide_name = i.slide_name
        group_acronym_id = i.group_acronym_id
        slide_num = i.slide_num
        irtf = i.irtf
        interim = i.interim   
        file_name = group_name 
    
    local_dir = 'slides'
    
    if request.method == 'POST':
        button_text = request.POST.get('submit','')
        upload_presentation  = UploadPresentationForm(request.POST,request.FILES)

        if upload_presentation.is_valid():
            slide_name = upload_presentation.cleaned_data['slide_name']
            file = request.FILES[request.FILES.keys()[0]]
            slide_type_id = 1
            file_name = group_name + "-" + str(slide_num)  
            group_dirname = file_name
            file_name = file_name + ".zip" 
            for file in request.FILES.values():
	    	handle_presentation_upload(file,file_name,group_dirname,id) 

            slide_obj = Slide(id=slide_id,meeting=meeting,group_acronym_id=group_acronym_id,slide_num=slide_num,slide_type_id=slide_type_id,slide_name=slide_name,irtf=irtf,interim=interim,in_q=0)
            slide_obj.save()

            create_message(request,'Presentation file uploaded sucessfully')
            url = reverse('sec.proceedings.views.upload_presentation', args=(id,slide_id))
            return HttpResponseRedirect(url)

    else:
         upload_presentation = UploadPresentationForm(initial={'slide_name': slide_name})

    return render_to_response('proceedings/upload_presentation.html', {
               'meeting': meeting,
               'proceeding': proceeding,
               'upload_presentation': upload_presentation,
               'slide_name': slide_name,
               'group_name': group_name,
               'slide_id': slide_id},
       RequestContext(request, {}),
    )


def current_material(request,id,acronym_id,menu):

    """
    Handles the Groupwise listing of current materials for the selected meeting 

    and menu(Group/Training/IRTF/Interim).
      
    **Templates:**

    * ``proceedings/current_material.html``

    **Template Variables:**

    * meeting , proceeding,menu,acronym,wg_filename,wg_id,min_filename,min_id,slides_list

    """

    # get meeting or return HTTP 404 if record not found

    meeting = get_object_or_404(Meeting, meeting_num=id)
    proceeding = get_object_or_404(Proceeding, meeting_num=id)

#Required Special handling for the menu training for negative acronym_id
#Required Special handling for the Wednesday plenary
#Required Special handling for the Thursday plenary

    if menu == "group":
        irtf = 0
        interim = 0   
	if acronym_id == '1' :
           acronym_id = -1  
           acronym = 'plenaryw'
    	elif acronym_id == '2' :
           acronym_id = -2
           acronym = 'plenaryt'
        else:
           acronym_list = Acronym.objects.filter(acronym_id=acronym_id)
           for i in acronym_list:
               acronym = i.acronym  
    elif menu == "training":
        irtf = 0
        interim = 0
	if acronym_id == '1' :
           acronym_id = -1
	   acronym = 'plenaryw'
    	elif acronym_id == '2' :
           acronym_id =  -2 
           acronym = 'plenaryt'
#------ This case is a special case DON'T KNOW THE REASON WHY NOT WORKING----------#
        elif  acronym_id == '16' :
           acronym_id = -16 
           acronym = 'IE'
#------ END OF special case ----------#
        elif acronym_id > '2' :
           tmp_acronym_id = int(acronym_id) 
           acronym_id = 0 - (tmp_acronym_id)
           acronym_list = Acronym.objects.filter(acronym_id=acronym_id)
           for i in acronym_list:
               acronym = i.acronym  
    elif menu == "irtf":
        irtf = 1
        interim = 0
	if acronym_id == '1' :
           acronym_id = -1
	   acronym = 'plenaryw'
    	elif acronym_id == '2' :
           acronym_id =  -2 
           acronym = 'plenaryt'
        else:
           acronym_list = IRTF.objects.filter(irtf_id=acronym_id)

           for i in acronym_list:
               acronym = i.acronym  
    elif menu == "interim":
        irtf = 0
        interim = 1
	if acronym_id == '1' :
           acronym_id = -1
	   acronym = 'plenaryw'
    	elif acronym_id == '2' :
           acronym_id =  -2 
           acronym = 'plenaryt'
        else:
           acronym_list = Acronym.objects.filter(acronym_id=acronym_id)
           for i in acronym_list:
               acronym = i.acronym  


    wg_agenda_list =  WgAgenda.objects.filter(meeting=id,group_acronym_id=acronym_id,irtf=irtf,interim=interim)
    if wg_agenda_list:
        for wg_item in wg_agenda_list:
	    wg_filename = wg_item.filename
            wg_id = wg_item.id     
    else:
        wg_filename = "Agenda not uploaded"
        wg_id = 0

    minute_list = Minute.objects.filter(meeting=id,group_acronym_id=acronym_id,irtf=irtf,interim=interim) 
    if minute_list:
        for min_item in minute_list:
	    min_filename = min_item.filename
            min_id = min_item.id
    else:
        min_filename = "Minutes not uploaded"
        min_id = 0

    slides_list = Slide.objects.filter(meeting=id,group_acronym_id=acronym_id,irtf=irtf,interim=interim).order_by('order_num')
       

          

    return render_to_response('proceedings/current_material.html', {
        'meeting': meeting,
        'proceeding': proceeding,
        'menu':menu, 
    	'acronym':acronym,
        'wg_filename':wg_filename,
        'wg_id':wg_id,
        'min_filename':min_filename,
        'min_id':min_id,
        'slides_list':slides_list},
        RequestContext(request, {}),
    )


def delete_file(request,id,menu,wg_id=0,min_id=0,slide_id=0):
    """
    Handles the Agenda/Minutes/Groups file deletion.

    Deletes the respective file from the database as well as from the machine.
      
    **Templates:**

    * ``proceedings/current_material.html``

    **Template Variables:**

    * meeting , proceeding,menu,acronym,wg_filename,wg_id,min_filename,min_id


    """

# get meeting or return HTTP 404 if record not found

    meeting = get_object_or_404(Meeting, meeting_num=id)
    proceeding = get_object_or_404(Proceeding, meeting_num=id)

    if wg_id > '0' :
        wg_agenda_obj = get_object_or_404(WgAgenda,id=wg_id)
        wg_file = wg_agenda_obj.filename
        acronym_id = wg_agenda_obj.group_acronym_id 
        wg_agenda_obj.delete()
        handle_delete_file(id,'agenda',wg_file)
    
        wg_agenda_list =  WgAgenda.objects.filter(id=wg_id)
        if wg_agenda_list:
            for wg_item in wg_agenda_list:
	        wg_filename = wg_item.filename
                wg_id = wg_item.id     
        else:
            wg_filename = "Agenda not uploaded"
            wg_id = 0
    elif wg_id == '0':
        wg_filename = "Agenda not uploaded"
        wg_id = 0

    if min_id > '0' :
        min_obj = get_object_or_404(Minute,id=min_id)
        min_file = min_obj.filename
        acronym_id = min_obj.group_acronym_id 
        min_obj.delete()
        handle_delete_file(id,'minutes',min_file)
        min_list =  Minute.objects.filter(id=min_id)
        if min_list:
            for min_item in min_list:
	        min_filename = min_item.filename
                min_id = min_item.id     
        else:
            min_filename = "Minutes not uploaded"
            min_id = 0
    elif min_id == '0':
        min_filename = "Minutes not uploaded"
        min_id = 0

    if slide_id > '0':    
        slide_obj = Slide.objects.filter(id=slide_id)
        for i in slide_obj:
            acronym_id = i.group_acronym_id
            slide_num = i.slide_num

#Get the acronym  
    if (acronym_id == '-1'):
        acronym = 'plenaryw'
    elif (acronym_id == '-2'):
        acronym = 'plenaryt'
    else:
        if menu != "irtf" :
            acronym_list = Acronym.objects.filter(acronym_id=acronym_id)
        else:
            acronym_list = IRTF.objects.filter(irtf_id=acronym_id)

        for x in acronym_list:
            acronym = x.acronym  
    
    if slide_id > '0':    
        slide_file = acronym + "-" + str(slide_num)
        slide_obj.delete()
        handle_delete_file(id,'slides',slide_file)
        slides_list = Slide.objects.filter(meeting=id,group_acronym_id=acronym_id)
    
    if slide_id == '0':
       slides_list = Slide.objects.filter(meeting=id,group_acronym_id=acronym_id)


    return render_to_response('proceedings/current_material.html', {
        'meeting': meeting,
        'proceeding': proceeding,
        'menu':menu, 
    	'acronym':acronym,
        'wg_filename':wg_filename,
        'wg_id':wg_id,
        'min_filename':min_filename,
        'min_id':min_id,
        'slides_list':slides_list},
        RequestContext(request, {}),
    )
































