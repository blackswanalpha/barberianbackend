from django.db import models
from django.contrib.auth.models import User

class Barber(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True)
    bio = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to='barber_profiles/', blank=True, null=True)
    years_of_experience = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.user.get_full_name() or self.user.username

class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    duration_minutes = models.PositiveIntegerField()
    image = models.ImageField(upload_to='service_images/', blank=True, null=True)

    def __str__(self):
        return self.name

class Appointment(models.Model):
    STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='client_appointments')
    barber = models.ForeignKey(Barber, on_delete=models.CASCADE, related_name='barber_appointments')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.client.get_full_name()} - {self.service.name} with {self.barber} on {self.date} at {self.start_time}"
