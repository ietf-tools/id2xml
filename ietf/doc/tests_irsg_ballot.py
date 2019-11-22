# Copyright The IETF Trust 2019, All Rights Reserved
# -*- coding: utf-8 -*-


# import datetime
# from pyquery import PyQuery

import debug                            # pyflakes:ignore

from django.urls import reverse as urlreverse

from ietf.utils.test_utils import TestCase, unicontent, login_testing_unauthorized
from ietf.doc.factories import IndividualDraftFactory, WgDraftFactory, RgDraftFactory, RgRfcFactory
from ietf.doc.models import BallotDocEvent
from ietf.doc.utils import create_ballot_if_not_open
from ietf.person.utils import get_active_irsg
from ietf.group.factories import RoleFactory

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

        url = urlreverse('ietf.doc.views_doc.document_main',kwargs=dict(name=rg_rfc.name))
        r = self.client.get(url, follow = True)
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

        # Login as the IRTF chair
        self.client.login(username='irtf-chair', password='irtf-chair+password')

        # Get the page with the Issue IRSG Ballot Yes/No buttons
        url = urlreverse('ietf.doc.views_ballot.issue_irsg_ballot',kwargs=dict(name=rg_draft.name))
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)

        # Press the Yes button
        r = self.client.post(url,dict(irsg_button="Yes", duedate="2038-01-19"))
        self.assertEqual(r.status_code, 302)
        self.assertTrue(rg_draft.ballot_open('irsg-approve'))

        # Logout - the Close button should not be available
        self.client.logout()
        url = urlreverse('ietf.doc.views_doc.document_main',kwargs=dict(name=rg_draft.name))
        r = self.client.get(url)
        self.assertEqual(r.status_code,200)
        self.assertNotIn("Close IRSG ballot", unicontent(r))

        # Login again as the IRTF chair
        self.client.login(username='irtf-chair', password='irtf-chair+password')

        # The close button should now be available
        r = self.client.get(url)
        self.assertEqual(r.status_code,200)
        self.assertIn("Close IRSG ballot", unicontent(r))

        # Get the page with the Close IRSG Ballot Yes/No buttons
        url = urlreverse('ietf.doc.views_ballot.close_irsg_ballot',kwargs=dict(name=rg_draft.name))
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)

        # Press the Yes button
        r = self.client.post(url,dict(irsg_button="Yes"))
        self.assertEqual(r.status_code,302)
        # Expect the draft not to have an open IRSG ballot anymore
        self.assertFalse(rg_draft.ballot_open('irsg-approve'))

        # Individual, IETF, and RFC docs should not show the Close button
        url = urlreverse('ietf.doc.views_doc.document_main',kwargs=dict(name=individual_draft.name))
        r = self.client.get(url)
        self.assertEqual(r.status_code,200)
        self.assertNotIn("Close IRSG ballot", unicontent(r))

        url = urlreverse('ietf.doc.views_doc.document_main',kwargs=dict(name=wg_draft.name))
        r = self.client.get(url)
        self.assertEqual(r.status_code,200)
        self.assertNotIn("Close IRSG ballot", unicontent(r))

        url = urlreverse('ietf.doc.views_doc.document_main',kwargs=dict(name=rg_rfc.name))
        r = self.client.get(url, follow = True)
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

        # Having issued a ballot, it should appear on the IRSG Ballot Status page
        url = urlreverse('ietf.doc.views_ballot.irsg_ballot_status')
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        # Does the draft name appear on the page?
        self.assertIn(rg_draft.name, unicontent(r))

    def test_edit_ballot_position_permissions(self):
            rg_draft = RgDraftFactory()
            wg_draft = WgDraftFactory()
            ad = RoleFactory(group__type_id='area',name_id='ad')
            pre_ad = RoleFactory(group__type_id='area',name_id='pre-ad')
            irsgmember = get_active_irsg()[0]
            secr = RoleFactory(group__acronym='secretariat',name_id='secr')
            wg_ballot = create_ballot_if_not_open(None, wg_draft, ad.person, 'approve')
            url = urlreverse('ietf.doc.views_ballot.edit_position', kwargs=dict(name=wg_draft.name, ballot_id=wg_ballot.pk))

            # Pre-ADs can see
            login_testing_unauthorized(self, pre_ad.person.user.username, url)

            # But Pre-ADs cannot take a position
            r = self.client.post(url, dict(position="discuss", discuss="Test discuss text"))
            self.assertEqual(r.status_code, 403)

            # PEY: is the logout required between logins?
            self.client.logout()

            # ADs can see and take a position
            login_testing_unauthorized(self, ad.person.user.username, url)
            r = self.client.post(url, dict(position="discuss", discuss="Test discuss text"))
            self.assertEqual(r.status_code, 302)
            self.client.logout()

            rg_ballot = create_ballot_if_not_open(None, rg_draft, secr.person, 'irsg-approve')
            url = urlreverse('ietf.doc.views_ballot.edit_position', kwargs=dict(name=rg_draft.name, ballot_id=rg_ballot.pk))

            # IRSG members should be able to enter a position on IRSG ballots
            login_testing_unauthorized(self, irsgmember.user.username, url)
            r = self.client.post(url, dict(position="yes"))
            self.assertEqual(r.status_code, 302)

