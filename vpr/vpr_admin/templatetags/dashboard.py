from django import template 

register = template.Library()


@register.inclusion_tag('dashboard_nav.html', takes_context=True)
def render_dashboard_nav(context):
    """docstring for render"""
    navItems = getNavigationItems(None)
    return {'navItems': navItems} 


def getNavigationItems(request):
    """ """
    BASE_URL = '/dashboard/'
    dashboard_items = (
        ('Overview', BASE_URL),
        ('API SERVICE', ''),
        ('Client Management', BASE_URL + 'clients/'),
        ('Statistics', BASE_URL + 'stats/'),
        ('SYSTEM', ''), 
        ('Processes', BASE_URL + 'processes/'),
        ('Resource Usages', BASE_URL + 'resources/'),
        ('Database', 'database'),
        ('CONTENT', ''), 
        ('Materials', '-'),
        ('Other Content', '-'),
        ('Statistics', '-'),
        ('VP COMPONENTS', ''),
        ('VP Web', '-'),
        ('VP Repository', '-'),
        ('VP Transformer', '-'),
        ) 
    return dashboard_items


