from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from barberian.auth.models import User
from django.db.models import Q

# Decorator to check if user is superuser
def superuser_required(view_func):
    decorated_view = user_passes_test(lambda u: u.is_superuser)(view_func)
    return decorated_view

@superuser_required
def dashboard_view(request):
    """
    Superuser dashboard with system stats and quick actions
    """
    # Get basic system stats
    total_users = User.objects.count()
    total_staff = User.objects.filter(role='staff').count()
    total_clients = User.objects.filter(role='client').count()
    
    context = {
        'total_users': total_users,
        'total_staff': total_staff,
        'total_clients': total_clients,
    }
    
    return render(request, 'administration/dashboard.html', context)

@superuser_required
def user_management_view(request):
    """
    Manage all users in the system
    """
    users = User.objects.all().order_by('-date_joined')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        users = users.filter(
            Q(email__icontains=search_query) | 
            Q(first_name__icontains=search_query) | 
            Q(last_name__icontains=search_query)
        )
    
    context = {
        'users': users,
        'search_query': search_query,
    }
    
    return render(request, 'administration/user_management.html', context)

@superuser_required
def staff_management_view(request):
    """
    Specifically manage staff members
    """
    # Get all staff members
    staff = User.objects.filter(role='staff').order_by('-date_joined')
    
    # Handle staff creation form submission
    if request.method == 'POST':
        # Extract form data
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')
        
        # Basic validation
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already in use')
        else:
            # Create new staff user
            new_staff = User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
                role='staff'
            )
            messages.success(request, f'Staff member {new_staff.get_full_name()} has been created successfully')
            return redirect('administration:staff_management')
    
    context = {
        'staff': staff,
    }
    
    return render(request, 'administration/staff_management.html', context)

@superuser_required
def system_settings_view(request):
    """
    Configure system-wide settings
    """
    # Get current settings
    
    # Handle settings update form submission
    if request.method == 'POST':
        # Update settings
        pass
    
    context = {
        # Add settings to context
    }
    
    return render(request, 'administration/system_settings.html', context)
