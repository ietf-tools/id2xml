# Copyright The IETF Trust 2020 All Rights Reserved

from django.db import migrations
import requests

def forward(apps, schema_editor):
    GroupExtResource = apps.get_model('group', 'GroupExtResource')

    for resource in GroupExtResource.objects.filter(value__contains='tools.ietf.org'):
        r = requests.get(resource.value)
        if 'trac.ietf.org' in r.url:
            resource.value = r.url
            resource.save()
        

def reverse(apps, schema_editor):
    # I'm not even going to try to guess a mapping from the redirected
    # URL back to the original.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0038_auto_20201109_0439'),
    ]

    operations = [
        migrations.RunPython(forward, reverse),
    ]
