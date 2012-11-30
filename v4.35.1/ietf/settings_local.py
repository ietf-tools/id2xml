DATABASES = {
    'default': {
        'NAME': 'ietf_utf8',
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'django_readonly',
        'PASSWORD': '??????', # Contact henrik@levkowetz.com to get the password
        'HOST': 'grenache.tools.ietf.org'
    },
    'legacy': {
        'NAME': 'ietf',
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'django_readonly',
        'PASSWORD': '??????', # Contact henrik@levkowetz.com to get the password
        'HOST': 'grenache.tools.ietf.org'
    },
}

# Since the grenache database above is read-only, you also need to have a
# different session backend in order to avoid exceptions due to attempts
# to save session data to the readonly database:
SESSION_ENGINE = "django.contrib.sessions.backends.cache"

CACHE_BACKEND     = 'locmem://'
SERVER_MODE	  = 'development'
DEBUG             = True

# If you need to debug email, you can start a debugging server that just
# outputs whatever it receives with:
#   python -m smtpd -n -c DebuggingServer localhost:1025
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025
EMAIL_HOST_USER = None
EMAIL_HOST_PASSWORD = None
