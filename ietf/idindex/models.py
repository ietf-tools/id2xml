from django.db import models

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

