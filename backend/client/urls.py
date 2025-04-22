from django.urls import path
from . import views

app_name = 'client'

urlpatterns = [
    # Services
    path('services/', views.ServiceListView.as_view(), name='service-list'),
    path('services/<int:pk>/', views.ServiceDetailView.as_view(), name='service-detail'),

    # Categories
    path('categories/', views.CategoryListView.as_view(), name='category-list'),

    # Staff
    path('staff/', views.StaffListView.as_view(), name='staff-list'),
    path('staff/<int:pk>/', views.StaffDetailView.as_view(), name='staff-detail'),
    path('staff/<int:pk>/availability/', views.StaffAvailabilityView.as_view(), name='staff-availability'),

    # Appointments
    path('appointments/', views.ClientAppointmentListView.as_view(), name='appointment-list'),
    path('appointments/create/', views.ClientAppointmentCreateView.as_view(), name='appointment-create'),
    path('appointments/<int:pk>/', views.ClientAppointmentDetailView.as_view(), name='appointment-detail'),
    path('appointments/<int:pk>/cancel/', views.ClientAppointmentCancelView.as_view(), name='appointment-cancel'),

    # Booking
    path('booking/', views.BookingView.as_view(), name='booking'),

    # Profile
    path('profile/', views.ClientProfileView.as_view(), name='profile'),

    # Business Info
    path('business-info/', views.BusinessInfoView.as_view(), name='business-info'),
]