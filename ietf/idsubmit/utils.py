# Copyright The IETF Trust 2008, All Rights Reserved

import subprocess
from django.conf import settings

def sync_docs(submission) :
    # sync docs with remote server.
    command = "sh %(BASE_DIR)s/idsubmit/sync_docs.sh --staging_path=%(staging_path)s --revision=%(revision)s --filename=%(filename)s --ssh_key_path=%(ssh_key_path)s --remote_web1=%(remote_web1)s --remote_ftp1=%(remote_ftp1)s" % {
        "filename" : submission.filename,
        "revision": submission.revision,
        "staging_path" : settings.STAGING_PATH,
        "BASE_DIR" : settings.BASE_DIR,
        "ssh_key_path" : settings.SSH_KEY_PATH,
        "remote_web1" : settings.TARGET_PATH_WEB1,
        "remote_ftp1" : settings.TARGET_PATH_FTP1,
    }
    # add options for extra web2 and ftp2 path
    try:
        command += " --remote_web2=%s" % settings.TARGET_PATH_WEB2
    except:
        pass
    try:
        command += " --remote_ftp2=%s" % settings.TARGET_PATH_FTP2
    except:
        pass
    try :
        p = subprocess.Popen([command], shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stderr = p.stderr
        if stderr:
            errmsg = []
            for msg in stderr.readlines():
                if not 'is not a tty' in msg and not msg in errmsg:
                    errmsg.append(msg)
            if errmsg:
                errmsg_html = '<br>\n'.join(errmsg)
                return False, errmsg_html
    except:
        return False, "<li>Failed to copy document to web server</li>"
    return True, None
