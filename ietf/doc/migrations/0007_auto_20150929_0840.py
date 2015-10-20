# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

def fill_in_docalias_relationship_names(apps, schema_editor):
    RelatedDocument = apps.get_model("doc", "RelatedDocument")
    for rel in RelatedDocument.objects.select_related("target").iterator():
        RelatedDocument.objects.filter(pk=rel.pk).update(target_name=rel.target.name)

    RelatedDocHistory = apps.get_model("doc", "RelatedDocHistory")
    for rel in RelatedDocHistory.objects.select_related("target").iterator():
        RelatedDocHistory.objects.filter(pk=rel.pk).update(target_name=rel.target.name)

def noop(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('doc', '0006_auto_20150929_0828'),
    ]

    operations = [
        migrations.RunPython(fill_in_docalias_relationship_names, noop)
    ]
