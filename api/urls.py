from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, BarberViewSet, ServiceViewSet, AppointmentViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'barbers', BarberViewSet)
router.register(r'services', ServiceViewSet)
router.register(r'appointments', AppointmentViewSet, basename='appointment')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls')),
]
