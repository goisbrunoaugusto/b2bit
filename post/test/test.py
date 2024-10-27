from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from post.models import Post
from django.core.cache import cache

User = get_user_model()


class PostAPITestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(email="user1@example.com", password="password123", name="User1")
        self.user2 = User.objects.create_user(email="user2@example.com", password="password123", name="User2")

        self.post1 = Post.objects.create(user=self.user1, content="First post")
        self.post2 = Post.objects.create(user=self.user1, content="Second post")

        self.client = APIClient()

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def test_create_post(self):
        self.authenticate(self.user1)
        url = reverse('create_post')
        data = {
            'content': 'New test post'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 3)
        self.assertEqual(Post.objects.last().user, self.user1)

    def test_delete_post(self):
        self.authenticate(self.user1)
        url = reverse('delete_post', kwargs={'pk': self.post1.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Post.objects.filter(pk=self.post1.pk).exists())

    def test_delete_post_unauthorized(self):
        self.authenticate(self.user2)
        url = reverse('delete_post', kwargs={'pk': self.post1.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # 3. Test Edit Post
    def test_edit_post(self):
        self.authenticate(self.user1)
        url = reverse('edit_post', kwargs={'pk': self.post1.pk})
        data = {
            'content': 'Updated post content'
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post1.refresh_from_db()
        self.assertEqual(self.post1.content, 'Updated post content')

    def test_edit_post_unauthorized(self):
        self.authenticate(self.user2)
        url = reverse('edit_post', kwargs={'pk': self.post1.pk})
        data = {
            'content': 'Unauthorized edit'
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # 4. Test Like Post
    def test_like_post(self):
        self.authenticate(self.user1)
        url = reverse('like_post', kwargs={'pk': self.post1.pk})

        # Like the post
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post1.refresh_from_db()
        self.assertEqual(self.post1.like.count(), 1)

        # Unlike the post
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post1.refresh_from_db()
        self.assertEqual(self.post1.like.count(), 0)

    # 5. Test Following Posts (Feed) with Pagination and Cache
    def test_following_posts_pagination_and_cache(self):
        # Simulate user1 following user2
        self.user1.following.add(self.user2)

        # Create posts for user2
        Post.objects.create(user=self.user2, content="User2's first post")
        Post.objects.create(user=self.user2, content="User2's second post")

        self.authenticate(self.user1)
        url = reverse('feed')

        # Check paginated response
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('User2', response.content.decode())

        # Simulate cache and ensure cache is being set
        cache_key = f"following_posts_{self.user1.id}_page_1"
        cached_data = cache.get(cache_key)
        self.assertIsNotNone(cached_data)

    # 6. Test User Posts (User's own posts)
    def test_user_posts(self):
        self.authenticate(self.user1)
        url = reverse('user_posts')

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # Check pagination
        self.assertIn('First post', response.content.decode())

        # Simulate cache and ensure cache is being set
        cache_key = f"my_posts_{self.user1.id}_page_1"
        cached_data = cache.get(cache_key)
        self.assertIsNotNone(cached_data)
