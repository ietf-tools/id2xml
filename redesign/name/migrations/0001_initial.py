
from south.db import db
from django.db import models
from redesign.name.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'DocTypeName'
        db.create_table('name_doctypename', (
            ('id', orm['name.DocTypeName:id']),
            ('name', orm['name.DocTypeName:name']),
            ('slug', orm['name.DocTypeName:slug']),
            ('desc', orm['name.DocTypeName:desc']),
            ('used', orm['name.DocTypeName:used']),
        ))
        db.send_create_signal('name', ['DocTypeName'])
        
        # Adding model 'BallotPositionName'
        db.create_table('name_ballotpositionname', (
            ('slug', orm['name.BallotPositionName:slug']),
            ('name', orm['name.BallotPositionName:name']),
            ('desc', orm['name.BallotPositionName:desc']),
            ('used', orm['name.BallotPositionName:used']),
        ))
        db.send_create_signal('name', ['BallotPositionName'])
        
        # Adding model 'WgDocStateName'
        db.create_table('name_wgdocstatename', (
            ('slug', orm['name.WgDocStateName:slug']),
            ('name', orm['name.WgDocStateName:name']),
            ('desc', orm['name.WgDocStateName:desc']),
            ('used', orm['name.WgDocStateName:used']),
        ))
        db.send_create_signal('name', ['WgDocStateName'])
        
        # Adding model 'RoleName'
        db.create_table('name_rolename', (
            ('slug', orm['name.RoleName:slug']),
            ('name', orm['name.RoleName:name']),
            ('desc', orm['name.RoleName:desc']),
            ('used', orm['name.RoleName:used']),
        ))
        db.send_create_signal('name', ['RoleName'])
        
        # Adding model 'MsgTypeName'
        db.create_table('name_msgtypename', (
            ('slug', orm['name.MsgTypeName:slug']),
            ('name', orm['name.MsgTypeName:name']),
            ('desc', orm['name.MsgTypeName:desc']),
            ('used', orm['name.MsgTypeName:used']),
        ))
        db.send_create_signal('name', ['MsgTypeName'])
        
        # Adding model 'IesgDocStateName'
        db.create_table('name_iesgdocstatename', (
            ('slug', orm['name.IesgDocStateName:slug']),
            ('name', orm['name.IesgDocStateName:name']),
            ('desc', orm['name.IesgDocStateName:desc']),
            ('used', orm['name.IesgDocStateName:used']),
        ))
        db.send_create_signal('name', ['IesgDocStateName'])
        
        # Adding model 'IanaDocStateName'
        db.create_table('name_ianadocstatename', (
            ('slug', orm['name.IanaDocStateName:slug']),
            ('name', orm['name.IanaDocStateName:name']),
            ('desc', orm['name.IanaDocStateName:desc']),
            ('used', orm['name.IanaDocStateName:used']),
        ))
        db.send_create_signal('name', ['IanaDocStateName'])
        
        # Adding model 'DocStreamName'
        db.create_table('name_docstreamname', (
            ('id', orm['name.DocStreamName:id']),
            ('name', orm['name.DocStreamName:name']),
            ('slug', orm['name.DocStreamName:slug']),
            ('desc', orm['name.DocStreamName:desc']),
            ('used', orm['name.DocStreamName:used']),
        ))
        db.send_create_signal('name', ['DocStreamName'])
        
        # Adding model 'RfcDocStateName'
        db.create_table('name_rfcdocstatename', (
            ('slug', orm['name.RfcDocStateName:slug']),
            ('name', orm['name.RfcDocStateName:name']),
            ('desc', orm['name.RfcDocStateName:desc']),
            ('used', orm['name.RfcDocStateName:used']),
        ))
        db.send_create_signal('name', ['RfcDocStateName'])
        
        # Adding model 'DocInfoTagName'
        db.create_table('name_docinfotagname', (
            ('slug', orm['name.DocInfoTagName:slug']),
            ('name', orm['name.DocInfoTagName:name']),
            ('desc', orm['name.DocInfoTagName:desc']),
            ('used', orm['name.DocInfoTagName:used']),
        ))
        db.send_create_signal('name', ['DocInfoTagName'])
        
        # Adding model 'DocStateName'
        db.create_table('name_docstatename', (
            ('slug', orm['name.DocStateName:slug']),
            ('name', orm['name.DocStateName:name']),
            ('desc', orm['name.DocStateName:desc']),
            ('used', orm['name.DocStateName:used']),
        ))
        db.send_create_signal('name', ['DocStateName'])
        
        # Adding model 'StdStatusName'
        db.create_table('name_stdstatusname', (
            ('slug', orm['name.StdStatusName:slug']),
            ('name', orm['name.StdStatusName:name']),
            ('desc', orm['name.StdStatusName:desc']),
            ('used', orm['name.StdStatusName:used']),
        ))
        db.send_create_signal('name', ['StdStatusName'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'DocTypeName'
        db.delete_table('name_doctypename')
        
        # Deleting model 'BallotPositionName'
        db.delete_table('name_ballotpositionname')
        
        # Deleting model 'WgDocStateName'
        db.delete_table('name_wgdocstatename')
        
        # Deleting model 'RoleName'
        db.delete_table('name_rolename')
        
        # Deleting model 'MsgTypeName'
        db.delete_table('name_msgtypename')
        
        # Deleting model 'IesgDocStateName'
        db.delete_table('name_iesgdocstatename')
        
        # Deleting model 'IanaDocStateName'
        db.delete_table('name_ianadocstatename')
        
        # Deleting model 'DocStreamName'
        db.delete_table('name_docstreamname')
        
        # Deleting model 'RfcDocStateName'
        db.delete_table('name_rfcdocstatename')
        
        # Deleting model 'DocInfoTagName'
        db.delete_table('name_docinfotagname')
        
        # Deleting model 'DocStateName'
        db.delete_table('name_docstatename')
        
        # Deleting model 'StdStatusName'
        db.delete_table('name_stdstatusname')
        
    
    
    models = {
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
        }
    }
    
    complete_apps = ['name']
