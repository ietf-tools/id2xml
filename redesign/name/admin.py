from django.contrib import admin
from models import *

class RoleNameAdmin(admin.ModelAdmin):
    list_display = ["slug", "name", "desc", "used"]
    pass
admin.site.register(RoleName, RoleNameAdmin)

class DocStreamNameAdmin(admin.ModelAdmin):
    list_display = ["slug", "name", "desc", "used"]
    pass
admin.site.register(DocStreamName, DocStreamNameAdmin)

class DocStateNameAdmin(admin.ModelAdmin):
    list_display = ["slug", "name", "desc", "used"]
    pass
admin.site.register(DocStateName, DocStateNameAdmin)

class DocRelationshipNameAdmin(admin.ModelAdmin):
    list_display = ["slug", "name", "desc", "used"]
    pass
admin.site.register(DocRelationshipName, DocRelationshipNameAdmin)

class WgDocStateNameAdmin(admin.ModelAdmin):
    list_display = ["slug", "name", "desc", "used"]
    pass
admin.site.register(WgDocStateName, WgDocStateNameAdmin)

class IesgDocStateNameAdmin(admin.ModelAdmin):
    list_display = ["slug", "name", "desc", "used"]
    pass
admin.site.register(IesgDocStateName, IesgDocStateNameAdmin)

class IanaDocStateNameAdmin(admin.ModelAdmin):
    list_display = ["slug", "name", "desc", "used"]
    pass
admin.site.register(IanaDocStateName, IanaDocStateNameAdmin)

class RfcDocStateNameAdmin(admin.ModelAdmin):
    list_display = ["slug", "name", "desc", "used"]
    pass
admin.site.register(RfcDocStateName, RfcDocStateNameAdmin)

class DocTypeNameAdmin(admin.ModelAdmin):
    list_display = ["slug", "name", "desc", "used"]
    pass
admin.site.register(DocTypeName, DocTypeNameAdmin)

class DocInfoTagNameAdmin(admin.ModelAdmin):
    list_display = ["slug", "name", "desc", "used"]
    pass
admin.site.register(DocInfoTagName, DocInfoTagNameAdmin)

class IntendedStatusNameAdmin(admin.ModelAdmin):
    list_display = ["slug", "name", "desc", "used"]
    pass
admin.site.register(IntendedStatusName, IntendedStatusNameAdmin)

class StdStatusNameAdmin(admin.ModelAdmin):
    list_display = ["slug", "name", "desc", "used"]
    pass
admin.site.register(StdStatusName, StdStatusNameAdmin)

class MsgTypeNameAdmin(admin.ModelAdmin):
    list_display = ["slug", "name", "desc", "used"]
    pass
admin.site.register(MsgTypeName, MsgTypeNameAdmin)

class BallotPositionNameAdmin(admin.ModelAdmin):
    list_display = ["slug", "name", "desc", "used"]
    pass
admin.site.register(BallotPositionName, BallotPositionNameAdmin)
