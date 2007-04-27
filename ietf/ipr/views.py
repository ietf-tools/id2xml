from models import IprDetail
from django.shortcuts import render_to_response as render

def default(request):
    return render("ipr/ipr_disclosure.html", {})

def updatelist(request):
    return list(request, 'ipr/ipr_update_list.html')

def showlist(request):
    return list(request, 'ipr/ipr_list.html')

def list(request, template):
    disclosures = IprDetail.objects.all()
    generic_disclosures  = disclosures.filter(status__in=[1,3], generic__exact=1)    
    specific_disclosures = disclosures.filter(status__in=[1,3], generic__exact=0, third_party__exact=0)
    thirdpty_disclosures = disclosures.filter(status__in=[1,3], generic__exact=0, third_party__exact=1)
    
    return render(template,
        {
            'generic_disclosures' : generic_disclosures.order_by(* ['-submitted_date', ] ),
            'specific_disclosures': specific_disclosures.order_by(* ['-submitted_date', ] ),
            'thirdpty_disclosures': thirdpty_disclosures.order_by(* ['-submitted_date', ] ),
        } )

