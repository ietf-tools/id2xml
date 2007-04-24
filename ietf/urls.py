from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Example:
      (r'^idtracker/', include('ietf.idtracker.urls')),
      (r'^my/', include('ietf.my.urls')),
      (r'^idindex/', include('ietf.idindex.urls')),
      (r'^liaisons/', include('ietf.liaisons.urls')),
      (r'^(?P<path>public|cgi-bin)/', include('ietf.redirects.urls')),

    # Uncomment this for admin:
     (r'^admin/', include('django.contrib.admin.urls')),
)
