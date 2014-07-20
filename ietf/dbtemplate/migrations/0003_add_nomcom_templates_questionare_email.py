# encoding: utf-8
from south.v2 import DataMigration


class Migration(DataMigration):

    depends_on = (
        ("name", "0013_add_dbtemplates_types"),
    )

    def forwards(self, orm):
        from django.core.management import call_command
        call_command("loaddata", "nomcom_templates_questionnaire_mail.xml")


    def backwards(self, orm):
        pass