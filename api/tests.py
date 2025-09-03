from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from decimal import Decimal
from api.models import Account, Report, Task, News
from django.utils import timezone


class AccountModelTest(TestCase):
    """Unit tests for Account model"""
    
    def setUp(self):
        self.account_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'phone_number': '+387603456789',
            'address': 'Test Address, Sarajevo',
            'authority_level': 'L'
        }
    
    def test_account_creation(self):
        """Test creating a new account"""
        account = Account.objects.create_user(**self.account_data)
        self.assertEqual(account.username, 'testuser')
        self.assertEqual(account.authority_level, 'L')
        self.assertTrue(account.is_active)
        self.assertFalse(account.is_deleted)
    
    def test_account_string_representation(self):
        """Test string representation of account"""
        account = Account.objects.create_user(**self.account_data)
        self.assertEqual(str(account), 'testuser')
    
    def test_authority_level_choices(self):
        """Test authority level validation"""
        # Valid authority levels
        valid_levels = ['N', 'L', 'E', 'O', 'A']
        for level in valid_levels:
            account_data = self.account_data.copy()
            account_data['username'] = f'user_{level}'
            account_data['authority_level'] = level
            account = Account.objects.create_user(**account_data)
            self.assertEqual(account.authority_level, level)
    
    def test_default_authority_level(self):
        """Test default authority level is 'L'"""
        account_data = self.account_data.copy()
        del account_data['authority_level']
        account = Account.objects.create_user(**account_data)
        self.assertEqual(account.authority_level, 'L')


class ReportModelTest(TestCase):
    """Unit tests for Report model"""
    
    def setUp(self):
        self.account = Account.objects.create_user(
            username='reporter',
            email='reporter@example.com',
            authority_level='L'
        )
        self.report_data = {
            'account': self.account,
            'title': 'Test Emergency',
            'description': 'Test emergency description',
            'address': 'Kolodvorska 13, Sarajevo',
            'latitude': Decimal('43.8563'),
            'longitude': Decimal('18.4131')
        }
    
    def test_report_creation(self):
        """Test creating a new report"""
        report = Report.objects.create(**self.report_data)
        self.assertEqual(report.title, 'Test Emergency')
        self.assertEqual(report.account, self.account)
        self.assertEqual(report.status, 'N')  # Default status
        self.assertFalse(report.has_task)  # Default value
        self.assertFalse(report.is_deleted)
    
    def test_report_string_representation(self):
        """Test string representation of report"""
        report = Report.objects.create(**self.report_data)
        self.assertEqual(str(report), 'Test Emergency')
    
    def test_report_coordinates(self):
        """Test report coordinate fields"""
        report = Report.objects.create(**self.report_data)
        self.assertEqual(report.latitude, Decimal('43.8563'))
        self.assertEqual(report.longitude, Decimal('18.4131'))
    
    def test_report_without_coordinates(self):
        """Test report creation without coordinates"""
        report_data = self.report_data.copy()
        del report_data['latitude']
        del report_data['longitude']
        report = Report.objects.create(**report_data)
        self.assertIsNone(report.latitude)
        self.assertIsNone(report.longitude)


class TaskModelTest(TestCase):
    """Unit tests for Task model"""
    
    def setUp(self):
        self.reporter = Account.objects.create_user(
            username='reporter',
            email='reporter@example.com',
            authority_level='L'
        )
        self.emergency_worker = Account.objects.create_user(
            username='emergency_worker',
            email='ew@example.com',
            authority_level='E'
        )
        self.report = Report.objects.create(
            account=self.reporter,
            title='Test Emergency',
            description='Test description',
            address='Test Address'
        )
        self.task_data = {
            'username': self.emergency_worker,
            'report': self.report,
            'title': 'Test Task',
            'descirption': 'Test task description',
            'status': 'I'
        }
    
    def test_task_creation(self):
        """Test creating a new task"""
        task = Task.objects.create(**self.task_data)
        self.assertEqual(task.title, 'Test Task')
        self.assertEqual(task.username, self.emergency_worker)
        self.assertEqual(task.report, self.report)
        self.assertEqual(task.status, 'I')
    
    def test_task_string_representation(self):
        """Test string representation of task"""
        task = Task.objects.create(**self.task_data)
        self.assertEqual(str(task), 'Test Task')
    
    def test_task_default_status(self):
        """Test default task status"""
        task_data = self.task_data.copy()
        del task_data['status']
        task = Task.objects.create(**task_data)
        self.assertEqual(task.status, 'N')  # Default status


class NewsModelTest(TestCase):
    """Unit tests for News model"""
    
    def setUp(self):
        self.organizer = Account.objects.create_user(
            username='organizer',
            email='organizer@example.com',
            authority_level='O'
        )
        self.news_data = {
            'account': self.organizer,
            'title': 'Test News',
            'description': 'Test news description',
            'address': 'Sarajevo Area',
            'status': 'N'
        }
    
    def test_news_creation(self):
        """Test creating a news item"""
        news = News.objects.create(**self.news_data)
        self.assertEqual(news.title, 'Test News')
        self.assertEqual(news.account, self.organizer)
        self.assertEqual(news.status, 'N')
        self.assertIsNotNone(news.date)
    
    def test_news_string_representation(self):
        """Test string representation of news"""
        news = News.objects.create(**self.news_data)
        self.assertEqual(str(news), 'Test News')