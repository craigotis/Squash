import re

def is_empty(string):
    return string is None or len(string.strip()) == 0

def get_ref(request):
    referer = request.META.get('HTTP_REFERER')
    if not referer:
        return None

    # Break off the http if it exists, and cut into pieces
    referer = re.sub('^https?:\/\/', '', referer).split('/')

    # Put everything back together, excluding the hostname
    return '/' + '/'.join(referer[1:])