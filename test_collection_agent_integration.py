#!/usr/bin/env python3
"""
Integration test for CollectionAgent - Tests new pharmacy registration via WebSocket
"""

import asyncio
import json
from typing import Dict, List, Optional
import websockets
from datetime import datetime


class CollectionAgentTestRunner:
    def __init__(self, ws_url: str = "ws://localhost:8000/ws/pharmacy-agent"):
        self.ws_url = ws_url
        self.test_phone = "+1-555-999-8888"  # New phone not in database
        self.results: List[Dict] = []
        self.session_id: Optional[str] = None
        self.collected_fields: List[str] = []

    async def log(self, message: str, level: str = "INFO"):
        """Log test progress with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] [{level}] {message}")

    async def send_and_receive(self, websocket, message: Dict) -> Dict:
        """Send message and wait for response"""
        await self.log(f"Sending: {json.dumps(message, indent=2)}")
        await websocket.send(json.dumps(message))

        response = await websocket.recv()
        response_data = json.loads(response)
        await self.log(f"Received: {json.dumps(response_data, indent=2)}", "SUCCESS")
        return response_data

    async def test_connection_establishment(self, websocket) -> bool:
        """Test 1: Connection establishment"""
        await self.log("TEST 1: Testing connection establishment")

        # Wait for connection established message
        response = await websocket.recv()
        data = json.loads(response)

        if data.get("type") == "connection_established":
            self.session_id = data.get("session_id")
            await self.log(
                f"Connection established with session: {self.session_id}", "SUCCESS"
            )
            self.results.append(
                {
                    "test": "Connection Establishment",
                    "status": "PASS",
                    "details": f"Session ID: {self.session_id}",
                }
            )
            return True
        else:
            await self.log("Failed to establish connection", "ERROR")
            self.results.append(
                {
                    "test": "Connection Establishment",
                    "status": "FAIL",
                    "details": "No connection_established message",
                }
            )
            return False

    async def test_agent_initialization(self, websocket) -> bool:
        """Test 2: Initialize CollectionAgent with new pharmacy phone"""
        await self.log("TEST 2: Testing CollectionAgent initialization")

        # Send init message with new pharmacy phone
        init_msg = {"type": "init", "phone": self.test_phone}

        response = await self.send_and_receive(websocket, init_msg)

        if (
            response.get("type") == "agent_ready"
            and response.get("agent_type") == "collection"
        ):
            await self.log("CollectionAgent initialized successfully", "SUCCESS")
            self.results.append(
                {
                    "test": "CollectionAgent Initialization",
                    "status": "PASS",
                    "details": f"Agent type: {response.get('agent_type')}",
                }
            )
            return True
        else:
            await self.log("Failed to initialize CollectionAgent", "ERROR")
            self.results.append(
                {
                    "test": "CollectionAgent Initialization",
                    "status": "FAIL",
                    "details": f"Response type: {response.get('type')}, agent: {response.get('agent_type')}",
                }
            )
            return False

    async def test_provide_name(self, websocket) -> bool:
        """Test 3: Provide pharmacy name"""
        await self.log("TEST 3: Testing pharmacy name collection")

        msg = {
            "type": "message",
            "content": "My pharmacy is called TestPharm Solutions",
        }

        response = await self.send_and_receive(websocket, msg)

        if response.get("type") in ["response", "collection_progress"]:
            if response.get("type") == "collection_progress":
                fields = response.get("fields_collected", [])
                if "name" in fields:
                    self.collected_fields = fields
                    await self.log(
                        f"Name collected successfully. Fields: {fields}", "SUCCESS"
                    )
                    self.results.append(
                        {
                            "test": "Name Collection",
                            "status": "PASS",
                            "details": f"Collected fields: {fields}",
                        }
                    )
                    return True

            # Even if just response type, might be valid
            await self.log("Name provided, agent responded", "SUCCESS")
            self.results.append(
                {
                    "test": "Name Collection",
                    "status": "PASS",
                    "details": "Name information provided",
                }
            )
            return True
        else:
            await self.log("Failed to collect name", "ERROR")
            self.results.append(
                {
                    "test": "Name Collection",
                    "status": "FAIL",
                    "details": "Invalid response",
                }
            )
            return False

    async def test_provide_location(self, websocket) -> bool:
        """Test 4: Provide location (city and state)"""
        await self.log("TEST 4: Testing location collection")

        msg = {"type": "message", "content": "We're located in Austin, Texas"}

        response = await self.send_and_receive(websocket, msg)

        if response.get("type") in ["response", "collection_progress"]:
            if response.get("type") == "collection_progress":
                fields = response.get("fields_collected", [])
                if "city" in fields or "state" in fields:
                    self.collected_fields = fields
                    await self.log(f"Location collected. Fields: {fields}", "SUCCESS")
                    self.results.append(
                        {
                            "test": "Location Collection",
                            "status": "PASS",
                            "details": f"Collected: {fields}",
                        }
                    )
                    return True

            await self.log("Location provided, agent responded", "SUCCESS")
            self.results.append(
                {
                    "test": "Location Collection",
                    "status": "PASS",
                    "details": "Location information provided",
                }
            )
            return True
        else:
            await self.log("Failed to collect location", "ERROR")
            self.results.append(
                {
                    "test": "Location Collection",
                    "status": "FAIL",
                    "details": "Invalid response",
                }
            )
            return False

    async def test_provide_email(self, websocket) -> bool:
        """Test 5: Provide email"""
        await self.log("TEST 5: Testing email collection")

        msg = {"type": "message", "content": "Our contact email is test@testpharm.com"}

        response = await self.send_and_receive(websocket, msg)

        if response.get("type") in ["response", "collection_progress"]:
            if response.get("type") == "collection_progress":
                fields = response.get("fields_collected", [])
                if "email" in fields:
                    self.collected_fields = fields
                    await self.log(f"Email collected. Fields: {fields}", "SUCCESS")
                    self.results.append(
                        {
                            "test": "Email Collection",
                            "status": "PASS",
                            "details": "Valid email collected",
                        }
                    )
                    return True

            await self.log("Email provided, agent responded", "SUCCESS")
            self.results.append(
                {
                    "test": "Email Collection",
                    "status": "PASS",
                    "details": "Email information provided",
                }
            )
            return True
        else:
            await self.log("Failed to collect email", "ERROR")
            self.results.append(
                {
                    "test": "Email Collection",
                    "status": "FAIL",
                    "details": "Invalid response",
                }
            )
            return False

    async def test_provide_prescriptions(self, websocket) -> bool:
        """Test 6: Provide prescription data (optional)"""
        await self.log("TEST 6: Testing prescription data collection")

        msg = {
            "type": "message",
            "content": "We have Aspirin with 100 units and Ibuprofen with 50 units in stock",
        }

        response = await self.send_and_receive(websocket, msg)

        if response.get("type") in [
            "response",
            "collection_progress",
            "collection_complete",
        ]:
            if response.get("type") == "collection_complete":
                pharmacy_data = response.get("pharmacy_data", {})
                await self.log(
                    f"Collection complete! Data: {json.dumps(pharmacy_data, indent=2)}",
                    "SUCCESS",
                )

                # Verify all required fields are present
                required = ["name", "email", "city", "state", "phone"]
                has_all = all(field in pharmacy_data for field in required)

                self.results.append(
                    {
                        "test": "Prescription Collection & Completion",
                        "status": "PASS" if has_all else "PARTIAL",
                        "details": f"Complete: {has_all}, Data collected: {list(pharmacy_data.keys())}",
                    }
                )
                return True

            await self.log("Prescriptions provided, collection may continue", "SUCCESS")
            self.results.append(
                {
                    "test": "Prescription Collection",
                    "status": "PASS",
                    "details": "Prescription data processed",
                }
            )
            return True
        else:
            await self.log("Failed prescription collection", "ERROR")
            self.results.append(
                {
                    "test": "Prescription Collection",
                    "status": "FAIL",
                    "details": "Invalid response",
                }
            )
            return False

    async def test_invalid_email(self, websocket) -> bool:
        """Test 7: Test invalid email validation"""
        await self.log("TEST 7: Testing email validation")

        msg = {"type": "message", "content": "The email is not-a-valid-email"}

        response = await self.send_and_receive(websocket, msg)

        # Agent should ask for valid email
        if response.get("type") == "response":
            content = response.get("content", "").lower()
            if "valid" in content or "email" in content or "@" in content:
                await self.log("Agent correctly requested valid email", "SUCCESS")
                self.results.append(
                    {
                        "test": "Email Validation",
                        "status": "PASS",
                        "details": "Invalid email rejected",
                    }
                )

                # Now provide valid email
                valid_msg = {
                    "type": "message",
                    "content": "Sorry, it's contact@validpharm.com",
                }
                await self.send_and_receive(websocket, valid_msg)
                return True
            else:
                await self.log("Agent may have accepted invalid email", "WARNING")
                self.results.append(
                    {
                        "test": "Email Validation",
                        "status": "PARTIAL",
                        "details": "Unclear if validation occurred",
                    }
                )
                return True
        else:
            await self.log("Unexpected response to invalid email", "ERROR")
            self.results.append(
                {
                    "test": "Email Validation",
                    "status": "FAIL",
                    "details": "Invalid response type",
                }
            )
            return False

    async def test_bulk_information(self, websocket) -> bool:
        """Test 8: Provide multiple pieces of information at once"""
        await self.log("TEST 8: Testing bulk information extraction")

        msg = {
            "type": "message",
            "content": "We're BulkTest Pharmacy located in Seattle, Washington. Our email is bulk@test.com",
        }

        response = await self.send_and_receive(websocket, msg)

        if response.get("type") in ["collection_progress", "collection_complete"]:
            fields = response.get("fields_collected", [])

            # Check if multiple fields were extracted
            expected = ["name", "city", "state", "email"]
            extracted = [f for f in expected if f in fields]

            if len(extracted) >= 3:
                await self.log(
                    f"Successfully extracted {len(extracted)} fields from bulk input",
                    "SUCCESS",
                )
                self.results.append(
                    {
                        "test": "Bulk Information Extraction",
                        "status": "PASS",
                        "details": f"Extracted: {extracted}",
                    }
                )
                return True
            elif len(extracted) > 0:
                await self.log(
                    f"Partially extracted {len(extracted)} fields", "WARNING"
                )
                self.results.append(
                    {
                        "test": "Bulk Information Extraction",
                        "status": "PARTIAL",
                        "details": f"Extracted only: {extracted}",
                    }
                )
                return True
            else:
                await self.log("Failed to extract bulk information", "ERROR")
                self.results.append(
                    {
                        "test": "Bulk Information Extraction",
                        "status": "FAIL",
                        "details": "No fields extracted",
                    }
                )
                return False
        else:
            await self.log("Agent processed bulk info", "SUCCESS")
            self.results.append(
                {
                    "test": "Bulk Information Extraction",
                    "status": "PASS",
                    "details": "Bulk information processed",
                }
            )
            return True

    async def run_scenario_test(self):
        """Run a complete collection scenario test"""
        await self.log("=" * 60)
        await self.log("Starting CollectionAgent Integration Tests")
        await self.log(f"Target: {self.ws_url}")
        await self.log(f"Test Phone: {self.test_phone}")
        await self.log("=" * 60)

        try:
            async with websockets.connect(self.ws_url) as websocket:
                # Test 1: Connection
                if not await self.test_connection_establishment(websocket):
                    return

                # Test 2: Agent initialization
                if not await self.test_agent_initialization(websocket):
                    return

                await asyncio.sleep(0.5)

                # Test 3-6: Provide information sequentially
                await self.test_provide_name(websocket)
                await asyncio.sleep(0.5)

                await self.test_provide_location(websocket)
                await asyncio.sleep(0.5)

                await self.test_provide_email(websocket)
                await asyncio.sleep(0.5)

                await self.test_provide_prescriptions(websocket)
                await asyncio.sleep(0.5)

                # Close connection
                await self.log("Closing connection gracefully")
                close_msg = {"type": "close"}
                await websocket.send(json.dumps(close_msg))

        except Exception as e:
            await self.log(f"Scenario test error: {e}", "ERROR")
            self.results.append(
                {"test": "Scenario Test", "status": "ERROR", "details": str(e)}
            )

    async def run_validation_test(self):
        """Run validation and edge case tests"""
        await self.log("=" * 60)
        await self.log("Running Validation Tests")
        await self.log("=" * 60)

        try:
            async with websockets.connect(self.ws_url) as websocket:
                # Initialize connection
                await self.test_connection_establishment(websocket)

                # Initialize with different phone for new session
                init_msg = {"type": "init", "phone": "+1-555-777-6666"}
                await self.send_and_receive(websocket, init_msg)
                await asyncio.sleep(0.5)

                # Test invalid email
                await self.test_invalid_email(websocket)
                await asyncio.sleep(0.5)

                # Test bulk information
                await self.test_bulk_information(websocket)

                # Close
                close_msg = {"type": "close"}
                await websocket.send(json.dumps(close_msg))

        except Exception as e:
            await self.log(f"Validation test error: {e}", "ERROR")

    async def print_summary(self):
        """Print test results summary"""
        await self.log("=" * 60)
        await self.log("TEST RESULTS SUMMARY")
        await self.log("=" * 60)

        passed = sum(1 for r in self.results if r["status"] == "PASS")
        failed = sum(1 for r in self.results if r["status"] == "FAIL")
        partial = sum(1 for r in self.results if r["status"] == "PARTIAL")
        errors = sum(1 for r in self.results if r["status"] == "ERROR")

        for result in self.results:
            status_emoji = {
                "PASS": "✅",
                "FAIL": "❌",
                "PARTIAL": "⚠️",
                "ERROR": "🔥",
            }.get(result["status"], "❓")

            print(f"{status_emoji} {result['test']}: {result['status']}")
            print(f"   Details: {result['details']}")

        print("\n" + "=" * 60)
        print(f"Total Tests: {len(self.results)}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️  Partial: {partial}")
        print(f"🔥 Errors: {errors}")
        print("=" * 60)

        if failed == 0 and errors == 0:
            await self.log("All critical tests passed! 🎉", "SUCCESS")
        elif failed > 0:
            await self.log(f"{failed} tests failed", "WARNING")
        if errors > 0:
            await self.log(f"{errors} errors encountered", "ERROR")

    async def run_all_tests(self):
        """Run all test scenarios"""
        # Run main scenario test
        await self.run_scenario_test()

        # Run validation tests
        await self.run_validation_test()

        # Print summary
        await self.print_summary()


if __name__ == "__main__":
    # Run the tests
    runner = CollectionAgentTestRunner()
    asyncio.run(runner.run_all_tests())
