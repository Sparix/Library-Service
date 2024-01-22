from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOrCreate(BasePermission):
    """
    Custom permission class that allows write access only to admin users,
    while allowing read access to all users, including anonim user.
    """

    def has_permission(self, request, view):
        return bool(
            (
                    request.method in SAFE_METHODS
                    or request.method == "POST"
            )
            or (request.user and request.user.is_staff)
        )
