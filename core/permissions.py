from rest_framework.permissions import BasePermission


class IsManager(BasePermission):
    """Allows access only to users with a manager profile."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and hasattr(request.user, "profile")
            and request.user.profile.role == "manager"
        )


class IsTeamMember(BasePermission):
    """Allows access to any authenticated user with a profile (member or manager)."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, "profile")
