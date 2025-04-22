import os
import logging
from typing import Optional
from django.conf import settings
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

logger = logging.getLogger(__name__)

# Get Twilio credentials from settings
TWILIO_ACCOUNT_SID = settings.TWILIO_ACCOUNT_SID
TWILIO_AUTH_TOKEN = settings.TWILIO_AUTH_TOKEN
TWILIO_PHONE_NUMBER = settings.TWILIO_PHONE_NUMBER

def send_twilio_message(to_phone_number: str, message: str) -> Optional[str]:
    """
    Send an SMS message using Twilio.

    Args:
        to_phone_number: The recipient's phone number in E.164 format (e.g., +1XXXXXXXXXX)
        message: The message content to send

    Returns:
        str: The Twilio message SID if successful, None otherwise
    """
    # Validate Twilio credentials
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER]):
        logger.error("Missing Twilio credentials. Make sure TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER are set.")
        return None

    # Sanitize phone number if needed
    sanitized_phone = sanitize_phone_number(to_phone_number)

    try:
        # Initialize Twilio client
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        # Send the message
        twilio_message = client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=sanitized_phone
        )

        logger.info(f"SMS sent successfully to {sanitized_phone}, SID: {twilio_message.sid}")
        return twilio_message.sid

    except TwilioRestException as e:
        logger.error(f"Twilio error: {e.code} - {e.msg}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error sending SMS: {str(e)}")
        return None

def get_message_status(message_sid: str) -> Optional[str]:
    """
    Get the status of a sent SMS message.

    Args:
        message_sid: The Twilio message SID

    Returns:
        str: The message status if successful, None otherwise
    """
    # Validate Twilio credentials
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN]):
        logger.error("Missing Twilio credentials. Make sure TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN are set.")
        return None

    try:
        # Initialize Twilio client
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        # Get the message
        message = client.messages.get(message_sid).fetch()

        logger.info(f"SMS status for {message_sid}: {message.status}")
        return message.status

    except TwilioRestException as e:
        logger.error(f"Twilio error checking message status: {e.code} - {e.msg}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error checking message status: {str(e)}")
        return None

def sanitize_phone_number(phone_number: str) -> str:
    """
    Sanitize a phone number to ensure it's in E.164 format.

    Args:
        phone_number: The phone number to sanitize

    Returns:
        str: The sanitized phone number
    """
    # Remove any non-digit characters
    digits_only = ''.join(filter(str.isdigit, phone_number))

    # If the number doesn't start with a '+', add it
    if not phone_number.startswith('+'):
        # If it's a US number (10 digits) without country code, add +1
        if len(digits_only) == 10:
            return f"+1{digits_only}"
        # If it already has a country code (>10 digits), add a +
        elif len(digits_only) > 10:
            return f"+{digits_only}"

    # If it already has a '+', return it as is
    return phone_number

def is_twilio_configured() -> bool:
    """
    Check if Twilio is properly configured.

    Returns:
        bool: True if Twilio is configured, False otherwise
    """
    return all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER])