from django.shortcuts import redirect
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from django.contrib.sessions.exceptions import SessionInterrupted
from django.shortcuts import redirect

class AuthAndRoleRequiredMiddleware:
    """
    Middleware that requires a user to be authenticated to access certain pages
    and restricts access to specific URLs based on user role (e.g., only 'admin' can access /aiwave/admin/).
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # List of exact paths that require authentication
        exact_protected_paths = [
            reverse('aiwave-text-generator'),
            reverse('aiwave-code-generator'),
            reverse('aiwave-email-generator'),
            reverse('aiwave-blog-generator'),
            reverse('aiwave-description-generator'),
            reverse('aiwave-summary-generator'),
            reverse('aiwave-blog-create'),
            reverse('aiwave-profile-details'),
            reverse('aiwave-chat-export'),
            reverse('aiwave-sessions-page'),

            # Add more exact protected paths as needed
        ]
        # List of path prefixes that require authentication
        prefix_protected_paths = [
            '/aiwave/admin/',
            'blog/delete/<int:pk>/',
            # Add more protected prefixes as needed
        ]

        # Normalize the request path for robust comparison
        normalized_request_path = request.path.rstrip('/')
        normalized_exact_protected_paths = [p.rstrip('/') for p in exact_protected_paths]

        # Check if the current path is protected
        is_protected_path = (
            normalized_request_path in normalized_exact_protected_paths or
            any(request.path.startswith(prefix) for prefix in prefix_protected_paths)
        )

        # If user is not authenticated and trying to access a protected page
        if is_protected_path and not request.user.is_authenticated:
            login_url = reverse('aiwave-signin')
            return redirect(login_url)

        # Restrict /aiwave/admin/ to admin role, superuser, or staff only
        if request.path.startswith('/aiwave/admin/'):
            if not (request.user.is_superuser or request.user.is_staff or (hasattr(request.user, 'profile') and request.user.profile.role != 'user')):
                raise PermissionDenied("You do not have permission to access this page.")

        # You can add more role-based rules here

        return self.get_response(request)

from django.http import HttpResponsePermanentRedirect


class CanonicalHostMiddleware:
    """Redirect www.marketingtool.pro to marketingtool.pro (canonical apex).
    301 Permanent Redirect, preserves the full path and query string."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().lower()
        if host.startswith("www."):
            new_url = "https://" + host[4:] + request.get_full_path()
            return HttpResponsePermanentRedirect(new_url)
        return self.get_response(request)
