#!/usr/bin/env python3
"""
Integration test for InfoAgent - Tests existing pharmacy queries via WebSocket
"""

import asyncio
import json
from typing import Dict, List, Optional
import websockets
from datetime import datetime


class InfoAgentTestRunner:
    def __init__(self, ws_url: str = "ws://localhost:8000/ws/pharmacy-agent"):
        self.ws_url = ws_url
        self.test_phone = "+1-555-123-4567"  # HealthFirst Pharmacy
        self.results: List[Dict] = []
        self.session_id: Optional[str] = None

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
        """Test 2: Initialize InfoAgent with existing pharmacy phone"""
        await self.log("TEST 2: Testing InfoAgent initialization")

        # Send init message with existing pharmacy phone
        init_msg = {"type": "init", "phone": self.test_phone}

        response = await self.send_and_receive(websocket, init_msg)

        if (
            response.get("type") == "agent_ready"
            and response.get("agent_type") == "info"
        ):
            await self.log("InfoAgent initialized successfully", "SUCCESS")
            self.results.append(
                {
                    "test": "InfoAgent Initialization",
                    "status": "PASS",
                    "details": f"Agent type: {response.get('agent_type')}",
                }
            )
            return True
        else:
            await self.log("Failed to initialize InfoAgent", "ERROR")
            self.results.append(
                {
                    "test": "InfoAgent Initialization",
                    "status": "FAIL",
                    "details": f"Response type: {response.get('type')}",
                }
            )
            return False

    async def test_prescription_query(self, websocket) -> bool:
        """Test 3: Query prescription information"""
        await self.log("TEST 3: Testing prescription query")

        query_msg = {
            "type": "message",
            "content": "What prescriptions do you have available?",
        }

        response = await self.send_and_receive(websocket, query_msg)

        if response.get("type") == "response":
            content = response.get("content", "")
            # Check if response mentions expected drugs
            expected_drugs = ["Lisinopril", "Atorvastatin", "Metformin"]
            drugs_found = [
                drug for drug in expected_drugs if drug.lower() in content.lower()
            ]

            if drugs_found:
                await self.log(
                    f"Prescription query successful. Found drugs: {drugs_found}",
                    "SUCCESS",
                )
                self.results.append(
                    {
                        "test": "Prescription Query",
                        "status": "PASS",
                        "details": f"Found {len(drugs_found)} expected drugs",
                    }
                )
                return True
            else:
                await self.log("Response doesn't contain prescription info", "WARNING")
                self.results.append(
                    {
                        "test": "Prescription Query",
                        "status": "PARTIAL",
                        "details": "Response received but no drugs mentioned",
                    }
                )
                return True
        else:
            await self.log("Failed to get prescription response", "ERROR")
            self.results.append(
                {
                    "test": "Prescription Query",
                    "status": "FAIL",
                    "details": "Invalid response type",
                }
            )
            return False

    async def test_pharmacy_details(self, websocket) -> bool:
        """Test 4: Query pharmacy details"""
        await self.log("TEST 4: Testing pharmacy details query")

        query_msg = {
            "type": "message",
            "content": "Can you tell me the pharmacy's name, email and location?",
        }

        response = await self.send_and_receive(websocket, query_msg)

        if response.get("type") == "response":
            content = response.get("content", "")
            # Check for expected pharmacy details
            expected_info = ["HealthFirst", "New York", "NY", "contact@healthfirst.com"]
            info_found = [
                info for info in expected_info if info.lower() in content.lower()
            ]

            if info_found:
                await self.log(
                    f"Pharmacy details query successful. Found: {info_found}", "SUCCESS"
                )
                self.results.append(
                    {
                        "test": "Pharmacy Details Query",
                        "status": "PASS",
                        "details": f"Found {len(info_found)}/{len(expected_info)} expected details",
                    }
                )
                return True
            else:
                await self.log("Response doesn't contain pharmacy details", "WARNING")
                self.results.append(
                    {
                        "test": "Pharmacy Details Query",
                        "status": "PARTIAL",
                        "details": "Response received but details missing",
                    }
                )
                return True
        else:
            await self.log("Failed to get pharmacy details", "ERROR")
            self.results.append(
                {
                    "test": "Pharmacy Details Query",
                    "status": "FAIL",
                    "details": "Invalid response type",
                }
            )
            return False

    async def test_specific_drug_query(self, websocket) -> bool:
        """Test 5: Query specific drug availability"""
        await self.log("TEST 5: Testing specific drug query")

        query_msg = {"type": "message", "content": "Do you have Lisinopril? How many?"}

        response = await self.send_and_receive(websocket, query_msg)

        if response.get("type") == "response":
            content = response.get("content", "")
            # Check if response mentions Lisinopril and count (42)
            has_drug = "lisinopril" in content.lower()
            has_count = "42" in content or "forty-two" in content.lower()

            if has_drug:
                await self.log("Specific drug query successful", "SUCCESS")
                self.results.append(
                    {
                        "test": "Specific Drug Query",
                        "status": "PASS" if has_count else "PARTIAL",
                        "details": f"Drug mentioned: {has_drug}, Count mentioned: {has_count}",
                    }
                )
                return True
            else:
                await self.log("Drug not mentioned in response", "WARNING")
                self.results.append(
                    {
                        "test": "Specific Drug Query",
                        "status": "FAIL",
                        "details": "Drug not mentioned",
                    }
                )
                return False
        else:
            await self.log("Failed to get drug query response", "ERROR")
            self.results.append(
                {
                    "test": "Specific Drug Query",
                    "status": "FAIL",
                    "details": "Invalid response type",
                }
            )
            return False

    async def test_conversation_context(self, websocket) -> bool:
        """Test 6: Test conversation memory/context"""
        await self.log("TEST 6: Testing conversation context")

        # First message
        msg1 = {"type": "message", "content": "What's your most popular drug?"}
        await self.send_and_receive(websocket, msg1)

        # Second message referencing context
        msg2 = {
            "type": "message",
            "content": "How many units of that drug do you have?",
        }
        response2 = await self.send_and_receive(websocket, msg2)

        if response2.get("type") == "response":
            content = response2.get("content", "")
            # Check if agent maintains context (should mention Lisinopril as it has 42 units)
            if any(
                word in content.lower() for word in ["lisinopril", "42", "forty-two"]
            ):
                await self.log("Conversation context maintained", "SUCCESS")
                self.results.append(
                    {
                        "test": "Conversation Context",
                        "status": "PASS",
                        "details": "Agent remembers previous conversation",
                    }
                )
                return True
            else:
                await self.log("Context may not be maintained", "WARNING")
                self.results.append(
                    {
                        "test": "Conversation Context",
                        "status": "PARTIAL",
                        "details": "Response received but context unclear",
                    }
                )
                return True
        else:
            await self.log("Failed context test", "ERROR")
            self.results.append(
                {
                    "test": "Conversation Context",
                    "status": "FAIL",
                    "details": "Invalid response",
                }
            )
            return False

    async def run_all_tests(self):
        """Run all InfoAgent integration tests"""
        await self.log("=" * 60)
        await self.log("Starting InfoAgent Integration Tests")
        await self.log(f"Target: {self.ws_url}")
        await self.log(f"Test Phone: {self.test_phone}")
        await self.log("=" * 60)

        try:
            async with websockets.connect(self.ws_url) as websocket:
                # Run tests in sequence
                tests = [
                    self.test_connection_establishment,
                    self.test_agent_initialization,
                    self.test_prescription_query,
                    self.test_pharmacy_details,
                    self.test_specific_drug_query,
                    self.test_conversation_context,
                ]

                for test in tests:
                    result = await test(websocket)
                    if not result and test.__name__ in [
                        "test_connection_establishment",
                        "test_agent_initialization",
                    ]:
                        await self.log("Critical test failed, stopping tests", "ERROR")
                        break
                    await asyncio.sleep(0.5)  # Small delay between tests

                # Send close message
                await self.log("Closing connection gracefully")
                close_msg = {"type": "close"}
                await websocket.send(json.dumps(close_msg))

        except Exception as e:
            await self.log(f"Test suite error: {e}", "ERROR")
            self.results.append(
                {"test": "Test Suite", "status": "ERROR", "details": str(e)}
            )

        # Print test summary
        await self.print_summary()

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


if __name__ == "__main__":
    # Run the tests
    runner = InfoAgentTestRunner()
    asyncio.run(runner.run_all_tests())
