from django.contrib.auth import get_user_model
from helpdesk.models import TeamMember

User = get_user_model()

demo = [
    ("alice", "Alice", "Anderson", "alice@example.com"),
    ("bob", "Bob", "Brown", "bob@example.com"),
    ("carol", "Carol", "Clark", "carol@example.com"),
]

for username, first, last, email in demo:
    u = User.objects.filter(username=username).first()
    if not u:
        u = User.objects.create_user(
            username=username,
            email=email,
            first_name=first,
            last_name=last,
            password="DemoPass123!",
        )
        print("CREATED user", u.username)
    else:
        print("EXISTS user", u.username)

    tm = TeamMember.objects.filter(user=u).first()
    if not tm:
        tm = TeamMember.objects.create(
            user=u,
            phone=("555-0100" if username == "alice" else "555-0101" if username == "bob" else "555-0102"),
            is_manager=(username == "carol"),
        )
        print("CREATED TeamMember for", u.username, "manager=", tm.is_manager)
    else:
        print("EXISTS TeamMember for", u.username, "manager=", tm.is_manager)
