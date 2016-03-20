# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('submit', '0006_submissionemail'),
    ]

    operations = [
        migrations.AddField(
            model_name='submissionemail',
            name='msgtype',
            field=models.CharField(default='msgin', max_length=25),
            preserve_default=False,
        ),
    ]
