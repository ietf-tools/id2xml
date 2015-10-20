# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

def fill_in_docalias_relationship_names(apps, schema_editor):
    IprDocRel = apps.get_model("ipr", "IprDocRel")
    for rel in IprDocRel.objects.select_related("document").iterator():
        IprDocRel.objects.filter(pk=rel.pk).update(document_name=rel.document.name)

def noop(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('ipr', '0004_iprdocrel_document_name'),
    ]

    operations = [
        migrations.RunPython(fill_in_docalias_relationship_names, noop)
    ]
