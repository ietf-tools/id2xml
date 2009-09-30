from django.db import models
from redesign.person.models import Email
from redesign.doc.models import Document, DocHistory

class Component(models.Model):
    text  = models.ForeignKey(Document, primary_key=True)
    owner = models.CharField(maxlength=64)
    description = models.TextField()
    class Admin:
        pass

class Ticket(models.Model):
    type = models.CharField(maxlength=256)
    time = models.DateTimeField()
    changetime = models.DateTimeField()
    component = models.ForeignKey(Component)
    severity = models.CharField(maxlength=256)
    priority = models.CharField(maxlength=256)
    owner = models.ForeignKey(Email)
    reporter = models.CharField(maxlength=256)
    cc = models.CharField(maxlength=256)
    version = models.CharField(maxlength=256)
    milestone = models.CharField(maxlength=256)
    status = models.CharField(maxlength=256)
    resolution = models.CharField(maxlength=256)
    summary = models.CharField(maxlength=256)
    description = models.CharField(maxlength=256)
    keywords = models.CharField(maxlength=256)
    class Admin:
        pass

