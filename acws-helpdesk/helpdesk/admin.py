from django.contrib import admin
from django import forms
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.urls import reverse
from .models import Ticket, TicketUpdate, TeamMember, HelpDeskUser
from django.contrib import messages
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin


class TeamMemberAddForm(forms.ModelForm):
    username = forms.CharField(required=True, label='Account name')
    password1 = forms.CharField(required=False, widget=forms.PasswordInput, label='Password')
    password2 = forms.CharField(required=False, widget=forms.PasswordInput, label='Verify password')

    class Meta:
        model = TeamMember
        fields = ["is_manager", "phone"]

    # ensure admin renders exactly in this order
    field_order = ['username', 'password1', 'password2', 'is_manager', 'phone']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username and User.objects.filter(username=username).exists():
            raise forms.ValidationError('A user with that account name already exists.')
        return username

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 or p2:
            if p1 != p2:
                raise forms.ValidationError("The two password fields didn't match.")
        return cleaned



@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "release_version", "status", "assigned_to", "created_at")
    list_filter = ("status",)
    search_fields = ("title", "description", "submitter_name", "contact_info", "release_version")

@admin.register(TicketUpdate)
class TicketUpdateAdmin(admin.ModelAdmin):
    list_display = ("ticket", "author", "created_at", "status_after")
    search_fields = ("note",)

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ("user_link", "phone", "is_manager")
    search_fields = ("user__username", "user__first_name", "user__last_name", "phone")

    def get_form(self, request, obj=None, **kwargs):
        # For the add view, return our custom form and enforce field order
        if obj is None:
            form = TeamMemberAddForm
            from collections import OrderedDict
            desired = ['username', 'password1', 'password2', 'is_manager', 'phone']
            # build an ordered mapping of base_fields in desired order
            base = form.base_fields
            new = OrderedDict()
            for name in desired:
                if name in base:
                    new[name] = base[name]
            # include any remaining fields after
            for name, field in base.items():
                if name not in new:
                    new[name] = field
            form.base_fields = new
            return form
        form = super().get_form(request, obj, **kwargs)
        # allow password reset on change form
        form.base_fields['password'] = forms.CharField(required=False, widget=forms.PasswordInput, help_text='Set or reset the user password (leave empty to keep current)')
        return form

    def save_model(self, request, obj, form, change):
        if not change:
            username = form.cleaned_data.get('username')
            pwd = form.cleaned_data.get('password1')
            user = User.objects.create(username=username)
            if pwd:
                user.set_password(pwd)
            else:
                user.set_unusable_password()
            user.save()
            # The post_save signal for User may have already created a TeamMember
            existing = TeamMember.objects.filter(user=user).first()
            if existing:
                # update the existing TeamMember instead of creating a duplicate
                existing.phone = getattr(obj, 'phone', '')
                existing.is_manager = getattr(obj, 'is_manager', False)
                existing.save()
                # ensure admin continues to treat this as the saved object
                obj.pk = existing.pk
                obj.user = user
                super().save_model(request, obj, form, change)
            else:
                obj.user = user
                super().save_model(request, obj, form, change)
        else:
            # updating an existing TeamMember: allow resetting password
            pwd = form.cleaned_data.get('password')
            if pwd:
                user = obj.user
                user.set_password(pwd)
                user.save()
            super().save_model(request, obj, form, change)

    def user_link(self, obj):
        if obj.user_id:
            url = reverse('admin:helpdesk_helpdeskuser_change', args=(obj.user_id,))
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        return '-'
    user_link.short_description = 'User'
    user_link.admin_order_field = 'user__username'


# Add a bulk admin action to the built-in User admin to ensure TeamMember records
# exist for selected users.
def create_teammembers(modeladmin, request, queryset):
    created = 0
    for user in queryset:
        tm, flag = TeamMember.objects.get_or_create(user=user)
        if flag:
            created += 1
    messages.info(request, f"Created {created} TeamMember(s) and verified {queryset.count()-created} existing.")


# Re-register the User admin to add our action — but surface it under helpdesk
from django.contrib.auth.models import Group

try:
    admin.site.unregister(User)
except Exception:
    pass

try:
    admin.site.unregister(Group)
except Exception:
    pass


class CustomUserAdmin(AuthUserAdmin):
    actions = AuthUserAdmin.actions or []
    actions = list(actions) + [create_teammembers]


admin.site.register(HelpDeskUser, CustomUserAdmin)
