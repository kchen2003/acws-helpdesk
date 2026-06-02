import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','acws_helpdesk.settings')
import django
django.setup()
from django.test import RequestFactory
from django.template.loader import render_to_string
from helpdesk.models import Ticket
from django.contrib.auth.models import AnonymousUser

rf = RequestFactory()
req = rf.get('/')
req.user = AnonymousUser()
html = render_to_string('helpdesk/ticket_list.html', {'object_list': Ticket.objects.all()}, request=req)
print('HAS_DATA_TOGGLE=', 'data-toggle="dropdown"' in html)
print('DROPDOWN_MENU_COUNT=', html.count('dropdown-menu'))
# Print the navbar snippet for inspection
start = html.find('<nav')
end = html.find('</nav>')
print(html[start:end+6])
