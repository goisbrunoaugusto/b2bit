from django.test import TestCase, Client
from django.urls import reverse
from post.models import Post
from account.models import UserData

class PostViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserData.objects.create_user(username='testuser',email='testeuser@hotmail.com' ,password='12345')
        self.client.login(username='testuser', password='12345')
        self.post = Post.objects.create(content='Test content', user=self.user)

    def test_create_post(self):
        response = self.client.post(reverse('create_post'), {'content': 'New post content'})
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Post.objects.filter(content='New post content').exists())

    def test_delete_post(self):
        response = self.client.delete(reverse('delete_post', args=[self.post.id]))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Post.objects.filter(id=self.post.id).exists())

    def test_edit_post(self):
        response = self.client.post(reverse('edit_post', args=[self.post.id]), {'content': 'Updated content'})
        self.assertEqual(response.status_code, 200)
        self.post.refresh_from_db()
        self.assertEqual(self.post.content, 'Updated content')

    def test_like_post(self):
        response = self.client.post(reverse('like_post', args=[self.post.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.user in self.post.like.all())
        response = self.client.post(reverse('like_post', args=[self.post.id]))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.user in self.post.like.all())