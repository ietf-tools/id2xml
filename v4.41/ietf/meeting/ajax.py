from django.utils import simplejson
from dajaxice.core import dajaxice_functions
from dajaxice.decorators import dajaxice_register


@dajaxice_register
def sayhello(request):
    return simplejson.dumps({'message':'Hello World'})
