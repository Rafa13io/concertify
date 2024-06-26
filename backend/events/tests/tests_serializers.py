from django.urls import reverse
from django.test import TestCase

from rest_framework.exceptions import ValidationError
from rest_framework.test import APIRequestFactory

from events import serializers
from events.models import Event, Location, Role, SocialMedia
from users.models import ConcertifyUser


class TestLocationSerializer(TestCase):
    def setUp(self):
        self.serializer_class = serializers.LocationSerializer
        self.data = {
            'name': 'test',
            'address_line': 'test',
            'city': 'test',
            'postal_code': 'test',
            'country': 'TST'
        }

    def test_create_new(self):
        """When creating not existing object nothing should happen"""
        serializer = self.serializer_class(data=self.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

    def test_create_existing(self):
        """When attempting to create existing object nothing should happen"""
        location = Location.objects.create(**self.data)

        serializer = self.serializer_class(data=self.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        self.assertEqual(location, instance)


class TestEventFeedSerializer(TestCase):
    def setUp(self):
        self.serializer_class = serializers.EventFeedSerializer
        self.factory = APIRequestFactory()
        self.user = ConcertifyUser.objects.create_user(
            username='test',
            password='test'
        )
        location = Location.objects.create(
            name='test',
            address_line='test',
            city='test',
            postal_code='test',
            country='TST'
        )
        self.data = {
            'title': 'test',
            'desc': 'Test test',
            'location': location.id
        }

    def test_create(self):
        """create method should make an owner role
           for the user that creates it."""
        request = self.factory.get(reverse('events:event-list'))
        request.user = self.user

        serializer = self.serializer_class(
            context={'request': request},
            data=self.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        role = Role.objects.get(user=self.user)

        self.assertIsNotNone(role)
        self.assertEqual(int(role.name), Role.NameChoice.OWNER)


class TestEventDetailsSerializer(TestCase):
    fixtures = ['fixtures/test_fixture.json']

    def setUp(self):
        self.event = Event.objects.get(id=1)
        self.serializer = serializers.EventDetailsSerializer(
            instance=self.event)

    def test_get_event_contacts(self):
        """Method should return list of EventContact object data"""
        event_contacts = [
            {
                'id': obj.id,
                'name': obj.name,
                'phone': obj.phone
            } for obj in self.event.event_contact.all()
        ]
        self.assertEqual(
            event_contacts,
            self.serializer.data['event_contacts']
        )

    def test_get_social_media(self):
        """Method should return list of SocialMedia object data"""
        social_media = [
            {
                'id': obj.id,
                'link': obj.link,
                'platform': obj.platform
            } for obj in self.event.social_media.all()
        ]
        self.assertEqual(
            social_media,
            self.serializer.data['social_media']
        )

    def test_get_location(self):
        """Method should return Location object data"""
        location = {
                'id': self.event.location.id,
                'name': self.event.location.name,
                'address_line': self.event.location.address_line,
                'postal_code': self.event.location.postal_code,
                'country': self.event.location.country
            }

        self.assertEqual(
            location,
            self.serializer.data['location']
        )


class TestRoleSerializer(TestCase):
    def setUp(self):
        self.serializer_class = serializers.RoleSerializer
        self.factory = APIRequestFactory()
        self.user = ConcertifyUser.objects.create_user(
            username='test',
            password='test'
        )
        location = Location.objects.create(
            name='test',
            address_line='test',
            city='test',
            postal_code='test',
            country='TST'
        )
        self.event1 = Event.objects.create(
            title='test1',
            desc='Test test1',
            location=location
        )
        self.event2 = Event.objects.create(
            title='test2',
            desc='Test test2',
            location=location
        )
        self.request = self.factory.post(reverse("events:role-list"))
        self.request.user = self.user

    def test_create_minimal_data(self):
        """Name and user field should be optional"""
        data = {
            'event': self.event1.id,
        }
        serializer = self.serializer_class(
            context={'request': self.request},
            data=data
        )
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        self.assertEqual(instance.event, self.event1)
        self.assertEqual(instance.user, self.user)
        self.assertEqual(instance.name, Role.NameChoice.USER)

    def test_create_high_role(self):
        """User shouldn't be able to create role other than USER"""
        data = {
            'event': self.event1.id,
            'name': 3
        }
        serializer = self.serializer_class(
            context={'request': self.request},
            data=data
        )
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        self.assertEqual(instance.name, Role.NameChoice.USER)

    def test_create_nonunique(self):
        """User cannot create mutiple roles for one event"""
        data = {
            'event': self.event1.id,
            'name': 2
        }
        Role.objects.create(user=self.user, event=self.event1, name=1)

        serializer = self.serializer_class(
            data=data,
            context={"request": self.request}
        )
        serializer.is_valid(raise_exception=True)

        with self.assertRaisesMessage(ValidationError,
                                      "Object with given data already exists"):
            serializer.save()

    def test_update_to_nonunique(self):
        """Role cannot be updated to a not unique one"""
        data = {
            'event': self.event2.id,
            'name': 2
        }
        role = Role.objects.create(user=self.user, event=self.event1, name=1)
        Role.objects.create(user=self.user, event=self.event2, name=1)
        request = self.factory.put(
            reverse("events:role-detail", kwargs={'pk': role.id}))
        request.user = self.user

        serializer = self.serializer_class(
            instance=role,
            data=data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        with self.assertRaisesMessage(ValidationError,
                                      "Object with given data already exists"):
            serializer.save()


class TestSocialMediaSerializer(TestCase):
    fixtures = ['fixtures/test_fixture.json']

    def setUp(self):
        self.serializer_class = serializers.SocialMediaSerializer
        self.user = ConcertifyUser.objects.create(
            username="test",
            email='test@email.com',
            password='test'
        )
        self.event = Event.objects.first()
        Role.objects.create(
            user=self.user,
            event=self.event,
            name=3
        )
        self.factory = APIRequestFactory()
        self.data = {
            'link': "https://www.ex.com",
            'platform': "INSTAGRAM",
            'event': self.event
        }
        self.instance = SocialMedia.objects.create(**self.data)

    def test_create_unique(self):
        """User can create unique SocialMedia"""
        self.data.update({
            'link': 'https://www.example.com',
            'event': self.event.id
        })
        request = self.factory.post(reverse('events:social-media-list'))
        request.user = self.user

        serializer = self.serializer_class(
            data=self.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        serializer.save()

    def test_create_nonunique(self):
        """User cannot create multiple instances of one link for given event"""
        self.data.update({'link': 'https://www.example.com'})
        request = self.factory.post(reverse('events:social-media-list'))
        request.user = self.user
        SocialMedia.objects.create(**self.data)
        self.data.update({'event': self.event.id})

        serializer = self.serializer_class(
            data=self.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        with self.assertRaisesMessage(ValidationError,
                                      "Object with given data already exists"):
            serializer.save()

    def test_update_to_unique(self):
        """User can update SocialMedia to a unique one"""
        self.data.update({
            'link': 'https://www.example.com',
            'event': self.event.id
        })
        request = self.factory.put(reverse('events:social-media-detail',
                                           kwargs={'pk': self.event.id}))
        request.user = self.user

        serializer = self.serializer_class(
            instance=self.instance,
            data=self.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        serializer.save()

    def test_update_to_nonunique(self):
        """User cannot update SocialMedia to a nonunique one"""
        self.data.update({'link': 'https://www.example.com'})
        request = self.factory.put(reverse('events:social-media-detail',
                                           kwargs={'pk': self.event.id}))
        request.user = self.user
        SocialMedia.objects.create(**self.data)
        self.data.update({'event': self.event.id})

        serializer = self.serializer_class(
            instance=self.instance,
            data=self.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        with self.assertRaisesMessage(ValidationError,
                                      "Object with given data already exists"):
            serializer.save()
