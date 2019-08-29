# Copyright The IETF Trust 2019, All Rights Reserved
# -*- coding: utf-8 -*-


# import datetime
# from pyquery import PyQuery

import debug                            # pyflakes:ignore

from django.urls import reverse as urlreverse

#from ietf.utils.test_utils import TestCase, login_testing_unauthorized, unicontent
from ietf.utils.test_utils import TestCase, unicontent
from ietf.doc.factories import IndividualDraftFactory, WgDraftFactory, RgDraftFactory
from ietf.doc.models import BallotDocEvent

class IssueIRSGBallotTests(TestCase):

    def test_issue_ballot_button(self):

        # creates empty drafts with lots of values filled in
        individual_draft = IndividualDraftFactory()
        wg_draft = WgDraftFactory()
        rg_draft = RgDraftFactory()

        # login as an IRTF chair
        self.client.login(username='irtf-chair', password='irtf-chair+password')

        # kwargs passes dict as keyword args
        url = urlreverse('ietf.doc.views_doc.document_main', kwargs=dict(name=individual_draft.name))
        # r is the response from the GET
        r = self.client.get(url)
        # GET successful?
        self.assertTrue(r.status_code == 200)

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

        self.client.logout()
        url = urlreverse('ietf.doc.views_doc.document_main',kwargs=dict(name=rg_draft.name))
        r = self.client.get(url)
        self.assertEqual(r.status_code,200)
        self.assertNotIn("Issue IRSG ballot", unicontent(r))

    def test_issue_ballot(self):

        # Just testing IRTF drafts
        rg_draft = RgDraftFactory()

        # login as an IRTF chair (who is a user who can issue an IRSG ballot)
        self.client.login(username='irtf-chair', password='irtf-chair+password')

        # Get the page with the Yes/No buttons
        url = urlreverse('ietf.doc.views_ballot.issue_irsg_ballot',kwargs=dict(name=rg_draft.name))
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        # Buttons present?
        self.assertIn("irsg_button", unicontent(r))

        # Press the No button - expect nothing but a redirect back to the draft's main page
        r = self.client.post(url,dict(irsg_button="No"))
        self.assertEqual(r.status_code, 302)
        # Insert assertion about the redirect URL

        # Press the Yes button
        r = self.client.post(url,dict(irsg_button="Yes"))
        self.assertEqual(r.status_code, 302)
        # Check on whether the ballot is reflected in the BallotDocEvents table
        ballot_open = BallotDocEvent.objects.filter(doc=rg_draft,
                                                type__in=("created_ballot"),
                                                ballot_type_in="irsg-approve")
        # Temporarily make use of ballot_open to prevent a squawk
        print(ballot_open)









