
from south.db import db
from django.db import models
from redesign.doc.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'DocAlias'
        db.create_table('doc_docalias', (
            ('id', orm['doc.docalias:id']),
            ('document', orm['doc.docalias:document']),
            ('name', orm['doc.docalias:name']),
        ))
        db.send_create_signal('doc', ['DocAlias'])
        
        # Deleting model 'alias'
        db.delete_table('doc_alias')
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'DocAlias'
        db.delete_table('doc_docalias')
        
        # Adding model 'alias'
        db.create_table('doc_alias', (
            ('document', orm['doc.docalias:document']),
            ('id', orm['doc.docalias:id']),
            ('name', orm['doc.docalias:name']),
        ))
        db.send_create_signal('doc', ['alias'])
        
    
    
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
            'ad': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ads_document_history'", 'null': 'True', 'to': "orm['person.Email']"}),
            'agent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'document_changes'", 'to': "orm['person.Email']"}),
            'authors': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['person.Email']", 'null': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {}),
            'doc_state': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['name.DocStateName']", 'null': 'True'}),
            'doc_stream': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['name.DocStreamName']", 'null': 'True'}),
            'iana_state': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['name.IanaDocStateName']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'iesg_state': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['name.IesgDocStateName']", 'null': 'True'}),
            'intended_status': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['name.StdStatusName']", 'null': 'True'}),
            'name': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['doc.Document']"}),
            'obsoletes': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['doc.Document']", 'null': 'True'}),
            'pages': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'replaces': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['doc.Document']", 'null': 'True'}),
            'rev': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'rfc_state': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['name.RfcDocStateName']", 'null': 'True'}),
            'shepherd': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'shepherded_document_history'", 'null': 'True', 'to': "orm['person.Email']"}),
            'time': ('django.db.models.fields.DateTimeField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['name.DocTypeName']"}),
            'updates': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['doc.Document']", 'null': 'True'}),
            'wg_state': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['name.WgDocStateName']", 'null': 'True'})
        },
        'doc.document': {
            'abstract': ('django.db.models.fields.TextField', [], {}),
            'ad': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ad_documents'", 'null': 'True', 'to': "orm['person.Email']"}),
            'agent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'changed_documents'", 'null': 'True', 'to': "orm['person.Email']"}),
            'authors': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['person.Email']", 'null': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {}),
            'doc_stream': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['name.DocStreamName']", 'null': 'True'}),
            'iana_state': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['name.IanaDocStateName']", 'null': 'True'}),
            'iesg_state': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['name.IesgDocStateName']", 'null': 'True'}),
            'intended_std_level': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['name.StdStatusName']", 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'primary_key': 'True'}),
            'obsoletes': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['doc.Document']", 'null': 'True'}),
            'pages': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'replaces': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['doc.Document']", 'null': 'True'}),
            'rev': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'reviews': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['doc.Document']", 'null': 'True'}),
            'rfc_state': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['name.RfcDocStateName']", 'null': 'True'}),
            'shepherd': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'shepherded_documents'", 'null': 'True', 'to': "orm['person.Email']"}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['name.DocStateName']", 'null': 'True'}),
            'time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['name.DocTypeName']", 'null': 'True'}),
            'updates': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['doc.Document']", 'null': 'True'}),
            'wg_state': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['name.WgDocStateName']", 'null': 'True'})
        },
        'doc.infotag': {
            'document': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['doc.Document']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'infotag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['name.DocInfoTagName']"})
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
