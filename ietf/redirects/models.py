from django.db import models

class Redirect(models.Model):
    cgi = models.CharField(maxlength=50)
    url = models.CharField(maxlength=255)
    rest = models.CharField(maxlength=100, blank=True)
    remove = models.CharField(maxlength=50, blank=True)
    def __str__(self):
	return "%s -> %s/%s" % (self.cgi, self.url, self.rest)
    class Admin:
        pass
