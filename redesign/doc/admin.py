from django.contrib import admin
from models import *
from person.models import *

class RelatedDocAdmin(admin.ModelAdmin):
    list_display = ["source", "relationship", "target"]
    search_fields = ["doc_alias__name", "related_document_set__name", ]
    list_display_links = ["relationship", ]
admin.site.register(RelatedDoc, RelatedDocAdmin)    

class DocumentAdmin(admin.ModelAdmin):
    list_display = ['name', 'rev', 'time', 'state', 'group', 'pages', 'intended_std_level', 'author_list', ]
    search_fields = ['name']
    raw_id_fields = ['authors', 'related']
admin.site.register(Document, DocumentAdmin)

class DocHistoryAdmin(admin.ModelAdmin):
    list_display = ['time', 'doc', 'rev', 'state', 'group', 'pages', 'intended_std_level', 'author_list', ]
    search_fields = ['doc__name']
    ordering = ['time', 'doc', 'rev']
    raw_id_fields = ['authors', 'related']
admin.site.register(DocHistory, DocHistoryAdmin)

class DocAliasAdmin(admin.ModelAdmin):
    list_display = [ 'name', 'document_link', ]
    search_fields = [ 'name', 'document__name', ]
    pass
admin.site.register(DocAlias, DocAliasAdmin)

class MessageAdmin(admin.ModelAdmin):
    pass
admin.site.register(Message, MessageAdmin)

class SendQueueAdmin(admin.ModelAdmin):
    pass
admin.site.register(SendQueue, SendQueueAdmin)

class BallotAdmin(admin.ModelAdmin):             # A collection of ballot positions
    pass
admin.site.register(Ballot, BallotAdmin)
