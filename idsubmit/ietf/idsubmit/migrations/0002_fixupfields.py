
from south.db import db
from django.db import models
from ietf.idsubmit.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding field 'SubmissionEnv.cut_off_warn_days'
        db.add_column('id_submission_env', 'cut_off_warn_days', orm['idsubmit.submissionenv:cut_off_warn_days'])
        
        # Adding field 'SubmissionEnv.cut_off_time'
        db.add_column('id_submission_env', 'cut_off_time', orm['idsubmit.submissionenv:cut_off_time'])
        
    
    
    def backwards(self, orm):
        
        # Deleting field 'SubmissionEnv.cut_off_warn_days'
        db.delete_column('id_submission_env', 'cut_off_warn_days')
        
        # Deleting field 'SubmissionEnv.cut_off_time'
        db.delete_column('id_submission_env', 'cut_off_time')
        
    
    
    models = {
        'idsubmit.idapproveddetail': {
            'Meta': {'db_table': "'id_approved_detail'"},
            'approved_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'approved_person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['idtracker.PersonOrOrgInfo']", 'db_column': "'approved_person_tag'"}),
            'approved_status': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'filename': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'recorded_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'idsubmission_recorded'", 'db_column': "'recorded_by'", 'to': "orm['idtracker.PersonOrOrgInfo']"})
        },
        'idsubmit.iddates': {
            'Meta': {'db_table': "'id_dates'"},
            'date_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'f_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'id_date': ('django.db.models.fields.DateField', [], {})
        },
        'idsubmit.idsubmissiondetail': {
            'Meta': {'db_table': "'id_submission_detail'"},
            'abstract': ('django.db.models.fields.TextField', [], {}),
            'auth_key': ('django.db.models.fields.CharField', [], {'max_length': '35', 'blank': 'True'}),
            'comment_to_sec': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'creation_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'error_message': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'file_type': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'filesize': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'first_two_pages': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['idtracker.Acronym']", 'db_column': "'group_acronym_id'"}),
            'idnits_failed': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'idnits_message': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'invalid_version': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'last_updated_date': ('django.db.models.fields.DateField', [], {'blank': 'True'}),
            'last_updated_time': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'man_posted_by': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'man_posted_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'remote_ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'blank': 'True'}),
            'revision': ('django.db.models.fields.CharField', [], {'max_length': '2', 'blank': 'True'}),
            'status_id': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'sub_email_priority': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'submission_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today'}),
            'submission_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'submitter': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['idtracker.PersonOrOrgInfo']", 'null': 'True', 'db_column': "'submitter_tag'", 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_column': "'id_document_name'"}),
            'txt_page_count': ('django.db.models.fields.IntegerField', [], {}),
            'warning_message': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'wg_submission': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'})
        },
        'idsubmit.submissionenv': {
            'Meta': {'db_table': "'id_submission_env'"},
            'current_manual_proc_date': ('django.db.models.fields.IntegerField', [], {}),
            'cut_off_time': ('django.db.models.fields.TimeField', [], {}),
            'cut_off_warn_days': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_daily_submission': ('django.db.models.fields.IntegerField', [], {}),
            'max_daily_submission_size': ('django.db.models.fields.IntegerField', [], {}),
            'max_same_draft_name': ('django.db.models.fields.IntegerField', [], {}),
            'max_same_draft_size': ('django.db.models.fields.IntegerField', [], {}),
            'max_same_submitter': ('django.db.models.fields.IntegerField', [], {}),
            'max_same_submitter_size': ('django.db.models.fields.IntegerField', [], {}),
            'max_same_wg_draft': ('django.db.models.fields.IntegerField', [], {}),
            'max_same_wg_draft_size': ('django.db.models.fields.IntegerField', [], {})
        },
        'idsubmit.tempidauthors': {
            'Meta': {'unique_together': "(('submission', 'author_order'),)", 'db_table': "'temp_id_authors'"},
            'author_order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'email_address': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified_date': ('django.db.models.fields.DateField', [], {}),
            'last_modified_time': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'submission': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'authors'", 'to': "orm['idsubmit.IdSubmissionDetail']"})
        },
        'idtracker.acronym': {
            'Meta': {'db_table': "'acronym'"},
            'acronym': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'acronym_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name_key': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'idtracker.personororginfo': {
            'Meta': {'db_table': "'person_or_org_info'"},
            'address_type': ('django.db.models.fields.CharField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.CharField', [], {'max_length': '8', 'null': 'True', 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'first_name_key': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'last_name_key': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'middle_initial': ('django.db.models.fields.CharField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'}),
            'middle_initial_key': ('django.db.models.fields.CharField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'}),
            'modified_by': ('django.db.models.fields.CharField', [], {'max_length': '8', 'null': 'True', 'blank': 'True'}),
            'name_prefix': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'name_suffix': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'person_or_org_tag': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'record_type': ('django.db.models.fields.CharField', [], {'max_length': '8', 'null': 'True', 'blank': 'True'})
        }
    }
    
    complete_apps = ['idsubmit']
