# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('submit', '0013_auto_20160323_1242'),
    ]

    operations = [
        migrations.AddField(
            model_name='submissionemailattachment',
            name='body',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
