import json
from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import Notification, SMSNotification
from .serializers import NotificationSerializer, SMSNotificationSerializer
from barberian.utils.permissions import IsAdmin
from barberian.utils.sms import send_twilio_message, get_message_status

User = get_user_model()

class NotificationListView(generics.ListAPIView):
    """
    API endpoint for listing user notifications
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Return only notifications for the current user
        return Notification.objects.filter(recipient=self.request.user).order_by('-created_at')

class NotificationDetailView(generics.RetrieveAPIView):
    """
    API endpoint for retrieving notification details
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Return only notifications for the current user
        return Notification.objects.filter(recipient=self.request.user)

class MarkNotificationReadView(APIView):
    """
    API endpoint for marking a notification as read
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        try:
            notification = Notification.objects.get(pk=pk, recipient=request.user)
            notification.is_read = True
            notification.save()
            return Response(
                {"message": "Notification marked as read"},
                status=status.HTTP_200_OK
            )
        except Notification.DoesNotExist:
            return Response(
                {"error": "Notification not found or does not belong to you"},
                status=status.HTTP_404_NOT_FOUND
            )

class MarkAllNotificationsReadView(APIView):
    """
    API endpoint for marking all notifications as read
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        return Response(
            {"message": "All notifications marked as read"},
            status=status.HTTP_200_OK
        )

class DeleteNotificationView(APIView):
    """
    API endpoint for deleting a notification
    """
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, pk):
        try:
            notification = Notification.objects.get(pk=pk, recipient=request.user)
            notification.delete()
            return Response(
                {"message": "Notification deleted"},
                status=status.HTTP_200_OK
            )
        except Notification.DoesNotExist:
            return Response(
                {"error": "Notification not found or does not belong to you"},
                status=status.HTTP_404_NOT_FOUND
            )

class DeleteAllNotificationsView(APIView):
    """
    API endpoint for deleting all notifications
    """
    permission_classes = [IsAuthenticated]
    
    def delete(self, request):
        Notification.objects.filter(recipient=request.user).delete()
        return Response(
            {"message": "All notifications deleted"},
            status=status.HTTP_200_OK
        )

# SMS Notification Views

class SMSNotificationListView(generics.ListAPIView):
    """
    API endpoint for listing SMS notifications (admin only)
    """
    serializer_class = SMSNotificationSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get_queryset(self):
        return SMSNotification.objects.all().order_by('-created_at')

class SMSNotificationDetailView(generics.RetrieveAPIView):
    """
    API endpoint for retrieving SMS notification details (admin only)
    """
    queryset = SMSNotification.objects.all()
    serializer_class = SMSNotificationSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

class SendSMSManualView(APIView):
    """
    API endpoint for manually sending an SMS (admin only)
    """
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def post(self, request):
        phone_number = request.data.get('phone_number')
        message = request.data.get('message')
        recipient_id = request.data.get('recipient_id')
        notification_type = request.data.get('notification_type', 'manual')
        reference_id = request.data.get('reference_id')
        
        # Validate required fields
        if not phone_number or not message:
            return Response(
                {"error": "Phone number and message are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # If recipient_id is provided, get the recipient
        recipient = None
        if recipient_id:
            try:
                recipient = User.objects.get(pk=recipient_id)
            except User.DoesNotExist:
                return Response(
                    {"error": "Recipient user not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Create the SMS notification record
        notification = SMSNotification.objects.create(
            recipient=recipient,
            phone_number=phone_number,
            message=message,
            notification_type=notification_type,
            reference_id=reference_id,
            status='pending'
        )
        
        # Send the SMS
        try:
            twilio_sid = send_twilio_message(
                to_phone_number=phone_number,
                message=message
            )
            
            if twilio_sid:
                notification.twilio_sid = twilio_sid
                notification.status = 'sent'
                notification.save()
                
                return Response({
                    "message": "SMS sent successfully",
                    "sms_id": notification.id,
                    "twilio_sid": twilio_sid
                }, status=status.HTTP_200_OK)
            else:
                notification.status = 'failed'
                notification.error_message = "Failed to get Twilio SID"
                notification.save()
                
                return Response({
                    "error": "Failed to send SMS",
                    "sms_id": notification.id
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        except Exception as e:
            notification.status = 'failed'
            notification.error_message = str(e)
            notification.save()
            
            return Response({
                "error": f"Failed to send SMS: {str(e)}",
                "sms_id": notification.id
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateSMSStatusView(APIView):
    """
    API endpoint for updating the status of SMS notifications from Twilio (admin only)
    """
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def post(self, request):
        sms_id = request.data.get('sms_id')
        
        if sms_id:
            # Update a specific SMS notification
            try:
                notification = SMSNotification.objects.get(pk=sms_id)
                
                if notification.twilio_sid:
                    status = get_message_status(notification.twilio_sid)
                    
                    if status:
                        notification.status = status
                        notification.save()
                        
                        return Response({
                            "message": f"SMS status updated to {status}",
                            "sms_id": notification.id,
                            "status": status
                        }, status=status.HTTP_200_OK)
                    else:
                        return Response({
                            "error": "Failed to get message status from Twilio",
                            "sms_id": notification.id
                        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                else:
                    return Response({
                        "error": "SMS notification has no Twilio SID",
                        "sms_id": notification.id
                    }, status=status.HTTP_400_BAD_REQUEST)
                
            except SMSNotification.DoesNotExist:
                return Response({
                    "error": "SMS notification not found",
                    "sms_id": sms_id
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            # Update all pending/sent SMS notifications
            updated_count = 0
            failed_count = 0
            
            # Get all SMS notifications with Twilio SID that are in 'pending' or 'sent' status
            notifications = SMSNotification.objects.filter(
                twilio_sid__isnull=False,
                status__in=['pending', 'sent']
            )
            
            for notification in notifications:
                try:
                    status_value = get_message_status(notification.twilio_sid)
                    
                    if status_value:
                        notification.status = status_value
                        notification.save()
                        updated_count += 1
                    else:
                        failed_count += 1
                
                except Exception as e:
                    notification.error_message = str(e)
                    notification.save()
                    failed_count += 1
            
            return Response({
                "message": f"Updated {updated_count} SMS notifications, {failed_count} failed",
                "updated": updated_count,
                "failed": failed_count,
                "total": notifications.count()
            }, status=status.HTTP_200_OK)