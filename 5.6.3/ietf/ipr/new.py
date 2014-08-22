# Copyright The IETF Trust 2007, All Rights Reserved

import re, datetime

from django.shortcuts import render_to_response as render, get_object_or_404
from django.template import RequestContext
from django.http import Http404
from django.conf import settings

from ietf.utils.log import log
from ietf.utils.mail import send_mail
from ietf.doc.models import Document, DocAlias
from ietf.ipr.forms import IprForm, UpdateForm
from ietf.ipr.models import IprDetail, IprDocAlias, IprContact, LICENSE_CHOICES, IprUpdate
from ietf.ipr.view_sections import section_table

# ----------------------------------------------------------------
# Form processing
# ----------------------------------------------------------------

def new(request, type, update=None, submitter=None):
    """Make a new IPR disclosure"""
    section_list = section_table[type].copy()
    section_list.update({"title":False, "new_intro":False, "form_intro":True,
        "form_submit":True, "form_legend": True, })

    # If we're POSTed, but we got passed a submitter, it was the
    # POST of the "get updater" form, so we don't want to validate
    # this one.  When we're posting *this* form, submitter is None,
    # even when updating.
    if request.method == 'POST' and not submitter:
        data = request.POST.copy()
        data["submitted_date"] = datetime.datetime.now().strftime("%Y-%m-%d")
        data["third_party"] = section_list["third_party"]
        data["generic"] = section_list["generic"]
        data["status"] = "0"
        data["comply"] = "1"
        
        # handle check boxes from section VII
        for src in ["hold", "ietf"]:
            if "%s_contact_is_submitter" % src in data:
                for subfield in ["name", "title", "department", "address1", "address2", "telephone", "fax", "email"]:
                    try:
                        data[ "subm_%s" % subfield ] = data[ "%s_%s" % (src,subfield) ]
                    except Exception:
                        pass
        
        form = IprForm(data)
        if form.is_valid():
            # Save data :
            #   IprDetail, IprUpdate, IprContact+, IprDocAlias+, IprNotification

            # Save IprDetail
            instance = form.save(commit=False)

            legal_name_genitive = data['legal_name'] + "'" if data['legal_name'].endswith('s') else data['legal_name'] + "'s"
            if type == "generic":
                instance.title = legal_name_genitive + " General License Statement" 
            elif type == "specific":
                data["ipr_summary"] = get_ipr_summary(form.cleaned_data)
                instance.title = legal_name_genitive + """ Statement about IPR related to %(ipr_summary)s""" % data
            elif type == "third-party":
                data["ipr_summary"] = get_ipr_summary(form.cleaned_data)
                ietf_name_genitive = data['ietf_name'] + "'" if data['ietf_name'].endswith('s') else data['ietf_name'] + "'s"
                instance.title = ietf_name_genitive + """ Statement about IPR related to %(ipr_summary)s belonging to %(legal_name)s""" % data

            # A long document list can create a too-long title;
            # saving a too-long title raises an exception,
            # so prevent truncation in the database layer by
            # performing it explicitly.
            if len(instance.title) > 255:
                instance.title = instance.title[:252] + "..."

            instance.save()

            if update:
                updater = IprUpdate(ipr=instance, updated=update, status_to_be=1, processed=0)
                updater.save()
            contact_type = {"hold":1, "ietf":2, "subm": 3}

            # Save IprContact(s)
            for prefix in ["hold", "ietf", "subm"]:
#                cdata = {"ipr": instance.ipr_id, "contact_type":contact_type[prefix]}
                cdata = {"ipr": instance, "contact_type":contact_type[prefix]}
                for item in data:
                    if item.startswith(prefix+"_"):
                        cdata[item[5:]] = data[item]
                try:
                    del cdata["contact_is_submitter"]
                except KeyError:
                    pass
                contact = IprContact(**dict([(str(a),b) for a,b in cdata.items()]))
                contact.save()
                # store this contact in the instance for the email
                # similar to what views.show() does
                if   prefix == "hold":
                    instance.holder_contact = contact
                elif prefix == "ietf":
                    instance.ietf_contact = contact
                elif prefix == "subm":
                    instance.submitter = contact
#                contact = ContactForm(cdata)
#                if contact.is_valid():
#                    contact.save()
#                else:
#                    log("Invalid contact: %s" % contact)

            # Save draft links
            for draft in form.cleaned_data["draftlist"].split():
                name = draft[:-3]
                rev = draft[-2:]

                IprDocAlias.objects.create(
                    doc_alias=DocAlias.objects.get(name=name),
                    ipr=instance,
                    rev=rev)

            for rfcnum in form.cleaned_data["rfclist"].split():
                IprDocAlias.objects.create(
                    doc_alias=DocAlias.objects.get(name="rfc%s" % int(rfcnum)),
                    ipr=instance,
                    rev="")

            send_mail(request, settings.IPR_EMAIL_TO, ('IPR Submitter App', 'ietf-ipr@ietf.org'), 'New IPR Submission Notification', "ipr/new_update_email.txt", {"ipr": instance, "update": update})
            return render("ipr/submitted.html", {"update": update}, context_instance=RequestContext(request))
        else:
            if 'ietf_contact_is_submitter' in data:
                form.ietf_contact_is_submitter_checked = True
            if 'hold_contact_is_submitter' in data:
                form.hold_contact_is_submitter_checked = True

            for error in form.errors:
                log("Form error for field: %s: %s"%(error, form.errors[error]))
            # Fall through, and let the partially bound form, with error
            # indications, be rendered again.
            pass
    else:
        if update:
            form = IprForm(initial=update.__dict__)
        else:
            form = IprForm()
        form.unbound_form = True

    # log(dir(form.ietf_contact_is_submitter))
    return render("ipr/details_edit.html", {"ipr": form, "section_list":section_list}, context_instance=RequestContext(request))

def update(request, ipr_id=None):
    """Update a specific IPR disclosure"""
    ipr = get_object_or_404(IprDetail, ipr_id=ipr_id)
    if not ipr.status in [1,3]:
        raise Http404
    type = "specific"
    if ipr.generic:
        type = "generic"
    if ipr.third_party:
        type = "third-party"
    
    # We're either asking for initial permission or we're in
    # the general ipr form.  If the POST argument has the first
    # field of the ipr form, then we must be dealing with that,
    # so just pass through - otherwise, collect the updater's
    # info first.
    submitter = None
    #if not(request.POST.has_key('legal_name')):
        # class UpdateForm...  moved to forms.py
                
    if request.method == 'POST':
        form = UpdateForm(request.POST)
    else:
        form = UpdateForm()

    if not(form.is_valid()):
        for error in form.errors:
            log("Form error for field: %s: %s"%(error, form.errors[error]))
        return render("ipr/update.html", {"form": form, "ipr": ipr, "type": type}, context_instance=RequestContext(request))
    else:
        submitter = form.cleaned_data

    return new(request, type, ipr, submitter)


def get_ipr_summary(data):

    rfc_ipr = [ "RFC %s" % item for item in data["rfclist"].split() ]
    draft_ipr = data["draftlist"].split()
    ipr = rfc_ipr + draft_ipr
    if data["other_designations"]:
        ipr += [ data["other_designations"] ]

    if len(ipr) == 1:
        ipr = ipr[0]
    elif len(ipr) == 2:
        ipr = " and ".join(ipr)
    else:
        ipr = ", ".join(ipr[:-1]) + ", and " + ipr[-1]

    return ipr
