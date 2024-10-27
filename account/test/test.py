from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from account.models import UserData


class UserAPITestCase(APITestCase):
    def set_up(self):
        self.user1 = UserData.objects.create_user(email="user1@example.com", name="User One", password="password123")
        self.user2 = UserData.objects.create_user(email="user2@example.com", name="User Two", password="password123")

        self.client = APIClient()

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def test_register_user(self):
        url = reverse('sign_up')
        data = {
            'email': 'testuser@example.com',
            'name': 'Test User',
            'password': 'testpassword'
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UserData.objects.count(), 3)
        self.assertEqual(UserData.objects.last().email, 'testuser@example.com')

    def test_get_user_info(self):
        self.authenticate(self.user1)
        url = reverse('info')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user1.email)
        self.assertEqual(response.data['name'], self.user1.name)

    def test_update_user_info(self):
        self.authenticate(self.user1)
        url = reverse('info')
        data = {
            'name': 'Updated User One'
        }
        response = self.client.put(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.name, 'Updated User One')

    def test_delete_user(self):
        self.authenticate(self.user1)
        url = reverse('info')
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(UserData.objects.filter(id=self.user1.id).exists())

    def test_follow_user(self):
        self.authenticate(self.user1)
        url = reverse('follow', kwargs={'pk': self.user2.pk})

        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Followed", response.data)
        self.assertTrue(self.user2.followers.filter(id=self.user1.id).exists())

        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Unfollowed", response.data)
        self.assertFalse(self.user2.followers.filter(id=self.user1.id).exists())

    def test_list_followers(self):
        # Add user1 as a follower of user2
        self.user2.followers.add(self.user1)

        self.authenticate(self.user2)
        url = reverse('followers')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_followers'], 1)
        self.assertEqual(response.data['followers'][0]['email'], self.user1.email)

    def test_list_following(self):
        # Add user2 as a following of user1
        self.user1.following.add(self.user2)

        self.authenticate(self.user1)
        url = reverse('following_list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_following'], 1)
        self.assertEqual(response.data['following'][0]['email'], self.user2.email)
