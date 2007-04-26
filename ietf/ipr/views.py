from models import IprDetail
from django.shortcuts import render_to_response as render

def default(request):
    return render("ipr/ipr_disclosure.html", {})

def update(request):
    generic_disclosures = IprDetail.objects.filter(status__in=[1,3], generic__exact=1)
    specific_disclosures = IprDetail.objects.filter(status__in=[1,3], generic__exact=0, third_party__exact=0)
    thirdpty_disclosures = IprDetail.objects.filter(status__in=[1,3], generic__exact=0, third_party__exact=1)

    return render('ipr/ipr_update_list.html',
        {
            'generic_disclosures' : generic_disclosures.order_by(* ['-submitted_date', ] ),
            'specific_disclosures': specific_disclosures.order_by(* ['-submitted_date', ] ),
            'thirdpty_disclosures': thirdpty_disclosures.order_by(* ['-submitted_date', ] ),
        } )

