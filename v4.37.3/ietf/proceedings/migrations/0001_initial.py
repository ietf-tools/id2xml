# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Registration'
        db.create_table('registrations', (
            ('rsn', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('fname', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('lname', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('company', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=2)),
        ))
        db.send_create_signal('proceedings', ['Registration'])


    def backwards(self, orm):
        # Deleting model 'Registration'
        db.delete_table('registrations')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'doc.docalias': {
            'Meta': {'object_name': 'DocAlias'},
            'document': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['doc.Document']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'})
        },
        'doc.document': {
            'Meta': {'object_name': 'Document'},
            'abstract': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'ad': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'ad_document_set'", 'null': 'True', 'to': "orm['person.Person']"}),
            'authors': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['person.Email']", 'symmetrical': 'False', 'through': "orm['doc.DocumentAuthor']", 'blank': 'True'}),
            'expires': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'external_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['group.Group']", 'null': 'True', 'blank': 'True'}),
            'intended_std_level': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['name.IntendedStdLevelName']", 'null': 'True', 'blank': 'True'}),
            'internal_comments': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'primary_key': 'True'}),
            'note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'notify': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '1', 'blank': 'True'}),
            'pages': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'related': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'reversely_related_document_set'", 'blank': 'True', 'through': "orm['doc.RelatedDocument']", 'to': "orm['doc.DocAlias']"}),
            'rev': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'shepherd': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'shepherd_document_set'", 'null': 'True', 'to': "orm['person.Person']"}),
            'states': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['doc.State']", 'symmetrical': 'False', 'blank': 'True'}),
            'std_level': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['name.StdLevelName']", 'null': 'True', 'blank': 'True'}),
            'stream': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['name.StreamName']", 'null': 'True', 'blank': 'True'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['name.DocTagName']", 'null': 'True', 'blank': 'True'}),
            'time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['name.DocTypeName']", 'null': 'True', 'blank': 'True'})
        },
        'doc.documentauthor': {
            'Meta': {'ordering': "['document', 'order']", 'object_name': 'DocumentAuthor'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['person.Email']"}),
            'document': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['doc.Document']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'doc.relateddocument': {
            'Meta': {'object_name': 'RelatedDocument'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'relationship': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['name.DocRelationshipName']"}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['doc.Document']"}),
            'target': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['doc.DocAlias']"})
        },
        'doc.state': {
            'Meta': {'ordering': "['type', 'order']", 'object_name': 'State'},
            'desc': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'next_states': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'previous_states'", 'blank': 'True', 'to': "orm['doc.State']"}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['doc.StateType']"}),
            'used': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'doc.statetype': {
            'Meta': {'object_name': 'StateType'},
            'label': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '30', 'primary_key': 'True'})
        },
        'group.group': {
            'Meta': {'object_name': 'Group'},
            'acronym': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '40'}),
            'ad': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['person.Person']", 'null': 'True', 'blank': 'True'}),
            'charter': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'chartered_group'", 'unique': 'True', 'null': 'True', 'to': "orm['doc.Document']"}),
            'comments': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'list_archive': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'list_email': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'list_subscribe': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['group.Group']", 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['name.GroupStateName']", 'null': 'True'}),
            'time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['name.GroupTypeName']", 'null': 'True'}),
            'unused_states': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['doc.State']", 'symmetrical': 'False', 'blank': 'True'}),
            'unused_tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['name.DocTagName']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'idtracker.personororginfo': {
            'Meta': {'ordering': "['last_name']", 'object_name': 'PersonOrOrgInfo', 'db_table': "'person_or_org_info'"},
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
        },
        'name.docrelationshipname': {
            'Meta': {'ordering': "['order']", 'object_name': 'DocRelationshipName'},
            'desc': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '8', 'primary_key': 'True'}),
            'used': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'name.doctagname': {
            'Meta': {'ordering': "['order']", 'object_name': 'DocTagName'},
            'desc': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '8', 'primary_key': 'True'}),
            'used': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'name.doctypename': {
            'Meta': {'ordering': "['order']", 'object_name': 'DocTypeName'},
            'desc': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '8', 'primary_key': 'True'}),
            'used': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'name.groupstatename': {
            'Meta': {'ordering': "['order']", 'object_name': 'GroupStateName'},
            'desc': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '8', 'primary_key': 'True'}),
            'used': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'name.grouptypename': {
            'Meta': {'ordering': "['order']", 'object_name': 'GroupTypeName'},
            'desc': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '8', 'primary_key': 'True'}),
            'used': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'name.intendedstdlevelname': {
            'Meta': {'ordering': "['order']", 'object_name': 'IntendedStdLevelName'},
            'desc': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '8', 'primary_key': 'True'}),
            'used': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'name.stdlevelname': {
            'Meta': {'ordering': "['order']", 'object_name': 'StdLevelName'},
            'desc': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '8', 'primary_key': 'True'}),
            'used': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'name.streamname': {
            'Meta': {'ordering': "['order']", 'object_name': 'StreamName'},
            'desc': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '8', 'primary_key': 'True'}),
            'used': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'person.email': {
            'Meta': {'object_name': 'Email'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'address': ('django.db.models.fields.CharField', [], {'max_length': '64', 'primary_key': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['person.Person']", 'null': 'True'}),
            'time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'person.person': {
            'Meta': {'object_name': 'Person'},
            'address': ('django.db.models.fields.TextField', [], {'max_length': '255', 'blank': 'True'}),
            'affiliation': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'ascii': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'ascii_short': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        'proceedings.iesghistory': {
            'Meta': {'object_name': 'IESGHistory', 'db_table': "'iesg_history'"},
            'area': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['group.Group']", 'db_column': "'area_acronym_id'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'meeting': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['proceedings.Meeting']", 'db_column': "'meeting_num'"}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['idtracker.PersonOrOrgInfo']", 'db_column': "'person_or_org_tag'"})
        },
        'proceedings.meeting': {
            'Meta': {'object_name': 'Meeting', 'db_table': "'meetings'"},
            'ack': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'agenda_html': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'agenda_text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateField', [], {}),
            'future_meeting': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'meeting_num': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'overview1': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'overview2': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'time_zone': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'proceedings.meetinghour': {
            'Meta': {'object_name': 'MeetingHour', 'db_table': "u'meeting_hours'"},
            'hour_desc': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'hour_id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'})
        },
        'proceedings.meetingroom': {
            'Meta': {'object_name': 'MeetingRoom', 'db_table': "'meeting_rooms'"},
            'meeting': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['proceedings.Meeting']", 'db_column': "'meeting_num'"}),
            'room_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'room_name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'proceedings.meetingvenue': {
            'Meta': {'object_name': 'MeetingVenue', 'db_table': "'meeting_venues'"},
            'break_area_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'meeting_num': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['proceedings.Meeting']", 'unique': 'True', 'db_column': "'meeting_num'"}),
            'reg_area_name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'proceedings.minute': {
            'Meta': {'object_name': 'Minute', 'db_table': "'minutes'"},
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'group_acronym_id': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interim': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'irtf': ('django.db.models.fields.IntegerField', [], {}),
            'meeting': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['proceedings.Meeting']", 'db_column': "'meeting_num'"})
        },
        'proceedings.nonsession': {
            'Meta': {'object_name': 'NonSession', 'db_table': "'non_session'"},
            'day_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'meeting': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['proceedings.Meeting']", 'db_column': "'meeting_num'"}),
            'non_session_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'non_session_ref': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['proceedings.NonSessionRef']"}),
            'show_break_location': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'time_desc': ('django.db.models.fields.CharField', [], {'max_length': '75', 'blank': 'True'})
        },
        'proceedings.nonsessionref': {
            'Meta': {'object_name': 'NonSessionRef', 'db_table': "'non_session_ref'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'proceedings.notmeetinggroup': {
            'Meta': {'object_name': 'NotMeetingGroup', 'db_table': "u'not_meeting_groups'"},
            'group_acronym': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['group.Group']", 'null': 'True', 'primary_key': 'True'}),
            'meeting': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['proceedings.Meeting']", 'null': 'True', 'db_column': "'meeting_num'", 'blank': 'True'})
        },
        'proceedings.proceeding': {
            'Meta': {'ordering': "['?']", 'object_name': 'Proceeding', 'db_table': "'proceedings'"},
            'c_sub_cut_off_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'dir_name': ('django.db.models.fields.CharField', [], {'max_length': '25', 'blank': 'True'}),
            'frozen': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'meeting_num': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['proceedings.Meeting']", 'unique': 'True', 'primary_key': 'True', 'db_column': "'meeting_num'"}),
            'pr_from_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'pr_to_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'sub_begin_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'sub_cut_off_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'})
        },
        'proceedings.registration': {
            'Meta': {'object_name': 'Registration', 'db_table': "'registrations'"},
            'company': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'fname': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'lname': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'rsn': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'proceedings.sessionconflict': {
            'Meta': {'object_name': 'SessionConflict', 'db_table': "'session_conflicts'"},
            'conflict_gid': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'conflicts_with_set'", 'db_column': "'conflict_gid'", 'to': "orm['group.Group']"}),
            'group_acronym': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'conflicts_set'", 'to': "orm['group.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'meeting_num': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['proceedings.Meeting']", 'db_column': "'meeting_num'"})
        },
        'proceedings.sessionname': {
            'Meta': {'object_name': 'SessionName', 'db_table': "'session_names'"},
            'session_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'session_name_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'proceedings.sessionstatus': {
            'Meta': {'object_name': 'SessionStatus', 'db_table': "'session_status'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True', 'db_column': "'status_id'"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32', 'db_column': "'status'"})
        },
        'proceedings.slide': {
            'Meta': {'object_name': 'Slide', 'db_table': "'slides'"},
            'group_acronym_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_q': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'interim': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'irtf': ('django.db.models.fields.IntegerField', [], {}),
            'meeting': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['proceedings.Meeting']", 'db_column': "'meeting_num'"}),
            'order_num': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'slide_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'slide_num': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'slide_type_id': ('django.db.models.fields.IntegerField', [], {})
        },
        'proceedings.switches': {
            'Meta': {'object_name': 'Switches', 'db_table': "'switches'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'updated_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'updated_time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'val': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'proceedings.wgagenda': {
            'Meta': {'object_name': 'WgAgenda', 'db_table': "'wg_agenda'"},
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'group_acronym_id': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interim': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'irtf': ('django.db.models.fields.IntegerField', [], {}),
            'meeting': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['proceedings.Meeting']", 'db_column': "'meeting_num'"})
        },
        'proceedings.wgmeetingsession': {
            'Meta': {'object_name': 'WgMeetingSession', 'db_table': "'wg_meeting_sessions'"},
            'ad_comments': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'approval_ad': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'approved_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'combined_room_id1': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'here4'", 'null': 'True', 'db_column': "'combined_room_id1'", 'to': "orm['proceedings.MeetingRoom']"}),
            'combined_room_id2': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'here5'", 'null': 'True', 'db_column': "'combined_room_id2'", 'to': "orm['proceedings.MeetingRoom']"}),
            'conflict1': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'conflict2': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'conflict3': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'conflict_other': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'group_acronym_id': ('django.db.models.fields.IntegerField', [], {}),
            'irtf': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'last_modified_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'length_session1': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'length_session2': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'length_session3': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'meeting': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['proceedings.Meeting']", 'db_column': "'meeting_num'"}),
            'num_session': ('django.db.models.fields.IntegerField', [], {}),
            'number_attendee': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'requested_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'sched_date1': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'sched_date2': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'sched_date3': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'sched_room_id1': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'here1'", 'null': 'True', 'db_column': "'sched_room_id1'", 'to': "orm['proceedings.MeetingRoom']"}),
            'sched_room_id2': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'here2'", 'null': 'True', 'db_column': "'sched_room_id2'", 'to': "orm['proceedings.MeetingRoom']"}),
            'sched_room_id3': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'here3'", 'null': 'True', 'db_column': "'sched_room_id3'", 'to': "orm['proceedings.MeetingRoom']"}),
            'scheduled_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'session_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'special_agenda_note': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'special_req': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['proceedings.SessionStatus']", 'null': 'True', 'blank': 'True'}),
            'ts_status_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'proceedings.wgproceedingsactivities': {
            'Meta': {'object_name': 'WgProceedingsActivities', 'db_table': "'wg_proceedings_activities'"},
            'act_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['idtracker.PersonOrOrgInfo']", 'db_column': "'act_by'"}),
            'act_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'act_time': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'activity': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'group_acronym': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['group.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'meeting': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['proceedings.Meeting']", 'db_column': "'meeting_num'"})
        }
    }

    complete_apps = ['proceedings']
