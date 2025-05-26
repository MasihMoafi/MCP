""
Test script for the ArXiv MCP Agent

This script tests the functionality of the ArXiv MCP Agent by:
1. Searching for papers on a topic
2. Saving the results
3. Listing saved topics
4. Testing the LLM integration
"""

import requests
import json
import time
from typing import Dict, Any, List

# MCP server configuration
MCP_SERVER_URL = "http://localhost:8000"
OLLAMA_URL = "http://localhost:11434/api/generate"

def test_ollama_connection() -> bool:
    """Test if Ollama is running and responding."""
    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": "qwen3:8b", "prompt": "Test", "stream": False},
            timeout=10
        )
        return response.status_code == 200
    except Exception as e:
        print(f"Ollama connection test failed: {e}")
        return False

def search_papers(query: str, max_results: int = 3) -> List[Dict[str, Any]]:
    """Test the search_arxiv_papers tool."""
    try:
        response = requests.post(
            f"{MCP_SERVER_URL}/tools/search_arxiv_papers",
            json={"query": query, "max_results": max_results},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error searching papers: {e}")
        return []

def save_papers(topic: str, papers: List[Dict[str, Any]]) -> str:
    """Test the save_paper_info tool."""
    try:
        response = requests.post(
            f"{MCP_SERVER_URL}/tools/save_paper_info",
            json={"topic": topic, "papers": papers},
            timeout=10
        )
        response.raise_for_status()
        return response.text
    except Exception as e:
        return f"Error saving papers: {e}"

def list_topics() -> str:
    """Test the list_saved_topics resource."""
    try:
        response = requests.get(
            f"{MCP_SERVER_URL}/resources/papers%3A//list",
            timeout=10
        )
        response.raise_for_status()
        return response.text
    except Exception as e:
        return f"Error listing topics: {e}"

def test_llm_integration() -> str:
    """Test the LLM integration through the MCP server."""
    try:
        # First, get some papers
        papers = search_papers("quantum machine learning", 2)
        if not papers or (isinstance(papers, list) and papers and "error" in papers[0]):
            return "Skipping LLM test: Could not fetch papers"
        
        # Create a prompt for the LLM
        prompt = f"""Summarize the key points of this paper in 3 bullet points:
        
Title: {papers[0]['title']}
Summary: {papers[0]['summary'][:1000]}..."""
        
        # Call the LLM through Ollama directly for this test
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": "qwen3:8b",
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )
        response.raise_for_status()
        return response.json().get("response", "No response")
    except Exception as e:
        return f"LLM test failed: {e}"

def run_tests():
    """Run all tests and print results."""
    print("="*50)
    print("Starting ArXiv MCP Agent Tests")
    print("="*50 + "\n")
    
    # Test 1: Check Ollama connection
    print("1. Testing Ollama connection...")
    if test_ollama_connection():
        print("✅ Ollama is running and responding\n")
    else:
        print("❌ Ollama is not running or not accessible")
        print("Please start Ollama first: ollama serve")
        return
    
    # Test 2: Search for papers
    print("2. Testing paper search...")
    papers = search_papers("quantum machine learning", 2)
    if papers and (not isinstance(papers, list) or (papers and "error" not in papers[0])):
        print(f"✅ Found {len(papers)} papers")
        for i, paper in enumerate(papers[:2], 1):
            print(f"   {i}. {paper.get('title', 'No title')}")
    else:
        print("❌ Failed to search papers")
        print(f"Response: {papers}")
    print()
    
    # Test 3: Save papers
    if papers and len(papers) > 0:
        print("3. Testing paper save...")
        save_result = save_papers("quantum_ml_test", papers)
        print(f"✅ {save_result}\n")
    else:
        print("⚠️  Skipping save test - no papers to save\n")
    
    # Test 4: List topics
    print("4. Testing topic listing...")
    topics = list_topics()
    print(topics + "\n")
    
    # Test 5: LLM Integration
    print("5. Testing LLM integration...")
    llm_response = test_llm_integration()
    print("LLM Response:")
    print("-"*30)
    print(llm_response)
    print("-"*30)
    
    print("\n" + "="*50)
    print("Tests completed!")
    print("="*50)

if __name__ == "__main__":
    run_tests()
