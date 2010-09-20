
from south.db import db
from django.db import models
from redesign.doc.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding field 'DocHistory.doc'
        db.add_column('doc_dochistory', 'doc', orm['doc.dochistory:doc'])
        
        # Deleting field 'DocHistory.name'
        db.delete_column('doc_dochistory', 'name_id')
        
    
    
    def backwards(self, orm):
        
        # Deleting field 'DocHistory.doc'
        db.delete_column('doc_dochistory', 'doc_id')
        
        # Adding field 'DocHistory.name'
        db.add_column('doc_dochistory', 'name', orm['doc.dochistory:name'])
        
    
    
    models = {
        'doc.ballot': {
            'announced': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'announced_ballots'", 'blank': 'True', 'null': 'True', 'to': "orm['doc.Message']"}),
            'closed': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'closed_ballots'", 'blank': 'True', 'null': 'True', 'to': "orm['doc.Message']"}),
            'deferred': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'deferred_ballots'", 'blank': 'True', 'null': 'True', 'to': "orm['doc.Message']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'initiated': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'initiated_ballots'", 'to': "orm['doc.Message']"}),
            'last_call': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'lastcalled_ballots'", 'blank': 'True', 'null': 'True', 'to': "orm['doc.Message']"})
        },
        'doc.docalias': {
            'document': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['doc.Document']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'doc.dochistory': {
            'abstract': ('django.db.models.fields.TextField', [], {}),
            'ad': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ad_dochistory_set'", 'null': 'True', 'to': "orm['person.Email']"}),
            'agent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'changed_dochistory_set'", 'null': 'True', 'to': "orm['person.Email']"}),
            'authors': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['person.Email']", 'null': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {}),
            'doc': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['doc.Document']"}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['group.Group']", 'null': 'True'}),
            'iana_state': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['name.IanaDocStateName']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'iesg_state': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['name.IesgDocStateName']", 'null': 'True'}),
            'intended_std_level': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['name.StdStatusName']", 'null': 'True'}),
            'notify': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'pages': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'related': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['doc.RelatedDoc']"}),
            'rev': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'rfc_state': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['name.RfcDocStateName']", 'null': 'True'}),
            'shepherd': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'shepherd_dochistory_set'", 'null': 'True', 'to': "orm['person.Email']"}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['name.DocStateName']", 'null': 'True'}),
            'stream': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['name.DocStreamName']", 'null': 'True'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['name.DocInfoTagName']", 'null': 'True'}),
            'time': ('django.db.models.fields.DateTimeField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['name.DocTypeName']", 'null': 'True'}),
            'wg_state': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['name.WgDocStateName']", 'null': 'True'})
        },
        'doc.document': {
            'abstract': ('django.db.models.fields.TextField', [], {}),
            'ad': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ad_document_set'", 'null': 'True', 'to': "orm['person.Email']"}),
            'agent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'changed_document_set'", 'null': 'True', 'to': "orm['person.Email']"}),
            'authors': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['person.Email']", 'null': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['group.Group']", 'null': 'True'}),
            'iana_state': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['name.IanaDocStateName']", 'null': 'True'}),
            'iesg_state': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['name.IesgDocStateName']", 'null': 'True'}),
            'intended_std_level': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['name.StdStatusName']", 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'primary_key': 'True'}),
            'notify': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'pages': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'related': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['doc.RelatedDoc']"}),
            'rev': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'rfc_state': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['name.RfcDocStateName']", 'null': 'True'}),
            'shepherd': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'shepherd_document_set'", 'null': 'True', 'to': "orm['person.Email']"}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['name.DocStateName']", 'null': 'True'}),
            'stream': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['name.DocStreamName']", 'null': 'True'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['name.DocInfoTagName']", 'null': 'True'}),
            'time': ('django.db.models.fields.DateTimeField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['name.DocTypeName']", 'null': 'True'}),
            'wg_state': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['name.WgDocStateName']", 'null': 'True'})
        },
        'doc.message': {
            'doc': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['doc.Document']"}),
            'frm': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'from_messages'", 'to': "orm['person.Email']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pos': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['name.BallotPositionName']"}),
            'subj': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'time': ('django.db.models.fields.DateTimeField', [], {}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['name.MsgTypeName']"})
        },
        'doc.relateddoc': {
            'document': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['doc.Document']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'relationship': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['name.DocRelationshipName']"})
        },
        'doc.sendqueue': {
            'agent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['person.Email']"}),
            'cc': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['person.Email']"}),
            'comment': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'msg': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['doc.Message']"}),
            'send': ('django.db.models.fields.DateTimeField', [], {}),
            'time': ('django.db.models.fields.DateTimeField', [], {}),
            'to': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'to_messages'", 'to': "orm['person.Email']"})
        },
        'group.group': {
            'acronym': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'chairs': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['person.Email']"}),
            'charter': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'chartered_group'", 'to': "orm['doc.Document']"}),
            'comments': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'list_email': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'list_pages': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['group.Group']"}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['group.GroupState']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['group.GroupType']"})
        },
        'group.groupstate': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'group.grouptype': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'name.ballotpositionname': {
            'desc': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '8', 'primary_key': 'True'}),
            'used': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'})
        },
        'name.docinfotagname': {
            'desc': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '8', 'primary_key': 'True'}),
            'used': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'})
        },
        'name.docrelationshipname': {
            'desc': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '8', 'primary_key': 'True'}),
            'used': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'})
        },
        'name.docstatename': {
            'desc': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '8', 'primary_key': 'True'}),
            'used': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'})
        },
        'name.docstreamname': {
            'desc': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'used': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'})
        },
        'name.doctypename': {
            'desc': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'used': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'})
        },
        'name.ianadocstatename': {
            'desc': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '8', 'primary_key': 'True'}),
            'used': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'})
        },
        'name.iesgdocstatename': {
            'desc': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '8', 'primary_key': 'True'}),
            'used': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'})
        },
        'name.msgtypename': {
            'desc': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '8', 'primary_key': 'True'}),
            'used': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'})
        },
        'name.rfcdocstatename': {
            'desc': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '8', 'primary_key': 'True'}),
            'used': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'})
        },
        'name.stdstatusname': {
            'desc': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '8', 'primary_key': 'True'}),
            'used': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'})
        },
        'name.wgdocstatename': {
            'desc': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '8', 'primary_key': 'True'}),
            'used': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'})
        },
        'person.email': {
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'address': ('django.db.models.fields.CharField', [], {'max_length': '64', 'primary_key': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['person.Person']"}),
            'time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'person.person': {
            'address': ('django.db.models.fields.TextField', [], {'max_length': '255', 'blank': 'True'}),
            'ascii': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'ascii_short': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        }
    }
    
    complete_apps = ['doc']
