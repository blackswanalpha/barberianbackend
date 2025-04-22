import os
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta

from backend.common.models import Appointment
from .models import Notification, SMSNotification

# Import send_twilio_message from utils
from backend.utils.sms import send_twilio_message, get_message_status

User = get_user_model()

def send_notification(recipient, title, message, notification_type='system', reference_id=None):
    """
    Send an in-app notification to a user.

    Args:
        recipient: User instance to receive the notification
        title: Notification title
        message: Notification message
        notification_type: Type of notification (default: 'system')
        reference_id: Optional ID of the referenced object (e.g., appointment ID)

    Returns:
        Notification: The created notification instance
    """
    notification = Notification.objects.create(
        recipient=recipient,
        title=title,
        message=message,
        notification_type=notification_type,
        reference_id=reference_id
    )

    return notification

def send_sms_notification(recipient, phone_number, message, notification_type='system', reference_id=None):
    """
    Send an SMS notification to a user.

    Args:
        recipient: User instance to receive the notification (optional)
        phone_number: The phone number to send the SMS to
        message: SMS message content
        notification_type: Type of notification (default: 'system')
        reference_id: Optional ID of the referenced object (e.g., appointment ID)

    Returns:
        SMSNotification: The created SMS notification instance
        str: The Twilio message SID if successful, None otherwise
    """
    # Create the SMS notification record
    sms_notification = SMSNotification.objects.create(
        recipient=recipient,
        phone_number=phone_number,
        message=message,
        notification_type=notification_type,
        reference_id=reference_id,
        status='pending'
    )

    # Send the SMS via Twilio
    try:
        twilio_sid = send_twilio_message(
            to_phone_number=phone_number,
            message=message
        )

        if twilio_sid:
            # Update the SMS notification record with the Twilio SID
            sms_notification.twilio_sid = twilio_sid
            sms_notification.status = 'sent'
            sms_notification.save()
            return sms_notification, twilio_sid
        else:
            # Failed to get Twilio SID
            sms_notification.status = 'failed'
            sms_notification.error_message = "Failed to get Twilio SID"
            sms_notification.save()
            return sms_notification, None

    except Exception as e:
        # Log the error and update the SMS notification record
        sms_notification.status = 'failed'
        sms_notification.error_message = str(e)
        sms_notification.save()
        return sms_notification, None

def send_appointment_reminder(appointment, hours_before=24):
    """
    Send a reminder for an upcoming appointment.

    Args:
        appointment: The appointment to send a reminder for
        hours_before: Hours before the appointment to send the reminder

    Returns:
        tuple: (in-app notification, SMS notification) or None if reminder already sent
    """
    # Check if the appointment is confirmed
    if appointment.status != 'confirmed':
        return None

    # Calculate the reminder time
    now = datetime.now(appointment.start_time.tzinfo)
    reminder_time = appointment.start_time - timedelta(hours=hours_before)

    # Check if it's time to send the reminder
    if now < reminder_time:
        return None

    # Check if a reminder has already been sent
    existing_reminders = Notification.objects.filter(
        recipient=appointment.client,
        notification_type='appointment_reminder',
        reference_id=str(appointment.id),
        created_at__gte=reminder_time
    )

    if existing_reminders.exists():
        # Reminder already sent
        return None

    # Create the reminder notification
    notification = Notification.objects.create(
        recipient=appointment.client,
        title="Appointment Reminder",
        message=f"Reminder: You have an appointment with {appointment.staff.get_full_name()} for {appointment.service.name} tomorrow at {appointment.start_time.strftime('%I:%M %p')}.",
        notification_type='appointment_reminder',
        reference_id=str(appointment.id)
    )

    # Send SMS reminder if the client has a phone number
    sms_notification = None
    if appointment.client.phone_number:
        sms_notification, _ = send_sms_notification(
            recipient=appointment.client,
            phone_number=appointment.client.phone_number,
            message=f"Reminder: You have an appointment with {appointment.staff.get_full_name()} for {appointment.service.name} tomorrow at {appointment.start_time.strftime('%I:%M %p')}.",
            notification_type='appointment_reminder',
            reference_id=str(appointment.id)
        )

    return notification, sms_notification

def update_sms_status(sms_id=None, max_age_hours=24):
    """
    Update the status of SMS notifications from Twilio.

    Args:
        sms_id: Specific SMS notification ID to update (optional)
        max_age_hours: Maximum age in hours for SMS records to update

    Returns:
        dict: Summary of update results
    """
    results = {
        'updated': 0,
        'failed': 0,
        'total': 0,
    }

    if sms_id:
        # Update a specific SMS notification
        try:
            notification = SMSNotification.objects.get(pk=sms_id)
            results['total'] = 1

            if notification.twilio_sid:
                status = get_message_status(notification.twilio_sid)

                if status:
                    notification.status = status
                    notification.save()
                    results['updated'] += 1
                else:
                    results['failed'] += 1
            else:
                results['failed'] += 1

        except SMSNotification.DoesNotExist:
            results['failed'] += 1

    else:
        # Update all pending/sent SMS notifications within the specified age
        oldest_time = datetime.now() - timedelta(hours=max_age_hours)

        notifications = SMSNotification.objects.filter(
            twilio_sid__isnull=False,
            status__in=['pending', 'sent'],
            created_at__gte=oldest_time
        )

        results['total'] = notifications.count()

        for notification in notifications:
            try:
                status = get_message_status(notification.twilio_sid)

                if status:
                    notification.status = status
                    notification.save()
                    results['updated'] += 1
                else:
                    results['failed'] += 1

            except Exception as e:
                notification.error_message = str(e)
                notification.save()
                results['failed'] += 1

    return results

def send_appointment_reminders_batch(hours_before=24, batch_size=100):
    """
    Send reminders for all upcoming appointments in a batch.

    Args:
        hours_before: Hours before the appointment to send the reminder
        batch_size: Maximum number of reminders to send

    Returns:
        dict: Summary of reminder results
    """
    results = {
        'sent': 0,
        'failed': 0,
        'total': 0,
    }

    # Calculate the time range for sending reminders
    now = datetime.now()
    reminder_start = now
    reminder_end = now + timedelta(hours=hours_before)

    # Find appointments that need reminders
    appointments = Appointment.objects.filter(
        status='confirmed',
        start_time__gte=reminder_start,
        start_time__lte=reminder_end
    ).order_by('start_time')[:batch_size]

    results['total'] = appointments.count()

    # Send reminders for each appointment
    for appointment in appointments:
        try:
            reminder = send_appointment_reminder(appointment, hours_before)
            if reminder:
                results['sent'] += 1
            else:
                results['failed'] += 1
        except Exception as e:
            print(f"Error sending reminder for appointment {appointment.id}: {str(e)}")
            results['failed'] += 1

    return results

def send_email_notification(recipient, subject, message, from_email=None, html_message=None):
    """
    Send an email notification to a user.

    Args:
        recipient: User instance or email address to receive the notification
        subject: Email subject
        message: Email text content
        from_email: Sender email address (default: settings.DEFAULT_FROM_EMAIL)
        html_message: Optional HTML version of the message

    Returns:
        bool: True if the email was sent successfully, False otherwise
    """
    # Get the recipient email
    if isinstance(recipient, User):
        to_email = recipient.email
    else:
        to_email = recipient

    # Get the sender email
    if not from_email:
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@backend.com')

    # Send the email
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=[to_email],
            html_message=html_message,
            fail_silently=False
        )
        return True
    except Exception as e:
        print(f"Error sending email to {to_email}: {str(e)}")
        return False

# Appointment notification functions

def notify_appointment_created(appointment):
    """
    Send notifications for a new appointment.

    Args:
        appointment: The newly created appointment

    Returns:
        tuple: (client notification, staff notification, SMS notification)
    """
    # Format the appointment time
    appointment_time = appointment.start_time.strftime('%A, %B %d at %I:%M %p')

    # Create notification for the client
    client_notification = send_notification(
        recipient=appointment.client,
        title="New Appointment Booked",
        message=f"Your appointment with {appointment.staff.get_full_name()} for {appointment.service.name} on {appointment_time} has been booked successfully.",
        notification_type="appointment_created",
        reference_id=str(appointment.id)
    )

    # Create notification for the staff
    staff_notification = send_notification(
        recipient=appointment.staff,
        title="New Appointment Scheduled",
        message=f"A new appointment with {appointment.client.get_full_name()} for {appointment.service.name} on {appointment_time} has been scheduled.",
        notification_type="appointment_created",
        reference_id=str(appointment.id)
    )

    # Send SMS to the client if phone number is available
    sms_notification = None
    if appointment.client.phone_number:
        sms_notification, _ = send_sms_notification(
            recipient=appointment.client,
            phone_number=appointment.client.phone_number,
            message=f"Your appointment with {appointment.staff.get_full_name()} for {appointment.service.name} on {appointment_time} has been booked successfully.",
            notification_type="appointment_created",
            reference_id=str(appointment.id)
        )

    return client_notification, staff_notification, sms_notification

def notify_appointment_updated(appointment, updated_fields=None):
    """
    Send notifications for an updated appointment.

    Args:
        appointment: The updated appointment
        updated_fields: List of fields that were updated

    Returns:
        tuple: (client notification, staff notification, SMS notification)
    """
    # Format the appointment time
    appointment_time = appointment.start_time.strftime('%A, %B %d at %I:%M %p')

    # Create a message based on the updated fields
    if updated_fields and 'start_time' in updated_fields:
        client_message = f"Your appointment with {appointment.staff.get_full_name()} for {appointment.service.name} has been rescheduled to {appointment_time}."
        staff_message = f"The appointment with {appointment.client.get_full_name()} for {appointment.service.name} has been rescheduled to {appointment_time}."
        title = "Appointment Rescheduled"
    elif updated_fields and 'status' in updated_fields and appointment.status == 'confirmed':
        client_message = f"Your appointment with {appointment.staff.get_full_name()} for {appointment.service.name} on {appointment_time} has been confirmed."
        staff_message = client_message
        title = "Appointment Confirmed"
    else:
        client_message = f"Your appointment with {appointment.staff.get_full_name()} for {appointment.service.name} on {appointment_time} has been updated."
        staff_message = f"The appointment with {appointment.client.get_full_name()} for {appointment.service.name} on {appointment_time} has been updated."
        title = "Appointment Updated"

    # Create notification for the client
    client_notification = send_notification(
        recipient=appointment.client,
        title=title,
        message=client_message,
        notification_type="appointment_updated",
        reference_id=str(appointment.id)
    )

    # Create notification for the staff
    staff_notification = send_notification(
        recipient=appointment.staff,
        title=title,
        message=staff_message,
        notification_type="appointment_updated",
        reference_id=str(appointment.id)
    )

    # Send SMS to the client if phone number is available and it's a significant update
    sms_notification = None
    if appointment.client.phone_number and (
        (updated_fields and 'start_time' in updated_fields) or
        (updated_fields and 'status' in updated_fields and appointment.status == 'confirmed')
    ):
        sms_notification, _ = send_sms_notification(
            recipient=appointment.client,
            phone_number=appointment.client.phone_number,
            message=client_message,
            notification_type="appointment_updated",
            reference_id=str(appointment.id)
        )

    return client_notification, staff_notification, sms_notification

def notify_appointment_canceled(appointment):
    """
    Send notifications for a canceled appointment.

    Args:
        appointment: The canceled appointment

    Returns:
        tuple: (client notification, staff notification, SMS notification)
    """
    # Format the appointment time
    appointment_time = appointment.start_time.strftime('%A, %B %d at %I:%M %p')

    # Create notification for the client
    client_notification = send_notification(
        recipient=appointment.client,
        title="Appointment Cancelled",
        message=f"Your appointment with {appointment.staff.get_full_name()} for {appointment.service.name} on {appointment_time} has been cancelled.",
        notification_type="appointment_cancelled",
        reference_id=str(appointment.id)
    )

    # Create notification for the staff
    staff_notification = send_notification(
        recipient=appointment.staff,
        title="Appointment Cancelled",
        message=f"The appointment with {appointment.client.get_full_name()} for {appointment.service.name} on {appointment_time} has been cancelled.",
        notification_type="appointment_cancelled",
        reference_id=str(appointment.id)
    )

    # Send SMS to the client if phone number is available
    sms_notification = None
    if appointment.client.phone_number:
        sms_notification, _ = send_sms_notification(
            recipient=appointment.client,
            phone_number=appointment.client.phone_number,
            message=f"Your appointment with {appointment.staff.get_full_name()} for {appointment.service.name} on {appointment_time} has been cancelled.",
            notification_type="appointment_cancelled",
            reference_id=str(appointment.id)
        )

    return client_notification, staff_notification, sms_notification