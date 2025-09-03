from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from api.models import Account, Report, Task, News
from unittest.mock import patch
import time


class SystemTestCase(TestCase):
    """Base class for system tests using Django test client"""
    
    def setUp(self):
        self.client = Client()
        
        # Create users for full workflow testing
        self.regular_user = Account.objects.create_user(
            username='citizen',
            email='citizen@example.com',
            password='testpass123',
            authority_level='L',
            first_name='John',
            last_name='Citizen'
        )
        
        self.emergency_worker = Account.objects.create_user(
            username='responder',
            email='responder@example.com',
            password='testpass123',
            authority_level='E',
            first_name='Jane',
            last_name='Responder'
        )
        
        self.organizer = Account.objects.create_user(
            username='coordinator',
            email='coordinator@example.com',
            password='testpass123',
            authority_level='O',
            first_name='Bob',
            last_name='Coordinator'
        )
        
        self.admin = Account.objects.create_user(
            username='administrator',
            email='admin@example.com',
            password='testpass123',
            authority_level='A',
            first_name='Alice',
            last_name='Administrator',
            is_staff=True,
            is_superuser=True
        )


class EmergencyReportingWorkflowTest(SystemTestCase):
    """Test complete emergency reporting workflow"""
    
    @patch('front_end.views.geocode_address')
    def test_complete_emergency_workflow(self, mock_geocode):
        """Test complete workflow from report creation to task completion"""
        # Mock geocoding
        mock_geocode.return_value = (43.8563, 18.4131)
        
        # Step 1: Citizen reports emergency
        self.client.login(username='citizen', password='testpass123')
        
        report_data = {
            'title': 'System Test Emergency',
            'description': 'Fire in building on main street',
            'address': 'Zmaja od Bosne 5, Sarajevo, Bosnia and Herzegovina'
        }
        
        response = self.client.post(reverse('create_report-page'), report_data)
        self.assertEqual(response.status_code, 302)
        
        # Verify report was created
        report = Report.objects.get(title='System Test Emergency')
        self.assertEqual(report.account, self.regular_user)
        self.assertIsNotNone(report.latitude)
        self.assertIsNotNone(report.longitude)
        
        # Step 2: Organizer creates task for the report
        self.client.login(username='coordinator', password='testpass123')
        
        task_data = {
            'username': self.emergency_worker.id,
            'title': 'Respond to building fire',
            'descirption': 'Investigate and respond to reported fire'
        }
        
        response = self.client.post(
            reverse('create_task-page', args=[report.id]), 
            task_data
        )
        self.assertEqual(response.status_code, 302)
        
        # Verify task was created
        task = Task.objects.get(title='Respond to building fire')
        self.assertEqual(task.report, report)
        self.assertEqual(task.username, self.emergency_worker)
        
        # Step 3: Emergency worker updates task status
        self.client.login(username='responder', password='testpass123')
        
        update_data = {
            'status': 'D'  # Done
        }
        
        response = self.client.post(
            reverse('update_task_status-page', args=[task.id]), 
            update_data
        )
        self.assertEqual(response.status_code, 302)
        
        # Verify task status was updated
        task.refresh_from_db()
        self.assertEqual(task.status, 'D')
        
        # Step 4: Verify emergency worker can see their assigned tasks
        response = self.client.get(
            reverse('assigned_task-page', args=['responder'])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Respond to building fire')


class NewsManagementWorkflowTest(SystemTestCase):
    """Test news management workflow"""
    
    def test_news_lifecycle(self):
        """Test complete news lifecycle"""
        # Step 1: Organizer creates news
        self.client.login(username='coordinator', password='testpass123')
        
        news_data = {
            'title': 'System Test News',
            'description': 'Important safety announcement for citizens',
            'address': 'Sarajevo Canton'
        }
        
        response = self.client.post(reverse('create_news-page'), news_data)
        self.assertEqual(response.status_code, 302)
        
        # Verify news was created
        news = News.objects.get(title='System Test News')
        self.assertEqual(news.account, self.organizer)
        
        # Step 2: Verify news appears on home page
        response = self.client.get(reverse('home-page'))
        self.assertContains(response, 'System Test News')
        
        # Step 3: Admin updates news
        self.client.login(username='administrator', password='testpass123')
        
        update_data = {
            'title': 'Updated System Test News',
            'description': 'Updated safety announcement',
            'address': 'Sarajevo Canton'
        }
        
        response = self.client.post(
            reverse('update_news-page', args=[news.id]), 
            update_data
        )
        self.assertEqual(response.status_code, 302)
        
        # Verify news was updated
        news.refresh_from_db()
        self.assertEqual(news.title, 'Updated System Test News')


class AuthorizationSystemTest(SystemTestCase):
    """Test system-wide authorization"""
    
    def test_authority_level_restrictions(self):
        """Test authority level restrictions across the system"""
        # Test regular user restrictions
        self.client.login(username='citizen', password='testpass123')
        
        # Cannot create tasks
        response = self.client.get(reverse('create_task-page', args=[1]))
        self.assertEqual(response.status_code, 302)
        
        # Cannot create news
        response = self.client.get(reverse('create_news-page'))
        self.assertEqual(response.status_code, 302)
        
        # Test emergency worker permissions
        self.client.login(username='responder', password='testpass123')
        
        # Can access their own tasks
        response = self.client.get(reverse('assigned_task-page', args=['responder']))
        self.assertEqual(response.status_code, 200)
        
        # Cannot access other's tasks
        response = self.client.get(reverse('assigned_task-page', args=['other_user']))
        self.assertEqual(response.status_code, 302)
        
        # Test organizer permissions
        self.client.login(username='coordinator', password='testpass123')
        
        # Can create news
        response = self.client.get(reverse('create_news-page'))
        self.assertEqual(response.status_code, 200)
        
        # Test admin permissions
        self.client.login(username='administrator', password='testpass123')
        
        # Can access everything
        response = self.client.get(reverse('create_news-page'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('assigned_task-page', args=['responder']))
        self.assertEqual(response.status_code, 200)


class MapSystemTest(SystemTestCase):
    """Test map system functionality"""
    
    def test_map_displays_reports_correctly(self):
        """Test map displays reports with coordinates"""
        # Create reports with and without coordinates
        report_with_coords = Report.objects.create(
            account=self.regular_user,
            title='Report with coordinates',
            description='Test report',
            address='Sarajevo',
            latitude=43.8563,
            longitude=18.4131
        )
        
        report_without_coords = Report.objects.create(
            account=self.regular_user,
            title='Report without coordinates',
            description='Test report',
            address='Unknown location'
        )
        
        response = self.client.get(reverse('map-page'))
        self.assertEqual(response.status_code, 200)
        
        # Check that reports are passed to template
        reports = response.context['reports']
        self.assertIn(report_with_coords, reports)
        self.assertIn(report_without_coords, reports)
        
        # Map should contain JavaScript for markers
        self.assertContains(response, 'L.marker')
        self.assertContains(response, report_with_coords.title)


class DataIntegritySystemTest(SystemTestCase):
    """Test data integrity across the system"""
    
    def test_report_deletion_cascade(self):
        """Test that related data is handled correctly when reports are deleted"""
        # Create report and related task
        report = Report.objects.create(
            account=self.regular_user,
            title='Test Report for Deletion',
            description='Test description',
            address='Test Address'
        )
        
        task = Task.objects.create(
            username=self.emergency_worker,
            report=report,
            title='Related Task',
            descirption='Task description'
        )
        
        # Login as organizer and delete report
        self.client.login(username='coordinator', password='testpass123')
        response = self.client.get(reverse('delete_report-page', args=[report.id]))
        self.assertEqual(response.status_code, 302)
        
        # Verify report is marked as deleted (soft delete)
        report.refresh_from_db()
        self.assertTrue(report.is_deleted)
        
        # Task should still exist but be associated with deleted report
        task.refresh_from_db()
        self.assertEqual(task.report, report)


class PerformanceSystemTest(SystemTestCase):
    """Test system performance with larger datasets"""
    
    def test_home_page_with_many_reports(self):
        """Test home page performance with many reports"""
        # Create multiple reports
        reports = []
        for i in range(20):
            report = Report.objects.create(
                account=self.regular_user,
                title=f'Performance Test Report {i}',
                description=f'Description {i}',
                address=f'Address {i}'
            )
            reports.append(report)
        
        # Test home page loads correctly
        response = self.client.get(reverse('home-page'))
        self.assertEqual(response.status_code, 200)
        
        # Should only show latest 5 reports
        self.assertEqual(len(response.context['reports']), 5)
    
    def test_map_with_many_reports(self):
        """Test map performance with many reports"""
        # Create reports with coordinates
        for i in range(50):
            Report.objects.create(
                account=self.regular_user,
                title=f'Map Test Report {i}',
                description=f'Description {i}',
                address=f'Address {i}',
                latitude=43.8563 + (i * 0.001),  # Slightly different coordinates
                longitude=18.4131 + (i * 0.001)
            )
        
        # Test map page loads
        response = self.client.get(reverse('map-page'))
        self.assertEqual(response.status_code, 200)
        
        # All reports should be included
        self.assertEqual(len(response.context['reports']), 50 + 1)  # +1 for any existing reports


# Uncomment and configure if you want to run browser-based tests
# Requires ChromeDriver installation
"""
class SeleniumSystemTest(StaticLiveServerTestCase):
    \"\"\"Browser-based system tests using Selenium\"\"\"
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Configure Chrome options for headless testing
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        try:
            cls.driver = webdriver.Chrome(options=chrome_options)
            cls.driver.implicitly_wait(10)
        except Exception as e:
            cls.driver = None
            print(f"Could not initialize Chrome driver: {e}")
    
    @classmethod
    def tearDownClass(cls):
        if cls.driver:
            cls.driver.quit()
        super().tearDownClass()
    
    def setUp(self):
        if not self.driver:
            self.skipTest("Chrome driver not available")
        
        # Create test user
        self.user = Account.objects.create_user(
            username='seleniumuser',
            email='selenium@example.com',
            password='testpass123',
            authority_level='L'
        )
    
    def test_login_workflow_browser(self):
        \"\"\"Test login workflow in browser\"\"\"
        self.driver.get(f"{self.live_server_url}/login/")
        
        # Find and fill login form
        username_input = self.driver.find_element(By.NAME, "username")
        password_input = self.driver.find_element(By.NAME, "password")
        
        username_input.send_keys("seleniumuser")
        password_input.send_keys("testpass123")
        
        # Submit form
        login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()
        
        # Should redirect to home page
        WebDriverWait(self.driver, 10).until(
            EC.url_contains(self.live_server_url)
        )
        
        # Check if logged in successfully
        self.assertIn("BNDMS", self.driver.title)
    
    def test_report_creation_workflow_browser(self):
        \"\"\"Test report creation in browser\"\"\"
        # Login first
        self.driver.get(f"{self.live_server_url}/login/")
        self.driver.find_element(By.NAME, "username").send_keys("seleniumuser")
        self.driver.find_element(By.NAME, "password").send_keys("testpass123")
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Navigate to create report
        self.driver.get(f"{self.live_server_url}/create_report/")
        
        # Fill report form
        self.driver.find_element(By.NAME, "title").send_keys("Selenium Test Emergency")
        self.driver.find_element(By.NAME, "description").send_keys("Test emergency report")
        self.driver.find_element(By.NAME, "address").send_keys("Test Address, Sarajevo")
        
        # Submit form
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Should redirect to home page
        WebDriverWait(self.driver, 10).until(
            EC.url_contains(self.live_server_url)
        )
        
        # Verify report was created
        self.assertTrue(Report.objects.filter(title="Selenium Test Emergency").exists())
"""
