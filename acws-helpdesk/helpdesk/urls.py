from django.urls import path
from django.views.generic.base import RedirectView
from . import views

app_name = "helpdesk"
urlpatterns = [
    path("", views.TicketListView.as_view(), name="ticket_list"),
    path("tickets/create/", views.TicketCreateView.as_view(), name="ticket_create"),
    # convenience redirect: /tickets/ -> ticket list at /
    path("tickets/", RedirectView.as_view(pattern_name='helpdesk:ticket_list', permanent=False)),
    path("tickets/<int:pk>/", views.TicketDetailView.as_view(), name="ticket_detail"),
    path("tickets/<int:pk>/assign/", views.assign_ticket, name="ticket_assign"),
    path("tickets/<int:pk>/update/", views.add_update, name="ticket_add_update"),
    path("members/", views.TeamMemberListView.as_view(), name="member_list"),
    path("members/create/", views.TeamMemberCreateView.as_view(), name="member_create"),
    path("search/", views.ticket_search, name="ticket_search"),
]
