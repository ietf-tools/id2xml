# Copyright The IETF Trust 2010, All Rights Reserved

from django.shortcuts import render_to_response as render, get_object_or_404
from django.template import RequestContext
from django.db.models import Max, Min
from ietf.idtracker.models import Area, Rfc, IETFWG
from ietf.idrfc.models import RfcIndex
from datetime import datetime

# Show RFC statistcs for area, wg or for all RFCs.
#
# If the area_or_wg is "all" then show statistics of all rfcs
# If the area_or_wg is area, then show statistics for that area
# otherwise assume it is working group acronym.

def rfcstats(request, area_or_wg="all"):
    # Find the list of RFCs, and the name to show in title.
    if area_or_wg == "all":
	name = 0
        rfcs = Rfc.objects.all()
    else:
	try:
	    id = Area.objects.get(area_acronym__acronym=area_or_wg)
	    name = id.area_acronym.name
	    rfcs = Rfc.objects.filter(area_acronym=area_or_wg)
	except:
	    id = get_object_or_404(IETFWG, group_acronym__acronym=area_or_wg)
	    name = id.group_acronym.name
	    rfcs = Rfc.objects.filter(group_acronym=area_or_wg)

    # Seach the RFCs from the RfcIndex (RFC editor mirror table
    # to get correct status
    rfccount = rfcs.count()
    rfcids = rfcs.values_list('rfc_number', flat=True)
    rfcmirror = RfcIndex.objects.filter(rfc_number__in=rfcids)

    # RfcIndex has status as string, and we do not necessarely know
    # which strings are used (or we do now, but not in the future)
    # So check out which strings are used as current_status
    rfcmirrorstatus = {}
    for s in rfcmirror:
      rfcmirrorstatus[s.current_status] = 100

    # Sort the status strings to "good" order
    rfcmirrorstatus["Standard"] = 10
    rfcmirrorstatus["Draft Standard"] = 20
    rfcmirrorstatus["Proposed Standard"] = 30
    rfcmirrorstatus["Best Current Practice"] = 40
    rfcmirrorstatus["Informational"] = 50
    rfcmirrorstatus["Experimental"] = 60
    rfcmirrorstatus["Historic"] = 70
    rfcmirrorstatus["Unknown"] = 80
    rfcstatuskeys = rfcmirrorstatus.keys()
    rfcstatuskeys.sort(cmp=lambda x,y: cmp(rfcmirrorstatus[x], rfcmirrorstatus[y]))
    # Count number RFCs in each status and fill in the promil and procent
    # fields to the table.
    rfcstatus = [ { "name" : s, "count" : (rfcmirror.filter(current_status=s).count()) } for s in rfcstatuskeys ]
    for s in rfcstatus:
       s["promil"] = s["count"] * 1000 / rfccount
       s["procent"] = s["count"] * 100 / rfccount

    # Find the minimum and maximum publication year from the rfc set
    minyear = rfcmirror.aggregate(Min('rfc_published_date')).values()[0].year
    maxyear = rfcmirror.aggregate(Max('rfc_published_date')).values()[0].year

    # Find the number of RFCs published in those years, and fill in the promil
    # and procent fields to the table.
    rfcyears = [ { "year" : y, "count" : rfcmirror.filter(rfc_published_date__gte = datetime(y, 1, 1), rfc_published_date__lte = datetime(y, 12, 31, 23, 59, 59)).count() } for y in range(minyear, maxyear)]
    for s in rfcyears:
       s["promil"] = s["count"] * 1000 / rfccount
       s["procent"] = s["count"] * 100 / rfccount

    # Create status / year table
    rfcstatusyears = [ [ { "year" : y, "name" : s, "count" : rfcmirror.filter(rfc_published_date__gte = datetime(y, 1, 1), rfc_published_date__lte = datetime(y, 12, 31, 23, 59, 59), current_status=s).count() } for s in rfcstatuskeys ] for y in range(minyear, maxyear) ]

    # Show the final page
    return render("stats/rfcstat.html",
	{
	   "name" : name,
	   "rfcstatus" : rfcstatus,
	   "rfcyears" : rfcyears,
	   "rfc" : rfcs,
	   "rfcmirrorstatus" : rfcstatuskeys,
	   "rfcstatusyears" : rfcstatusyears
	}, context_instance=RequestContext(request))
