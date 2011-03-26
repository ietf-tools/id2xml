import django.contrib.admin
from django.conf.urls.defaults import patterns, url
from django.contrib.admin import *
from django.contrib.admin.util import unquote
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.core.serializers import serialize
from django.core.serializers.json import Serializer, DjangoJSONEncoder
from django.http import HttpResponse, Http404
from django.utils import simplejson as json
from django.utils.encoding import smart_unicode
from django.utils.functional import update_wrapper
from django.utils.html import escape
from django.db.models import Field, ForeignKey

from reversion.admin import VersionAdmin

from netnod.utils import filter_from_queryargs

class AdminJsonSerializer(Serializer):
    """
    Serializes a QuerySet to Json, with selectable object expansion.
    The representation is different from that of the builtin Json
    serializer in that there is no separate "model", "pk" and "fields"
    entries for each object, instead only the "fields" dictionary is
    serialized, and the model is the key of a top-level dictionary
    entry which encloses the table serialization:
    {
        "app.model": {
            "1": {
                "foo": "1",
                "bar": 42,
            }
        }
    }
    """

    internal_use_only = False

    def end_object(self, obj):
        expansions = [ n.split("__")[0] for n in self.options["expand"] if n ]
        serialize = self.__class__().serialize
        for name in expansions:
            try:
                field = getattr(obj, name)
                #self._current["_"+name] = smart_unicode(field)
                if not isinstance(field, Field):
                    options = self.options.copy()
                    options["expand"] = [ v[len(name)+2:] for v in options["expand"] if v.startswith(name+"__") ]
                    if hasattr(field, "all"):
                        if options["expand"]:
                            self._current[name] = dict([ (rel.pk, self.expand_related(rel, name)) for rel in field.all().select_related() ])
                        else:
                            self._current[name] = dict([ (rel.pk, self.expand_related(rel, name)) for rel in field.all() ])
                    elif callable(field):
                        self._current[name] = dict([ (rel.pk, self.expand_related(rel, name)) for rel in field() ])
            except ObjectDoesNotExist:
                pass
            except AttributeError:
                names = obj._meta.get_all_field_names() + [ f.get_accessor_name() for f in obj._meta.get_all_related_objects()]
                raise Http404("Cannot resolve keyword '%s' into field. "
                    "Choices are: %s" % (name, ", ".join(names)))
        self.objects.append(self._current)
        self._current = None

    def end_serialization(self):
        self.options.pop('stream', None)
        self.options.pop('fields', None)
        self.options.pop('expand', None)
        json.dump(self.objects, self.stream, cls=DjangoJSONEncoder, **self.options)

    def expand_related(self, related, name):
        options = self.options.copy()
        options["expand"] = [ v[len(name)+2:] for v in options["expand"] if v.startswith(name+"__") ]
        return json.loads(self.__class__().serialize([ related ], **options))[0]

    def handle_fk_field(self, obj, field):
        try:
            related = getattr(obj, field.name)
        except ObjectDoesNotExist:
            related = None
        if related is not None:
            if field.name in self.options["expand"]:
                related = self.expand_related(related, field.name)
            elif self.use_natural_keys and hasattr(related, 'natural_key'):
                related = related.natural_key()
            elif field.rel.field_name == related._meta.pk.name:
                # Related to remote object via primary key
                related = smart_unicode(related._get_pk_val(), strings_only=True)
            else:
                # Related to remote object via other field
                related = smart_unicode(getattr(related, field.rel.field_name), strings_only=True)
        self._current[field.name] = related

    def handle_m2m_field(self, obj, field):
        if field.rel.through._meta.auto_created:
            if field.name in self.options["expand"]:
                m2m_value = lambda value: self.expand_related(value, field.name)
            elif self.use_natural_keys and hasattr(field.rel.to, 'natural_key'):
                m2m_value = lambda value: value.natural_key()
            else:
                m2m_value = lambda value: smart_unicode(value._get_pk_val(), strings_only=True)
            self._current[field.name] = [m2m_value(related)
                               for related in getattr(obj, field.name).iterator()]

        

class ModelAdmin(VersionAdmin):
    def get_urls(self):
        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.module_name

        urlpatterns = super(ModelAdmin, self).get_urls()
        urlpatterns = patterns('',
            url(r'^json/$',
                wrap(self.json_listview),
                name='%s_%s_jsonlist' % info),
            url(r'^(.+)/json/$',
                wrap(self.json_view),
                name='%s_%s_json' % info),
        ) + urlpatterns
        return urlpatterns

    def json_listview(self, request):
        "The json admin list view for this model."
        if not self.has_change_permission(request, None):
            raise PermissionDenied
        filter, exclude = filter_from_queryargs(request)
        for k in filter.keys():
            if k.startswith("_"):
                del filter[k]
        key = request.REQUEST.get("_key", "pk")
        exp = request.REQUEST.get("_expand", "").split(",")
        type = request.REQUEST.get("_type", 'application/json')
        qs = self.queryset(request).filter(**filter).exclude(**exclude)
        if exp:
            qs = qs.select_related()
        qd = dict( ( (getattr(o, key), json.loads(AdminJsonSerializer().serialize([o], expand=exp))[0] )  for o in qs ) )
        return HttpResponse(json.dumps({smart_unicode(self.model._meta): qd}, sort_keys=True, indent=3), content_type=type)

    def json_view(self, request, object_id, extra_context=None):
        "The json view for an object of this model."
        try:
            obj = self.queryset(request).get(pk=unquote(object_id))
        except self.model.DoesNotExist:
            # Don't raise Http404 just yet, because we haven't checked
            # permissions yet. We don't want an unauthenticated user to be able
            # to determine whether a given object exists.
            obj = None

        if not self.has_change_permission(request, obj):
            raise PermissionDenied

        if obj is None:
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {'name': force_unicode(self.model._meta.verbose_name), 'key': escape(object_id)})

        return HttpResponse(serialize("json", [ obj ], sort_keys=True, indent=3)[2:-2], content_type='application/json')
        