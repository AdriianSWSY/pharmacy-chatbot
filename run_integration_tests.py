#!/usr/bin/env python3
"""
Master test runner for WebSocket agent integration tests
Provides options to run individual test suites or all tests
"""

import asyncio
import sys
import argparse
from datetime import datetime
import subprocess


class TestRunner:
    def __init__(self):
        self.test_files = {
            "info": {
                "file": "test_info_agent_integration.py",
                "description": "InfoAgent tests for existing pharmacy queries",
            },
            "collection": {
                "file": "test_collection_agent_integration.py",
                "description": "CollectionAgent tests for new pharmacy registration",
            },
            "comprehensive": {
                "file": "test_websocket_comprehensive.py",
                "description": "Comprehensive test suite with edge cases and performance",
            },
        }

    def print_header(self, title: str):
        """Print formatted header"""
        print("\n" + "=" * 70)
        print(f"  {title}")
        print("=" * 70)

    def check_server_running(self) -> bool:
        """Check if the server is running"""
        import socket

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(("localhost", 8000))
        sock.close()

        return result == 0

    async def run_test_file(self, test_key: str) -> bool:
        """Run a specific test file"""
        test_info = self.test_files.get(test_key)
        if not test_info:
            print(f"❌ Unknown test key: {test_key}")
            return False

        self.print_header(f"Running {test_info['description']}")
        print(f"📝 Test file: {test_info['file']}")
        print(f"🕐 Started at: {datetime.now().strftime('%H:%M:%S')}")
        print("-" * 70)

        try:
            # Run the test file as a subprocess
            result = subprocess.run(
                [sys.executable, test_info["file"]], capture_output=False, text=True
            )

            if result.returncode == 0:
                print(f"\n✅ {test_info['description']} completed successfully")
                return True
            else:
                print(
                    f"\n❌ {test_info['description']} failed with code: {result.returncode}"
                )
                return False

        except FileNotFoundError:
            print(f"❌ Test file not found: {test_info['file']}")
            return False
        except Exception as e:
            print(f"❌ Error running test: {e}")
            return False

    async def run_all_tests(self):
        """Run all test suites in sequence"""
        self.print_header("Running All Integration Tests")

        results = {}
        test_order = ["info", "collection", "comprehensive"]

        for test_key in test_order:
            success = await self.run_test_file(test_key)
            results[test_key] = success

            # Add delay between test suites
            if test_key != test_order[-1]:
                print("\n⏳ Waiting 2 seconds before next test suite...")
                await asyncio.sleep(2)

        # Print final summary
        self.print_header("Final Test Summary")

        for test_key in test_order:
            test_info = self.test_files[test_key]
            status = "✅ PASS" if results.get(test_key) else "❌ FAIL"
            print(f"{status} - {test_info['description']}")

        all_passed = all(results.values())

        print("\n" + "=" * 70)
        if all_passed:
            print("🎉 All tests passed successfully!")
        else:
            failed_count = sum(1 for v in results.values() if not v)
            print(f"⚠️  {failed_count} test suite(s) failed")
        print("=" * 70)

        return all_passed

    async def interactive_menu(self):
        """Show interactive menu for test selection"""
        while True:
            self.print_header("WebSocket Integration Test Runner")
            print("\nAvailable test suites:")
            print("  1. InfoAgent Tests - Test existing pharmacy queries")
            print("  2. CollectionAgent Tests - Test new pharmacy registration")
            print("  3. Comprehensive Tests - Full suite with edge cases")
            print("  4. Run All Tests")
            print("  5. Exit")
            print("\n" + "-" * 70)

            choice = input("Select option (1-5): ").strip()

            if choice == "1":
                await self.run_test_file("info")
            elif choice == "2":
                await self.run_test_file("collection")
            elif choice == "3":
                await self.run_test_file("comprehensive")
            elif choice == "4":
                await self.run_all_tests()
            elif choice == "5":
                print("\n👋 Exiting test runner")
                break
            else:
                print("❌ Invalid choice. Please select 1-5")

            if choice in ["1", "2", "3", "4"]:
                input("\nPress Enter to continue...")

    async def main(self):
        """Main entry point"""
        parser = argparse.ArgumentParser(
            description="WebSocket Agent Integration Test Runner"
        )
        parser.add_argument(
            "--test",
            choices=["info", "collection", "comprehensive", "all"],
            help="Run specific test suite",
        )
        parser.add_argument("--no-check", action="store_true", help="Skip server check")

        args = parser.parse_args()

        # Check if server is running
        if not args.no_check:
            print("🔍 Checking if server is running...")
            if not self.check_server_running():
                print("❌ Server is not running on localhost:8000")
                print("Please start the server with: uv run python main.py")
                return False
            print("✅ Server is running")

        # Run tests based on arguments
        if args.test:
            if args.test == "all":
                return await self.run_all_tests()
            else:
                return await self.run_test_file(args.test)
        else:
            # Interactive mode
            await self.interactive_menu()
            return True


if __name__ == "__main__":
    runner = TestRunner()
    success = asyncio.run(runner.main())
    sys.exit(0 if success else 1)
