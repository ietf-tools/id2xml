
from south.db import db
from django.db import models
from redesign.group.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'GroupHistory'
        db.create_table('group_grouphistory', (
            ('id', orm['group.GroupHistory:id']),
            ('group', orm['group.GroupHistory:group']),
            ('time', orm['group.GroupHistory:time']),
            ('comment', orm['group.GroupHistory:comment']),
            ('who', orm['group.GroupHistory:who']),
            ('name', orm['group.GroupHistory:name']),
            ('acronym', orm['group.GroupHistory:acronym']),
            ('status', orm['group.GroupHistory:status']),
            ('type', orm['group.GroupHistory:type']),
            ('charter', orm['group.GroupHistory:charter']),
            ('parent', orm['group.GroupHistory:parent']),
            ('list_email', orm['group.GroupHistory:list_email']),
            ('list_pages', orm['group.GroupHistory:list_pages']),
            ('comments', orm['group.GroupHistory:comments']),
        ))
        db.send_create_signal('group', ['GroupHistory'])
        
        # Adding model 'GroupState'
        db.create_table('group_groupstate', (
            ('id', orm['group.GroupState:id']),
            ('name', orm['group.GroupState:name']),
        ))
        db.send_create_signal('group', ['GroupState'])
        
        # Adding model 'Role'
        db.create_table('group_role', (
            ('id', orm['group.Role:id']),
            ('name', orm['group.Role:name']),
            ('group', orm['group.Role:group']),
            ('email', orm['group.Role:email']),
            ('auth', orm['group.Role:auth']),
        ))
        db.send_create_signal('group', ['Role'])
        
        # Adding model 'GroupType'
        db.create_table('group_grouptype', (
            ('id', orm['group.GroupType:id']),
            ('name', orm['group.GroupType:name']),
        ))
        db.send_create_signal('group', ['GroupType'])
        
        # Adding model 'Group'
        db.create_table('group_group', (
            ('id', orm['group.Group:id']),
            ('name', orm['group.Group:name']),
            ('acronym', orm['group.Group:acronym']),
            ('status', orm['group.Group:status']),
            ('type', orm['group.Group:type']),
            ('charter', orm['group.Group:charter']),
            ('parent', orm['group.Group:parent']),
            ('list_email', orm['group.Group:list_email']),
            ('list_pages', orm['group.Group:list_pages']),
            ('comments', orm['group.Group:comments']),
        ))
        db.send_create_signal('group', ['Group'])
        
        # Adding ManyToManyField 'Group.documents'
        db.create_table('group_group_documents', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('group', models.ForeignKey(orm.Group, null=False)),
            ('document', models.ForeignKey(orm['doc.Document'], null=False))
        ))
        
        # Adding ManyToManyField 'GroupHistory.documents'
        db.create_table('group_grouphistory_documents', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('grouphistory', models.ForeignKey(orm.GroupHistory, null=False)),
            ('document', models.ForeignKey(orm['doc.Document'], null=False))
        ))
        
        # Adding ManyToManyField 'GroupHistory.chairs'
        db.create_table('group_grouphistory_chairs', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('grouphistory', models.ForeignKey(orm.GroupHistory, null=False)),
            ('email', models.ForeignKey(orm['person.Email'], null=False))
        ))
        
        # Adding ManyToManyField 'Group.chairs'
        db.create_table('group_group_chairs', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('group', models.ForeignKey(orm.Group, null=False)),
            ('email', models.ForeignKey(orm['person.Email'], null=False))
        ))
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'GroupHistory'
        db.delete_table('group_grouphistory')
        
        # Deleting model 'GroupState'
        db.delete_table('group_groupstate')
        
        # Deleting model 'Role'
        db.delete_table('group_role')
        
        # Deleting model 'GroupType'
        db.delete_table('group_grouptype')
        
        # Deleting model 'Group'
        db.delete_table('group_group')
        
        # Dropping ManyToManyField 'Group.documents'
        db.delete_table('group_group_documents')
        
        # Dropping ManyToManyField 'GroupHistory.documents'
        db.delete_table('group_grouphistory_documents')
        
        # Dropping ManyToManyField 'GroupHistory.chairs'
        db.delete_table('group_grouphistory_chairs')
        
        # Dropping ManyToManyField 'Group.chairs'
        db.delete_table('group_group_chairs')
        
    
    
    models = {
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
            'obsoletes': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['doc.Document']", 'null': 'True'}),
            'pages': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'replaces': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['doc.Document']", 'null': 'True'}),
            'rev': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'reviews': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['doc.Document']", 'null': 'True'}),
            'rfc_state': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['name.RfcDocStateName']", 'null': 'True'}),
            'shepherd': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'shepherd_document_set'", 'null': 'True', 'to': "orm['person.Email']"}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['name.DocStateName']", 'null': 'True'}),
            'stream': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['name.DocStreamName']", 'null': 'True'}),
            'time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['name.DocTypeName']", 'null': 'True'}),
            'updates': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['doc.Document']", 'null': 'True'}),
            'wg_state': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['name.WgDocStateName']", 'null': 'True'})
        },
        'group.group': {
            'acronym': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'chairs': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['person.Email']"}),
            'charter': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'chartered_group'", 'to': "orm['doc.Document']"}),
            'comments': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'documents': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['doc.Document']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'list_email': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'list_pages': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['group.Group']"}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['group.GroupState']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['group.GroupType']"})
        },
        'group.grouphistory': {
            'acronym': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'chairs': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['person.Email']"}),
            'charter': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'chartered_group_history'", 'to': "orm['doc.Document']"}),
            'comment': ('django.db.models.fields.TextField', [], {}),
            'comments': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'documents': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['doc.Document']"}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'group_history'", 'to': "orm['group.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'list_email': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'list_pages': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['group.Group']"}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['group.GroupState']"}),
            'time': ('django.db.models.fields.DateTimeField', [], {}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['group.GroupType']"}),
            'who': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'group_changes'", 'to': "orm['person.Email']"})
        },
        'group.groupstate': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'group.grouptype': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'group.role': {
            'auth': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'email': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['person.Email']"}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['group.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['name.RoleName']"})
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
        'name.rfcdocstatename': {
            'desc': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '8', 'primary_key': 'True'}),
            'used': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'})
        },
        'name.rolename': {
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
    
    complete_apps = ['group']
