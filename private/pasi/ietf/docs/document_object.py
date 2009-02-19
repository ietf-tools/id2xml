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

from ietf.idtracker.models import Acronym, IETFWG, InternetDraft, Rfc, IDInternal, BallotInfo, IESGDiscuss, IESGComment, IESGDiscuss, Rfc, BallotInfo, Position, IESGLogin
from ietf.docs.models import RfcIndex, RfcEditorQueue, DraftVersions
import re
from django.http import HttpResponse
from django.db.models.query import QuerySet
from django.utils import simplejson
from datetime import date, timedelta
import types

BALLOT_ACTIVE_STATES = ['In Last Call',
                        'Waiting for Writeup',
                        'Waiting for AD Go-Ahead',
                        'IESG Evaluation',
                        'IESG Evaluation - Defer']

class MyJsonEncoder(simplejson.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, IDInternal) or isinstance(obj, InternetDraft):
            d = Document(draft=obj)
            return d.__dict__
        elif isinstance(obj, Document):
            return obj.__dict__
        elif isinstance(obj, types.GeneratorType):
            return list(obj)
        elif isinstance(obj, QuerySet):
            return list(obj)
        else:
            return simplejson.JSONEncoder.default(self, obj)

class JsonResponse(HttpResponse):
    def __init__(self, request, data):
        content = simplejson.dumps(data, indent=2, cls=MyJsonEncoder)
        HttpResponse.__init__(self, content, mimetype='text/plain')

class Document:
    def __init__(self, draft=None, rfc=None, rfcIndex=None):
        create_document_object(base=self.__dict__, draft=draft, rfc=rfc, rfcIndex=rfcIndex)
    def __str__(self):
        if 'draftName' in self.__dict__:
            return "Document("+self.draftName+")"
        else:
            return "Document(?)"
    
            
def create_document_object(draft=None, rfc=None, rfcIndex=None, base=None):
    if base == None:
        o = {}
    else:
        o = base

    if isinstance(draft, IDInternal):
        idinternal = draft
        draft = idinternal.draft
    else:
        if draft and draft.idinternal:
            idinternal = draft.idinternal
        else:
            idinternal = None
        
    if draft:
        o['draftName'] = draft.filename
        o['draftRevision'] = draft.revision
        o['draftNameAndRevision'] = draft.filename+"-"+draft.revision
        o['revisionDate'] = str(draft.revision_date)
        o['trackerId'] = draft.id_document_tag
        o['inIesgTracker'] = False
        o['pageCount'] = draft.txt_page_count
        o['title'] = draft.title
        o['status'] = str(draft.status)
        o['fileTypes'] = draft.file_type.split(",")
        if draft.intended_status and str(draft.intended_status) != "None":
            o['intendedStatus'] = str(draft.intended_status)
        else:
            o['intendedStatus'] = None
        if (draft.group_id != 0) and (draft.group != None) and (str(draft.group) != "none"):
            o['group'] = str(draft.group)
        else:
            o['group'] = None

        r = [str(r.filename) for r in draft.replaces_set.all()]
        if len(r) > 0:
            o['replaces'] = r
        try:
            if draft.replaced_by:
                o['replacedBy'] = [draft.replaced_by.filename]
        except InternetDraft.DoesNotExist:
            pass
        if draft.rfc_number:
            o['rfcNumber'] = int(draft.rfc_number)

    if idinternal:
        o['inIesgTracker'] = True
        o['state'] = str(idinternal.docstate())
        o['mainState'] = str(idinternal.cur_state)
        o['eventDate'] = str(idinternal.event_date)
        if idinternal.cur_sub_state_id > 0:
            o['subState'] = str(idinternal.cur_sub_state)
        else:
            o['subState'] = None
        if o['state'] == "In Last Call":
            o['lastCallEnds'] = str(draft.lc_expiration_date)
        o['iesgNote'] = str(idinternal.note)
            
        o['adName'] = idinternal.token_name
        # Some old documents have token name as "Surname, Firstname";
        # newer ones have "Firstname Surname"
        m = re.match(r'^(\w+), (\w+)$', o['adName'])
        if m:
            o['adName'] = m.group(2)+" "+m.group(1)
        if idinternal.via_rfc_editor > 0:
            o['rfcEditorSubmission'] = True
        o['stateChangeNoticeTo'] = idinternal.state_change_notice_to
        if idinternal.returning_item > 0:
            o['telechatReturningItem'] = True
        if idinternal.telechat_date:
            o['telechatDate'] = str(idinternal.telechat_date)
            o['onTelechatAgenda'] = (idinternal.agenda > 0)
            delta = date.today() - idinternal.telechat_date
            if delta.days < 30:
                o['telechatDateRecent'] = True

    if not draft:
        o['friendlyState'] = "RFC"
    elif o['status'] == "Active":
        if idinternal and o['state'] != "Dead":
            o['friendlyState'] = o['state']
        else:
            o['friendlyState'] = "I-D Exists";
    else:
        o['friendlyState'] = o['status']
    # fix
    if (o['friendlyState'] == "RFC Ed Queue") and (rfc or rfcIndex):
        o['friendlyState'] = "RFC"

    try:
        if idinternal and idinternal.ballot.ballot_issued:
            o['ballotId'] = idinternal.ballot_id
            o['ballotActive'] = o['mainState'] in BALLOT_ACTIVE_STATES
            o['ballotPositions'] = create_ballot_object(idinternal, o)
        else:
            o['ballotId'] = None
    except BallotInfo.DoesNotExist:
        o['ballotId'] = None

    # RFC
    # NOT READY REALLY
    
    if rfc:
        o['rfcNumber'] = rfc.rfc_number
        # intentional overwrites, if already set above
        o['title'] = rfc.title
        o['revisionDate'] = str(rfc.rfc_published_date)
        if rfc.group_acronym and (rfc.group_acronym != 'none'):
            o['group'] = rfc.group_acronym
        o['intendedStatus'] = None
        o['rfcStatus'] = str(rfc.status)
    if rfcIndex:
        # intentional overwrites, rfcIndex information is more accurate
        o['rfcNumber'] = rfcIndex.rfc_number
        if not draft:
            o['draftName'] = rfcIndex.draft
        o['title'] = rfcIndex.title
        o['rfcStatus'] = rfcIndex.current_status
        o['rfcUpdates'] = rfcIndex.updates
        o['rfcUpdatedBy'] = rfcIndex.updated_by
        o['rfcObsoletes'] = rfcIndex.obsoletes
        o['rfcObsoletedBy'] = rfcIndex.obsoleted_by
        o['rfcAlso'] = rfcIndex.also
        o['hasErrata'] = rfcIndex.has_errata > 0
        for k in ['rfcUpdates','rfcUpdatedBy','rfcObsoletes','rfcObsoletedBy','rfcAlso']:
            if o[k]:
                o[k] = o[k].replace(",", ",  ")
                o[k] = re.sub("([A-Z])([0-9])", "\\1 \\2", o[k])

    if draft:
        qs = RfcEditorQueue.objects.filter(draft=o['draftName'])
        if len(qs) >= 1:
            o['rfcEditorState'] = qs[0].state

    if 'rfcNumber' in o:
        o['friendlyGroup'] = 'RFCs'
        o['friendlyGroupSort'] = "2%04d" % o['rfcNumber']
    elif draft and o['status'] == "Active":
        o['friendlyGroup'] = "Active Internet-Drafts"
        o['friendlyGroupSort'] = "1"+o['draftName']
    else:
        o['friendlyGroup'] = "Old Internet-Drafts"
        o['friendlyGroupSort'] = "3"+o['draftName']

    s = ""
    if draft:
        s = s + "draft("+draft.filename+","+str(draft.id_document_tag)+","+str(draft.rfc_number)+")"
    if idinternal:
        s = s + ",idinternal()"
    if rfc:
        s = s + ",rfc("+str(rfc.rfc_number)+")"
    if rfcIndex:
        s = s + ",rfcIndex("+str(rfcIndex.rfc_number)+")"
    o['debug1'] = s
        
    return o

def create_ballot_object(idinternal, o):
    ads = set()
    for p in idinternal.ballot.positions.all():
        po = create_position_object(idinternal.ballot, p)
        ads.add(str(p.ad))
        yield po
    if o['ballotActive']:
        for ad in IESGLogin.active_iesg():
            if str(ad) not in ads:
                yield {"adName":str(ad), "position":None}
    return

def position_to_string(position):
    positions = {"yes":"Yes",
                 "noobj":"No Objection",
                 "discuss":"Discuss",
                 "abstain":"Abstain",
                 "recuse":"Recuse"}
    if not position:
        return "No Record"
    p = None
    for k,v in positions.iteritems():
        if position.__dict__[k] > 0:
            p = v
    if not p:
        p = "No Record"
    return p

def create_position_object(ballot, position):
    positions = {"yes":"Yes",
                 "noobj":"No Objection",
                 "discuss":"Discuss",
                 "abstain":"Abstain",
                 "recuse":"Recuse"}
    p = None
    for k,v in positions.iteritems():
        if position.__dict__[k] > 0:
            p = v
    r = {"adName":str(position.ad), "position":p}
    if not position.ad.is_current_ad():
        r['oldAd'] = True
        
    was = [v for k,v in positions.iteritems() if position.__dict__[k] < 0]
    if len(was) > 0:
        r['oldPositions'] = was

    try:
        comment = ballot.comments.get(ad=position.ad)
        if comment:
            r['commentText'] = comment.text
            r['commentDate'] = str(comment.date)
            r['commentRevision'] = str(comment.revision)
    except IESGComment.DoesNotExist:
        pass

    if p == "Discuss":
        try:
            discuss = ballot.discusses.get(ad=position.ad)
            if discuss and discuss.text:
                r['discussText'] = discuss.text
                r['discussRevision'] = str(discuss.revision)
                r['discussDate'] = str(discuss.date)
        except IESGDiscuss.DoesNotExist:
            pass
    return r

