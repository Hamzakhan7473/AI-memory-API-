"""
Test RAG integration with document uploads
"""
import requests
import time

BASE_URL = "http://localhost:8000/api/use-cases"

def test_upload_and_rag():
    """Test uploading a document and then searching with RAG"""
    print("=" * 60)
    print("🧪 Testing RAG Integration with Document Upload")
    print("=" * 60)
    
    # Step 1: Create a simple text document (simulating PDF upload)
    print("\n1️⃣ Creating test document manually...")
    try:
        response = requests.post(
            f"{BASE_URL}/knowledge-base/document",
            json={
                "title": "Test RAG Document",
                "content": "Machine learning is a subset of artificial intelligence. Deep learning uses neural networks. Transformers are a type of neural network architecture used in NLP.",
                "category": "Technology",
                "tags": ["AI", "ML", "NLP"]
            },
            timeout=30
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            doc_data = response.json()
            print(f"   ✅ Document created: {doc_data.get('memory_id')}")
            memory_id = doc_data.get('memory_id')
        else:
            print(f"   ❌ Error: {response.text}")
            return
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return
    
    # Wait a bit for embeddings to be processed
    print("\n   ⏳ Waiting for embeddings to be processed...")
    time.sleep(2)
    
    # Step 2: Search with RAG
    print("\n2️⃣ Testing RAG search...")
    try:
        response = requests.get(
            f"{BASE_URL}/knowledge-base/search",
            params={
                "query": "What is machine learning?",
                "limit": 5
            },
            timeout=30
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            search_data = response.json()
            print(f"   ✅ Found {search_data.get('total', 0)} results")
            if search_data.get('results'):
                for i, result in enumerate(search_data['results'][:3], 1):
                    print(f"   Result {i}:")
                    print(f"      Title: {result.get('title', 'N/A')}")
                    print(f"      Similarity: {result.get('similarity', 0):.2%}")
                    print(f"      Category: {result.get('category', 'N/A')}")
                    print(f"      Tags: {result.get('tags', [])}")
            else:
                print("   ⚠️  No results found - this might indicate an issue")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Step 3: Test RAG query endpoint
    print("\n3️⃣ Testing RAG query endpoint...")
    try:
        response = requests.post(
            "http://localhost:8000/api/rag/query",
            json={
                "query": "Explain machine learning",
                "retrieval_limit": 5,
                "min_similarity": 0.3,  # Lower threshold to find uploaded documents
                "rerank": True,
                "model": "gpt-4",
                "max_tokens": 200
            },
            timeout=60
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            rag_data = response.json()
            print(f"   ✅ RAG Response:")
            print(f"      Answer: {rag_data.get('answer', 'N/A')[:200]}...")
            print(f"      Citations: {len(rag_data.get('citations', []))}")
            print(f"      Retrieved Memories: {len(rag_data.get('retrieved_memories', []))}")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Test Complete")
    print("=" * 60)

if __name__ == "__main__":
    test_upload_and_rag()

