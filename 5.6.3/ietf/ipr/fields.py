import json

from django.utils.html import escape
from django import forms
from django.core.urlresolvers import reverse as urlreverse

import debug                            # pyflakes:ignore

from ietf.ipr.models import IprDisclosureBase

def tokeninput_id_name_json(objs):
    def formatter(x):
        return escape(u"%s <%s>" % (x.title, x.pk))

    return json.dumps([{ "id": o.pk, "name": formatter(o) } for o in objs])

class AutocompletedIprDisclosuresField(forms.CharField):
    """Tokenizing autocompleted multi-select field for choosing
    IPR disclosures using jquery.tokeninput.js.

    The field uses a comma-separated list of primary keys in a
    CharField element as its API, the tokeninput Javascript adds some
    selection magic on top of this so we have to pass it a JSON
    representation of ids and user-understandable labels."""

    def __init__(self,
                 max_entries=None, # max number of selected objs
                 model=IprDisclosureBase,
                 hint_text="Type in term(s) to search disclosure title",
                 *args, **kwargs):
        kwargs["max_length"] = 1000
        self.max_entries = max_entries
        self.model = model

        super(AutocompletedIprDisclosuresField, self).__init__(*args, **kwargs)

        self.widget.attrs["class"] = "tokenized-field"
        self.widget.attrs["data-hint-text"] = hint_text
        if self.max_entries != None:
            self.widget.attrs["data-max-entries"] = self.max_entries

    def parse_tokenized_value(self, value):
        return [x.strip() for x in value.split(",") if x.strip()]

    def prepare_value(self, value):
        if not value:
            value = ""
        if isinstance(value, basestring):
            pks = self.parse_tokenized_value(value)
            value = self.model.objects.filter(pk__in=pks)
        if isinstance(value, self.model):
            value = [value]

        self.widget.attrs["data-pre"] = tokeninput_id_name_json(value)

        # doing this in the constructor is difficult because the URL
        # patterns may not have been fully constructed there yet
        self.widget.attrs["data-ajax-url"] = urlreverse("ipr_ajax_search")

        return ",".join(e.pk for e in value)

    def clean(self, value):
        value = super(AutocompletedIprDisclosuresField, self).clean(value)
        pks = self.parse_tokenized_value(value)

        objs = self.model.objects.filter(pk__in=pks)

        found_pks = [str(o.pk) for o in objs]
        failed_pks = [x for x in pks if x not in found_pks]
        if failed_pks:
            raise forms.ValidationError(u"Could not recognize the following {model_name}s: {pks}. You can only input {model_name}s already registered in the Datatracker.".format(pks=", ".join(failed_pks), model_name=self.model.__name__.lower()))

        if self.max_entries != None and len(objs) > self.max_entries:
            raise forms.ValidationError(u"You can select at most %s entries only." % self.max_entries)

        return objs

