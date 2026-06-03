from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from helpdesk.models import TeamMember, Ticket

class Command(BaseCommand):
    help = 'Populates initial demo users, team members, and tickets for testing'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting database population...")
        
        User = get_user_model()

        # ==========================================
        # 1. POPULATE USERS & TEAM MEMBERS
        # ==========================================
        demo_users = [
            ("alice.anderson", "Alice", "Anderson", "alice@example.com"),
            ("bob.brown", "Bob", "Brown", "bob@example.com"),
            ("carol.clark", "Carol", "Clark", "carol@example.com"),
            ("david.chen", "David", "Chen", "david@example.com"),
            ("clayton.miller", "Clayton", "Miller", "clayton@example.com"),
            ("audrey.barry", "Audrey", "Barry", "audrey@example.com"),
            ("kevin.chen", "Kevin", "Chen", "kevin@example.com"),
          ]

        for username, first, last, email in demo_users:
            u = User.objects.filter(username=username).first()
            if not u:
                u = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=first,
                    last_name=last,
                    password="Welcome1!",
                )
                self.stdout.write(self.style.SUCCESS(f"CREATED user {u.username}"))
            else:
                self.stdout.write(f"EXISTS user {u.username}")

            tm = TeamMember.objects.filter(user=u).first()
            if not tm:
                tm = TeamMember.objects.create(
                    user=u,
                    phone=("555-0100" if username == "alice.anderson" else "555-0101" if username == "bob.brown" else "555-0102"),
                    is_manager=(username == "carol.clark"),
                )
                self.stdout.write(self.style.SUCCESS(f"CREATED TeamMember for {u.username} manager={tm.is_manager}"))
            else:
                self.stdout.write(f"EXISTS TeamMember for {u.username} manager={tm.is_manager}")

        # ==========================================
        # 2. POPULATE TICKETS
        # ==========================================
        self.stdout.write("\nPopulating demo tickets...")
        
        demo_tickets = [
            ("Printer offline", "Printer on 3rd floor not responding.", "Eve", "eve@example.com", "alice.anderson", Ticket.STATUS_ASSIGNED),
            ("Email bounce", "External emails bouncing for multiple recipients.", "Frank", "frank@example.com", "bob.brown", Ticket.STATUS_IN_PROGRESS),
            ("Laptop battery issue", "Battery not charging; adapter OK.", "Grace", "grace@example.com", "carol", Ticket.STATUS_ASSIGNED),
            ("Email bounce", "External emails bouncing for multiple recipients.", "Frank", "frank@example.com", "bob.brown", Ticket.STATUS_IN_PROGRESS),
            ("Password not working", "Working yesterday", "Dave", "dave@example.com", "kevin.chen", Ticket.STATUS_ASSIGNED),
            ("Missing Org field", "In item details", "Amy", "amy@example.com", "clayton.miller", Ticket.STATUS_NEW),
            ("Missing network cable", "Can't not be found", "Lily", "lily@example.com", "audrey.barry", Ticket.STATUS_RESOLVED),
        ]

        tickets_created_count = 0
        for title, desc, submitter, contact, assignee_username, status in demo_tickets:
            # Check if this specific ticket title already exists to prevent duplication
            if not Ticket.objects.filter(title=title).exists():
                assignee = User.objects.filter(username=assignee_username).first()
                t = Ticket.objects.create(
                    title=title,
                    description=desc,
                    submitter_name=submitter,
                    contact_info=contact,
                    assigned_to=assignee,
                    status=status,
                )
                tickets_created_count += 1
                self.stdout.write(self.style.SUCCESS(f"CREATED Ticket #{t.pk}: '{title}' assigned to {assignee_username}"))
            else:
                self.stdout.write(f"EXISTS Ticket with title: '{title}'")

        self.stdout.write(self.style.SUCCESS(f"\nDONE: Created {tickets_created_count} new tickets."))
        self.stdout.write(self.style.SUCCESS("Database successfully populated!"))