import re

from django.conf import settings
from django.http import HttpResponseForbidden
from django.shortcuts import render_to_response
#from sec.core.models import IESGLogin, LegacyWgPassword
import sec.core.models


class SecAuthMiddleware(object):
    """
    Middleware component that performs custom auth check for every
    request except those excluded by SEC_AUTH_UNRESTRICTED_URLS.

    Since authentication is performed externally at the apache level
    REMOTE_USER should contain the name of the authenticated
    user.  If this login exists in iesg_login table with user_level=0
    than access is granted.  Otherwise return a 401 error page.

    To use, add the class to MIDDLEWARE_CLASSES and define
    SEC_AUTH_UNRESTRCITED_URLS in your settings.py.

    The following example allows access to anything under "/interim/"
    to non-secretariat users:

    SEC_AUTH_UNRESTRCITED_URLS = (
        (r'^/interim/'),

    Also sets two custom request attributes:
    user_is_secretariat
    user_is_chair
    user_is_ad
    )

    """
 
    def __init__(self):
        self.unrestricted = [re.compile(pattern) for pattern in
            settings.SEC_AUTH_UNRESTRICTED_URLS]

    def process_view(self, request, view_func, view_args, view_kwargs):
        # need to initialize user, it doesn't get set when running tests for example
        user = ''
        request.user_is_secretariat = False
        request.user_is_chair = False
        request.user_is_ad = False

        if 'REMOTE_USER' in request.META:
            # do custom auth
            user = request.META['REMOTE_USER']
            try:
                iesg = sec.core.models.IESGLogin.objects.get(login_name=user)
                if iesg.user_level == 0:
                    request.user_is_secretariat = True
                elif iesg.user_level == 1:
                    request.user_is_ad = True
                request.person = iesg.person
            except sec.core.models.IESGLogin.DoesNotExist:
                try: 
                    # if the login is not found in IESGLogin try LegacyWgPassword
                    lwp = sec.core.models.LegacyWgPassword.objects.get(login_name=user)
                    request.person = lwp.person
                    request.user_is_chair = True
                except sec.core.models.LegacyWgPassword.DoesNotExist:
                    request.person = None

            for regex in self.unrestricted:
                if regex.match(request.path):
                    return None

            if request.user_is_secretariat:
                # Access granted
                return None

        return render_to_response('401.html', {'user':user})
