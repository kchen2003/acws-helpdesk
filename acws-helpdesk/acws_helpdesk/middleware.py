from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth.views import LoginView


class LoginRequiredMiddleware:
    """Require authentication for all views except a small whitelist.

    Exemptions include the login/logout URLs, admin, static and media files.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        login_url = settings.LOGIN_URL or "/accounts/login/"
        self.exempt_paths = (
            login_url,
            "/accounts/logout/",
            "/admin/",
            "/static/",
            "/media/",
            "/favicon.ico",
        )

    def __call__(self, request):
        path = request.path_info
        if not request.user.is_authenticated:
            for p in self.exempt_paths:
                if path.startswith(p):
                    return self.get_response(request)
            # If user hits root, render the login form at '/' instead of redirecting.
            if path == "/":
                view = LoginView.as_view(template_name="registration/login.html")
                response = view(request)
                # Ensure TemplateResponse is rendered before being returned
                if hasattr(response, "render"):
                    response = response.render()
                return response
            return redirect(f"{settings.LOGIN_URL}?next={request.path}")
        return self.get_response(request)
