# Copyright The IETF Trust 2019, All Rights Reserved
# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2019-11-18 08:50
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('name', '0008_reviewerqueuepolicyname'),
        ('review', '0020_add_request_assignment_next'),
    ]

    operations = [
        migrations.AddField(
            model_name='reviewteamsettings',
            name='reviewer_queue_policy',
            field=models.ForeignKey(default='RotateAlphabetically', on_delete=django.db.models.deletion.PROTECT, to='name.ReviewerQueuePolicyName'),
        ),
    ]