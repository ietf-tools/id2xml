import datetime

from django.shortcuts import render, get_object_or_404
from django.http import  Http404

from ietf.doc.models import DocEvent
from ietf.meeting.models import Meeting
from ietf.name.models import DocTypeName

# Create your views here.

def index(request):
    return render(request,'stats/index.html',dict())

def docevents(request,doctype,weeks=52):

    type = get_object_or_404(DocTypeName,slug=doctype)
    if not int(weeks) in range(1,157):
        print "Not happy with", weeks
        raise Http404

# TODO: quantize on a fixed day of week.
    now = datetime.datetime.now()
    num_weeks = int(weeks )
    event_counts=dict()
    for week in range(num_weeks):
        for event in DocEvent.objects.filter(time__gt=now-datetime.timedelta(weeks=week+1),time__lte=now-datetime.timedelta(weeks=week)).filter(doc__type=type):
            if not event.type in event_counts:
                event_counts[event.type] = [0]*num_weeks
            event_counts[event.type][week] += 1
    for key in event_counts:
        event_counts[key].reverse()
    labels = range(num_weeks-1,-1,-1)
    labels = ['%s'%label for label in labels]
    for mtg in Meeting.objects.filter(type='ietf',date__lte=now,date__gte=now-datetime.timedelta(weeks=num_weeks)):
        labels[num_weeks - int((now.date()-mtg.date).days/7) -1 ] = 'IETF %s'%mtg.number

    template = 'stats/docevents_draft.html' if type.slug=='draft' else 'stats/docevents_base.html'

    return render(request,template,dict(event_counts=event_counts,labels=labels,type=type))

