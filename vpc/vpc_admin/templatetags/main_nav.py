from django import template

register = template.Library()


class DashboarNavBar(template.Node):
    """DashboardNavBar"""
    def __init__(self):
        pass
    def render(self, context):
        """docstring for render"""
        tpl = template.loader.get_template('dashboard_nav_bar.html')
        navItems = getNavigationItems(None)
        return tpl.render(Context({'navItems': 


def getNavigationItems(request):
    """ """
    BASE_URL = '/dashboard/'
    dashboard_items = {
        'Overview': BASE_URL,
        'API SERVICE': {
            'Client Management': BASE_URL + 'clients/',
            'Statistics': BASE_URL + 'stats/',
            },
        'SYSTEM': {
            'Processes': BASE_URL + 'processes/',
            'Resource Usages': BASE_URL + '',
            'Database': '',
            },
        'CONTENT MANAGEMENT': {
            'Materials': '',
            'Other Content': '',
            'Statistics': '',
            },
        'VP COMPONENTS': {
            'VP Web': '',
            'VP Core': '',
            'VP Transformer': '',
            },
        } 
    return dashboard_items
