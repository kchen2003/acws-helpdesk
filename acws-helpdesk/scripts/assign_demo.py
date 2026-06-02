from helpdesk.models import Ticket
from django.contrib.auth import get_user_model

User = get_user_model()

demo_tickets = [
    ("Printer offline", "Printer on 3rd floor not responding.", "Eve", "eve@example.com", "alice", Ticket.STATUS_ASSIGNED),
    ("Email bounce", "External emails bouncing for multiple recipients.", "Frank", "frank@example.com", "bob", Ticket.STATUS_IN_PROGRESS),
    ("Laptop battery issue", "Battery not charging; adapter OK.", "Grace", "grace@example.com", "carol", Ticket.STATUS_ASSIGNED),
]

created = []
for title, desc, submitter, contact, assignee_username, status in demo_tickets:
    assignee = User.objects.filter(username=assignee_username).first()
    t = Ticket.objects.create(
        title=title,
        description=desc,
        submitter_name=submitter,
        contact_info=contact,
        assigned_to=assignee,
        status=status,
    )
    created.append((t.pk, assignee_username if assignee else None))
    print("CREATED", t.pk, "assigned_to", assignee_username)

print('DONE: created', len(created), 'tickets')
