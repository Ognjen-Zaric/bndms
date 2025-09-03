from django.core.management.base import BaseCommand
from django.test.utils import get_runner
from django.conf import settings
import sys


class Command(BaseCommand):
    help = 'Run comprehensive tests for BNDMS'

    def add_arguments(self, parser):
        parser.add_argument(
            '--unit',
            action='store_true',
            help='Run only unit tests',
        )
        parser.add_argument(
            '--integration',
            action='store_true',
            help='Run only integration tests',
        )
        parser.add_argument(
            '--system',
            action='store_true',
            help='Run only system tests',
        )
        parser.add_argument(
            '--coverage',
            action='store_true',
            help='Run tests with coverage report',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Verbose output',
        )

    def handle(self, *args, **options):
        """Run tests based on specified options"""
        
        # Determine which tests to run
        test_labels = []
        
        if options['unit']:
            test_labels.extend(['api.tests'])
            self.stdout.write(self.style.SUCCESS('Running unit tests...'))
        elif options['integration']:
            test_labels.extend(['front_end.tests'])
            self.stdout.write(self.style.SUCCESS('Running integration tests...'))
        elif options['system']:
            test_labels.extend(['tests.system_tests'])
            self.stdout.write(self.style.SUCCESS('Running system tests...'))
        else:
            # Run all tests
            test_labels.extend(['api.tests', 'front_end.tests', 'tests.system_tests'])
            self.stdout.write(self.style.SUCCESS('Running all tests...'))
        
        # Set up test runner
        TestRunner = get_runner(settings)
        test_runner = TestRunner(verbosity=2 if options['verbose'] else 1)
        
        # Run tests with coverage if requested
        if options['coverage']:
            try:
                import coverage
                cov = coverage.Coverage()
                cov.start()
                
                failures = test_runner.run_tests(test_labels)
                
                cov.stop()
                cov.save()
                
                self.stdout.write('\n' + '='*50)
                self.stdout.write('COVERAGE REPORT')
                self.stdout.write('='*50)
                cov.report()
                
            except ImportError:
                self.stdout.write(
                    self.style.ERROR(
                        'Coverage.py not installed. Install with: pip install coverage'
                    )
                )
                failures = test_runner.run_tests(test_labels)
        else:
            failures = test_runner.run_tests(test_labels)
        
        # Exit with appropriate code
        if failures:
            self.stdout.write(
                self.style.ERROR(f'\n{failures} test(s) failed!')
            )
            sys.exit(1)
        else:
            self.stdout.write(
                self.style.SUCCESS('\nAll tests passed!')
            )
            sys.exit(0)
