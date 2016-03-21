# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('submit', '0009_submissionemailattachment_filename'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='submissionemailattachment',
            name='filename',
        ),
    ]
