from django.views.generic.list_detail import object_list
from django.db.models import Q
from django.http import Http404
from ietf.idtracker.models import Acronym, GroupIETF, InternetDraft
import operator

alphabet = [chr(65 + i) for i in range(0, 26)]
orgs_initial = {
	'iab': { 'name': 'IAB' },
	'iana': { 'name': 'IANA' },
	'iasa': { 'name': 'IASA' },
	'iesg': { 'name': 'IESG' },
	'irtf': { 'name': 'IRTF' },
	'proto': { 'name': 'PROTO' },
	'rfc-editor': { 'name': 'RFC Editor', 'prefixes': [ 'rfc-editor', 'rfced' ] },
	'tools': { 'name': 'Tools' },
}
orgs_keys = orgs_initial.keys()
for o in orgs_keys:
    orgs_initial[o]['key'] = o
orgs_keys.sort()
orgs = [orgs_initial[o] for o in orgs_keys]

base_extra = { 'alphabet': alphabet, 'orgs': orgs }

def wglist(request, wg=None):
    if wg == 'other':
        queryset = GroupIETF.objects.filter(
	    reduce(operator.__or__, [Q(group_acronym__acronym__istartswith="%d" % i) for i in range(0,10)])
	    )
    else:
	queryset = GroupIETF.objects.filter(group_acronym__acronym__istartswith=wg)
    queryset = queryset.filter(group_type__type='WG').select_related().order_by('g_status.status', 'acronym.acronym')
    return object_list(request, queryset=queryset, template_name='idindex/wglist.html', extra_context=base_extra)

def wgdocs(request, **kwargs):
    if kwargs.has_key('id'):
	queryset = InternetDraft.objects.filter(group=kwargs['id'])
	group = Acronym.objects.get(acronym_id=kwargs['id'])
    else:
        queryset = InternetDraft.objects.filter(group__acronym=kwargs['slug'])
	group = Acronym.objects.get(acronym=kwargs['slug'])
    queryset = queryset.order_by('status_id', 'filename')
    extra = base_extra
    extra['group'] = group
    return object_list(request, queryset=queryset, template_name='idindex/wgdocs.html', extra_context=extra)

def inddocs(request, filter=None):
    # I'd rather this wasn't here.
    # However, the info doesn't seem to be in the database.
    # todo: use orgs to generate this
    ind_exception_list = [
	    'draft-ietf-',
	    'draft-iesg-',
	    'draft-iab-',
	    'draft-iana-',
	    'draft-irtf-',
	    'draft-rfced-',
	    'draft-rfc-editor-',
	    'draft-proto-',
	    'draft-tools-',
	    'draft-iasa-',
    ]
    ind_exception = reduce(operator.__or__, [Q(filename__istartswith=e) for e in ind_exception_list])
    if filter == 'other':
        queryset = InternetDraft.objects.filter(
	    reduce(operator.__or__, [Q(filename__istartswith="draft-%d" % i) for i in range(0,10)])
	    )
    else:
	queryset = InternetDraft.objects.filter(filename__istartswith='draft-' + filter)
    queryset = queryset.exclude(ind_exception).filter(group__acronym='none').order_by('filename')
    extra = base_extra
    extra['filter'] = filter
    return object_list(request, queryset=queryset, template_name='idindex/inddocs.html', extra_context=extra)

def otherdocs(request, cat=None):
    # todo: use orgs to generate this
    exceptions = { 'rfc-editor':
			Q(filename__istartswith='draft-rfc-editor-') |
			Q(filename__istartswith='draft-ietf-rfc-editor-') |
			Q(filename__istartswith='draft-rfced-') |
			Q(filename__istartswith='draft-ietf-rfced-') }
    if exceptions.has_key(cat):
	queryset = InternetDraft.objects.filter(exceptions[cat])
    else:
	queryset = InternetDraft.objects.filter(
			Q(filename__istartswith='draft-' + cat + '-') |
			Q(filename__istartswith='draft-ietf-' + cat + '-'))
    queryset = queryset.order_by('filename')
    extra = base_extra
    extra['category'] = cat
    return object_list(request, queryset=queryset, template_name='idindex/otherdocs.html', extra_context=extra)

def showdocs(request, cat=None, sortby=None):
    catmap = {
	'all': { 'extra': { 'header': 'All' } },
	'current': { 'extra': { 'header': 'Current', 'norfc': 1 },
		     'query': Q(status__status="Active") },
	'rfc': { 'extra': { 'header': 'Published' },
		 'query': Q(status__status="RFC") },
	'dead': { 'extra': { 'header': "Expired/Withdrawn/Replaced", 'norfc': 1 },
		  'query': Q(status__in=[2,4,5,6]) },	# Using the words seems fragile here for some reason
	}
    if not(catmap.has_key(cat)):
	raise Http404
    sortmap = { 'date': { 'header': "Submission Date",
			  'fields': ['revision_date','filename'] },
	        'name': { 'header': "Filename",
			  'fields': ['filename'] },
		'': { 'header': "WHA?",
			'fields': ['filename'] },
	}
    if sortby is None:
	sortby = 'name'
    queryset = InternetDraft.objects.all()
    if catmap[cat].has_key('query'):
	queryset = queryset.filter(catmap[cat]['query'])
    queryset = queryset.order_by(*list(['status_id'] + sortmap[sortby]['fields']))
    extra = catmap[cat]['extra']
    extra['sort_header'] = sortmap[sortby]['header']
    extra.update(base_extra)
    return object_list(request, queryset=queryset, template_name='idindex/showdocs.html', extra_context=extra)
