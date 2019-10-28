# Copyright The IETF Trust 2019, All Rights Reserved
# -*- coding: utf-8 -*-


# import datetime
# from pyquery import PyQuery

import debug                            # pyflakes:ignore

from django.urls import reverse as urlreverse

from ietf.utils.test_utils import TestCase, login_testing_unauthorized, unicontent
from ietf.doc.factories import IndividualDraftFactory, WgDraftFactory, RgDraftFactory, RgRfcFactory
from ietf.doc.models import BallotDocEvent
from ietf.person.utils import get_active_irsg, get_active_ads

class IssueIRSGBallotTests(TestCase):

    def test_issue_ballot_button(self):

        # creates empty drafts with lots of values filled in
        individual_draft = IndividualDraftFactory()
        wg_draft = WgDraftFactory()
        rg_draft = RgDraftFactory()
        rg_rfc = RgRfcFactory()

        # login as an IRTF chair
        self.client.login(username='irtf-chair', password='irtf-chair+password')

        url = urlreverse('ietf.doc.views_doc.document_main',kwargs=dict(name=individual_draft.name))
        r = self.client.get(url)
        self.assertEqual(r.status_code,200)
        self.assertNotIn("Issue IRSG ballot", unicontent(r))

        url = urlreverse('ietf.doc.views_doc.document_main',kwargs=dict(name=wg_draft.name))
        r = self.client.get(url)
        self.assertEqual(r.status_code,200)
        self.assertNotIn("Issue IRSG ballot", unicontent(r))

        url = urlreverse('ietf.doc.views_doc.document_main',kwargs=dict(name=rg_draft.name))
        r = self.client.get(url)
        self.assertEqual(r.status_code,200)
        self.assertIn("Issue IRSG ballot", unicontent(r))

        debug.say("Issue test rg rfc")
        debug.show("rg_rfc")
        url = urlreverse('ietf.doc.views_doc.document_main',kwargs=dict(name=rg_rfc.name))
        r = self.client.get(url)
        debug.show("r")
        self.assertEqual(r.status_code,200)
        self.assertNotIn("Issue IRSG ballot", unicontent(r))        

        self.client.logout()
        url = urlreverse('ietf.doc.views_doc.document_main',kwargs=dict(name=rg_draft.name))
        r = self.client.get(url)
        self.assertEqual(r.status_code,200)
        self.assertNotIn("Issue IRSG ballot", unicontent(r))

    def test_close_ballot_button(self):

        # creates empty drafts with lots of values filled in
        individual_draft = IndividualDraftFactory()
        wg_draft = WgDraftFactory()
        rg_draft = RgDraftFactory()
        rg_rfc = RgRfcFactory()

        # login as an IRTF chair
        self.client.login(username='irtf-chair', password='irtf-chair+password')

        # Get the page with the Issue IRSG Ballot Yes/No buttons
        url = urlreverse('ietf.doc.views_ballot.issue_irsg_ballot',kwargs=dict(name=rg_draft.name))
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)

        # Press the Yes button
        r = self.client.post(url,dict(irsg_button="Yes", duedate="2038-01-19"))
        self.assertEqual(r.status_code, 302)

        url = urlreverse('ietf.doc.views_doc.document_main',kwargs=dict(name=individual_draft.name))
        r = self.client.get(url)
        self.assertEqual(r.status_code,200)
        self.assertNotIn("Close IRSG ballot", unicontent(r))

        url = urlreverse('ietf.doc.views_doc.document_main',kwargs=dict(name=wg_draft.name))
        r = self.client.get(url)
        self.assertEqual(r.status_code,200)
        self.assertNotIn("Close IRSG ballot", unicontent(r))

        url = urlreverse('ietf.doc.views_doc.document_main',kwargs=dict(name=rg_draft.name))
        r = self.client.get(url)
        self.assertEqual(r.status_code,200)
        self.assertIn("Close IRSG ballot", unicontent(r))

        debug.say("Close IRSG ballot test rfc")
        debug.show('rg_rfc')
        url = urlreverse('ietf.doc.views_doc.document_main',kwargs=dict(name=rg_rfc.name))
        r = self.client.get(url)
        self.assertEqual(r.status_code,200)
        self.assertNotIn("Close IRSG ballot", unicontent(r))        

        self.client.logout()
        url = urlreverse('ietf.doc.views_doc.document_main',kwargs=dict(name=rg_draft.name))
        r = self.client.get(url)
        self.assertEqual(r.status_code,200)
        self.assertNotIn("Close IRSG ballot", unicontent(r))

    def test_issue_ballot(self):

        # Just testing IRTF drafts
        rg_draft = RgDraftFactory()

        # login as an IRTF chair (who is a user who can issue an IRSG ballot)
        self.client.login(username='irtf-chair', password='irtf-chair+password')

        # Get the page with the Issue IRSG Ballot Yes/No buttons
        url = urlreverse('ietf.doc.views_ballot.issue_irsg_ballot',kwargs=dict(name=rg_draft.name))
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        # Buttons present?
        self.assertIn("irsg_button", unicontent(r))

        # Press the No button - expect nothing but a redirect back to the draft's main page
        r = self.client.post(url,dict(irsg_button="No"))
        self.assertEqual(r.status_code, 302)
        # PEY: Insert assertion about the redirect URL

        # Press the Yes button
        r = self.client.post(url,dict(irsg_button="Yes", duedate="2038-01-19"))
        self.assertEqual(r.status_code, 302)
        # PEY: Check on whether the ballot is reflected in the BallotDocEvents table
        # Can't get ballot_type to work in the filter below, so commented out for now
        # ballot_type = BallotType.objects.get(doc_type=rg_draft.type,slug='irsg-approve')
        # debug.show("ballot_type")
        ballot_created = list(BallotDocEvent.objects.filter(doc=rg_draft,
                                                type="created_ballot"))
        self.assertNotEqual(len(ballot_created), 0)

        # Having issued a ballot, the Issue IRSG ballot button should be gone
        url = urlreverse('ietf.doc.views_doc.document_main',kwargs=dict(name=rg_draft.name))
        r = self.client.get(url)
        self.assertEqual(r.status_code,200)
        self.assertNotIn("Issue IRSG ballot", unicontent(r))

        # The IRSG evaluation record tab should exist
        self.assertIn("IRSG evaluation record", unicontent(r))
        # The IRSG evaluation record tab should not indicate unavailability
        self.assertNotIn("IRSG Evaluation Ballot has not been created yet", unicontent(r))

        # We should find an IRSG member's name on the IRSG evaluation tab regardless of any positions taken or not
        url = urlreverse('ietf.doc.views_doc.document_irsg_ballot',kwargs=dict(name=rg_draft.name))
        r = self.client.get(url)
        self.assertEqual(r.status_code,200)
        irsgmembers = get_active_irsg()
        self.assertNotEqual(len(irsgmembers), 0)
        self.assertIn(irsgmembers[0].name, unicontent(r))

        # Also issue a contemporaneous IESG ballot
        url = urlreverse('ietf.doc.views_ballot.ballot_writeupnotes', kwargs=dict(name=rg_draft.name))
        login_testing_unauthorized(self, "ad", url)
        
        r = self.client.post(url, dict(
                ballot_writeup="This is a test.",
                issue_ballot="1"))
        self.assertEqual(r.status_code, 200)

        # Look for IESG member name in the ballot list
        url = urlreverse('ietf.doc.views_doc.document_ballot',kwargs=dict(name=rg_draft.name))
        r = self.client.get(url)
        self.assertEqual(r.status_code,200)
        iesgmembers = get_active_ads()
        self.assertNotEqual(len(iesgmembers), 0)
        self.assertIn(iesgmembers[0].name, unicontent(r))
