from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from unittest.mock import patch
from api.models import Account, Report, Task, News
from decimal import Decimal


class ViewIntegrationTest(TestCase):
    """Integration tests for views"""
    
    def setUp(self):
        self.client = Client()
        
        # Create test users with different authority levels
        self.regular_user = Account.objects.create_user(
            username='regular',
            email='regular@example.com',
            password='testpass123',
            authority_level='L'
        )
        
        self.emergency_worker = Account.objects.create_user(
            username='emergency',
            email='emergency@example.com',
            password='testpass123',
            authority_level='E'
        )
        
        self.organizer = Account.objects.create_user(
            username='organizer',
            email='organizer@example.com',
            password='testpass123',
            authority_level='O'
        )
        
        self.admin = Account.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123',
            authority_level='A'
        )
        
        # Create test data
        self.test_report = Report.objects.create(
            account=self.regular_user,
            title='Test Emergency Report',
            description='Test description',
            address='Kolodvorska 13, Sarajevo',
            latitude=Decimal('43.8563'),
            longitude=Decimal('18.4131')
        )
        
        self.test_task = Task.objects.create(
            username=self.emergency_worker,
            report=self.test_report,
            title='Test Task',
            descirption='Test task description'
        )


class HomePageTest(ViewIntegrationTest):
    """Test home page functionality"""
    
    def test_home_page_accessible(self):
        """Test home page is accessible"""
        response = self.client.get(reverse('home-page'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'BNDMS')
    
    def test_home_page_displays_reports(self):
        """Test home page displays latest reports"""
        response = self.client.get(reverse('home-page'))
        self.assertContains(response, self.test_report.title)


class AuthenticationTest(ViewIntegrationTest):
    """Test authentication functionality"""
    
    def test_login_page_accessible(self):
        """Test login page is accessible"""
        response = self.client.get(reverse('login-page'))
        self.assertEqual(response.status_code, 200)
    
    def test_register_page_accessible(self):
        """Test register page is accessible"""
        response = self.client.get(reverse('register-page'))
        self.assertEqual(response.status_code, 200)
    
    def test_user_registration(self):
        """Test user registration with automatic authority level"""
        registration_data = {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'newuser@example.com',
            'phone_number': '+387603456789',
            'address': 'New Address',
            'password1': 'complexpass123',
            'password2': 'complexpass123'
        }
        
        response = self.client.post(reverse('register-page'), registration_data)
        
        # Should redirect to login after successful registration
        self.assertEqual(response.status_code, 302)
        
        # Check user was created with correct authority level
        new_user = Account.objects.get(username='newuser')
        self.assertEqual(new_user.authority_level, 'L')
    
    def test_user_login(self):
        """Test user login functionality"""
        login_data = {
            'username': 'regular',
            'password': 'testpass123'
        }
        
        response = self.client.post(reverse('login-page'), login_data)
        self.assertEqual(response.status_code, 302)  # Redirect after login


class ReportTest(ViewIntegrationTest):
    """Test report functionality"""
    
    def test_reports_page_accessible(self):
        """Test reports page is accessible"""
        response = self.client.get(reverse('reports-page'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.test_report.title)
    
    def test_create_report_requires_login(self):
        """Test creating report requires authentication"""
        response = self.client.get(reverse('create_report-page'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    @patch('front_end.views.geocode_address')
    def test_create_report_authenticated(self, mock_geocode):
        """Test authenticated user can create report"""
        # Mock geocoding response
        mock_geocode.return_value = (43.8563, 18.4131)
        
        self.client.login(username='regular', password='testpass123')
        
        report_data = {
            'title': 'New Emergency',
            'description': 'New emergency description',
            'address': 'New Address, Sarajevo'
        }
        
        response = self.client.post(reverse('create_report-page'), report_data)
        self.assertEqual(response.status_code, 302)  # Redirect after creation
        
        # Check report was created
        self.assertTrue(Report.objects.filter(title='New Emergency').exists())


class AuthorizationTest(ViewIntegrationTest):
    """Test authorization and permission controls"""
    
    def test_create_task_organizer_only(self):
        """Test only organizers can create tasks"""
        # Test regular user cannot access
        self.client.login(username='regular', password='testpass123')
        response = self.client.get(reverse('create_task-page', args=[self.test_report.id]))
        self.assertEqual(response.status_code, 302)  # Redirected
        
        # Test organizer can access
        self.client.login(username='organizer', password='testpass123')
        response = self.client.get(reverse('create_task-page', args=[self.test_report.id]))
        self.assertEqual(response.status_code, 200)
        
        # Test admin can access
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('create_task-page', args=[self.test_report.id]))
        self.assertEqual(response.status_code, 200)
    
    def test_emergency_worker_task_access(self):
        """Test emergency workers can only see their tasks"""
        self.client.login(username='emergency', password='testpass123')
        response = self.client.get(reverse('assigned_task-page', args=['emergency']))
        self.assertEqual(response.status_code, 200)
        
        # Should not be able to access other user's tasks
        response = self.client.get(reverse('assigned_task-page', args=['other_user']))
        self.assertEqual(response.status_code, 302)  # Redirected
    
    def test_admin_access_all(self):
        """Test admin can access everything"""
        self.client.login(username='admin', password='testpass123')
        
        # Can access task creation
        response = self.client.get(reverse('create_task-page', args=[self.test_report.id]))
        self.assertEqual(response.status_code, 200)
        
        # Can access any user's tasks
        response = self.client.get(reverse('assigned_task-page', args=['emergency']))
        self.assertEqual(response.status_code, 200)


class MapTest(ViewIntegrationTest):
    """Test map functionality"""
    
    def test_map_page_accessible(self):
        """Test map page is accessible"""
        response = self.client.get(reverse('map-page'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'leaflet')  # Check map library loaded
    
    def test_map_displays_reports(self):
        """Test map displays reports with coordinates"""
        response = self.client.get(reverse('map-page'))
        # Check if report data is passed to template
        self.assertIn('reports', response.context)
        reports = response.context['reports']
        self.assertIn(self.test_report, reports)


class NewsTest(ViewIntegrationTest):
    """Test news functionality"""
    
    def test_news_page_accessible(self):
        """Test news page is accessible"""
        response = self.client.get(reverse('news-page'))
        self.assertEqual(response.status_code, 200)
    
    def test_create_news_organizer_only(self):
        """Test only organizers and admins can create news"""
        # Test regular user cannot access
        self.client.login(username='regular', password='testpass123')
        response = self.client.get(reverse('create_news-page'))
        self.assertEqual(response.status_code, 302)  # Redirected
        
        # Test organizer can access
        self.client.login(username='organizer', password='testpass123')
        response = self.client.get(reverse('create_news-page'))
        self.assertEqual(response.status_code, 200)


class GeocodingTest(TestCase):
    """Test geocoding functionality"""
    
    @patch('front_end.views.requests.get')
    def test_geocode_address_success(self, mock_get):
        """Test successful geocoding"""
        from front_end.views import geocode_address
        
        # Mock successful response
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {'lat': '43.8563', 'lon': '18.4131'}
        ]
        
        lat, lon = geocode_address('Kolodvorska 13, Sarajevo')
        
        self.assertEqual(lat, 43.8563)
        self.assertEqual(lon, 18.4131)
        
        # Check that Bosnia and Herzegovina was added to the query
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        self.assertIn('Bosnia and Herzegovina', call_args[1]['params']['q'])
    
    @patch('front_end.views.requests.get')
    def test_geocode_address_failure(self, mock_get):
        """Test geocoding failure"""
        from front_end.views import geocode_address
        
        # Mock failed response
        mock_response = mock_get.return_value
        mock_response.status_code = 404
        
        lat, lon = geocode_address('Invalid Address')
        
        self.assertIsNone(lat)
        self.assertIsNone(lon)
