# Copyright The IETF Trust 2007, All Rights Reserved

import datetime

from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed
from django.core.urlresolvers import reverse_lazy
from django.utils.safestring import mark_safe

from ietf.ipr.models import IprDisclosureBase

class LatestIprDisclosuresFeed(Feed):
    feed_type = Atom1Feed
    title = "IPR Disclosures to the IETF"
    link = reverse_lazy('ipr_showlist')
    description = "Updates on new IPR Disclosures made to the IETF."
    language = "en"
    feed_url = "/feed/ipr/"

    def items(self):
        q = IprDisclosureBase.objects.filter(state__in=('posted','removed'))
        return sorted(q, key=lambda x: x.submitted_date, reverse=True)[:30]

    def item_title(self, item):
        return mark_safe(item.title)

    def item_description(self, item):
        return unicode(item.title)
        
    def item_pubdate(self, item):
        return item.submitted_date

    def item_author_name(self, item):
        if item.by:
            return item.by.name
        else:
            return None

    def item_author_email(self, item):
        if item.by:
            return item.by.email_address()
        else:
            return None
