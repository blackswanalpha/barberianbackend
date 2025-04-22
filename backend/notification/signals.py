from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from backend.common.models import Appointment
from .models import Notification, SMSNotification
from .utils import send_sms_notification

User = get_user_model()

# Appointment signals to create notifications

@receiver(post_save, sender=Appointment)
def appointment_post_save_handler(sender, instance, created, **kwargs):
    """
    Signal handler for appointment creation and updates.
    Creates notifications for both client and staff.
    """
    if created:
        # New appointment created
        create_appointment_created_notifications(instance)
    else:
        # Appointment updated
        create_appointment_updated_notifications(instance)

def create_appointment_created_notifications(appointment):
    """
    Create notifications for a new appointment.

    Args:
        appointment: The appointment instance that was created
    """
    # Notification for the client
    Notification.objects.create(
        recipient=appointment.client,
        title="New Appointment Booked",
        message=f"Your appointment with {appointment.staff.get_full_name()} for {appointment.service.name} on {appointment.start_time.strftime('%A, %B %d at %I:%M %p')} has been booked successfully.",
        notification_type="appointment_created",
        reference_id=str(appointment.id)
    )

    # Notification for the staff
    Notification.objects.create(
        recipient=appointment.staff,
        title="New Appointment Scheduled",
        message=f"A new appointment with {appointment.client.get_full_name()} for {appointment.service.name} on {appointment.start_time.strftime('%A, %B %d at %I:%M %p')} has been scheduled.",
        notification_type="appointment_created",
        reference_id=str(appointment.id)
    )

    # Send SMS if phone numbers are available
    if appointment.client.phone_number:
        send_sms_notification(
            recipient=appointment.client,
            phone_number=appointment.client.phone_number,
            message=f"Your appointment with {appointment.staff.get_full_name()} for {appointment.service.name} on {appointment.start_time.strftime('%A, %B %d at %I:%M %p')} has been booked successfully.",
            notification_type="appointment_created",
            reference_id=str(appointment.id)
        )

def create_appointment_updated_notifications(appointment):
    """
    Create notifications when an appointment is updated.

    Args:
        appointment: The appointment instance that was updated
    """
    # Check if status field was updated (most common change to track)
    if 'status' in appointment.get_dirty_fields():
        old_status = appointment.get_dirty_fields()['status']
        new_status = appointment.status

        if new_status == 'confirmed':
            create_appointment_confirmed_notifications(appointment)
        elif new_status == 'cancelled':
            create_appointment_cancelled_notifications(appointment, old_status)
        elif new_status == 'completed':
            create_appointment_completed_notifications(appointment)
        else:
            # Generic status update notification
            create_generic_appointment_update_notifications(appointment, old_status, new_status)
    elif 'start_time' in appointment.get_dirty_fields():
        # Appointment was rescheduled
        create_appointment_rescheduled_notifications(appointment)
    else:
        # Generic update notification
        create_generic_appointment_update_notifications(appointment)

def create_appointment_confirmed_notifications(appointment):
    """
    Create notifications when an appointment is confirmed.

    Args:
        appointment: The appointment instance that was confirmed
    """
    # Notification for the client
    Notification.objects.create(
        recipient=appointment.client,
        title="Appointment Confirmed",
        message=f"Your appointment with {appointment.staff.get_full_name()} for {appointment.service.name} on {appointment.start_time.strftime('%A, %B %d at %I:%M %p')} has been confirmed.",
        notification_type="appointment_updated",
        reference_id=str(appointment.id)
    )

    # Send SMS if phone number is available
    if appointment.client.phone_number:
        send_sms_notification(
            recipient=appointment.client,
            phone_number=appointment.client.phone_number,
            message=f"Your appointment with {appointment.staff.get_full_name()} for {appointment.service.name} on {appointment.start_time.strftime('%A, %B %d at %I:%M %p')} has been confirmed.",
            notification_type="appointment_updated",
            reference_id=str(appointment.id)
        )

def create_appointment_cancelled_notifications(appointment, old_status):
    """
    Create notifications when an appointment is cancelled.

    Args:
        appointment: The appointment instance that was cancelled
        old_status: The previous status of the appointment
    """
    # Notification for the client
    Notification.objects.create(
        recipient=appointment.client,
        title="Appointment Cancelled",
        message=f"Your appointment with {appointment.staff.get_full_name()} for {appointment.service.name} on {appointment.start_time.strftime('%A, %B %d at %I:%M %p')} has been cancelled.",
        notification_type="appointment_cancelled",
        reference_id=str(appointment.id)
    )

    # Notification for the staff (if the client cancelled it)
    Notification.objects.create(
        recipient=appointment.staff,
        title="Appointment Cancelled",
        message=f"The appointment with {appointment.client.get_full_name()} for {appointment.service.name} on {appointment.start_time.strftime('%A, %B %d at %I:%M %p')} has been cancelled.",
        notification_type="appointment_cancelled",
        reference_id=str(appointment.id)
    )

    # Send SMS if phone number is available and the appointment was previously confirmed
    if appointment.client.phone_number and old_status == 'confirmed':
        send_sms_notification(
            recipient=appointment.client,
            phone_number=appointment.client.phone_number,
            message=f"Your appointment with {appointment.staff.get_full_name()} for {appointment.service.name} on {appointment.start_time.strftime('%A, %B %d at %I:%M %p')} has been cancelled.",
            notification_type="appointment_cancelled",
            reference_id=str(appointment.id)
        )

def create_appointment_completed_notifications(appointment):
    """
    Create notifications when an appointment is marked as completed.

    Args:
        appointment: The appointment instance that was completed
    """
    # Notification for the client
    Notification.objects.create(
        recipient=appointment.client,
        title="Appointment Completed",
        message=f"Your appointment with {appointment.staff.get_full_name()} for {appointment.service.name} has been completed. We hope you enjoyed your visit!",
        notification_type="appointment_completed",
        reference_id=str(appointment.id)
    )

    # Send SMS if phone number is available
    if appointment.client.phone_number:
        send_sms_notification(
            recipient=appointment.client,
            phone_number=appointment.client.phone_number,
            message=f"Thank you for visiting Barberian! Your appointment with {appointment.staff.get_full_name()} has been completed. We hope to see you again soon!",
            notification_type="appointment_completed",
            reference_id=str(appointment.id)
        )

def create_appointment_rescheduled_notifications(appointment):
    """
    Create notifications when an appointment is rescheduled.

    Args:
        appointment: The appointment instance that was rescheduled
    """
    # Notification for the client
    Notification.objects.create(
        recipient=appointment.client,
        title="Appointment Rescheduled",
        message=f"Your appointment with {appointment.staff.get_full_name()} for {appointment.service.name} has been rescheduled to {appointment.start_time.strftime('%A, %B %d at %I:%M %p')}.",
        notification_type="appointment_updated",
        reference_id=str(appointment.id)
    )

    # Notification for the staff
    Notification.objects.create(
        recipient=appointment.staff,
        title="Appointment Rescheduled",
        message=f"The appointment with {appointment.client.get_full_name()} for {appointment.service.name} has been rescheduled to {appointment.start_time.strftime('%A, %B %d at %I:%M %p')}.",
        notification_type="appointment_updated",
        reference_id=str(appointment.id)
    )

    # Send SMS if phone number is available and appointment is confirmed
    if appointment.client.phone_number and appointment.status == 'confirmed':
        send_sms_notification(
            recipient=appointment.client,
            phone_number=appointment.client.phone_number,
            message=f"Your appointment with {appointment.staff.get_full_name()} for {appointment.service.name} has been rescheduled to {appointment.start_time.strftime('%A, %B %d at %I:%M %p')}.",
            notification_type="appointment_updated",
            reference_id=str(appointment.id)
        )

def create_generic_appointment_update_notifications(appointment, old_status=None, new_status=None):
    """
    Create generic notifications when an appointment is updated.

    Args:
        appointment: The appointment instance that was updated
        old_status: The previous status of the appointment (optional)
        new_status: The new status of the appointment (optional)
    """
    status_message = ""
    if old_status and new_status:
        status_message = f" Status changed from {old_status} to {new_status}."

    # Notification for the client
    Notification.objects.create(
        recipient=appointment.client,
        title="Appointment Updated",
        message=f"Your appointment with {appointment.staff.get_full_name()} for {appointment.service.name} on {appointment.start_time.strftime('%A, %B %d at %I:%M %p')} has been updated.{status_message}",
        notification_type="appointment_updated",
        reference_id=str(appointment.id)
    )

    # Send SMS only for significant updates and if phone number is available
    if appointment.client.phone_number and old_status and new_status and old_status != new_status:
        send_sms_notification(
            recipient=appointment.client,
            phone_number=appointment.client.phone_number,
            message=f"Your appointment with {appointment.staff.get_full_name()} for {appointment.service.name} on {appointment.start_time.strftime('%A, %B %d at %I:%M %p')} has been updated. Status: {new_status}.",
            notification_type="appointment_updated",
            reference_id=str(appointment.id)
        )