#!/usr/bin/env python3
"""Check MemMachine status and functionality"""
import asyncio
import httpx
from app.services.memmachine_service import memmachine_service

async def check_memmachine():
    """Check MemMachine status"""
    print("=" * 60)
    print("MEM MACHINE STATUS CHECK")
    print("=" * 60)
    print()
    
    # Health check
    print("1. Health Check:")
    health = await memmachine_service.health_check()
    print(f"   {'✅' if health else '❌'} MemMachine Health: {'Healthy' if health else 'Unavailable'}")
    print()
    
    # Get sessions
    print("2. Sessions:")
    sessions = await memmachine_service.get_sessions()
    print(f"   {'✅' if sessions else '⚠️'} Total Sessions: {len(sessions)}")
    if sessions:
        print(f"   Sessions: {sessions[:5]}")
    print()
    
    # Test search
    print("3. Search Test:")
    if sessions:
        test_session = sessions[0]
        search_results = await memmachine_service.search_memories(
            session_id=test_session,
            query="test",
            limit=3
        )
        print(f"   {'✅' if search_results is not None else '❌'} Search Working: {len(search_results)} results")
    else:
        print("   ⚠️ No sessions to test search")
    print()
    
    # Test unified search
    print("4. Unified Search Test:")
    all_results = await memmachine_service.search_all_memories(
        query="test",
        limit=5
    )
    print(f"   {'✅' if all_results is not None else '❌'} Unified Search: {len(all_results)} results across all sessions")
    print()
    
    # Direct API check
    print("5. Direct API Check:")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://localhost:8080/health")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Direct API: {data.get('status', 'unknown')}")
                print(f"   Version: {data.get('version', 'unknown')}")
                print(f"   Memory Managers: {data.get('memory_managers', {})}")
            else:
                print(f"   ❌ Direct API: Status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Direct API: {str(e)[:50]}")
    print()
    
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    if health and len(sessions) >= 0:
        print("✅ MemMachine is working!")
    else:
        print("⚠️ MemMachine may have issues")
    print()

if __name__ == "__main__":
    asyncio.run(check_memmachine())
