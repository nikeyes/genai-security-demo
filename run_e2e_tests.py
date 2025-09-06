#!/usr/bin/env python3
"""
Script to run E2E tests for the web UI.
This script runs the tests in headless mode by default.
Use --headed to run with browser visible.
"""

import subprocess
import sys
import argparse


def main():
    parser = argparse.ArgumentParser(description='Run E2E tests for the web UI')
    parser.add_argument('--headed', action='store_true', help='Run tests with browser visible')
    parser.add_argument('--browser', default='chromium', choices=['chromium', 'firefox', 'webkit'], help='Browser to use for testing')
    args = parser.parse_args()

    # Base pytest command
    cmd = [
        'uv',
        'run',
        'pytest',
        'tests/e2e_tests/',
        '-v',
        '-s',  # Don't capture output so we can see server startup
        f'--browser={args.browser}',
    ]

    if args.headed:
        cmd.append('--headed')

    print(f'Running E2E tests with command: {" ".join(cmd)}')
    print('Note: This will start the web server automatically')

    try:
        subprocess.run(cmd, check=True)
        print('✅ All E2E tests passed!')
        return 0
    except subprocess.CalledProcessError as e:
        print(f'❌ E2E tests failed with exit code {e.returncode}')
        return e.returncode
    except KeyboardInterrupt:
        print('\n⚠️ Tests interrupted by user')
        return 1


if __name__ == '__main__':
    sys.exit(main())
