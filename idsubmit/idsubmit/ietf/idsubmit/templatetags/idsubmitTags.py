from django.template import Library

register = Library()

@register.simple_tag
def get_bgColor_Code(meta_data_errors, keyName):
    isError = meta_data_errors.get(keyName, False)
    
    if isError:
        return '#ffaaaa'
    else:
        return '#ddddff'

