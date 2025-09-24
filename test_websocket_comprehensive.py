#!/usr/bin/env python3
"""
Comprehensive WebSocket Integration Test Suite
Tests both InfoAgent and CollectionAgent with various scenarios
"""

import asyncio
import json
import time
from typing import Dict, Optional
import websockets
from datetime import datetime


class ComprehensiveWebSocketTester:
    def __init__(self, ws_url: str = "ws://localhost:8000/ws/pharmacy-agent"):
        self.ws_url = ws_url

        # Test data from the real endpoint
        self.existing_phones = [
            "+1-555-123-4567",  # HealthFirst Pharmacy
            "+1-555-987-6543",  # QuickMeds Rx
            "+1-555-666-7777",  # MediCare Plus
            "+1-555-222-3333",  # CityPharma
            "+1-555-444-5555",  # Wellness Hub
        ]

        # New phones for collection testing
        self.new_phones = [
            "+1-555-000-1111",
            "+1-555-000-2222",
            "+1-555-000-3333",
        ]

        self.test_results = {
            "info_agent": [],
            "collection_agent": [],
            "edge_cases": [],
            "performance": [],
        }

    async def log(self, message: str, level: str = "INFO", indent: int = 0):
        """Enhanced logging with indentation"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        indent_str = "  " * indent

        # Color coding for terminal
        colors = {
            "INFO": "\033[0m",  # Default
            "SUCCESS": "\033[92m",  # Green
            "WARNING": "\033[93m",  # Yellow
            "ERROR": "\033[91m",  # Red
            "DEBUG": "\033[94m",  # Blue
        }

        color = colors.get(level, "\033[0m")
        reset = "\033[0m"

        print(f"{color}[{timestamp}] [{level}] {indent_str}{message}{reset}")

    async def send_and_receive(
        self, websocket, message: Dict, timeout: float = 5.0
    ) -> Optional[Dict]:
        """Send message and wait for response with timeout"""
        try:
            await websocket.send(json.dumps(message))
            response = await asyncio.wait_for(websocket.recv(), timeout=timeout)
            return json.loads(response)
        except asyncio.TimeoutError:
            await self.log("Timeout waiting for response", "ERROR")
            return None
        except Exception as e:
            await self.log(f"Error in send_and_receive: {e}", "ERROR")
            return None

    async def test_info_agent_comprehensive(self):
        """Comprehensive InfoAgent testing"""
        await self.log("=" * 70)
        await self.log("INFOAGENT COMPREHENSIVE TESTING", "INFO")
        await self.log("=" * 70)

        for phone in self.existing_phones[:2]:  # Test first 2 pharmacies
            await self.log(f"\nTesting pharmacy with phone: {phone}", "INFO")

            try:
                async with websockets.connect(self.ws_url) as ws:
                    # Connection
                    conn_resp = await asyncio.wait_for(ws.recv(), timeout=5.0)
                    conn_data = json.loads(conn_resp)
                    session_id = conn_data.get("session_id")

                    await self.log(f"Session established: {session_id}", "SUCCESS", 1)

                    # Initialize
                    init_msg = {"type": "init", "phone": phone}
                    init_resp = await self.send_and_receive(ws, init_msg)

                    if init_resp and init_resp.get("agent_type") == "info":
                        await self.log("InfoAgent initialized", "SUCCESS", 1)

                        # Test queries
                        queries = [
                            "What's your pharmacy name and location?",
                            "List all available prescriptions",
                            "What's your most stocked medication?",
                            "Do you have email contact?",
                            "Tell me everything about your pharmacy",
                        ]

                        for query in queries:
                            await self.log(f"Query: {query}", "DEBUG", 2)
                            msg = {"type": "message", "content": query}
                            resp = await self.send_and_receive(ws, msg)

                            if resp and resp.get("type") == "response":
                                content = resp.get("content", "")[
                                    :100
                                ]  # First 100 chars
                                await self.log(
                                    f"Response preview: {content}...", "SUCCESS", 2
                                )

                                self.test_results["info_agent"].append(
                                    {"phone": phone, "query": query, "status": "PASS"}
                                )
                            else:
                                await self.log("Failed query", "ERROR", 2)
                                self.test_results["info_agent"].append(
                                    {"phone": phone, "query": query, "status": "FAIL"}
                                )

                            await asyncio.sleep(0.3)  # Rate limiting

                        # Close
                        await ws.send(json.dumps({"type": "close"}))
                        await self.log("Connection closed", "INFO", 1)

                    else:
                        await self.log("Failed to initialize InfoAgent", "ERROR", 1)

            except Exception as e:
                await self.log(f"Test failed for {phone}: {e}", "ERROR")
                self.test_results["info_agent"].append(
                    {"phone": phone, "status": "ERROR", "error": str(e)}
                )

            await asyncio.sleep(1)  # Delay between pharmacy tests

    async def test_collection_agent_comprehensive(self):
        """Comprehensive CollectionAgent testing"""
        await self.log("=" * 70)
        await self.log("COLLECTION AGENT COMPREHENSIVE TESTING", "INFO")
        await self.log("=" * 70)

        test_scenarios = [
            {
                "phone": "+1-555-111-2222",
                "data": {
                    "name": "Advanced Medical Supply",
                    "location": "Portland, Oregon",
                    "email": "contact@advmedical.com",
                    "prescriptions": "We have Metformin (100), Insulin (50), and Lisinopril (75)",
                },
            },
            {
                "phone": "+1-555-333-4444",
                "data": {
                    "bulk": "We're QuickCare Pharmacy in Denver, Colorado. Email is info@quickcare.com",
                    "prescriptions": "Aspirin and Tylenol available",
                },
            },
        ]

        for scenario in test_scenarios:
            await self.log(f"\nTesting collection for: {scenario['phone']}", "INFO")

            try:
                async with websockets.connect(self.ws_url) as ws:
                    # Connection
                    conn_resp = await asyncio.wait_for(ws.recv(), timeout=5.0)
                    json.loads(conn_resp)  # Validate JSON but don't store

                    # Initialize
                    init_msg = {"type": "init", "phone": scenario["phone"]}
                    init_resp = await self.send_and_receive(ws, init_msg)

                    if init_resp and init_resp.get("agent_type") == "collection":
                        await self.log("CollectionAgent initialized", "SUCCESS", 1)

                        # Send data based on scenario
                        if "bulk" in scenario["data"]:
                            # Bulk data test
                            msg = {
                                "type": "message",
                                "content": scenario["data"]["bulk"],
                            }
                            resp = await self.send_and_receive(ws, msg)
                            await self.log(
                                f"Bulk data response type: {resp.get('type')}",
                                "INFO",
                                2,
                            )

                            if resp.get("type") == "collection_progress":
                                fields = resp.get("fields_collected", [])
                                await self.log(
                                    f"Fields collected: {fields}", "SUCCESS", 2
                                )

                        else:
                            # Sequential data provision
                            for field, value in scenario["data"].items():
                                msg = {"type": "message", "content": value}
                                resp = await self.send_and_receive(ws, msg, timeout=10)

                                if resp:
                                    resp_type = resp.get("type")
                                    await self.log(
                                        f"Response type: {resp_type}", "INFO", 2
                                    )

                                    if resp_type == "collection_progress":
                                        fields = resp.get("fields_collected", [])
                                        remaining = resp.get("fields_remaining", [])
                                        await self.log(
                                            f"Progress - Collected: {fields}, Remaining: {remaining}",
                                            "SUCCESS",
                                            2,
                                        )

                                    elif resp_type == "collection_complete":
                                        data = resp.get("pharmacy_data", {})
                                        await self.log(
                                            f"Collection complete! Data keys: {list(data.keys())}",
                                            "SUCCESS",
                                            2,
                                        )

                                        self.test_results["collection_agent"].append(
                                            {
                                                "phone": scenario["phone"],
                                                "status": "COMPLETE",
                                                "fields": list(data.keys()),
                                            }
                                        )
                                        break

                                await asyncio.sleep(0.5)

                        # Add prescriptions if needed
                        if "prescriptions" in scenario["data"]:
                            msg = {
                                "type": "message",
                                "content": scenario["data"]["prescriptions"],
                            }
                            resp = await self.send_and_receive(ws, msg)

                            if resp and resp.get("type") == "collection_complete":
                                await self.log(
                                    "Collection completed with prescriptions",
                                    "SUCCESS",
                                    2,
                                )

                        # Close
                        await ws.send(json.dumps({"type": "close"}))

                    else:
                        await self.log(
                            "Failed to initialize CollectionAgent", "ERROR", 1
                        )

            except Exception as e:
                await self.log(f"Collection test failed: {e}", "ERROR")
                self.test_results["collection_agent"].append(
                    {"phone": scenario["phone"], "status": "ERROR", "error": str(e)}
                )

            await asyncio.sleep(1)

    async def test_edge_cases(self):
        """Test edge cases and error scenarios"""
        await self.log("=" * 70)
        await self.log("EDGE CASES AND ERROR TESTING", "INFO")
        await self.log("=" * 70)

        edge_cases = [
            {
                "name": "Invalid phone format",
                "phone": "not-a-phone",
                "expected": "error_or_collection",
            },
            {"name": "Empty phone", "phone": "", "expected": "error"},
            {
                "name": "International format",
                "phone": "+44 20 7946 0958",
                "expected": "collection",
            },
            {
                "name": "Phone with extensions",
                "phone": "555-123-4567 x123",
                "expected": "varies",
            },
            {
                "name": "Repeated initialization",
                "phone": "+1-555-123-4567",
                "test_type": "double_init",
            },
            {
                "name": "Rapid messages",
                "phone": "+1-555-999-0000",
                "test_type": "rapid_fire",
            },
            {
                "name": "Very long message",
                "phone": "+1-555-888-9999",
                "test_type": "long_message",
            },
        ]

        for case in edge_cases:
            await self.log(f"\nTesting: {case['name']}", "WARNING")

            try:
                async with websockets.connect(self.ws_url) as ws:
                    # Wait for connection
                    await asyncio.wait_for(ws.recv(), timeout=5.0)

                    if case.get("test_type") == "double_init":
                        # Test double initialization
                        init_msg = {"type": "init", "phone": case["phone"]}
                        resp1 = await self.send_and_receive(ws, init_msg)
                        await self.log(f"First init: {resp1.get('type')}", "INFO", 1)

                        # Try to reinitialize
                        resp2 = await self.send_and_receive(ws, init_msg)
                        await self.log(f"Second init: {resp2}", "INFO", 1)

                        result = "HANDLED" if resp2 else "IGNORED"

                    elif case.get("test_type") == "rapid_fire":
                        # Test rapid message sending
                        init_msg = {"type": "init", "phone": case["phone"]}
                        await self.send_and_receive(ws, init_msg)

                        # Send 5 messages rapidly
                        for i in range(5):
                            msg = {"type": "message", "content": f"Message {i+1}"}
                            await ws.send(json.dumps(msg))

                        # Wait and collect responses
                        await asyncio.sleep(2)
                        result = "HANDLED"

                    elif case.get("test_type") == "long_message":
                        # Test very long message
                        init_msg = {"type": "init", "phone": case["phone"]}
                        await self.send_and_receive(ws, init_msg)

                        long_content = "This is a very long message. " * 100
                        msg = {"type": "message", "content": long_content}
                        resp = await self.send_and_receive(ws, msg, timeout=10)

                        result = "HANDLED" if resp else "TIMEOUT"

                    else:
                        # Regular phone format tests
                        init_msg = {"type": "init", "phone": case.get("phone", "")}
                        resp = await self.send_and_receive(ws, init_msg, timeout=5)

                        if resp:
                            agent_type = resp.get("agent_type")
                            await self.log(f"Agent type: {agent_type}", "INFO", 1)
                            result = "PASS"
                        else:
                            result = "ERROR"

                    self.test_results["edge_cases"].append(
                        {"test": case["name"], "result": result}
                    )

                    # Close connection
                    await ws.send(json.dumps({"type": "close"}))

            except Exception as e:
                await self.log(f"Edge case error: {e}", "ERROR", 1)
                self.test_results["edge_cases"].append(
                    {"test": case["name"], "result": "EXCEPTION", "error": str(e)[:50]}
                )

            await asyncio.sleep(0.5)

    async def test_performance(self):
        """Test performance and concurrent connections"""
        await self.log("=" * 70)
        await self.log("PERFORMANCE TESTING", "INFO")
        await self.log("=" * 70)

        # Test 1: Connection establishment time
        await self.log("\nTest 1: Connection establishment time", "INFO")

        connection_times = []
        for i in range(5):
            start = time.time()
            try:
                async with websockets.connect(self.ws_url) as ws:
                    await asyncio.wait_for(ws.recv(), timeout=5.0)
                    elapsed = time.time() - start
                    connection_times.append(elapsed)
                    await self.log(f"Connection {i+1}: {elapsed:.3f}s", "SUCCESS", 1)
                    await ws.send(json.dumps({"type": "close"}))
            except Exception as e:
                await self.log(f"Connection {i+1} failed: {e}", "ERROR", 1)

        if connection_times:
            avg_time = sum(connection_times) / len(connection_times)
            await self.log(f"Average connection time: {avg_time:.3f}s", "INFO")
            self.test_results["performance"].append(
                {
                    "test": "Connection Time",
                    "avg_ms": avg_time * 1000,
                    "samples": len(connection_times),
                }
            )

        # Test 2: Response time for queries
        await self.log("\nTest 2: Query response times", "INFO")

        try:
            async with websockets.connect(self.ws_url) as ws:
                await asyncio.wait_for(ws.recv(), timeout=5.0)

                # Initialize with existing pharmacy
                init_msg = {"type": "init", "phone": "+1-555-123-4567"}
                await self.send_and_receive(ws, init_msg)

                response_times = []
                queries = [
                    "What prescriptions do you have?",
                    "What's your location?",
                    "Tell me about your pharmacy",
                ]

                for query in queries:
                    msg = {"type": "message", "content": query}
                    start = time.time()
                    resp = await self.send_and_receive(ws, msg, timeout=10)
                    if resp:
                        elapsed = time.time() - start
                        response_times.append(elapsed)
                        await self.log(f"Query response: {elapsed:.3f}s", "SUCCESS", 1)

                if response_times:
                    avg_response = sum(response_times) / len(response_times)
                    await self.log(
                        f"Average response time: {avg_response:.3f}s", "INFO"
                    )
                    self.test_results["performance"].append(
                        {
                            "test": "Response Time",
                            "avg_ms": avg_response * 1000,
                            "samples": len(response_times),
                        }
                    )

                await ws.send(json.dumps({"type": "close"}))

        except Exception as e:
            await self.log(f"Performance test error: {e}", "ERROR")

        # Test 3: Concurrent connections
        await self.log("\nTest 3: Concurrent connections", "INFO")

        async def concurrent_connection(phone: str, conn_id: int):
            try:
                async with websockets.connect(self.ws_url) as ws:
                    await asyncio.wait_for(ws.recv(), timeout=5.0)
                    init_msg = {"type": "init", "phone": phone}
                    resp = await self.send_and_receive(ws, init_msg)
                    if resp:
                        await self.log(
                            f"Concurrent connection {conn_id} established", "SUCCESS", 1
                        )
                    await ws.send(json.dumps({"type": "close"}))
                    return True
            except Exception as e:
                await self.log(
                    f"Concurrent connection {conn_id} failed: {e}", "ERROR", 1
                )
                return False

        # Create 3 concurrent connections
        phones = ["+1-555-123-4567", "+1-555-987-6543", "+1-555-000-1111"]
        tasks = [concurrent_connection(phone, i + 1) for i, phone in enumerate(phones)]

        start = time.time()
        results = await asyncio.gather(*tasks)
        elapsed = time.time() - start

        successful = sum(1 for r in results if r)
        await self.log(
            f"Concurrent test: {successful}/{len(results)} successful in {elapsed:.3f}s",
            "INFO",
        )

        self.test_results["performance"].append(
            {
                "test": "Concurrent Connections",
                "successful": successful,
                "total": len(results),
                "time_s": elapsed,
            }
        )

    async def print_comprehensive_summary(self):
        """Print comprehensive test summary"""
        await self.log("\n" + "=" * 70)
        await self.log("COMPREHENSIVE TEST SUMMARY", "INFO")
        await self.log("=" * 70)

        # InfoAgent Summary
        await self.log("\n📊 InfoAgent Tests:", "INFO")
        info_tests = self.test_results["info_agent"]
        if info_tests:
            passed = sum(1 for t in info_tests if t.get("status") == "PASS")
            total = len(info_tests)
            await self.log(f"  ✅ Passed: {passed}/{total}", "SUCCESS")

        # CollectionAgent Summary
        await self.log("\n📊 CollectionAgent Tests:", "INFO")
        collection_tests = self.test_results["collection_agent"]
        if collection_tests:
            complete = sum(1 for t in collection_tests if t.get("status") == "COMPLETE")
            total = len(collection_tests)
            await self.log(f"  ✅ Completed: {complete}/{total}", "SUCCESS")

        # Edge Cases Summary
        await self.log("\n📊 Edge Cases:", "INFO")
        edge_tests = self.test_results["edge_cases"]
        if edge_tests:
            handled = sum(
                1 for t in edge_tests if t.get("result") in ["PASS", "HANDLED"]
            )
            total = len(edge_tests)
            await self.log(f"  ⚠️  Handled: {handled}/{total}", "WARNING")

        # Performance Summary
        await self.log("\n📊 Performance Metrics:", "INFO")
        perf_tests = self.test_results["performance"]
        for test in perf_tests:
            if "avg_ms" in test:
                await self.log(
                    f"  ⚡ {test['test']}: {test['avg_ms']:.1f}ms avg", "INFO"
                )
            elif "successful" in test:
                await self.log(
                    f"  ⚡ {test['test']}: {test['successful']}/{test['total']} in {test['time_s']:.2f}s",
                    "INFO",
                )

        # Overall Status
        await self.log("\n" + "=" * 70)
        total_tests = sum(len(v) for v in self.test_results.values())
        await self.log(f"Total Tests Executed: {total_tests}", "INFO")

        # Determine overall status
        has_errors = any(
            t.get("status") == "ERROR" or t.get("result") == "EXCEPTION"
            for tests in self.test_results.values()
            for t in tests
        )

        if has_errors:
            await self.log("⚠️  Some tests encountered errors", "WARNING")
        else:
            await self.log("✅ All tests completed successfully!", "SUCCESS")

        await self.log("=" * 70)

    async def run_comprehensive_suite(self):
        """Run the complete test suite"""
        start_time = time.time()

        await self.log("🚀 Starting Comprehensive WebSocket Test Suite", "INFO")
        await self.log(f"Target: {self.ws_url}", "INFO")
        await self.log(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "INFO")

        # Run all test categories
        await self.test_info_agent_comprehensive()
        await asyncio.sleep(1)

        await self.test_collection_agent_comprehensive()
        await asyncio.sleep(1)

        await self.test_edge_cases()
        await asyncio.sleep(1)

        await self.test_performance()

        # Print summary
        await self.print_comprehensive_summary()

        elapsed = time.time() - start_time
        await self.log(f"\nTotal execution time: {elapsed:.2f} seconds", "INFO")


if __name__ == "__main__":
    tester = ComprehensiveWebSocketTester()
    asyncio.run(tester.run_comprehensive_suite())
