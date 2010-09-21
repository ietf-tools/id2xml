
from south.db import db
from django.db import models
from ietf.idsubmit.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'IdSubmissionDetail'
        db.create_table('id_submission_detail', (
            ('submission_id', orm['idsubmit.IdSubmissionDetail:submission_id']),
            ('status_id', orm['idsubmit.IdSubmissionDetail:status_id']),
            ('last_updated_date', orm['idsubmit.IdSubmissionDetail:last_updated_date']),
            ('last_updated_time', orm['idsubmit.IdSubmissionDetail:last_updated_time']),
            ('title', orm['idsubmit.IdSubmissionDetail:title']),
            ('group', orm['idsubmit.IdSubmissionDetail:group']),
            ('filename', orm['idsubmit.IdSubmissionDetail:filename']),
            ('creation_date', orm['idsubmit.IdSubmissionDetail:creation_date']),
            ('submission_date', orm['idsubmit.IdSubmissionDetail:submission_date']),
            ('remote_ip', orm['idsubmit.IdSubmissionDetail:remote_ip']),
            ('revision', orm['idsubmit.IdSubmissionDetail:revision']),
            ('auth_key', orm['idsubmit.IdSubmissionDetail:auth_key']),
            ('idnits_message', orm['idsubmit.IdSubmissionDetail:idnits_message']),
            ('file_type', orm['idsubmit.IdSubmissionDetail:file_type']),
            ('comment_to_sec', orm['idsubmit.IdSubmissionDetail:comment_to_sec']),
            ('abstract', orm['idsubmit.IdSubmissionDetail:abstract']),
            ('txt_page_count', orm['idsubmit.IdSubmissionDetail:txt_page_count']),
            ('error_message', orm['idsubmit.IdSubmissionDetail:error_message']),
            ('warning_message', orm['idsubmit.IdSubmissionDetail:warning_message']),
            ('wg_submission', orm['idsubmit.IdSubmissionDetail:wg_submission']),
            ('filesize', orm['idsubmit.IdSubmissionDetail:filesize']),
            ('man_posted_date', orm['idsubmit.IdSubmissionDetail:man_posted_date']),
            ('man_posted_by', orm['idsubmit.IdSubmissionDetail:man_posted_by']),
            ('first_two_pages', orm['idsubmit.IdSubmissionDetail:first_two_pages']),
            ('sub_email_priority', orm['idsubmit.IdSubmissionDetail:sub_email_priority']),
            ('invalid_version', orm['idsubmit.IdSubmissionDetail:invalid_version']),
            ('idnits_failed', orm['idsubmit.IdSubmissionDetail:idnits_failed']),
            ('submitter', orm['idsubmit.IdSubmissionDetail:submitter']),
        ))
        db.send_create_signal('idsubmit', ['IdSubmissionDetail'])
        
        # Adding model 'SubmissionEnv'
        db.create_table('id_submission_env', (
            ('id', orm['idsubmit.SubmissionEnv:id']),
            ('current_manual_proc_date', orm['idsubmit.SubmissionEnv:current_manual_proc_date']),
            ('max_same_draft_name', orm['idsubmit.SubmissionEnv:max_same_draft_name']),
            ('max_same_draft_size', orm['idsubmit.SubmissionEnv:max_same_draft_size']),
            ('max_same_submitter', orm['idsubmit.SubmissionEnv:max_same_submitter']),
            ('max_same_submitter_size', orm['idsubmit.SubmissionEnv:max_same_submitter_size']),
            ('max_same_wg_draft', orm['idsubmit.SubmissionEnv:max_same_wg_draft']),
            ('max_same_wg_draft_size', orm['idsubmit.SubmissionEnv:max_same_wg_draft_size']),
            ('max_daily_submission', orm['idsubmit.SubmissionEnv:max_daily_submission']),
            ('max_daily_submission_size', orm['idsubmit.SubmissionEnv:max_daily_submission_size']),
        ))
        db.send_create_signal('idsubmit', ['SubmissionEnv'])
        
        # Adding model 'IdDates'
        db.create_table('id_dates', (
            ('id', orm['idsubmit.IdDates:id']),
            ('id_date', orm['idsubmit.IdDates:id_date']),
            ('date_name', orm['idsubmit.IdDates:date_name']),
            ('f_name', orm['idsubmit.IdDates:f_name']),
        ))
        db.send_create_signal('idsubmit', ['IdDates'])
        
        # Adding model 'TempIdAuthors'
        db.create_table('temp_id_authors', (
            ('id', orm['idsubmit.TempIdAuthors:id']),
            ('first_name', orm['idsubmit.TempIdAuthors:first_name']),
            ('last_name', orm['idsubmit.TempIdAuthors:last_name']),
            ('email_address', orm['idsubmit.TempIdAuthors:email_address']),
            ('last_modified_date', orm['idsubmit.TempIdAuthors:last_modified_date']),
            ('last_modified_time', orm['idsubmit.TempIdAuthors:last_modified_time']),
            ('author_order', orm['idsubmit.TempIdAuthors:author_order']),
            ('submission', orm['idsubmit.TempIdAuthors:submission']),
        ))
        db.send_create_signal('idsubmit', ['TempIdAuthors'])
        
        # Adding model 'IdApprovedDetail'
        db.create_table('id_approved_detail', (
            ('id', orm['idsubmit.IdApprovedDetail:id']),
            ('filename', orm['idsubmit.IdApprovedDetail:filename']),
            ('approved_status', orm['idsubmit.IdApprovedDetail:approved_status']),
            ('approved_person', orm['idsubmit.IdApprovedDetail:approved_person']),
            ('approved_date', orm['idsubmit.IdApprovedDetail:approved_date']),
            ('recorded_by', orm['idsubmit.IdApprovedDetail:recorded_by']),
        ))
        db.send_create_signal('idsubmit', ['IdApprovedDetail'])
        
        # Creating unique_together for [submission, author_order] on TempIdAuthors.
        db.create_unique('temp_id_authors', ['submission_id', 'author_order'])
        
    
    
    def backwards(self, orm):
        
        # Deleting unique_together for [submission, author_order] on TempIdAuthors.
        db.delete_unique('temp_id_authors', ['submission_id', 'author_order'])
        
        # Deleting model 'IdSubmissionDetail'
        db.delete_table('id_submission_detail')
        
        # Deleting model 'SubmissionEnv'
        db.delete_table('id_submission_env')
        
        # Deleting model 'IdDates'
        db.delete_table('id_dates')
        
        # Deleting model 'TempIdAuthors'
        db.delete_table('temp_id_authors')
        
        # Deleting model 'IdApprovedDetail'
        db.delete_table('id_approved_detail')
        
    
    
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
