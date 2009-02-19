# Copyright (C) 2009 Nokia Corporation and/or its subsidiary(-ies).
# All rights reserved. Contact: Pasi Eronen <pasi.eronen@nokia.com>
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
#
#  * Neither the name of the Nokia Corporation and/or its
#    subsidiary(-ies) nor the names of its contributors may be used
#    to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from django import newforms as forms
from ietf.idtracker.models import IDState, IDStatus, IETFWG, IESGLogin, IDSubState, Area
from ietf.idindex.models import orgs
from ietf.utils import normalize_draftname


class SearchForm(forms.Form):
    filename = forms.CharField(required=False)
    author = forms.CharField(required=False)
    rfcs = forms.BooleanField(required=False,initial=True)
    activeDrafts = forms.BooleanField(required=False,initial=True)
    oldDrafts = forms.BooleanField(required=False,initial=False)

    group = forms.CharField(required=False)
    area = forms.ModelChoiceField(Area.objects.filter(status=Area.ACTIVE), empty_label="any area", required=False)

    ad = forms.ChoiceField(choices=(), required=False)
    state = forms.ModelChoiceField(IDState.objects.all(), empty_label="any state", required=False)
    subState = forms.ChoiceField(choices=(), required=False)
        
    def clean_filename(self):
        value = self.clean_data.get('filename','')
        return normalize_draftname(value)
    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        self.fields['ad'].choices = [('', 'any AD')] + [(ad.id, "%s %s" % (ad.first_name, ad.last_name)) for ad in IESGLogin.objects.filter(user_level=1).order_by('last_name')] + [('-99', '------------------')] + [(ad.id, "%s %s" % (ad.first_name, ad.last_name)) for ad in IESGLogin.objects.filter(user_level=2).order_by('last_name')]
        self.fields['subState'].choices = [('', 'any substate'), ('0', 'no substate')] + [(state.sub_state_id, state.sub_state) for state in IDSubState.objects.all()]
                                                                        
