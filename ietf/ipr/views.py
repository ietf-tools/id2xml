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

def show(request, ipr_id=None):
    assert ipr_id != None
    ipr = IprDetail.objects.filter(ipr_id__exact=ipr_id)[0]
    ipr.disclosure_type = get_disclosure_type(ipr)
    try:
        ipr.holder_contact = ipr.contact.filter(contact_type__exact=1)[0]    
    except IndexError:
        ipr.holder_contact = ""
    try:
        ipr.ietf_contact = ipr.contact.filter(contact_type__exact=2)[0]
    except IndexError:
        ipr.ietf_contact = ""
    try:
        ipr.submitter = ipr.contact.filter(contact_type__exact=3)[0]
    except IndexError:
        ipr.submitter = ""

    if   ipr.generic:
        return render("ipr/ipr_details_generic.html",  {"ipr": ipr})
    if ipr.third_party:
        return render("ipr/ipr_details_thirdpty.html", {"ipr": ipr})
    else:
        return render("ipr/ipr_details_specific.html", {"ipr": ipr})
        

def update(request, ipr_id=None):
    return show(request, ipr_id)

# ---- Helper functions ------------------------------------------------------

def get_disclosure_type(ipr):
    if   ipr.generic:
        assert not ipr.third_party
        return "Generic"
    if ipr.third_party:
        return "Third Party"
    else:
        return "Specific"
