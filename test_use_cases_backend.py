"""
Test script for all use case backend endpoints
"""
import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000/api/use-cases"

def test_chatbot_message():
    """Test chatbot message endpoint"""
    print("\n🧪 Testing Chatbot Message...")
    try:
        response = requests.post(
            f"{BASE_URL}/chatbots/message",
            json={
                "user_id": "test_user_123",
                "session_id": "test_session_456",
                "message": "What is machine learning?",
                "context": {"timestamp": "2024-01-01T00:00:00Z"}
            },
            timeout=30
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response: {data.get('response', '')[:100]}...")
            print(f"Memory ID: {data.get('memory_id')}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_knowledge_base_document():
    """Test knowledge base document creation"""
    print("\n🧪 Testing Knowledge Base Document...")
    try:
        response = requests.post(
            f"{BASE_URL}/knowledge-base/document",
            json={
                "title": "Machine Learning Basics",
                "content": "Machine learning is a subset of artificial intelligence that enables computers to learn from data without being explicitly programmed.",
                "category": "Technology",
                "tags": ["AI", "ML", "Data Science"]
            },
            timeout=30
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Memory ID: {data.get('memory_id')}")
            print(f"Document ID: {data.get('document_id')}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_educational_concept():
    """Test educational concept creation"""
    print("\n🧪 Testing Educational Concept...")
    try:
        response = requests.post(
            f"{BASE_URL}/education/concept",
            json={
                "concept_name": "Neural Networks",
                "description": "Neural networks are computing systems inspired by biological neural networks.",
                "category": "Machine Learning",
                "difficulty_level": "intermediate",
                "prerequisites": ["Linear Algebra", "Calculus"]
            },
            timeout=30
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Memory ID: {data.get('memory_id')}")
            print(f"Concept ID: {data.get('concept_id')}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_healthcare_record():
    """Test healthcare record creation"""
    print("\n🧪 Testing Healthcare Record...")
    try:
        response = requests.post(
            f"{BASE_URL}/healthcare/record",
            json={
                "patient_id": "patient_123",
                "record_type": "examination",
                "content": "Patient presents with chest pain. Vital signs stable.",
                "doctor_id": "doctor_456"
            },
            timeout=30
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Memory ID: {data.get('memory_id')}")
            print(f"Record ID: {data.get('record_id')}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_customer_interaction():
    """Test customer interaction creation"""
    print("\n🧪 Testing Customer Interaction...")
    try:
        response = requests.post(
            f"{BASE_URL}/support/interaction",
            json={
                "customer_id": "customer_789",
                "interaction_type": "chat",
                "content": "Customer prefers email notifications and has issue with billing.",
                "agent_id": "agent_123",
                "sentiment": "neutral"
            },
            timeout=30
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Memory ID: {data.get('memory_id')}")
            print(f"Interaction ID: {data.get('interaction_id')}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_research_document():
    """Test research document creation"""
    print("\n🧪 Testing Research Document...")
    try:
        response = requests.post(
            f"{BASE_URL}/research/document",
            json={
                "title": "Transformer Models for NLP",
                "authors": ["Author 1", "Author 2"],
                "abstract": "This paper presents transformer models for natural language processing.",
                "content": "Full paper content discussing transformer architecture and applications.",
                "doi": "10.1000/xyz123",
                "keywords": ["NLP", "Transformers", "Deep Learning"]
            },
            timeout=30
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Memory ID: {data.get('memory_id')}")
            print(f"Document ID: {data.get('document_id')}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_search_endpoints():
    """Test search endpoints"""
    print("\n🧪 Testing Search Endpoints...")
    
    # Test knowledge base search
    try:
        response = requests.get(
            f"{BASE_URL}/knowledge-base/search",
            params={"query": "machine learning", "limit": 5},
            timeout=30
        )
        print(f"Knowledge Base Search Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {data.get('total', 0)} results")
    except Exception as e:
        print(f"❌ Knowledge Base Search Error: {e}")
    
    # Test research search
    try:
        response = requests.get(
            f"{BASE_URL}/research/search",
            params={"query": "transformer", "limit": 5},
            timeout=30
        )
        print(f"Research Search Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {data.get('total', 0)} results")
    except Exception as e:
        print(f"❌ Research Search Error: {e}")

def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 Testing All Use Case Backend Endpoints")
    print("=" * 60)
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code != 200:
            print("❌ Backend server is not running or not healthy")
            print("Please start the backend: uvicorn app.main:app --reload --port 8000")
            return
    except Exception as e:
        print("❌ Cannot connect to backend server")
        print("Please start the backend: uvicorn app.main:app --reload --port 8000")
        return
    
    results = []
    
    # Test all endpoints
    results.append(("Chatbot Message", test_chatbot_message()))
    results.append(("Knowledge Base Document", test_knowledge_base_document()))
    results.append(("Educational Concept", test_educational_concept()))
    results.append(("Healthcare Record", test_healthcare_record()))
    results.append(("Customer Interaction", test_customer_interaction()))
    results.append(("Research Document", test_research_document()))
    
    # Test search endpoints
    test_search_endpoints()
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name}: {status}")
    
    total = len(results)
    passed = sum(1 for _, result in results if result)
    print(f"\nTotal: {total}, Passed: {passed}, Failed: {total - passed}")

if __name__ == "__main__":
    main()

