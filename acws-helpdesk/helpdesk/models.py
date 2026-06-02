from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver


# Proxy model to surface the built-in User under the `helpdesk` app in admin
class HelpDeskUser(User):
    class Meta:
        proxy = True
        app_label = 'helpdesk'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

class TeamMember(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=50, blank=True)
    is_manager = models.BooleanField(default=False)

    def __str__(self):
        return self.user.get_full_name() or self.user.username

class Ticket(models.Model):
    STATUS_NEW = "NEW"
    STATUS_ASSIGNED = "ASSIGNED"
    STATUS_IN_PROGRESS = "IN_PROGRESS"
    STATUS_RESOLVED = "RESOLVED"
    STATUS_CLOSED = "CLOSED"
    STATUS_CHOICES = [
        (STATUS_NEW, "New"),
        (STATUS_ASSIGNED, "Assigned"),
        (STATUS_IN_PROGRESS, "In progress"),
        (STATUS_RESOLVED, "Resolved"),
        (STATUS_CLOSED, "Closed"),
    ]

    title = models.CharField(max_length=200)
    release_version = models.CharField(max_length=50, blank=True)
    description = models.TextField()
    submitter_name = models.CharField(max_length=200)
    contact_info = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW)
    assigned_to = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="assigned_tickets")

    def __str__(self):
        return f"#{self.id} {self.title}"

    def get_absolute_url(self):
        return reverse("helpdesk:ticket_detail", args=[self.pk])

class TicketUpdate(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="updates")
    author = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status_after = models.CharField(max_length=20, choices=Ticket.STATUS_CHOICES, null=True, blank=True)

    class Meta:
        ordering = ["created_at"]


@receiver(post_save, sender=User)
def ensure_team_member(sender, instance, created, **kwargs):
    """Automatically create an empty TeamMember when a User is created.

    This ensures users added via the Django admin (or elsewhere) show up
    in the Team list and can be edited to add phone/is_manager.
    """
    if created:
        TeamMember.objects.create(user=instance)
