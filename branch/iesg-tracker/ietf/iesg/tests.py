import django.test
from django.core.urlresolvers import reverse as urlreverse

from pyquery import PyQuery

from ietf.idrfc.models import RfcIndex
from ietf.idtracker.models import *
from ietf.iesg.models import TelechatDates
from ietf.utils.test_utils import SimpleUrlTestCase, RealDatabaseTest, canonicalize_feed, login_testing_unauthorized

class RescheduleOnAgendaTestCase(django.test.TestCase):
    fixtures = ['base', 'draft']

    def test_reschedule(self):
        draft = InternetDraft.objects.get(filename="draft-ietf-mipshop-pfmipv6")
        draft.idinternal.telechat_date = TelechatDates.objects.all()[0].dates()[0]
        draft.idinternal.agenda = True
        draft.idinternal.returning_item = True
        draft.idinternal.save()

        form_id = draft.idinternal.draft_id
        telechat_date_before = draft.idinternal.telechat_date
        
        url = urlreverse('ietf.iesg.views.agenda_documents')
        self.client.login(remote_user="klm")

        # normal get
        r = self.client.get(url)
        self.assertEquals(r.status_code, 200)
        q = PyQuery(r.content)
        self.assertEquals(len(q('form select[name=%s-telechat_date]' % form_id)), 1)
        self.assertEquals(len(q('form input[name=%s-clear_returning_item]' % form_id)), 1)

        # reschedule
        comments_before = draft.idinternal.comments().count()
        d = TelechatDates.objects.all()[0].dates()[2]

        r = self.client.post(url, { '%s-telechat_date' % form_id: d.strftime("%Y-%m-%d"),
                                    '%s-clear_returning_item' % form_id: "1" })
        self.assertEquals(r.status_code, 200)

        # check that it moved below the right header in the DOM
        d_header_pos = r.content.find("IESG telechat %s" % d.strftime("%Y-%m-%d"))
        draft_pos = r.content.find(draft.filename)
        self.assertTrue(d_header_pos < draft_pos)

        draft = InternetDraft.objects.get(filename="draft-ietf-mipshop-pfmipv6")
        self.assertEquals(draft.idinternal.telechat_date, d)
        self.assertTrue(not draft.idinternal.returning_item)
        self.assertEquals(draft.idinternal.comments().count(), comments_before + 1)
        self.assertTrue("Telechat" in draft.idinternal.comments()[0].comment_text)


class IesgUrlTestCase(SimpleUrlTestCase):
    def testUrls(self):
        self.doTestUrls(__file__)
    def doCanonicalize(self, url, content):
        if url.startswith("/feed/"):
            return canonicalize_feed(content)
        else:
            return content

