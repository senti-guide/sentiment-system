from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Event
from datetime import datetime

class EventTests(TestCase):
    def test_admin_results_url(self):
        # Create a user (make sure it's an admin if the view requires admin access)
        user = User.objects.create_user(username='admin', password='password')
        user.is_staff = True  # Grant admin access
        user.save()

        # Log the user in
        self.client.login(username='admin', password='password')

        # Create an event with the required date field
        event = Event.objects.create(title="Sample Event", date=datetime.now())
        
        # Check if the URL returns a 200 response
        response = self.client.get(reverse('admin_results', kwargs={'event_id': event.id}))
        self.assertEqual(response.status_code, 200)
