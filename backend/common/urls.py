from django.urls import path
from . import views

urlpatterns = [
    # General endpoints
    path('services/', views.ServiceListView.as_view(), name='service-list'),
    path('services/<int:pk>/', views.ServiceDetailView.as_view(), name='service-detail'),
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('categories/<int:pk>/', views.CategoryDetailView.as_view(), name='category-detail'),
    path('business-settings/', views.BusinessSettingsView.as_view(), name='business-settings'),
    path('business-hours/', views.BusinessHoursListView.as_view(), name='business-hours-list'),
]
