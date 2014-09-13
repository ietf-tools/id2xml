import os
import shutil
import urllib

from pyquery import PyQuery

from django.conf import settings
from django.core.urlresolvers import reverse as urlreverse

from ietf.doc.models import DocAlias
from ietf.ipr.models import IprDetail # remove
from ietf.ipr.models import IprDisclosureBase
from ietf.utils.test_utils import TestCase
from ietf.utils.test_data import make_test_data


class IprTests(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass
    
    def test_showlist(self):
        make_test_data()
        ipr = IprDisclosureBase.objects.get(title='Statement regarding rights')
        
        r = self.client.get(urlreverse("ipr_showlist"))
        self.assertEqual(r.status_code, 200)
        self.assertTrue(ipr.title in r.content)

    def test_show(self):
        make_test_data()
        ipr = IprDisclosureBase.objects.get(title='Statement regarding rights')

        r = self.client.get(urlreverse("ipr_show", kwargs=dict(id=ipr.pk)))
        self.assertEqual(r.status_code, 200)
        self.assertTrue(ipr.title in r.content)
        
    def test_iprs_for_drafts(self):
        draft = make_test_data()
        ipr = IprDisclosureBase.objects.get(title='Statement regarding rights')

        r = self.client.get(urlreverse("ietf.ipr.views.iprs_for_drafts_txt"))
        self.assertEqual(r.status_code, 200)
        self.assertTrue(draft.name in r.content)
        self.assertTrue(str(ipr.pk) in r.content)

    def test_about(self):
        r = self.client.get(urlreverse("ietf.ipr.views.about"))
        self.assertEqual(r.status_code, 200)
        self.assertTrue("File a disclosure" in r.content)

    def test_search(self):
        draft = make_test_data()
        ipr = IprDisclosureBase.objects.get(title="Statement regarding rights")

        url = urlreverse("ipr_search")

        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        q = PyQuery(r.content)
        self.assertTrue(q("form input[name=document_search]"))

        # find by id
        r = self.client.get(url + "?option=document_search&id=%s" % draft.name)
        self.assertEqual(r.status_code, 200)
        self.assertTrue(ipr.title in r.content)

        # find draft
        r = self.client.get(url + "?option=document_search&document_search=%s" % draft.name)
        self.assertEqual(r.status_code, 200)
        self.assertTrue(ipr.title in r.content)

        # search + select document
        r = self.client.get(url + "?option=document_search&document_search=draft")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(draft.name in r.content)
        self.assertTrue(ipr.title not in r.content)

        DocAlias.objects.create(name="rfc321", document=draft)

        # find RFC
        r = self.client.get(url + "?option=rfc_search&rfc_search=321")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(ipr.title in r.content)

        # find by patent owner
        r = self.client.get(url + "?option=patent_search&patent_search=%s" % ipr.holder_legal_name)
        self.assertEqual(r.status_code, 200)
        self.assertTrue(ipr.title in r.content)
        
        # find by patent info
        r = self.client.get(url + "?option=patent_info_search&patent_info_search=%s" % ipr.patent_info)
        self.assertEqual(r.status_code, 200)
        self.assertTrue(ipr.title in r.content)

        r = self.client.get(url + "?option=patent_info_search&patent_info_search=PTO9876")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(ipr.title in r.content)

        # find by group acronym
        r = self.client.get(url + "?option=wg_search&wg_search=%s" % draft.group.acronym)
        self.assertEqual(r.status_code, 200)
        self.assertTrue(ipr.title in r.content)

        # find by doc title
        r = self.client.get(url + "?option=title_search&title_search=%s" % urllib.quote(draft.title))
        self.assertEqual(r.status_code, 200)
        self.assertTrue(ipr.title in r.content)

        # find by ipr title
        r = self.client.get(url + "?option=ipr_title_search&ipr_title_search=%s" % urllib.quote(ipr.title))
        self.assertEqual(r.status_code, 200)
        self.assertTrue(ipr.title in r.content)

    def test_feed(self):
        make_test_data()
        ipr = IprDisclosureBase.objects.get(title='Statement regarding rights')

        r = self.client.get("/feed/ipr/")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(ipr.title in r.content)

    def test_sitemap(self):
        make_test_data()
        ipr = IprDisclosureBase.objects.get(title='Statement regarding rights')

        r = self.client.get("/sitemap-ipr.xml")
        self.assertEqual(r.status_code, 200)
        self.assertTrue("/ipr/%s/" % ipr.pk in r.content)

    def test_new_generic(self):
        make_test_data()
        url = urlreverse("ietf.ipr.views.new", kwargs={ "type": "generic" })

        # faulty post
        r = self.client.post(url, {
            "holder_legal_name": "Test Legal",
            })
        self.assertEqual(r.status_code, 200)
        q = PyQuery(r.content)
        self.assertTrue(len(q("ul.errorlist")) > 0)

        # successful post
        r = self.client.post(url, {
            "holder_legal_name": "Test Legal",
            "holder_contact_name": "Test Holder",
            "holder_contact_info": "555-555-0100",
            "licensing_option": "5",
            "notes": "some notes"
            })
        self.assertEqual(r.status_code, 200)
        self.assertTrue("Your IPR disclosure has been submitted" in r.content)

        iprs = IprDisclosureBase.objects.filter(title__icontains="General License Statement")
        self.assertEqual(len(iprs), 1)
        ipr = iprs[0]
        self.assertEqual(ipr.legal_name, "Test Legal")
        self.assertEqual(ipr.status, 0)

    def test_new_specific(self):
        draft = make_test_data()
        url = urlreverse("ietf.ipr.views.new", kwargs={ "type": "specific" })

        # successful post
        r = self.client.post(url, {
            "holder_legal_name": "Test Legal",
            "holder_contact_name": "Test Holder",
            "holder_contact_info": "555-555-0100",
            "ietfer_name": "Test Participant",
            "ietfer_contact_info": "555-555-0101",
            "rfc-TOTAL_FORMS": 1,
            "rfc-INITIAL_FORMS": 0,
            "rfc-0-document": DocAlias.objects.filter(name__startswith="rfc").first().name,
            "draft-TOTAL_FORMS": 1,
            "draft-INITIAL_FORMS": 0,
            "draft-0-document": "%s" % draft.name,
            "draft-0-revisions": '00',
            "patent_info": "none",
            "has_patent_pending": False,
            "licensing": "royalty",
            })
        self.assertEqual(r.status_code, 200)
        # print r.content
        self.assertTrue("Your IPR disclosure has been submitted" in r.content)

        iprs = IprDisclosureBase.objects.filter(title__icontains=draft.name)
        self.assertEqual(len(iprs), 1)
        ipr = iprs[0]
        self.assertEqual(ipr.holder_legal_name, "Test Legal")
        self.assertEqual(ipr.state.slug, 'pending')

    def test_new_thirdparty(self):
        draft = make_test_data()
        url = urlreverse("ietf.ipr.views.new", kwargs={ "type": "third-party" })

        # successful post
        r = self.client.post(url, {
            "holder_legal_name": "Test Legal",
            "holder_contact_name": "Test Holder",
            "holder_contact_info": "555-555-0100",
            "ietfer_name": "Test Participant",
            "ietfer_contact_info": "555-555-0101",
            "rfc-TOTAL_FORMS": 1,
            "rfc-INITIAL_FORMS": 0,
            "rfc-0-document": DocAlias.objects.filter(name__startswith="rfc").first().name,
            "draft-TOTAL_FORMS": 1,
            "draft-INITIAL_FORMS": 0,
            "draft-0-document": "%s" % draft.name,
            "draft-0-revisions": '00',
            "patent_info": "none",
            "has_patent_pending": False,
            "licensing": "royalty",
            })
        self.assertEqual(r.status_code, 200)
        # print r.content
        self.assertTrue("Your IPR disclosure has been submitted" in r.content)

        iprs = IprDisclosureBase.objects.filter(title__icontains="belonging to Test Legal")
        self.assertEqual(len(iprs), 1)
        ipr = iprs[0]
        self.assertEqual(ipr.holder_legal_name, "Test Legal")
        self.assertEqual(ipr.state.slug, "pending")

    def test_update(self):
        draft = make_test_data()
        original_ipr = IprDisclosureBase.objects.get(title='Statement regarding rights')
        url = urlreverse("ietf.ipr.views.new", kwargs={ "type": "specific" })

        # successful post
        r = self.client.post(url, {
            "updates": str(original_ipr.pk),
            "holder_legal_name": "Test Legal",
            "holder_contact_name": "Test Holder",
            "holder_contact_info": "555-555-0100",
            "ietfer_name": "Test Participant",
            "ietfer_contact_info": "555-555-0101",
            "rfc-TOTAL_FORMS": 1,
            "rfc-INITIAL_FORMS": 0,
            "rfc-0-document": DocAlias.objects.filter(name__startswith="rfc").first().name,
            "draft-TOTAL_FORMS": 1,
            "draft-INITIAL_FORMS": 0,
            "draft-0-document": "%s" % draft.name,
            "draft-0-revisions": '00',
            "patent_info": "none",
            "has_patent_pending": False,
            "licensing": "royalty",
            })
        self.assertEqual(r.status_code, 200)
        self.assertTrue("Your IPR disclosure has been submitted" in r.content)

        iprs = IprDisclosureBase.objects.filter(title__icontains=draft.name)
        self.assertEqual(len(iprs), 1)
        ipr = iprs[0]
        self.assertEqual(ipr.holder_legal_name, "Test Legal")
        self.assertEqual(ipr.state.slug, 'pending')

        self.assertTrue(ipr.relatedipr_source_set.filter(target=original_ipr))
