import datetime

from django.shortcuts import render

from ietf.doc.models import DocEvent

# Create your views here.

def index(request):
    return render(request,'stats/index.html',dict())

def docevents(request):
# TODO: quantize on a fixed day of week.
    num_weeks = 52 
    event_counts=dict()
    for week in range(num_weeks):
        for event in DocEvent.objects.filter(time__gt=datetime.datetime.now()-datetime.timedelta(weeks=week+1),time__lte=datetime.datetime.now()-datetime.timedelta(weeks=week)).filter(doc__type='draft'):
            if not event.type in event_counts:
                event_counts[event.type] = [0]*num_weeks
            event_counts[event.type][week] += 1
    for key in event_counts:
        event_counts[key].reverse()
    labels = range(51,-1,-1)

    return render(request,'stats/docevents.html',dict(event_counts=event_counts,labels=labels))

