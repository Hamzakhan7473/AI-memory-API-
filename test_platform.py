#!/usr/bin/env python3
"""
Comprehensive Platform Testing Script
Tests all major features of the AI Memory Platform
"""
import requests
import json
import time
import sys
from typing import Dict, Any

BASE_URL = "http://localhost:8000/api"
TEST_RESULTS = []


def print_test(name: str, status: str, details: str = ""):
    """Print test result"""
    icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
    print(f"{icon} {name}: {status}")
    if details:
        print(f"   {details}")
    TEST_RESULTS.append({"name": name, "status": status, "details": details})


def test_health_check():
    """Test 1: Health check endpoint"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print_test("Health Check", "PASS", f"Status: {response.json()}")
            return True
        else:
            print_test("Health Check", "FAIL", f"Status code: {response.status_code}")
            return False
    except Exception as e:
        print_test("Health Check", "FAIL", f"Error: {str(e)}")
        return False


def test_api_docs():
    """Test 2: API documentation"""
    try:
        response = requests.get("http://localhost:8000/docs", timeout=5)
        if response.status_code == 200:
            print_test("API Documentation", "PASS", "Swagger UI accessible")
            return True
        else:
            print_test("API Documentation", "FAIL", f"Status code: {response.status_code}")
            return False
    except Exception as e:
        print_test("API Documentation", "FAIL", f"Error: {str(e)}")
        return False


def test_create_memory():
    """Test 3: Create memory"""
    try:
        data = {
            "content": "Test memory: Python is a programming language used for AI and data science.",
            "metadata": {"test": True, "category": "technology"},
            "source_type": "text",
            "source_id": "test_001"
        }
        response = requests.post(f"{BASE_URL}/memories/", json=data, timeout=10)
        if response.status_code == 201:
            memory = response.json()
            memory_id = memory.get("id")
            print_test("Create Memory", "PASS", f"Created: {memory_id}")
            return memory_id
        else:
            print_test("Create Memory", "FAIL", f"Status: {response.status_code}, {response.text[:100]}")
            return None
    except Exception as e:
        print_test("Create Memory", "FAIL", f"Error: {str(e)}")
        return None


def test_get_memory(memory_id: str):
    """Test 4: Get memory"""
    if not memory_id:
        print_test("Get Memory", "SKIP", "No memory ID available")
        return False
    
    try:
        response = requests.get(f"{BASE_URL}/memories/{memory_id}", timeout=5)
        if response.status_code == 200:
            memory = response.json()
            print_test("Get Memory", "PASS", f"Retrieved: {memory.get('id')}")
            return True
        else:
            print_test("Get Memory", "FAIL", f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("Get Memory", "FAIL", f"Error: {str(e)}")
        return False


def test_list_memories():
    """Test 5: List memories"""
    try:
        response = requests.get(f"{BASE_URL}/memories/?limit=10&only_latest=true", timeout=5)
        if response.status_code == 200:
            memories = response.json()
            count = len(memories) if isinstance(memories, list) else 0
            print_test("List Memories", "PASS", f"Found {count} memories")
            return True
        else:
            print_test("List Memories", "FAIL", f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("List Memories", "FAIL", f"Error: {str(e)}")
        return False


def test_semantic_search():
    """Test 6: Semantic search"""
    try:
        data = {
            "query": "What is Python programming?",
            "limit": 5,
            "min_similarity": 0.5,
            "include_subgraph": False
        }
        response = requests.post(f"{BASE_URL}/search/", json=data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            memories_count = len(result.get("memories", []))
            print_test("Semantic Search", "PASS", f"Found {memories_count} results")
            return True
        else:
            print_test("Semantic Search", "FAIL", f"Status: {response.status_code}, {response.text[:100]}")
            return False
    except Exception as e:
        print_test("Semantic Search", "FAIL", f"Error: {str(e)}")
        return False


def test_graph_stats():
    """Test 7: Graph statistics"""
    try:
        response = requests.get(f"{BASE_URL}/graph/stats", timeout=5)
        if response.status_code == 200:
            stats = response.json()
            total = stats.get("total_memories", 0)
            print_test("Graph Statistics", "PASS", f"Total memories: {total}")
            return True
        else:
            print_test("Graph Statistics", "FAIL", f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("Graph Statistics", "FAIL", f"Error: {str(e)}")
        return False


def test_detailed_stats():
    """Test 8: Detailed graph statistics"""
    try:
        response = requests.get(f"{BASE_URL}/graph/stats/detailed", timeout=10)
        if response.status_code == 200:
            stats = response.json()
            print_test("Detailed Statistics", "PASS", "Retrieved detailed stats")
            return True
        else:
            print_test("Detailed Statistics", "FAIL", f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("Detailed Statistics", "FAIL", f"Error: {str(e)}")
        return False


def test_dashboard_graph():
    """Test 9: Dashboard graph data"""
    try:
        response = requests.get(f"{BASE_URL}/dashboard/graph?limit=50&only_latest=true", timeout=10)
        if response.status_code == 200:
            data = response.json()
            nodes = len(data.get("nodes", []))
            edges = len(data.get("edges", []))
            print_test("Dashboard Graph", "PASS", f"Nodes: {nodes}, Edges: {edges}")
            return True
        else:
            print_test("Dashboard Graph", "FAIL", f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("Dashboard Graph", "FAIL", f"Error: {str(e)}")
        return False


def test_rag_retrieve():
    """Test 10: RAG retrieval"""
    try:
        data = {
            "query": "What is machine learning?",
            "limit": 5,
            "min_similarity": 0.5,
            "rerank": True
        }
        response = requests.post(f"{BASE_URL}/rag/retrieve", json=data, timeout=15)
        if response.status_code == 200:
            result = response.json()
            results_count = len(result.get("results", []))
            print_test("RAG Retrieve", "PASS", f"Retrieved {results_count} results")
            return True
        else:
            print_test("RAG Retrieve", "FAIL", f"Status: {response.status_code}, {response.text[:100]}")
            return False
    except Exception as e:
        print_test("RAG Retrieve", "FAIL", f"Error: {str(e)}")
        return False


def test_rag_query():
    """Test 11: RAG query (retrieve + generate)"""
    try:
        data = {
            "query": "What is artificial intelligence?",
            "retrieval_limit": 3,
            "min_similarity": 0.5,
            "rerank": True,
            "model": "gpt-4",
            "max_tokens": 200
        }
        response = requests.post(f"{BASE_URL}/rag/query", json=data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            answer = result.get("answer", "")
            print_test("RAG Query", "PASS", f"Generated answer ({len(answer)} chars)")
            return True
        else:
            print_test("RAG Query", "FAIL", f"Status: {response.status_code}, {response.text[:100]}")
            return False
    except Exception as e:
        print_test("RAG Query", "FAIL", f"Error: {str(e)}")
        return False


def test_auth_register():
    """Test 12: User registration"""
    try:
        data = {
            "email": f"test_{int(time.time())}@example.com",
            "username": f"testuser_{int(time.time())}",
            "password": "testpass123"  # Shorter password for bcrypt compatibility
        }
        response = requests.post(f"{BASE_URL}/auth/register", json=data, timeout=5)
        if response.status_code == 201:
            user = response.json()
            print_test("User Registration", "PASS", f"User created: {user.get('id')}")
            return True
        else:
            print_test("User Registration", "FAIL", f"Status: {response.status_code}, {response.text[:100]}")
            return False
    except Exception as e:
        print_test("User Registration", "FAIL", f"Error: {str(e)}")
        return False


def test_update_memory(memory_id: str):
    """Test 13: Update memory (creates new version)"""
    if not memory_id:
        print_test("Update Memory", "SKIP", "No memory ID available")
        return False
    
    try:
        data = {
            "content": "Updated: Python is a versatile programming language used for AI, data science, and web development.",
            "metadata": {"updated": True, "version": 2}
        }
        response = requests.put(f"{BASE_URL}/memories/{memory_id}", json=data, timeout=10)
        if response.status_code == 200:
            memory = response.json()
            new_id = memory.get("id")
            print_test("Update Memory", "PASS", f"New version created: {new_id}")
            return True
        else:
            print_test("Update Memory", "FAIL", f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("Update Memory", "FAIL", f"Error: {str(e)}")
        return False


def test_memory_lineage(memory_id: str):
    """Test 14: Memory lineage"""
    if not memory_id:
        print_test("Memory Lineage", "SKIP", "No memory ID available")
        return False
    
    try:
        response = requests.get(f"{BASE_URL}/graph/lineage/{memory_id}", timeout=10)
        if response.status_code == 200:
            lineage = response.json()
            versions = len(lineage.get("lineage", []))
            print_test("Memory Lineage", "PASS", f"Found {versions} versions")
            return True
        else:
            print_test("Memory Lineage", "FAIL", f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("Memory Lineage", "FAIL", f"Error: {str(e)}")
        return False


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("AI Memory Platform - Comprehensive Test Suite")
    print("=" * 60)
    print()
    
    # Basic connectivity tests
    print("📡 Connectivity Tests")
    print("-" * 60)
    test_health_check()
    test_api_docs()
    print()
    
    # Memory management tests
    print("💾 Memory Management Tests")
    print("-" * 60)
    memory_id = test_create_memory()
    test_get_memory(memory_id)
    test_list_memories()
    test_update_memory(memory_id)
    test_memory_lineage(memory_id)
    print()
    
    # Search tests
    print("🔍 Search Tests")
    print("-" * 60)
    test_semantic_search()
    print()
    
    # Graph tests
    print("📊 Graph Tests")
    print("-" * 60)
    test_graph_stats()
    test_detailed_stats()
    test_dashboard_graph()
    print()
    
    # RAG tests
    print("🤖 RAG Pipeline Tests")
    print("-" * 60)
    test_rag_retrieve()
    test_rag_query()
    print()
    
    # Auth tests
    print("🔐 Authentication Tests")
    print("-" * 60)
    test_auth_register()
    print()
    
    # Summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for r in TEST_RESULTS if r["status"] == "PASS")
    failed = sum(1 for r in TEST_RESULTS if r["status"] == "FAIL")
    skipped = sum(1 for r in TEST_RESULTS if r["status"] == "SKIP")
    total = len(TEST_RESULTS)
    
    print(f"Total Tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"⚠️  Skipped: {skipped}")
    print()
    
    if failed == 0:
        print("🎉 All tests passed! Platform is ready.")
        return 0
    else:
        print(f"⚠️  {failed} test(s) failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())

