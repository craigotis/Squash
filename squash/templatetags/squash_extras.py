from django import template
from django.template import RequestContext
from django.template import context

register = template.Library()

########## START FILTERS ##########

@register.filter
def user_has_perm(obj, perm):
    return obj.has_perm(perm)
    
@register.filter
def is_not_None(val):
    return val is not None

@register.filter
def delete_session_var(request, var):
    if var in request.session:
        del request.session[var]
        
## HTML Output Filters ##

def bStr (bVar):
    if bVar:
        return 'True'
    else:
        return 'False'

@register.filter
def td_for_perm(user, perm):
    return td_for_bool(user_has_perm(user, perm));

@register.filter    
def td_for_bool(value):
    if value:
        td_class = 'green-bold';
    else:
        td_class = 'red-bold';
    return '<td class=\"' + td_class + '\">' + bStr(value) + '</td>'