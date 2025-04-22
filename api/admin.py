from django.contrib import admin
from .models import Barber, Service, Appointment

@admin.register(Barber)
class BarberAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_full_name', 'phone_number', 'years_of_experience')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'phone_number')

    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    get_full_name.short_description = 'Name'

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'duration_minutes')
    search_fields = ('name', 'description')
    list_filter = ('duration_minutes',)

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'barber', 'service', 'date', 'start_time', 'status')
    list_filter = ('status', 'date')
    search_fields = ('client__username', 'barber__user__username', 'service__name')
    date_hierarchy = 'date'
