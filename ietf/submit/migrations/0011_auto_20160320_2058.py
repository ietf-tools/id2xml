# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('submit', '0010_remove_submissionemailattachment_filename'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='submissionemail',
            name='attachments',
        ),
        migrations.RemoveField(
            model_name='submissionemailattachment',
            name='document',
        ),
        migrations.AddField(
            model_name='submissionemailattachment',
            name='filename',
            field=models.CharField(db_index=True, max_length=255, blank=True),
            preserve_default=True,
        ),
    ]
