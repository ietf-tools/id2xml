from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from models import FromBodies
from forms import FromBodiesForm

def add_liaison(request):
    """ 
    Displays the add liaisons form for models.FromBodies

    Shows a list of existing records and allows user to add new records to :model:`models.FromBodies`
    
    Name field validation

    * stripped of leading and trailing spaces
    * checks to see the name doesn't already exist in the dbase, case insensitive
    * allows only alphanumeric, spaces and '-', '.', '/' characters

    **Templates:**

    * ``liaison/add_liaisons.html``

    **Variables:**

    * ``from_bodies : query set of FromBodies where poc = 0 or poc = NULL``
    * ``form : an instance of FromBodiesForm``


    """
    if request.method == 'POST':
        form = FromBodiesForm(request.POST)
        if form.is_valid():
            # hard coding defaults
            # this would be unnecessary if defaults can be defined in the model
            # "poc" field is absent (NULL), which is allowed by the model
            name = form.cleaned_data['name']
            f = FromBodies(body_name=name,
                    is_liaison_manager=False,
                    other_sdo='1',
                    email_priority='1')
            f.save()
            # we are expecting anonymous users for this view
            # cannot use message_set with anonymous users so need redirect
            if request.user.is_authenticated():
                request.user.message_set.create(message="New Liaison, %s, added successfully!" % name)
            else:
                messages.success(request, 'New Liaison, %s, added successfully!' % name)
                # form.reset()
            url = reverse('sec.liaison.views.add_liaison')
            return HttpResponseRedirect(url)
    else:
        form = FromBodiesForm()
    # only show those records where poc=0 or poc=NULL
    from_bodies = FromBodies.objects.filter(Q(poc__isnull=True) | Q(poc=0))
    return render_to_response(
        "liaison/add_liaison.html",
        {'from_bodies' : from_bodies, 'form': form, },
        RequestContext(request, {}),
    )
