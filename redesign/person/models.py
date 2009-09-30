# Copyright The IETF Trust 2007, All Rights Reserved

from django.db import models

class Person(models.Model):
    time = models.DateTimeField(auto_now_add=True)       # When this Person record entered the system
    prefix = models.CharField(maxlength=16)
    given = models.CharField(maxlength=64)
    middle = models.CharField(maxlength=64)
    family = models.CharField(maxlength=64)
    suffix = models.CharField(maxlength=64)
    address = models.TextField(maxlength=255)
    def __str__(self):
        return u'%s %s %s' % (self.given, self.middle, self.family)
    class Admin:
        list_display = ["time", "prefix", "given", "middle", "family", "suffix", "address"]
        pass

class Email(models.Model):
    address = models.CharField(maxlength=64, primary_key=True)
    person = models.ForeignKey(Person)
    time = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)      # Old email addresses are *not* purged, as history
                                        # information points to persons through these
    def __str__(self):
        return self.address
    class Admin:
        pass
