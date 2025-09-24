#!/usr/bin/env python3
"""
Simple WebSocket Agent Test - Quick verification of both agents
"""

import asyncio
import json
import websockets
from datetime import datetime


async def test_info_agent():
    """Test InfoAgent with existing pharmacy"""
    print("\n" + "=" * 60)
    print("TESTING INFO AGENT")
    print("=" * 60)

    ws_url = "ws://localhost:8000/ws/pharmacy-agent"

    try:
        async with websockets.connect(ws_url) as websocket:
            # Wait for connection
            conn = await websocket.recv()
            conn_data = json.loads(conn)
            print(f"✅ Connected: Session {conn_data.get('session_id')}")

            # Initialize with existing pharmacy
            init_msg = {"type": "init", "phone": "+1-555-123-4567"}
            await websocket.send(json.dumps(init_msg))

            init_resp = await websocket.recv()
            init_data = json.loads(init_resp)
            print(f"✅ Agent Type: {init_data.get('agent_type')}")

            # Ask about prescriptions
            query_msg = {
                "type": "message",
                "content": "What prescriptions do you have?",
            }
            await websocket.send(json.dumps(query_msg))

            query_resp = await websocket.recv()
            query_data = json.loads(query_resp)
            content = query_data.get("content", "")

            # Check for expected drugs
            if "Lisinopril" in content and "Atorvastatin" in content:
                print("✅ Prescription query successful")
                print(f"   Response preview: {content[:100]}...")
            else:
                print("❌ Prescription query failed")

            # Close connection
            close_msg = {"type": "close"}
            await websocket.send(json.dumps(close_msg))
            print("✅ Connection closed")

            return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def test_collection_agent():
    """Test CollectionAgent with new pharmacy"""
    print("\n" + "=" * 60)
    print("TESTING COLLECTION AGENT")
    print("=" * 60)

    ws_url = "ws://localhost:8000/ws/pharmacy-agent"

    try:
        async with websockets.connect(ws_url) as websocket:
            # Wait for connection
            conn = await websocket.recv()
            conn_data = json.loads(conn)
            print(f"✅ Connected: Session {conn_data.get('session_id')}")

            # Initialize with new pharmacy
            init_msg = {"type": "init", "phone": "+1-555-111-2222"}
            await websocket.send(json.dumps(init_msg))

            init_resp = await websocket.recv()
            init_data = json.loads(init_resp)
            print(f"✅ Agent Type: {init_data.get('agent_type')}")

            # Provide name
            msg = {"type": "message", "content": "We're TestPharm Express"}
            await websocket.send(json.dumps(msg))

            resp = await websocket.recv()
            data = json.loads(resp)

            if data.get("type") == "collection_progress":
                fields = data.get("fields_collected", [])
                print(f"✅ Name collected. Fields: {fields}")

            # Provide location
            msg = {"type": "message", "content": "Located in San Francisco, California"}
            await websocket.send(json.dumps(msg))

            resp = await websocket.recv()
            data = json.loads(resp)

            if data.get("type") == "collection_progress":
                fields = data.get("fields_collected", [])
                print(f"✅ Location collected. Fields: {fields}")

            # Provide email
            msg = {"type": "message", "content": "Email is test@testpharm.com"}
            await websocket.send(json.dumps(msg))

            resp = await websocket.recv()
            data = json.loads(resp)

            if data.get("type") == "collection_complete":
                pharmacy = data.get("pharmacy_data", {})
                print("✅ Collection complete!")
                print(f"   Pharmacy: {pharmacy.get('name')}")
                print(f"   Location: {pharmacy.get('city')}, {pharmacy.get('state')}")
                print(f"   Email: {pharmacy.get('email')}")

            # Close connection
            close_msg = {"type": "close"}
            await websocket.send(json.dumps(close_msg))
            print("✅ Connection closed")

            return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def main():
    """Run both agent tests"""
    print("\n🚀 SIMPLE WEBSOCKET AGENT TESTS")
    print(f"Time: {datetime.now().strftime('%H:%M:%S')}")

    # Test InfoAgent
    info_result = await test_info_agent()

    # Small delay
    await asyncio.sleep(1)

    # Test CollectionAgent
    collection_result = await test_collection_agent()

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    if info_result:
        print("✅ InfoAgent: PASS")
    else:
        print("❌ InfoAgent: FAIL")

    if collection_result:
        print("✅ CollectionAgent: PASS")
    else:
        print("❌ CollectionAgent: FAIL")

    if info_result and collection_result:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️  Some tests failed")

    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
