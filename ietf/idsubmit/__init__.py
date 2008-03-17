# Copyright The IETF Trust 2007, All Rights Reserved
from django.conf import settings
import sys
print "Checking mendatory settings..."
fatal_error = 0
try:
    print "Remote path to FTP server 1: %s" % settings.TARGET_PATH_FTP1
except:
    print "Not Found: Remote path to FTP server 1, TARGET_PATH_FTP1"
    fatal_error = 1
try:
    print "Remote path to WEB server 1: %s" % settings.TARGET_PATH_WEB1
except:
    print "Not Found: Remote WEB server 1, TARGET_PATH_WEB1"
    fatal_error = 1
try:
    print "Path to ssh key: %s" % settings.SSH_KEY_PATH
except:
    print "Not Found: Path to ssh key, SSH_KEY_PATH"
    fatal_error = 1
try:
    print "Path to staging location: %s" % settings.STAGING_PATH
except:
    print "Not Found: Path to staging location, STAGING_PATH"
    fatal_error = 1
try:
    print "URL of staging location: %s" % settings.STAGING_URL
except:
    print "Not Found: URL of staging location, STAGING_URL"
    fatal_error = 1
print "\nChecking optional settings..."
try:
    print "Remote path to FTP server 2: %s" % settings.TARGET_PATH_FTP2
except:
    print "Not Found: Remote path to FTP server 2, TARGET_PATH_FTP2"
try:
    print "Remote path to WEB server 2: %s" % settings.TARGET_PATH_WEB2
except:
    print "Not Found: Remote path to WEB server 2, TARGET_PATH_WEB2"
if fatal_error:
    print "Missing mendatory settings value. Terminating program"
    sys.exit(0)
else:
    print "Looks good. Starting django..."

    
