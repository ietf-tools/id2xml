from django.template import loader, Context
from django.http import HttpResponse

def default(request):
    t = loader.get_template("ipr/ipr_disclosure.html")
    return HttpResponse(t.render(Context()))

