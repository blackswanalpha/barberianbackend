from django.core.management.base import BaseCommand, CommandError
from barberian.utils.sms import send_twilio_message, is_twilio_configured
from barberian.notification.models import SMSNotification

class Command(BaseCommand):
    help = 'Send an SMS message to a specified phone number'

    def add_arguments(self, parser):
        parser.add_argument('phone_number', type=str, help='The recipient phone number in E.164 format (e.g., +1XXXXXXXXXX)')
        parser.add_argument('message', type=str, help='The message content to send')
        parser.add_argument('--save', action='store_true', help='Save the SMS in the database')

    def handle(self, *args, **options):
        phone_number = options['phone_number']
        message = options['message']
        save_to_db = options.get('save', False)
        
        # Check if Twilio is configured
        if not is_twilio_configured():
            raise CommandError('Twilio is not properly configured. Please check your settings.')
        
        self.stdout.write(f"Sending SMS to {phone_number}: {message}")
        
        # Send the message
        message_sid = send_twilio_message(phone_number, message)
        
        if message_sid:
            self.stdout.write(self.style.SUCCESS(f"SMS sent successfully! Message SID: {message_sid}"))
            
            # Save to database if requested
            if save_to_db:
                sms = SMSNotification.objects.create(
                    phone_number=phone_number,
                    message=message,
                    twilio_sid=message_sid,
                    status='sent',
                    notification_type='manual'
                )
                self.stdout.write(self.style.SUCCESS(f"SMS saved to database with ID: {sms.id}"))
        else:
            raise CommandError("Failed to send SMS. Check the logs for details.")
