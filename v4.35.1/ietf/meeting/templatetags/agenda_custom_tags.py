from django import template

register = template.Library()



# returns the a dictioary's value from it's key.
@register.filter(name='lookup')
def lookup(dict, index):
    if index in dict:
        return dict[index]
    return ''

@register.filter(name='get_id')
def get_id(room,day):
    date = ""
    print "getid"
    print " "
    from ietf.meeting.models import TimeSlot
    print "ROOM=", room
    print "date=", date
    x = TimeSlot.objects.filter(time=date)
    return "bla"

# returns the length of the value of a dict. 
# We are doing this to how long the title for the calendar should be. (this should return the number of time slots)
@register.filter(name='colWidth')
def get_col_width(dict, index):
    if index in dict:
        return len(dict[index])
    return 0
    
