from rest_framework import serializers
from rest_framework.exceptions import NotAuthenticated, ValidationError

from celery import shared_task
from datetime import datetime, timedelta
from celery.result import AsyncResult

from events import models
from users import models as users_models
import copy

class ValidateUserInContextMixin:
    def validate(self, attrs):
        request = self.context.get("request")

        if request.method != 'GET':
            if not hasattr(request, "user"):
                msg = "Serializer is missing user in context"
                raise ValidationError(msg)

            if not request.user.is_authenticated:
                raise NotAuthenticated()
        return attrs


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Location
        fields = '__all__'

    def create(self, validated_data):
        location, created = models.Location.objects\
            .get_or_create(**validated_data)
        return location


class EventFeedSerializer(ValidateUserInContextMixin,
                          serializers.ModelSerializer):
    class Meta:
        model = models.Event
        fields = '__all__'

    def create(self, validated_data):
        event = models.Event.objects.create(**validated_data)
        models.Role.objects.create(
            event=event,
            user=self.context.get('request').user,
            name=models.Role.NameChoice.OWNER
        )
        self._schedule_reminder(event)
        return event

    def update(self, instance, validated_data):
        self.revoke_task(instance)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        self._schedule_reminder(instance)
        return instance
    
    def _schedule_reminder(self, event):
        eta = event.start - timedelta(days=1)
        EventFeedSerializer.send_reminders.apply_async(args=(event.id, event.title, event.start),eta=eta, task_id = self.generate_task_id(event))
    @staticmethod
    def revoke_task(event):
        try:
            result = AsyncResult(EventFeedSerializer.generate_task_id(event))
            if result.state in ['PENDING']:
                result.revoke(terminate=False)
        except Exception:
            print("Error while revoking task related with reminder ")
    @staticmethod
    def generate_task_id(event):
        return "event: " +  str(event.pk)
    @staticmethod
    @shared_task
    def send_reminders(event_id, event_name, start_date):
        users = users_models.ConcertifyUser.objects.filter(role__event_id=event_id, role__name= models.Role.NameChoice.USER)
        template = users_models.Notification(title="Reminder about upcoming event", desc= 'The event "' + event_name + '" starts '+start_date.strftime('%Y-%m-%d %H:%M:%S') , notification_type=users_models.Notification.TypeChoice.REMINDER)
        NotificationSerializer.create_notifications_for_users(template, users)

class EventDetailsSerializer(EventFeedSerializer):
    event_contacts = serializers.SerializerMethodField()
    social_media = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()

    def get_event_contacts(self, event):
        response = []
        for contact in event.event_contact.all():
            response.append({
                'id': contact.id,
                'name': contact.name,
                'phone': str(contact.phone)
            })
        return response

    def get_social_media(self, event):
        response = []
        for media in event.social_media.all():
            response.append({
                'id': media.id,
                'link': media.link,
                'platform': media.platform
            })
        return response

    def get_location(self, event):
        return {
            'id': event.location.id,
            'name': event.location.name,
            'address_line': event.location.address_line,
            'postal_code': event.location.postal_code,
            'country': event.location.country
        }


class RoleSerializer(ValidateUserInContextMixin,
                     serializers.ModelSerializer):
    class Meta:
        model = models.Role
        fields = ['id', 'event', 'user', 'name']
        extra_kwargs = {
            'user': {'read_only': True},
            'name': {'required': False},
        }

    def create(self, validated_data):
        event = validated_data.get('event')
        user = self.context.get("request").user

        if models.Role.objects.filter(event=event, user=user).exists():
            raise ValidationError("Object with given data already exists")

        role = models.Role.objects.create(
            event=validated_data.get('event'),
            user=self.context.get('request').user,
            name=models.Role.NameChoice.USER
        )
        return role

    def update(self, instance, validated_data):
        event = validated_data.get('event')
        user = self.context.get("request").user
        obj = models.Role.objects.filter(event=event, user=user).first()

        if obj and obj != instance:
            raise ValidationError("Object with given data already exists")

        return super().update(instance, validated_data)


class EventContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EventContact
        fields = '__all__'


class SocialMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SocialMedia
        fields = '__all__'

    def create(self, validated_data):
        event = validated_data.get('event')
        link = validated_data.get('link')

        if models.SocialMedia.objects.filter(event=event, link=link).exists():
            raise ValidationError("Object with given data already exists")

        return super().create(validated_data)

    def update(self, instance, validated_data):
        event = validated_data.get('event')
        link = validated_data.get('link')
        obj = models.SocialMedia.objects.filter(event=event, link=link).first()

        if obj and obj != instance:
            raise ValidationError("Object with given data already exists")

        return super().update(instance, validated_data)

class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = users_models.Notification
        fields = ('title', 'desc', 'notification_type')
    def create(self, validated_data):
              request = self.context.get('request')
              pk = request.parser_context['kwargs'].get('pk')
              users = users_models.ConcertifyUser.objects.filter(role__event_id=pk, role__name= models.Role.NameChoice.USER)
              template = users_models.Notification(**validated_data)
              self.create_notifications_for_users(template, users)
              return template

    @staticmethod
    def create_notifications_for_users(template, users):
        for user in users:
            notification = copy.deepcopy(template)
            notification.user = user
            notification.save()