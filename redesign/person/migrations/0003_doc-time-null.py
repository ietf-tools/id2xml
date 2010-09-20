
from south.db import db
from django.db import models
from redesign.person.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Changing field 'Email.person'
        # (to signature: django.db.models.fields.related.ForeignKey(to=orm['person.Person'], null=True))
        db.alter_column('person_email', 'person_id', orm['person.email:person'])
        
    
    
    def backwards(self, orm):
        
        # Changing field 'Email.person'
        # (to signature: django.db.models.fields.related.ForeignKey(to=orm['person.Person']))
        db.alter_column('person_email', 'person_id', orm['person.email:person'])
        
    
    
    models = {
        'person.alias': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['person.Person']"})
        },
        'person.email': {
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'address': ('django.db.models.fields.CharField', [], {'max_length': '64', 'primary_key': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['person.Person']", 'null': 'True'}),
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
