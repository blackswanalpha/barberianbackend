import os
import logging
import sys
from typing import Optional
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content

logger = logging.getLogger(__name__)

# Get SendGrid API key from environment variable
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')

def send_email(
    to_email: str,
    from_email: str,
    subject: str,
    text_content: Optional[str] = None,
    html_content: Optional[str] = None
) -> bool:
    """
    Send an email using SendGrid.
    
    Args:
        to_email: Recipient's email address
        from_email: Sender's email address
        subject: Email subject
        text_content: Plain text content (optional if html_content is provided)
        html_content: HTML content (optional if text_content is provided)
        
    Returns:
        bool: True if the email was sent successfully, False otherwise
    """
    # Validate SendGrid API key
    if not SENDGRID_API_KEY:
        logger.error("Missing SendGrid API key. Make sure SENDGRID_API_KEY is set.")
        return False
    
    # Ensure at least one content type is provided
    if not text_content and not html_content:
        logger.error("Either text_content or html_content must be provided.")
        return False
    
    try:
        # Initialize SendGrid client
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        
        # Create email message
        message = Mail(
            from_email=Email(from_email),
            to_emails=To(to_email),
            subject=subject
        )
        
        # Add content based on provided parameters
        if html_content:
            message.content = Content("text/html", html_content)
        elif text_content:
            message.content = Content("text/plain", text_content)
        
        # Send the email
        response = sg.send(message)
        
        # Check response status
        if 200 <= response.status_code < 300:
            logger.info(f"Email sent successfully to {to_email}")
            return True
        else:
            logger.error(f"SendGrid API error: {response.status_code} - {response.body}")
            return False
    
    except Exception as e:
        logger.error(f"Unexpected error sending email: {str(e)}")
        return False

def is_sendgrid_configured() -> bool:
    """
    Check if SendGrid is properly configured.
    
    Returns:
        bool: True if SendGrid is configured, False otherwise
    """
    return bool(SENDGRID_API_KEY)

def send_appointment_email(
    to_email: str,
    from_email: str,
    appointment_type: str,
    client_name: str,
    staff_name: str,
    service_name: str,
    appointment_time: str,
    additional_info: Optional[str] = None
) -> bool:
    """
    Send an appointment-related email using SendGrid.
    
    Args:
        to_email: Recipient's email address
        from_email: Sender's email address
        appointment_type: Type of appointment email (e.g., 'confirmation', 'cancellation')
        client_name: Name of the client
        staff_name: Name of the staff member
        service_name: Name of the service
        appointment_time: Formatted appointment time string
        additional_info: Any additional information to include (optional)
        
    Returns:
        bool: True if the email was sent successfully, False otherwise
    """
    # Set up email subject based on appointment type
    subject_mapping = {
        'confirmation': f"Appointment Confirmation - {service_name}",
        'cancellation': "Appointment Cancelled",
        'rescheduled': "Appointment Rescheduled",
        'reminder': "Appointment Reminder",
        'completed': "Thank You for Your Visit"
    }
    
    subject = subject_mapping.get(appointment_type, f"Appointment {appointment_type.title()}")
    
    # Create HTML content for the email
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #2c3e50; color: white; padding: 15px; text-align: center; }}
            .content {{ padding: 20px; background-color: #f9f9f9; }}
            .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #777; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Barberian Barber Shop</h1>
            </div>
            <div class="content">
    """
    
    # Add content based on appointment type
    if appointment_type == 'confirmation':
        html_content += f"""
                <h2>Appointment Confirmed</h2>
                <p>Dear {client_name},</p>
                <p>Your appointment has been confirmed with the following details:</p>
                <ul>
                    <li><strong>Service:</strong> {service_name}</li>
                    <li><strong>Barber:</strong> {staff_name}</li>
                    <li><strong>Date & Time:</strong> {appointment_time}</li>
                </ul>
                <p>We look forward to seeing you!</p>
        """
    elif appointment_type == 'cancellation':
        html_content += f"""
                <h2>Appointment Cancelled</h2>
                <p>Dear {client_name},</p>
                <p>Your appointment for {service_name} with {staff_name} on {appointment_time} has been cancelled.</p>
                <p>If you would like to reschedule, please visit our website or contact us directly.</p>
        """
    elif appointment_type == 'rescheduled':
        html_content += f"""
                <h2>Appointment Rescheduled</h2>
                <p>Dear {client_name},</p>
                <p>Your appointment has been rescheduled to the following:</p>
                <ul>
                    <li><strong>Service:</strong> {service_name}</li>
                    <li><strong>Barber:</strong> {staff_name}</li>
                    <li><strong>New Date & Time:</strong> {appointment_time}</li>
                </ul>
                <p>We look forward to seeing you at the new time!</p>
        """
    elif appointment_type == 'reminder':
        html_content += f"""
                <h2>Appointment Reminder</h2>
                <p>Dear {client_name},</p>
                <p>This is a friendly reminder about your upcoming appointment:</p>
                <ul>
                    <li><strong>Service:</strong> {service_name}</li>
                    <li><strong>Barber:</strong> {staff_name}</li>
                    <li><strong>Date & Time:</strong> {appointment_time}</li>
                </ul>
                <p>We look forward to seeing you soon!</p>
        """
    else:
        html_content += f"""
                <h2>Appointment Update</h2>
                <p>Dear {client_name},</p>
                <p>There has been an update to your appointment for {service_name} with {staff_name} on {appointment_time}.</p>
        """
    
    # Add additional info if provided
    if additional_info:
        html_content += f"""
                <p>{additional_info}</p>
        """
    
    # Complete the HTML
    html_content += """
            </div>
            <div class="footer">
                <p>© 2025 Barberian Barber Shop. All rights reserved.</p>
                <p>If you have any questions, please contact us.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Create plain text version
    text_content = f"""
    Barberian Barber Shop

    Dear {client_name},

    {"Your appointment has been confirmed" if appointment_type == 'confirmation' else
     "Your appointment has been cancelled" if appointment_type == 'cancellation' else
     "Your appointment has been rescheduled" if appointment_type == 'rescheduled' else
     "This is a friendly reminder about your upcoming appointment" if appointment_type == 'reminder' else
     "There has been an update to your appointment"}

    Service: {service_name}
    Barber: {staff_name}
    Date & Time: {appointment_time}

    {additional_info if additional_info else ""}

    {"We look forward to seeing you!" if appointment_type in ['confirmation', 'rescheduled', 'reminder'] else ""}

    © 2025 Barberian Barber Shop. All rights reserved.
    """
    
    # Send the email with both HTML and plain text content
    return send_email(
        to_email=to_email,
        from_email=from_email,
        subject=subject,
        text_content=text_content,
        html_content=html_content
    )