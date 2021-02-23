# Copyright The IETF Trust 2020 All Rights Reserved

from django.db import migrations
import requests

def forward(apps, schema_editor):
    DocExtResource = apps.get_model('doc', 'DocExtResource')

    for resource in DocExtResource.objects.filter(value__contains='tools.ietf.org'):
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
        ('doc', '0039_auto_20201109_0439'),
    ]

    operations = [
        migrations.RunPython(forward, reverse),
    ]
