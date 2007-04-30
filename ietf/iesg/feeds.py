from django.contrib.syndication.feeds import Feed
from django.utils.feedgenerator import Atom1Feed
from django.utils.dateformat import format
from ietf.iesg.models import TelechatMinutes

class IESGMinutes(Feed):
    title = "IESG Telechat Minutes"
    link = "/iesg/telechat/"
    subtitle = "Minutes from IESG Telechats."
    feed_type = Atom1Feed

    def items(self):
	return TelechatMinutes.objects.order_by('-telechat_date')[:10]

    def item_link(self, item):
	return "/iesg/telechat/%s/%d/" % (format(item.telechat_date, "Y/b/j"), item.id)

    # The approval date isn't stored, so let's just say they're
    # published on the date of the telechat.
    def item_pubdate(self, item):
	# (slightly better would be 0900 Eastern on this date)
	return item.telechat_date
