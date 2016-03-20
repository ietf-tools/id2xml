# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('message', '__first__'),
        ('submit', '0005_auto_20160227_0809'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubmissionEmail',
            fields=[
                ('submissionevent_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='submit.SubmissionEvent')),
                ('in_reply_to', models.ForeignKey(related_name='irtomanual', blank=True, to='message.Message', null=True)),
                ('message', models.ForeignKey(related_name='manualevents', blank=True, to='message.Message', null=True)),
            ],
            options={
                'ordering': ['-time', '-id'],
            },
            bases=('submit.submissionevent',),
        ),
    ]
