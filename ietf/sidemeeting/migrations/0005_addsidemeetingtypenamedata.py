# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

TYPES = ["IETF", "IRTF", "IAB", "Corporate", "Non-profit"]

def forwards_func(apps, schema_editor):
    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version
    SideMeetingTypeName = apps.get_model("sidemeeting", "SideMeetingTypeName")
    db_alias = schema_editor.connection.alias
    SideMeetingTypeName.objects.using(db_alias).bulk_create(
        [ SideMeetingTypeName(name=t, slug=t.lower()) for t in TYPES ]
    )
        
def reverse_func(apps, schema_editor):
    SideMeetingTypeName = apps.get_model("myapp", "SideMeetingTypeName")
    db_alias = schema_editor.connection.alias
    SideMeetingTypeName.objects.using(db_alias).filter(name__in=TYPES).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("sidemeeting", "0004_sidemeetingsession_area"),
        ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]
