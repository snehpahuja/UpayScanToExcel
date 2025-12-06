from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

class APITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@upayngo.com',
            password='testpass123',
            role='employee'
        )
    
    def test_login(self):
        """Test login endpoint"""
        response = self.client.post('/api/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
    
    def test_dashboard_requires_auth(self):
        """Test dashboard requires authentication"""
        response = self.client.get('/api/dashboard/attendance/')
        self.assertEqual(response.status_code, 401)
    
    # Add more tests...