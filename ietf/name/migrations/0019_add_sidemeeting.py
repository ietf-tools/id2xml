# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

TYPES = ["IETF", "IRTF", "IAB", "Corporate", "Non-profit"]

def forwards_func(apps, schema_editor):
    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version
    TimeSlotTypeName = apps.get_model("name", "TimeSlotTypeName")
    db_alias = schema_editor.connection.alias
    TimeSlotTypeName(name="SideMeeting", slug="sidemeeting").save()
        
def reverse_func(apps, schema_editor):
    TimeSlotTypeName = apps.get_model("name", "TimeSlotTypeName")
    db_alias = schema_editor.connection.alias
    TimeSlotTypeName.objects.using(db_alias).filter(name="sidemeeting").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("name", "0018_iab_programs"),
        ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]
