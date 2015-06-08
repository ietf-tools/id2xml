import json

from django.utils.html import escape
from django import forms
from django.core.urlresolvers import reverse as urlreverse

from ietf.liaisons.models import LiaisonStatement
from ietf.group.models import Group

def select2_id_liaison_json(objs):
    return json.dumps([{ "id": o.pk, "text": escape(o.title) } for o in objs])

def select2_id_group_json(objs):
    return json.dumps([{ "id": o.pk, "text": escape(o.acronym) } for o in objs])
    
class SearchableLiaisonStatementField(forms.IntegerField):
    """Server-based multi-select field for choosing liaison statements using
    select2.js."""

    def __init__(self, hint_text="Type in title to search for document", *args, **kwargs):
        super(SearchableLiaisonStatementField, self).__init__(*args, **kwargs)

        self.widget.attrs["class"] = "select2-field"
        self.widget.attrs["data-placeholder"] = hint_text
        self.widget.attrs["data-max-entries"] = 1

    def prepare_value(self, value):
        if not value:
            value = None
        elif isinstance(value, LiaisonStatement):
            value = value
        else:
            value = LiaisonStatement.objects.exclude(approved=None).filter(pk=value).first()

        self.widget.attrs["data-pre"] = select2_id_liaison_json([value] if value else [])

        # doing this in the constructor is difficult because the URL
        # patterns may not have been fully constructed there yet
        self.widget.attrs["data-ajax-url"] = urlreverse("ajax_select2_search_liaison_statements")

        return value

    def clean(self, value):
        value = super(SearchableLiaisonStatementField, self).clean(value)

        if value == None:
            return None

        obj = LiaisonStatement.objects.filter(pk=value).first()
        if not obj and self.required:
            raise forms.ValidationError(u"You must select a value.")

        return obj

class SearchableGroupsField(forms.CharField):
    """Server-based multi-select field for choosing groups using
    select2.js.

    The field uses a comma-separated list of primary keys in a
    CharField element as its API with some extra attributes used by
    the Javascript part."""

    def __init__(self,
                 max_entries=None, # max number of selected objs
                 model=Group,
                 hint_text="Type in name to search for organization",
                 group_type="external",
                 *args, **kwargs):
        kwargs["max_length"] = 10000
        self.max_entries = max_entries
        self.group_type = group_type
        self.model = model

        super(SearchableGroupsField, self).__init__(*args, **kwargs)

        self.widget.attrs["class"] = "select2-field form-control"
        self.widget.attrs["data-placeholder"] = hint_text
        if self.max_entries != None:
            self.widget.attrs["data-max-entries"] = self.max_entries

    def parse_select2_value(self, value):
        return [x.strip() for x in value.split(",") if x.strip()]

    def prepare_value(self, value):
        if not value:
            value = ""
        if isinstance(value, (int, long)):
            value = str(value)
        if isinstance(value, basestring):
            pks = self.parse_select2_value(value)
            value = self.model.objects.filter(pk__in=pks)
            filter_args = {}
            filter_args["type"] = self.group_type
            value = value.filter(**filter_args)
        if isinstance(value, self.model):
            value = [value]

        self.widget.attrs["data-pre"] = select2_id_group_json(value)

        # doing this in the constructor is difficult because the URL
        # patterns may not have been fully constructed there yet
        self.widget.attrs["data-ajax-url"] = urlreverse("ajax_select2_search_groups", kwargs={
            "group_type": self.group_type,
            #"model_name": self.model.__name__.lower()
        })

        return u",".join(unicode(o.pk) for o in value)

    def clean(self, value):
        value = super(SearchableGroupsField, self).clean(value)
        pks = self.parse_select2_value(value)

        objs = self.model.objects.filter(pk__in=pks)

        found_pks = [str(o.pk) for o in objs]
        failed_pks = [x for x in pks if x not in found_pks]
        if failed_pks:
            raise forms.ValidationError(u"Could not recognize the following groups: {pks}.".format(pks=", ".join(failed_pks)))

        if self.max_entries != None and len(objs) > self.max_entries:
            raise forms.ValidationError(u"You can select at most %s entries only." % self.max_entries)

        return objs
        
class SearchableGroupField(SearchableGroupsField):
    """Version of SearchableGroupsField specialized to a single object."""

    def __init__(self, *args, **kwargs):
        kwargs["max_entries"] = 1
        super(SearchableGroupField, self).__init__(*args, **kwargs)

    def clean(self, value):
        return super(SearchableGroupField, self).clean(value).first()