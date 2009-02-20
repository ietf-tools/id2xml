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

from ietf import settings
from django.core import management
management.setup_environ(settings)
from django import db

from xml.dom import pulldom
from xml.dom import Node
import re
import urllib2

QUEUE_URL = "http://www.rfc-editor.org/queue2.xml"
TABLE = "rfc_editor_queue_mirror"
REF_TABLE = "rfc_editor_queue_mirror_refs"

def getChildText(parentNode, tagName):
    for node in parentNode.childNodes:
        if node.nodeType == Node.ELEMENT_NODE and node.localName == tagName:
            return node.firstChild.data
    return None

cursor = db.connection.cursor()

print "mirror_rfc_editor_queue: downloading "+QUEUE_URL

response = urllib2.urlopen(QUEUE_URL)
events = pulldom.parse(response)
data = []
draft_names = {}
draft_ids = {}
refs = []
for (event, node) in events:
    if event == pulldom.START_ELEMENT and node.tagName == "entry":
        events.expandNode(node)
        node.normalize()
        draft_name = getChildText(node, "draft")
        if re.search("-\d\d\.txt$", draft_name):
            draft_name = draft_name[0:-7]

        # convert draft filename to id_document_tag
        cursor.execute("SELECT id_document_tag FROM internet_drafts WHERE filename=%s", [draft_name])
        row = cursor.fetchone()
        if not row:
            print "mirror_rfc_editor_queue: warning, unknown draft name "+draft_name
            continue
        draft_id = row[0]
        draft_ids[draft_name] = draft_id
        draft_names[draft_id] = draft_name
        
        date_received = getChildText(node, "date-received")
        state = getChildText(node, "state")
        if not state:
            state = "?"
        data.append([draft_id, date_received, state, stream])

        for node2 in node.childNodes:
            if node2.nodeType == Node.ELEMENT_NODE and node2.localName == "normRef":
                ref_name = getChildText(node2, "ref-name")
                ref_state = getChildText(node2, "ref-state")
                in_queue = ref_state.startswith("IN-QUEUE")
                refs.append([draft_id, ref_name, in_queue, True])
        
    elif event == pulldom.START_ELEMENT and node.tagName == "section":
        name = node.getAttribute('name')
        if name.startswith("IETF"):
            stream = 1
        elif name.startswith("IAB"):
            stream = 2
        elif name.startswith("IRTF"):
            stream = 3
        elif name.startswith("INDEPENDENT"):
            stream = 4
        else:
            stream = 0
            print "mirror_rfc_editor_queue: warning, unrecognized section "+name

print "mirror_rfc_editor_queue: parsed " + str(len(data)) + " drafts"
print "mirror_rfc_editor_queue: parsed " + str(len(refs)) + " direct refs"

# Find set of all normative references (whether direct or via some
# other normative reference)

indirect_refs = []
def recurse_refs(draft_id, draft_name, ref_name_set, level):
    for (source_id, destination_name, in_queue, direct) in refs:
        if source_id == draft_id:
            if destination_name in ref_name_set:
                pass
            else:
                ref_name_set.add(destination_name)
                if destination_name in draft_ids:
                    recurse_refs(draft_ids[destination_name], None, ref_name_set, level+1)
    if level == 0:
        for ref_name in ref_name_set:
            if ref_name != draft_name:
                indirect_refs.append([draft_id, ref_name, ref_name in draft_ids, False])

for draft_id, draft_name in draft_names.iteritems():
    recurse_refs(draft_id, draft_name, set([draft_name]), 0)

print "mirror_rfc_editor_queue: found " + str(len(indirect_refs)) + " indirect refs"
if len(data) < 1:
    raise Exception('No data')

cursor.execute("DELETE FROM "+TABLE)
cursor.executemany("INSERT INTO "+TABLE+" (id_document_tag, date_received, state, stream) VALUES (%s, %s, %s, %s)", data)
cursor.execute("DELETE FROM "+REF_TABLE)
cursor.executemany("INSERT INTO "+REF_TABLE+" (source, destination, in_queue, direct) VALUES (%s, %s, %s, %s)", refs+indirect_refs)
cursor.close()
db.connection._commit()
db.connection.close()

print "mirror_rfc_editor_queue: done"
