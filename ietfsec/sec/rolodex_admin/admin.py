from django.contrib import admin
from django import forms
from sec.rolodex_admin.models import *
from sec.rolodex_admin.forms import *

class PostalAddressInline(admin.StackedInline):
    model = PostalAddress
    extra = 1
    form = AddressForm
    #template =

class PhoneNumberInline(admin.TabularInline):
    extra = 1
    form = PhoneForm
    model = PhoneNumber
    #template =

"""
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name.endswith('phone_type'):
            return forms.CharField(widget=forms.Select)
        return super(PhoneNumberInline, self).formfield_for_dbfield(db_field, **kwargs)
"""

class EmailAddressInline(admin.TabularInline):
    extra = 1
    form = EmailForm
    model = EmailAddress

class PersonOrOrgInfoAdmin(admin.ModelAdmin):
    # NOTE: this uses models.py regardless of imports
    fieldsets = (
        (None, {
            'fields': (('name_prefix', 'first_name', 'middle_initial', 'last_name', 'name_suffix'),)
        }),
    )
    inlines = [ PhoneNumberInline, EmailAddressInline, PostalAddressInline, ]
    list_display = ('__unicode__', 'affiliation', 'email', 'person_or_org_tag')
    save_on_top = True
    search_fields = ('^first_name', '^last_name', 'emailaddress__address', '=person_or_org_tag')

    class Media:
        js = ["/media/js/jquery-1.3.2.min.js",
              "/media/js/dynamic_inlines.js"]

        css = {"all": ("/media/css/custom_admin.css",)}

admin.site.register(PersonOrOrgInfo, PersonOrOrgInfoAdmin)
