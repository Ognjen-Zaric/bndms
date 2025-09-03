#!/usr/bin/env python
"""
BNDMS Test Runner Script

This script provides easy commands to run different types of tests:
- Unit tests (models, utilities)
- Integration tests (views, forms)
- System tests (end-to-end workflows)

Usage:
    python run_tests.py [options]

Options:
    --unit          Run only unit tests
    --integration   Run only integration tests  
    --system        Run only system tests
    --all           Run all tests (default)
    --coverage      Generate coverage report
    --fast          Skip slow tests
"""

import os
import sys
import subprocess
import argparse


def main():
    parser = argparse.ArgumentParser(description='BNDMS Test Runner')
    parser.add_argument('--unit', action='store_true', help='Run unit tests only')
    parser.add_argument('--integration', action='store_true', help='Run integration tests only')
    parser.add_argument('--system', action='store_true', help='Run system tests only')
    parser.add_argument('--all', action='store_true', help='Run all tests')
    parser.add_argument('--coverage', action='store_true', help='Generate coverage report')
    parser.add_argument('--fast', action='store_true', help='Skip slow tests')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Default to all tests if no specific test type is selected
    if not any([args.unit, args.integration, args.system]):
        args.all = True
    
    print("🧪 BNDMS Test Suite")
    print("=" * 50)
    
    # Determine test commands
    commands = []
    
    if args.unit or args.all:
        print("📊 Running Unit Tests...")
        commands.append(['python', 'manage.py', 'test', 'api.tests'])
    
    if args.integration or args.all:
        print("🔗 Running Integration Tests...")
        commands.append(['python', 'manage.py', 'test', 'front_end.tests'])
    
    if args.system or args.all:
        print("🌐 Running System Tests...")
        commands.append(['python', 'manage.py', 'test', 'tests.system_tests'])
    
    # Add verbosity if requested
    verbosity = ['--verbosity', '2'] if args.verbose else ['--verbosity', '1']
    
    # Run tests
    total_failures = 0
    
    for command in commands:
        full_command = command + verbosity
        print(f"\n▶️  Running: {' '.join(full_command)}")
        print("-" * 40)
        
        result = subprocess.run(full_command, capture_output=False)
        
        if result.returncode != 0:
            total_failures += 1
            print(f"❌ Test suite failed: {' '.join(command)}")
        else:
            print(f"✅ Test suite passed: {' '.join(command)}")
    
    # Summary
    print("\n" + "=" * 50)
    if total_failures == 0:
        print("🎉 All test suites passed!")
        print("\n📋 Test Summary:")
        if args.unit or args.all:
            print("   ✅ Unit Tests: PASSED")
        if args.integration or args.all:
            print("   ✅ Integration Tests: PASSED")
        if args.system or args.all:
            print("   ✅ System Tests: PASSED")
        
        print("\n💡 Next Steps:")
        print("   - Run with --coverage to see code coverage")
        print("   - Run individual test classes for focused testing")
        print("   - Add more tests as you develop new features")
        
        sys.exit(0)
    else:
        print(f"❌ {total_failures} test suite(s) failed!")
        print("\n🔍 Debugging Tips:")
        print("   - Run tests with --verbose for more details")
        print("   - Check the error messages above")
        print("   - Run individual failing tests for isolation")
        
        sys.exit(1)


if __name__ == '__main__':
    main()
