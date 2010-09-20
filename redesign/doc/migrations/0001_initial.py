
from south.db import db
from django.db import models
from redesign.doc.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'Ballot'
        db.create_table('doc_ballot', (
            ('id', orm['doc.Ballot:id']),
            ('initiated', orm['doc.Ballot:initiated']),
            ('deferred', orm['doc.Ballot:deferred']),
            ('last_call', orm['doc.Ballot:last_call']),
            ('closed', orm['doc.Ballot:closed']),
            ('announced', orm['doc.Ballot:announced']),
        ))
        db.send_create_signal('doc', ['Ballot'])
        
        # Adding model 'Message'
        db.create_table('doc_message', (
            ('id', orm['doc.Message:id']),
            ('time', orm['doc.Message:time']),
            ('type', orm['doc.Message:type']),
            ('doc', orm['doc.Message:doc']),
            ('frm', orm['doc.Message:frm']),
            ('subj', orm['doc.Message:subj']),
            ('pos', orm['doc.Message:pos']),
            ('text', orm['doc.Message:text']),
        ))
        db.send_create_signal('doc', ['Message'])
        
        # Adding model 'InfoTag'
        db.create_table('doc_infotag', (
            ('id', orm['doc.InfoTag:id']),
            ('document', orm['doc.InfoTag:document']),
            ('infotag', orm['doc.InfoTag:infotag']),
        ))
        db.send_create_signal('doc', ['InfoTag'])
        
        # Adding model 'Alias'
        db.create_table('doc_alias', (
            ('id', orm['doc.Alias:id']),
            ('document', orm['doc.Alias:document']),
            ('name', orm['doc.Alias:name']),
        ))
        db.send_create_signal('doc', ['Alias'])
        
        # Adding model 'SendQueue'
        db.create_table('doc_sendqueue', (
            ('id', orm['doc.SendQueue:id']),
            ('time', orm['doc.SendQueue:time']),
            ('agent', orm['doc.SendQueue:agent']),
            ('comment', orm['doc.SendQueue:comment']),
            ('msg', orm['doc.SendQueue:msg']),
            ('to', orm['doc.SendQueue:to']),
            ('send', orm['doc.SendQueue:send']),
        ))
        db.send_create_signal('doc', ['SendQueue'])
        
        # Adding model 'Document'
        db.create_table('doc_document', (
            ('name', orm['doc.Document:name']),
            ('time', orm['doc.Document:time']),
            ('comment', orm['doc.Document:comment']),
            ('agent', orm['doc.Document:agent']),
            ('type', orm['doc.Document:type']),
            ('title', orm['doc.Document:title']),
            ('state', orm['doc.Document:state']),
            ('doc_stream', orm['doc.Document:doc_stream']),
            ('wg_state', orm['doc.Document:wg_state']),
            ('iesg_state', orm['doc.Document:iesg_state']),
            ('iana_state', orm['doc.Document:iana_state']),
            ('rfc_state', orm['doc.Document:rfc_state']),
            ('abstract', orm['doc.Document:abstract']),
            ('rev', orm['doc.Document:rev']),
            ('pages', orm['doc.Document:pages']),
            ('intended_std_level', orm['doc.Document:intended_std_level']),
            ('ad', orm['doc.Document:ad']),
            ('shepherd', orm['doc.Document:shepherd']),
        ))
        db.send_create_signal('doc', ['Document'])
        
        # Adding model 'DocHistory'
        db.create_table('doc_dochistory', (
            ('id', orm['doc.DocHistory:id']),
            ('name', orm['doc.DocHistory:name']),
            ('time', orm['doc.DocHistory:time']),
            ('comment', orm['doc.DocHistory:comment']),
            ('agent', orm['doc.DocHistory:agent']),
            ('type', orm['doc.DocHistory:type']),
            ('title', orm['doc.DocHistory:title']),
            ('doc_stream', orm['doc.DocHistory:doc_stream']),
            ('doc_state', orm['doc.DocHistory:doc_state']),
            ('wg_state', orm['doc.DocHistory:wg_state']),
            ('iesg_state', orm['doc.DocHistory:iesg_state']),
            ('iana_state', orm['doc.DocHistory:iana_state']),
            ('rfc_state', orm['doc.DocHistory:rfc_state']),
            ('abstract', orm['doc.DocHistory:abstract']),
            ('rev', orm['doc.DocHistory:rev']),
            ('pages', orm['doc.DocHistory:pages']),
            ('intended_status', orm['doc.DocHistory:intended_status']),
            ('ad', orm['doc.DocHistory:ad']),
            ('shepherd', orm['doc.DocHistory:shepherd']),
        ))
        db.send_create_signal('doc', ['DocHistory'])
        
        # Adding ManyToManyField 'DocHistory.obsoletes'
        db.create_table('doc_dochistory_obsoletes', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('dochistory', models.ForeignKey(orm.DocHistory, null=False)),
            ('document', models.ForeignKey(orm.Document, null=False))
        ))
        
        # Adding ManyToManyField 'Document.obsoletes'
        db.create_table('doc_document_obsoletes', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_document', models.ForeignKey(orm.Document, null=False)),
            ('to_document', models.ForeignKey(orm.Document, null=False))
        ))
        
        # Adding ManyToManyField 'Document.authors'
        db.create_table('doc_document_authors', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('document', models.ForeignKey(orm.Document, null=False)),
            ('email', models.ForeignKey(orm['person.Email'], null=False))
        ))
        
        # Adding ManyToManyField 'Document.replaces'
        db.create_table('doc_document_replaces', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_document', models.ForeignKey(orm.Document, null=False)),
            ('to_document', models.ForeignKey(orm.Document, null=False))
        ))
        
        # Adding ManyToManyField 'DocHistory.authors'
        db.create_table('doc_dochistory_authors', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('dochistory', models.ForeignKey(orm.DocHistory, null=False)),
            ('email', models.ForeignKey(orm['person.Email'], null=False))
        ))
        
        # Adding ManyToManyField 'Document.updates'
        db.create_table('doc_document_updates', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_document', models.ForeignKey(orm.Document, null=False)),
            ('to_document', models.ForeignKey(orm.Document, null=False))
        ))
        
        # Adding ManyToManyField 'DocHistory.replaces'
        db.create_table('doc_dochistory_replaces', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('dochistory', models.ForeignKey(orm.DocHistory, null=False)),
            ('document', models.ForeignKey(orm.Document, null=False))
        ))
        
        # Adding ManyToManyField 'DocHistory.updates'
        db.create_table('doc_dochistory_updates', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('dochistory', models.ForeignKey(orm.DocHistory, null=False)),
            ('document', models.ForeignKey(orm.Document, null=False))
        ))
        
        # Adding ManyToManyField 'Document.reviews'
        db.create_table('doc_document_reviews', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_document', models.ForeignKey(orm.Document, null=False)),
            ('to_document', models.ForeignKey(orm.Document, null=False))
        ))
        
        # Adding ManyToManyField 'SendQueue.cc'
        db.create_table('doc_sendqueue_cc', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('sendqueue', models.ForeignKey(orm.SendQueue, null=False)),
            ('email', models.ForeignKey(orm['person.Email'], null=False))
        ))
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'Ballot'
        db.delete_table('doc_ballot')
        
        # Deleting model 'Message'
        db.delete_table('doc_message')
        
        # Deleting model 'InfoTag'
        db.delete_table('doc_infotag')
        
        # Deleting model 'Alias'
        db.delete_table('doc_alias')
        
        # Deleting model 'SendQueue'
        db.delete_table('doc_sendqueue')
        
        # Deleting model 'Document'
        db.delete_table('doc_document')
        
        # Deleting model 'DocHistory'
        db.delete_table('doc_dochistory')
        
        # Dropping ManyToManyField 'DocHistory.obsoletes'
        db.delete_table('doc_dochistory_obsoletes')
        
        # Dropping ManyToManyField 'Document.obsoletes'
        db.delete_table('doc_document_obsoletes')
        
        # Dropping ManyToManyField 'Document.authors'
        db.delete_table('doc_document_authors')
        
        # Dropping ManyToManyField 'Document.replaces'
        db.delete_table('doc_document_replaces')
        
        # Dropping ManyToManyField 'DocHistory.authors'
        db.delete_table('doc_dochistory_authors')
        
        # Dropping ManyToManyField 'Document.updates'
        db.delete_table('doc_document_updates')
        
        # Dropping ManyToManyField 'DocHistory.replaces'
        db.delete_table('doc_dochistory_replaces')
        
        # Dropping ManyToManyField 'DocHistory.updates'
        db.delete_table('doc_dochistory_updates')
        
        # Dropping ManyToManyField 'Document.reviews'
        db.delete_table('doc_document_reviews')
        
        # Dropping ManyToManyField 'SendQueue.cc'
        db.delete_table('doc_sendqueue_cc')
        
    
    
    models = {
        'doc.alias': {
            'document': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['doc.Document']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'doc.ballot': {
            'announced': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'announced_ballots'", 'blank': 'True', 'null': 'True', 'to': "orm['doc.Message']"}),
            'closed': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'closed_ballots'", 'blank': 'True', 'null': 'True', 'to': "orm['doc.Message']"}),
            'deferred': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'deferred_ballots'", 'blank': 'True', 'null': 'True', 'to': "orm['doc.Message']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'initiated': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'initiated_ballots'", 'to': "orm['doc.Message']"}),
            'last_call': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'lastcalled_ballots'", 'blank': 'True', 'null': 'True', 'to': "orm['doc.Message']"})
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
            'family': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'given': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'middle': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'prefix': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'suffix': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        }
    }
    
    complete_apps = ['doc']
