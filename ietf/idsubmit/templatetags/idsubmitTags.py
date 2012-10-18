from django.template import Library, Node

register = Library()

@register.simple_tag
def get_bgColor_Code(meta_data_errors, keyName):
    # meta_data_errors, keyName = token.split_contents()
    try:
        isError = meta_data_errors[keyName]
    except KeyError:
        isError = False
    
    if isError:
        return '#ffaaaa'
    else:
        return '#ddddff'

