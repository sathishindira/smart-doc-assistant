#!/usr/bin/env python3
"""
Test script for AI Document Assistant
This script tests each component to ensure everything is working correctly
"""

import sys
import os
import traceback
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        import streamlit
        print("✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
        return False
    
    try:
        from langchain_huggingface import HuggingFaceEmbeddings
        print("✅ LangChain HuggingFace imported successfully")
    except ImportError as e:
        print(f"❌ LangChain HuggingFace import failed: {e}")
        return False
    
    try:
        from langchain_community.vectorstores import FAISS
        print("✅ FAISS imported successfully")
    except ImportError as e:
        print(f"❌ FAISS import failed: {e}")
        return False
    
    try:
        import sentence_transformers
        print("✅ Sentence Transformers imported successfully")
    except ImportError as e:
        print(f"❌ Sentence Transformers import failed: {e}")
        return False
    
    return True

def test_components():
    """Test individual components"""
    print("\n🧪 Testing components...")
    
    # Test unified processor
    try:
        from unified_processor_fixed import UnifiedDataProcessor
        processor = UnifiedDataProcessor()
        print("✅ UnifiedDataProcessor initialized successfully")
    except Exception as e:
        print(f"❌ UnifiedDataProcessor failed: {e}")
        traceback.print_exc()
        return False
    
    # Test confluence processor
    try:
        from extract_confluence_fixed import ConfluenceProcessor
        confluence = ConfluenceProcessor()
        status = confluence.get_connection_status()
        if status['available']:
            print("✅ Confluence connection working")
        else:
            print(f"⚠️ Confluence not configured: {status['error']}")
    except Exception as e:
        print(f"❌ Confluence processor failed: {e}")
        return False
    
    # Test design document generator
    try:
        from design_doc_generator_fixed import DesignDocumentGenerator
        doc_gen = DesignDocumentGenerator()
        print("✅ DesignDocumentGenerator initialized successfully")
    except Exception as e:
        print(f"❌ DesignDocumentGenerator failed: {e}")
        traceback.print_exc()
        return False
    
    return True

def test_embeddings():
    """Test embeddings functionality"""
    print("\n🧪 Testing embeddings...")
    
    try:
        from langchain_huggingface import HuggingFaceEmbeddings
        embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
        
        # Test embedding generation
        test_text = "This is a test sentence for embedding generation."
        embedding = embeddings.embed_query(test_text)
        
        if len(embedding) > 0:
            print(f"✅ Embeddings working - dimension: {len(embedding)}")
            return True
        else:
            print("❌ Empty embedding generated")
            return False
    except Exception as e:
        print(f"❌ Embeddings test failed: {e}")
        traceback.print_exc()
        return False

def test_vector_store():
    """Test vector store functionality"""
    print("\n🧪 Testing vector store...")
    
    try:
        from langchain_community.vectorstores import FAISS
        from langchain_huggingface import HuggingFaceEmbeddings
        from langchain.schema import Document
        
        # Create test documents
        docs = [
            Document(page_content="This is a test document about AI.", metadata={"source": "test1"}),
            Document(page_content="This document discusses machine learning.", metadata={"source": "test2"}),
            Document(page_content="Vector stores are useful for similarity search.", metadata={"source": "test3"})
        ]
        
        # Create embeddings and vector store
        embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
        vectorstore = FAISS.from_documents(docs, embeddings)
        
        # Test search
        results = vectorstore.similarity_search("AI and machine learning", k=2)
        
        if len(results) > 0:
            print(f"✅ Vector store working - found {len(results)} results")
            return True
        else:
            print("❌ No search results returned")
            return False
    except Exception as e:
        print(f"❌ Vector store test failed: {e}")
        traceback.print_exc()
        return False

def test_environment():
    """Test environment setup"""
    print("\n🧪 Testing environment...")
    
    # Check directories
    required_dirs = ['./vector_store/']
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ Directory exists: {dir_path}")
        else:
            print(f"⚠️ Creating directory: {dir_path}")
            os.makedirs(dir_path, exist_ok=True)
    
    # Check environment variables
    env_vars = ['CONFLUENCE_URL', 'CONFLUENCE_USERNAME', 'CONFLUENCE_API_TOKEN']
    configured_vars = 0
    for var in env_vars:
        if os.getenv(var):
            configured_vars += 1
    
    if configured_vars == len(env_vars):
        print("✅ All Confluence environment variables configured")
    elif configured_vars > 0:
        print(f"⚠️ Partial Confluence configuration: {configured_vars}/{len(env_vars)} variables set")
    else:
        print("ℹ️ No Confluence environment variables configured (optional)")
    
    return True

def main():
    """Run all tests"""
    print("🚀 AI Document Assistant - System Test")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Environment Test", test_environment),
        ("Embeddings Test", test_embeddings),
        ("Vector Store Test", test_vector_store),
        ("Components Test", test_components),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
            traceback.print_exc()
    
    print(f"\n{'='*50}")
    print(f"🏁 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready to use.")
        print("\nTo start the application:")
        print("  streamlit run 06_streamlit_app_complete.py")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        print("Make sure all requirements are installed:")
        print("  pip install -r requirements_complete.txt")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)