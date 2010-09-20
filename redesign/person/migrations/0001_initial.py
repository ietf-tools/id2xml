
from south.db import db
from django.db import models
from redesign.person.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'Person'
        db.create_table('person_person', (
            ('id', orm['person.Person:id']),
            ('time', orm['person.Person:time']),
            ('prefix', orm['person.Person:prefix']),
            ('given', orm['person.Person:given']),
            ('middle', orm['person.Person:middle']),
            ('family', orm['person.Person:family']),
            ('suffix', orm['person.Person:suffix']),
            ('address', orm['person.Person:address']),
        ))
        db.send_create_signal('person', ['Person'])
        
        # Adding model 'Email'
        db.create_table('person_email', (
            ('address', orm['person.Email:address']),
            ('person', orm['person.Email:person']),
            ('time', orm['person.Email:time']),
            ('active', orm['person.Email:active']),
        ))
        db.send_create_signal('person', ['Email'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'Person'
        db.delete_table('person_person')
        
        # Deleting model 'Email'
        db.delete_table('person_email')
        
    
    
    models = {
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
    
    complete_apps = ['person']
