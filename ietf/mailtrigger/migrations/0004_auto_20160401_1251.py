# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    def add_recipient(apps, schema_editor):
        # We can't import the model directly as it may be a newer
        # version than this migration expects. We use the historical version.
        Recipient = apps.get_model("mailtrigger", "Recipient")
        Recipient.objects.create(slug="submission_message",
                                 desc="Submission requests to the secretariat",
                                 template='<ietf-submit@ietf.org>')


    dependencies = [
        ('mailtrigger', '0003_merge_request_trigger'),
    ]

    operations = [
        migrations.RunPython(add_recipient),
    ]
