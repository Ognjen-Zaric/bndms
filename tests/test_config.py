"""
Test configuration and utilities for BNDMS
"""

from django.test import TestCase
from django.test.runner import DiscoverRunner
from django.core.management import call_command
from django.db import transaction
import logging


class BNDMSTestRunner(DiscoverRunner):
    """Custom test runner for BNDMS"""
    
    def setup_test_environment(self, **kwargs):
        super().setup_test_environment(**kwargs)
        # Disable logging during tests
        logging.disable(logging.CRITICAL)
    
    def teardown_test_environment(self, **kwargs):
        super().teardown_test_environment(**kwargs)
        logging.disable(logging.NOTSET)


class BaseTestCase(TestCase):
    """Base test case with common utilities"""
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data for the test case"""
        super().setUpTestData()
        # Common test data setup can go here
    
    def setUp(self):
        """Set up test fixtures for each test method"""
        super().setUp()
    
    def tearDown(self):
        """Clean up after each test method"""
        super().tearDown()
    
    def assertRedirectsToLogin(self, response, target_url=None):
        """Assert that response redirects to login page"""
        self.assertEqual(response.status_code, 302)
        if target_url:
            self.assertIn('/login/', response.url)
    
    def assertPermissionDenied(self, response):
        """Assert that response indicates permission denied"""
        self.assertIn(response.status_code, [302, 403])
    
    def create_test_user(self, username, authority_level='L', **kwargs):
        """Helper method to create test users"""
        from api.models import Account
        
        defaults = {
            'email': f'{username}@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'authority_level': authority_level
        }
        defaults.update(kwargs)
        
        return Account.objects.create_user(username=username, **defaults)
    
    def create_test_report(self, account=None, **kwargs):
        """Helper method to create test reports"""
        from api.models import Report
        
        if account is None:
            account = self.create_test_user('test_reporter')
        
        defaults = {
            'title': 'Test Emergency Report',
            'description': 'Test description',
            'address': 'Test Address, Sarajevo'
        }
        defaults.update(kwargs)
        
        return Report.objects.create(account=account, **defaults)
    
    def create_test_task(self, report=None, username=None, **kwargs):
        """Helper method to create test tasks"""
        from api.models import Task
        
        if report is None:
            report = self.create_test_report()
        
        if username is None:
            username = self.create_test_user('test_worker', authority_level='E')
        
        defaults = {
            'title': 'Test Task',
            'descirption': 'Test task description'
        }
        defaults.update(kwargs)
        
        return Task.objects.create(
            report=report, 
            username=username, 
            **defaults
        )


# Test data fixtures
TEST_USERS = {
    'regular': {
        'username': 'regular_user',
        'authority_level': 'L',
        'email': 'regular@example.com'
    },
    'emergency': {
        'username': 'emergency_worker',
        'authority_level': 'E',
        'email': 'emergency@example.com'
    },
    'organizer': {
        'username': 'organizer_user',
        'authority_level': 'O',
        'email': 'organizer@example.com'
    },
    'admin': {
        'username': 'admin_user',
        'authority_level': 'A',
        'email': 'admin@example.com'
    }
}

TEST_REPORTS = [
    {
        'title': 'Building Fire Emergency',
        'description': 'Fire reported in downtown building',
        'address': 'Zmaja od Bosne 5, Sarajevo',
        'latitude': 43.8563,
        'longitude': 18.4131
    },
    {
        'title': 'Flood Warning',
        'description': 'Rising water levels in river area',
        'address': 'Obala Kulina bana, Sarajevo',
        'latitude': 43.8587,
        'longitude': 18.4095
    },
    {
        'title': 'Medical Emergency',
        'description': 'Medical assistance needed',
        'address': 'Bolnička 25, Sarajevo'
    }
]

TEST_NEWS = [
    {
        'title': 'Safety Guidelines Update',
        'description': 'New safety guidelines for emergency situations',
        'address': 'Sarajevo Canton'
    },
    {
        'title': 'Emergency Contact Numbers',
        'description': 'Updated emergency contact information',
        'address': 'Bosnia and Herzegovina'
    }
]
