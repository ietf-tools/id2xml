# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import date

from django.db import migrations


class Migration(migrations.Migration):
    def remove_old_submissions(apps, schema_editor):
        """
        We'll remove any submissions awaiting manual post that are older
        than a date provided here.
        
        These alll showed up when we added the ability to list submissions
        awaiting manual post and go back many years
        """
        
        # We can't import the model directly as it may be a newer
        # version than this migration expects. We use the historical version.
        before=date(2016, 3, 1)
        Submission = apps.get_model("submit", "Submission")
        for submission in Submission.objects.filter(state_id = "manual", submission_date__lt=before).distinct():
            submission.delete()

    dependencies = [
        ('submit', '0011_auto_20160320_2058'),
    ]

    operations = [
        migrations.RunPython(remove_old_submissions),
    ]
