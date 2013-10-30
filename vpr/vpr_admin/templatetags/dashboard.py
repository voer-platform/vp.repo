from django import template 

register = template.Library()


@register.inclusion_tag('dashboard_nav.html', takes_context=True)
def render_dashboard_nav(context):
    """docstring for render"""
    navItems = getNavigationItems(None)
    return {'navItems': navItems} 


def getNavigationItems(request):
    """ """
    dashboard_items = (
        ('Overview', adminURL()),
        ('API SERVICE', ''),
        ('Client Management', BASE_URL + 'clients/'),
        ('Active Tokens', BASE_URL + 'tokens/'),
        ('Records', BASE_URL + 'api-records/'),
        ('SYSTEM', ''), 
        ('Processes', adminURL('processes/')),
        ('Resource Usages', adminURL('resources/')),
        ('Database', adminURL('database')),
        ('CONTENT', ''), 
        ('Materials', adminURL('materials/')),
        ('Other Content', '-'),
        ('Statistics', '-'),
        ('VP COMPONENTS', ''),
        ('VP Web', '-'),
        ('VP Repository', '-'),
        ('VP Transformer', '-'),
        ) 
    return dashboard_items


def adminURL(path=''):
    BASE_URL = '/dashboard/'
    return BASE_URL + path
