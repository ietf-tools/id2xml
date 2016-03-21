# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('submit', '0008_auto_20160319_1912'),
    ]

    operations = [
        migrations.AddField(
            model_name='submissionemailattachment',
            name='filename',
            field=models.CharField(db_index=True, max_length=255, blank=True),
            preserve_default=True,
        ),
    ]
