# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('doc', '0012_auto_20160207_0537'),
        ('submit', '0007_submissionemail_msgtype'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubmissionEmailAttachment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('removed', models.BooleanField(default=False)),
                ('document', models.ForeignKey(to='doc.Document')),
                ('submission_email', models.ForeignKey(to='submit.SubmissionEmail')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='submissionemail',
            name='attachments',
            field=models.ManyToManyField(to='doc.Document', through='submit.SubmissionEmailAttachment', blank=True),
            preserve_default=True,
        ),
    ]
