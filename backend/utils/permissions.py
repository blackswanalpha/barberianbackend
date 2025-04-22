from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    """
    Permission to only allow admin users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'admin'

class IsStaff(permissions.BasePermission):
    """
    Permission to only allow staff members.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'staff'

class IsClient(permissions.BasePermission):
    """
    Permission to only allow clients.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'client'

class IsAdminOrStaff(permissions.BasePermission):
    """
    Permission to allow admin users or staff members.
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            (request.user.role == 'admin' or request.user.role == 'staff')
        )

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission to only allow owners of an object or admin users.
    """
    def has_object_permission(self, request, view, obj):
        # Admin can see everything
        if request.user.role == 'admin':
            return True
        
        # Check if the object has a recipient/user attribute
        if hasattr(obj, 'recipient'):
            return obj.recipient == request.user
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'client'):
            return obj.client == request.user
        
        # Default to False
        return False

class IsAppointmentParticipant(permissions.BasePermission):
    """
    Permission to allow access to appointment participants (client, staff) or admin users.
    """
    def has_object_permission(self, request, view, obj):
        # Admin can see everything
        if request.user.role == 'admin':
            return True
        
        # Check if the user is a participant in the appointment
        return obj.client == request.user or obj.staff == request.user