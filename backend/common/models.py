from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, BaseUserManager
from dirtyfields import DirtyFieldsMixin

class CustomUserManager(BaseUserManager):
    """
    Custom user manager for the User model.
    """
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a user with the given email and password.
        """
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and save a superuser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    """
    Custom user model that uses email as the unique identifier.
    """
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('staff', 'Staff'),
        ('client', 'Client'),
    )

    username = None  # Remove username field
    email = models.EmailField('Email Address', unique=True)
    first_name = models.CharField('First Name', max_length=150)
    last_name = models.CharField('Last Name', max_length=150)
    phone_number = models.CharField('Phone Number', max_length=20, blank=True)
    role = models.CharField('Role', max_length=10, choices=ROLE_CHOICES, default='client')
    bio = models.TextField('Bio', blank=True)
    profile_image = models.URLField('Profile Image URL', blank=True)
    specialization = models.CharField('Specialization', max_length=100, blank=True)

    # Timestamps
    date_joined = models.DateTimeField('Date Joined', auto_now_add=True)
    last_login = models.DateTimeField('Last Login', null=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_staff_member(self):
        return self.role == 'staff'

    @property
    def is_client(self):
        return self.role == 'client'

class Category(models.Model):
    """
    Service categories, e.g., Haircut, Shave, Coloring, etc.
    """
    name = models.CharField('Name', max_length=100)
    description = models.TextField('Description', blank=True, null=True)
    icon = models.CharField('Icon', max_length=50, blank=True, null=True)

    # Timestamps
    created_at = models.DateTimeField('Created At', auto_now_add=True)
    updated_at = models.DateTimeField('Updated At', auto_now=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

class Service(models.Model):
    """
    Services offered by the barber shop, e.g., Haircut, Beard Trim, etc.
    """
    name = models.CharField('Name', max_length=100)
    description = models.TextField('Description', blank=True, null=True)
    price = models.DecimalField('Price', max_digits=10, decimal_places=2)
    duration = models.IntegerField('Duration (minutes)')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='services')
    is_active = models.BooleanField('Is Active', default=True)

    # Timestamps
    created_at = models.DateTimeField('Created At', auto_now_add=True)
    updated_at = models.DateTimeField('Updated At', auto_now=True)

    class Meta:
        verbose_name = 'Service'
        verbose_name_plural = 'Services'
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} (${self.price})"

class Appointment(DirtyFieldsMixin, models.Model):
    """
    Appointments made by clients with staff.
    """
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
        ('no_show', 'No Show'),
    )

    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='client_appointments')
    staff = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='staff_appointments')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='appointments')
    start_time = models.DateTimeField('Start Time')
    end_time = models.DateTimeField('End Time')
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField('Notes', blank=True, default='')

    # Timestamps
    created_at = models.DateTimeField('Created At', auto_now_add=True)
    updated_at = models.DateTimeField('Updated At', auto_now=True)

    class Meta:
        verbose_name = 'Appointment'
        verbose_name_plural = 'Appointments'
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.client.get_full_name()} with {self.staff.get_full_name()} on {self.start_time.strftime('%Y-%m-%d %H:%M')}"

    def save(self, *args, **kwargs):
        """
        Calculate the end time based on the service duration if not set.
        """
        if not self.end_time and self.start_time and self.service:
            duration_minutes = self.service.duration
            self.end_time = self.start_time + timezone.timedelta(minutes=duration_minutes)

        super().save(*args, **kwargs)

class BusinessHours(models.Model):
    """
    Business hours for each day of the week.
    """
    DAY_CHOICES = (
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    )

    day_of_week = models.IntegerField('Day of Week', choices=DAY_CHOICES, unique=True)
    is_open = models.BooleanField('Is Open', default=True)
    opening_time = models.TimeField('Opening Time', default='09:00')
    closing_time = models.TimeField('Closing Time', default='18:00')

    class Meta:
        verbose_name = 'Business Hours'
        verbose_name_plural = 'Business Hours'
        ordering = ['day_of_week']

    def __str__(self):
        return f"{self.get_day_of_week_display()}: {'Open' if self.is_open else 'Closed'} ({self.opening_time} - {self.closing_time})"

class Holiday(models.Model):
    """
    Holiday dates when the shop is closed.
    """
    name = models.CharField('Name', max_length=100)
    date = models.DateField('Date')
    is_recurring = models.BooleanField('Is Recurring', default=False, help_text='Recurring annually')

    class Meta:
        verbose_name = 'Holiday'
        verbose_name_plural = 'Holidays'
        ordering = ['date']

    def __str__(self):
        return f"{self.name} ({self.date.strftime('%Y-%m-%d')})"

class Schedule(models.Model):
    """
    Staff work schedule.
    """
    staff = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='schedules')
    date = models.DateField('Date')
    start_time = models.TimeField('Start Time')
    end_time = models.TimeField('End Time')
    is_available = models.BooleanField('Is Available', default=True)

    # Timestamps
    created_at = models.DateTimeField('Created At', auto_now_add=True)
    updated_at = models.DateTimeField('Updated At', auto_now=True)

    class Meta:
        verbose_name = 'Schedule'
        verbose_name_plural = 'Schedules'
        ordering = ['date', 'start_time']
        unique_together = ['staff', 'date', 'start_time']

    def __str__(self):
        return f"{self.staff.get_full_name()} - {self.date.strftime('%Y-%m-%d')} ({self.start_time} - {self.end_time})"

class BusinessSettings(models.Model):
    """
    General business settings.
    """
    business_name = models.CharField('Business Name', max_length=100, default='Barberian')
    address = models.TextField('Address', blank=True)
    phone = models.CharField('Phone', max_length=20, blank=True)
    email = models.EmailField('Email', blank=True)
    logo_url = models.URLField('Logo URL', blank=True)
    about = models.TextField('About', blank=True)

    # Social media links
    facebook_url = models.URLField('Facebook URL', blank=True)
    instagram_url = models.URLField('Instagram URL', blank=True)
    twitter_url = models.URLField('Twitter URL', blank=True)

    # Timestamps
    created_at = models.DateTimeField('Created At', auto_now_add=True)
    updated_at = models.DateTimeField('Updated At', auto_now=True)

    class Meta:
        verbose_name = 'Business Settings'
        verbose_name_plural = 'Business Settings'

    def __str__(self):
        return self.business_name

    def save(self, *args, **kwargs):
        """
        Ensure there is only one instance of Business Settings.
        """
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        """
        Load the singleton instance of Business Settings.
        """
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

class ServiceMedia(models.Model):
    """
    Media files (images/videos) for services
    """
    service = models.ForeignKey('Service', on_delete=models.CASCADE, related_name='media')
    file = models.FileField(upload_to='service_media/')
    file_type = models.CharField(max_length=10, choices=[('image', 'Image'), ('video', 'Video')])
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Service Media'
        verbose_name_plural = 'Service Media'
        ordering = ['-is_primary', 'created_at']

    def __str__(self):
        return f"{self.service.name} - {self.file_type}"