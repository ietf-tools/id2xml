from django.db import models
from redesign.person.models import Email
from redesign.doc.models import Document, DocHistory

class Component(models.Model):
    text  = models.ForeignKey(Document, primary_key=True)
    owner = models.CharField(max_length=64)
    description = models.TextField()
    class Admin:
        pass

class Ticket(models.Model):
    type = models.CharField(max_length=256)
    time = models.DateTimeField()
    changetime = models.DateTimeField()
    component = models.ForeignKey(Component)
    severity = models.CharField(max_length=256)
    priority = models.CharField(max_length=256)
    owner = models.ForeignKey(Email)
    reporter = models.CharField(max_length=256)
    cc = models.CharField(max_length=256)
    version = models.CharField(max_length=256)
    milestone = models.CharField(max_length=256)
    status = models.CharField(max_length=256)
    resolution = models.CharField(max_length=256)
    summary = models.CharField(max_length=256)
    description = models.CharField(max_length=256)
    keywords = models.CharField(max_length=256)
    class Admin:
        pass

