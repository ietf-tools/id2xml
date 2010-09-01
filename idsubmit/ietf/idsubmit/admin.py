from django.contrib import admin
from ietf.idsubmit.models import *

class SubmissionEnvAdmin(admin.ModelAdmin):
    pass
admin.site.register(SubmissionEnv, SubmissionEnvAdmin)

class IdSubmissionDetailAdmin(admin.ModelAdmin):
    raw_id_fields = ('group','submitter')
    save_on_top = True
    search_fields = ('filename','title','group__name','submitter__first_name','submitter__last_name')
    list_display = ('__unicode__','group','submitter','submission_date','status_id')
    list_filter = ('submission_date','status_id','group')
    fieldsets = (
        (None, {'fields': ('title','filename','revision','file_type','filesize','invalid_version')}),
        ('Working Group', {'fields': ('group','wg_submission')}),
        ('Dates', {'fields': ('creation_date','last_updated_date','last_updated_time')}),
        ('Submission', {'fields': ('status_id', 'submission_date', 'submitter', 'remote_ip', 'auth_key', 'man_posted_date','man_posted_by','sub_email_priority' )}),
        ('Abstract', {'fields': ('abstract', 'txt_page_count','first_two_pages')}),
        ('Comment', {'fields': ('comment_to_sec',)}),
        ('Messages', {'fields': ('idnits_failed','idnits_message','error_message','warning_message')}),

    )
admin.site.register(IdSubmissionDetail, IdSubmissionDetailAdmin)

class IdApprovedDetailAdmin(admin.ModelAdmin):
    raw_id_fields = ('approved_person','recorded_by')
    list_display = ('filename','approved_status','approved_person','approved_date','recorded_by')
    search_fields = ('filename', 'approved_person__first_name','approved_person__last_name', 'recorded_by__first_name','recorded_by__last_name')
admin.site.register(IdApprovedDetail, IdApprovedDetailAdmin)
