from django.core.urlresolvers import reverse as urlreverse
from django.contrib import admin
from django.utils.safestring import mark_safe

from ietf.submit.models import *

class IdSubmissionStatusAdmin(admin.ModelAdmin):
    pass
admin.site.register(IdSubmissionStatus, IdSubmissionStatusAdmin)    

class IdSubmissionDetailAdmin(admin.ModelAdmin):
    list_display = ['submission_id', 'draft_link', 'status_link', 'submission_date', 'last_updated_date',]
    ordering = [ '-submission_date' ]
    search_fields = ['filename', ]
    raw_id_fields = ['group_acronym']

    def status_link(self, instance):
        url = urlreverse('draft_status_by_hash',
                         kwargs=dict(submission_id=instance.submission_id,
                                     submission_hash=instance.get_hash()))
        return '<a href="%s">%s</a>' % (url, instance.status)
    status_link.allow_tags = True

    def draft_link(self, instance):
        if instance.status_id in (-1, -2):
            return '<a href="http://www.ietf.org/id/%s-%s.txt">%s</a>' % (instance.filename, instance.revision, instance.filename)
        else:
            return instance.filename
    draft_link.allow_tags = True

admin.site.register(IdSubmissionDetail, IdSubmissionDetailAdmin)

class PreapprovalAdmin(admin.ModelAdmin):
    pass
admin.site.register(Preapproval, PreapprovalAdmin)

class TempIdAuthorsAdmin(admin.ModelAdmin):
    ordering = ["-id"]
admin.site.register(TempIdAuthors, TempIdAuthorsAdmin)

