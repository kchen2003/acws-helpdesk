from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, DetailView
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from .models import Ticket, TicketUpdate, TeamMember
from .forms import TicketForm, AssignForm, TicketUpdateForm
from django.db.models import Q
from django.contrib import messages

class TicketListView(ListView):
    model = Ticket
    template_name = "helpdesk/ticket_list.html"
    paginate_by = 20
    ordering = ["-created_at"]
    
    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q', '')
        if q:
            qs = qs.filter(
                Q(title__icontains=q) |
                Q(description__icontains=q) |
                Q(submitter_name__icontains=q) |
                Q(contact_info__icontains=q) |
                Q(assigned_to__username__icontains=q)
            ).distinct()
        status = self.request.GET.get("status")
        if status:
            qs = qs.filter(status=status)
        # allow ordering via GET param `ordering`, validate against allowed fields
        ordering = self.request.GET.get('ordering', '')
        allowed = {"id", "release_version", "title", "status", "assigned_to__username", "created_at"}
        if ordering:
            desc = ordering.startswith('-')
            base = ordering[1:] if desc else ordering
            if base in allowed:
                qs = qs.order_by(('-' if desc else '') + base)
                return qs
        return qs.order_by(*self.ordering)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["current_status"] = self.request.GET.get("status", "")
        # expose current ordering and toggle values for list headers
        cur = self.request.GET.get('ordering', '') or self.ordering[0]
        ctx['current_ordering'] = cur
        headers = [
            ('number', 'id'),
            ('release', 'release_version'),
            ('title', 'title'),
            ('status', 'status'),
            ('assigned', 'assigned_to__username'),
            ('created', 'created_at'),
        ]
        toggles = {}
        for key, field in headers:
            if cur == field:
                toggles[key] = '-' + field
            elif cur == '-' + field:
                toggles[key] = field
            else:
                toggles[key] = field
        ctx['ordering_toggles'] = toggles
        return ctx

class TicketCreateView(CreateView):
    model = Ticket
    form_class = TicketForm
    template_name = "helpdesk/ticket_form.html"
    success_url = reverse_lazy("helpdesk:ticket_list")

class TicketDetailView(DetailView):
    model = Ticket
    template_name = "helpdesk/ticket_detail.html"

@login_required
def assign_ticket(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    try:
        if not request.user.teammember.is_manager:
            messages.error(request, "Permission denied")
            return redirect(ticket.get_absolute_url())
    except TeamMember.DoesNotExist:
        messages.error(request, "Permission denied")
        return redirect(ticket.get_absolute_url())

    if request.method == "POST":
        form = AssignForm(request.POST, instance=ticket)
        if form.is_valid():
            form.save()
            messages.success(request, "Ticket updated")
            return redirect("helpdesk:ticket_detail", pk=pk)
    else:
        form = AssignForm(instance=ticket)
    return render(request, "helpdesk/assign_form.html", {"form": form, "ticket": ticket})

@login_required
def add_update(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    if request.method == "POST":
        form = TicketUpdateForm(request.POST)
        if form.is_valid():
            upd = form.save(commit=False)
            upd.ticket = ticket
            upd.author = request.user
            upd.save()
            if upd.status_after:
                ticket.status = upd.status_after
                ticket.save()
            messages.success(request, "Update added")
            return redirect("helpdesk:ticket_detail", pk=pk)
    else:
        form = TicketUpdateForm()
    return render(request, "helpdesk/add_update.html", {"form": form, "ticket": ticket})

class TeamMemberListView(ListView):
    model = TeamMember
    template_name = "helpdesk/member_list.html"
    paginate_by = 50
    ordering = ["user__username"]

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q', '')
        if q:
            qs = qs.filter(
                Q(user__username__icontains=q) |
                Q(user__first_name__icontains=q) |
                Q(user__last_name__icontains=q) |
                Q(phone__icontains=q)
            ).distinct()
        # ordering via GET `ordering`
        ordering = self.request.GET.get('ordering', '')
        allowed = {"user__username", "user__first_name", "user__last_name", "phone", "is_manager"}
        if ordering:
            desc = ordering.startswith('-')
            base = ordering[1:] if desc else ordering
            if base in allowed:
                qs = qs.order_by(('-' if desc else '') + base)
                return qs
        return qs.order_by(*self.ordering)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        cur = self.request.GET.get('ordering', '') or self.ordering[0]
        ctx['current_ordering'] = cur
        headers = [
            ('user', 'user__username'),
            ('phone', 'phone'),
            ('manager', 'is_manager'),
        ]
        toggles = {}
        for key, field in headers:
            if cur == field:
                toggles[key] = '-' + field
            elif cur == '-' + field:
                toggles[key] = field
            else:
                toggles[key] = field
        ctx['ordering_toggles'] = toggles
        return ctx
        return qs

class TeamMemberCreateView(CreateView):
    model = TeamMember
    fields = ["user", "phone", "is_manager"]
    template_name = "helpdesk/member_form.html"
    success_url = reverse_lazy("helpdesk:member_list")

def ticket_search(request):
    q = request.GET.get("q", "")
    tickets = Ticket.objects.none()
    if q:
        tickets = Ticket.objects.filter(
            Q(title__icontains=q) |
            Q(description__icontains=q) |
            Q(submitter_name__icontains=q) |
            Q(contact_info__icontains=q) |
            Q(assigned_to__username__icontains=q)
        ).distinct()
    return render(request, "helpdesk/search_results.html", {"tickets": tickets, "q": q})
