from django.urls import reverse
from django.utils.timezone import now, timedelta

from rest_framework import status
from rest_framework.test import APITestCase

from knox.models import AuthToken

from events.models import Event, Location, Role
from events.serializers import EventDetailsSerializer, EventFeedSerializer

from users.models import ConcertifyUser


class TestEventViewSet(APITestCase):
    def setUp(self):
        self.location = Location.objects.create(
            name="test",
            address_line="test",
            city="test",
            postal_code="12-345",
            country="TST"
        )
        self.event1 = Event.objects.create(
            title="test1",
            desc="test1",
            start=now() - timedelta(days=20),
            end=now() - timedelta(days=10),
            location=self.location
        )
        self.event2 = Event.objects.create(
            title="test2",
            desc="test2",
            start=now() - timedelta(days=20),
            end=now() + timedelta(days=10),
            location=self.location
        )
        self.user = ConcertifyUser.objects.create(
            username='test',
            email='test@email.com',
            password='test'
        )
        self.token = f"Token {AuthToken.objects.create(user=self.user)[-1]}"
        self.url = reverse('events:event-list')
        self.url_details = reverse(
            'events:event-detail',
            kwargs={'pk': self.event1.id}
        )

    def test_get_queryset(self):
        "get_queryset should return filtered list of events"
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(
            response.data['results'][0],
            EventFeedSerializer(instance=self.event2).data
        )

    def test_serializer_class_retrieve(self):
        """When using retrieve action data should be serialized
           using EventDetailsSerializer"""
        response = self.client.get(self.url_details)
        serializer = EventDetailsSerializer(instance=self.event1)

        self.assertDictEqual(serializer.data, response.data)

    def test_serializer_class_other(self):
        """When using other actions data should be serialized
           using EventFeedSerializer"""
        response = self.client.get(self.url)
        serializer = EventFeedSerializer(instance=self.event2)

        self.assertDictEqual(serializer.data, response.data['results'][0])

    def test_get_permission_list(self):
        """Anyone should be able to use list actions"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_permission_retrieve(self):
        """Anyone should be able to use retrieve actions"""
        response = self.client.get(self.url_details)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_action(self):
        """Only authenticated users should be able to create events"""
        data = {
            'title': 'test',
            'desc': 'test',
            'location': self.location.id
        }
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.url, data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        for k, v in response.data.items():
            self.assertEqual(v, response.data.get(k))

    def test_update_action(self):
        """Only users with at least moderator permission can update event"""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        serializer = EventFeedSerializer(instance=self.event1)
        data = serializer.data
        data.update({'title': 'PUT', 'picture': ""})

        response = self.client.put(self.url_details, data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        Role.objects.create(user=self.user, event=self.event1,
                            name=Role.NameChoice.MODERATOR)
        response = self.client.put(self.url_details, data=data)
        data.update({'picture': None})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(data, response.data)

    def test_partial_update_action(self):
        """Only users with at least moderator permission
           can partially update event"""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        serializer = EventFeedSerializer(instance=self.event1)
        data = serializer.data
        partial = {'title': 'PATCH'}
        data.update(partial)

        response = self.client.patch(self.url_details, data=partial)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        Role.objects.create(user=self.user, event=self.event1,
                            name=Role.NameChoice.MODERATOR)
        response = self.client.patch(self.url_details, data=partial)
        data.update({'picture': None})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(data, response.data)

    def test_destroy_action(self):
        """Only users with at least owner permissions can delete event"""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)

        response = self.client.delete(self.url_details)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        Role.objects.create(user=self.user, event=self.event1,
                            name=Role.NameChoice.OWNER)
        response = self.client.delete(self.url_details)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class TestRoleViewSet(APITestCase):
    fixtures = ['fixtures/test_fixture.json']

    def setUp(self):
        self.event = Event.objects.first()
        self.user = ConcertifyUser.objects.create(
            username='test',
            email='test@email.com',
            password='test'
        )
        self.token = f"Token {AuthToken.objects.create(self.user)[-1]}"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)

    def test_create_action(self):
        """Create should return whole event, role and default role"""
        data = {
            'event': self.event.id,
            'user': self.user.id
        }
        response = self.client.post(reverse("events:role-list"), data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['event'], self.event.id)
        self.assertEqual(response.data['user'], self.user.id)
        self.assertEqual(response.data['name'], Role.NameChoice.USER)

    def test_destroy_action(self):
        """Destroy should return 204 No content"""
        role = Role.objects.create(
            event=self.event,
            user=self.user,
            name=Role.NameChoice.STAFF
        )
        response = self.client.delete(
            reverse("events:role-detail", kwargs={'pk': role.id})
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_update_action(self):
        """Update should return new role data"""
        role = Role.objects.create(
            event=self.event,
            user=self.user,
            name=Role.NameChoice.OWNER
        )
        data = {
            'event': self.event.id,
            'user': self.user.id,
            'name': Role.NameChoice.STAFF
        }
        response = self.client.put(
            reverse("events:role-detail", kwargs={'pk': role.id}),
            data=data
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data, data)
