
from south.db import db
from django.db import models
from redesign.person.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'Alias'
        db.create_table('person_alias', (
            ('id', orm['person.alias:id']),
            ('person', orm['person.alias:person']),
            ('name', orm['person.alias:name']),
        ))
        db.send_create_signal('person', ['Alias'])
        
        # Adding field 'Person.name'
        db.add_column('person_person', 'name', orm['person.person:name'])
        
        # Adding field 'Person.ascii_short'
        db.add_column('person_person', 'ascii_short', orm['person.person:ascii_short'])
        
        # Adding field 'Person.ascii'
        db.add_column('person_person', 'ascii', orm['person.person:ascii'])
        
        # Deleting field 'Person.given'
        db.delete_column('person_person', 'given')
        
        # Deleting field 'Person.suffix'
        db.delete_column('person_person', 'suffix')
        
        # Deleting field 'Person.prefix'
        db.delete_column('person_person', 'prefix')
        
        # Deleting field 'Person.family'
        db.delete_column('person_person', 'family')
        
        # Deleting field 'Person.middle'
        db.delete_column('person_person', 'middle')
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'Alias'
        db.delete_table('person_alias')
        
        # Deleting field 'Person.name'
        db.delete_column('person_person', 'name')
        
        # Deleting field 'Person.ascii_short'
        db.delete_column('person_person', 'ascii_short')
        
        # Deleting field 'Person.ascii'
        db.delete_column('person_person', 'ascii')
        
        # Adding field 'Person.given'
        db.add_column('person_person', 'given', orm['person.person:given'])
        
        # Adding field 'Person.suffix'
        db.add_column('person_person', 'suffix', orm['person.person:suffix'])
        
        # Adding field 'Person.prefix'
        db.add_column('person_person', 'prefix', orm['person.person:prefix'])
        
        # Adding field 'Person.family'
        db.add_column('person_person', 'family', orm['person.person:family'])
        
        # Adding field 'Person.middle'
        db.add_column('person_person', 'middle', orm['person.person:middle'])
        
    
    
    models = {
        'person.alias': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['person.Person']"})
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
    
    complete_apps = ['person']
