"""
ArXiv MCP Agent with Qwen 3 8B via Ollama

This script implements an MCP server for searching and interacting with arXiv papers
using Qwen 3 8B through Ollama as the LLM backend.

Key Concepts:
- MCP (Model Context Protocol): Standardizes how LLM applications interact with tools and resources.
- MCP Servers: Provide tools, resources, and prompts that can be discovered and used by clients.
- Agents: Autonomous entities that use MCP servers to accomplish tasks by selecting appropriate tools.
"""

import os
import json
import arxiv
import requests
from typing import List, Dict, Any, Optional
from mcp.server.fastmcp import FastMCP
from dataclasses import dataclass
from pathlib import Path

# Configuration
PAPER_DIR = "papers"
OLLAMA_API_URL = "http://localhost:11434/api/generate"  # Default Ollama API URL
MODEL_NAME = "qwen3:8b"  # Using Qwen 3 8B via Ollama

# Create papers directory if it doesn't exist
os.makedirs(PAPER_DIR, exist_ok=True)

# Initialize FastMCP server
mcp = FastMCP("arxiv_agent")

# ===== Helper Functions =====

def query_llm(prompt: str, system_prompt: str = "") -> str:
    """Query the local Ollama API with Qwen 3 8B model."""
    try:
        data = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False
        }
        
        response = requests.post(OLLAMA_API_URL, json=data, timeout=60)
        response.raise_for_status()
        return response.json().get("response", "No response from model")
    except Exception as e:
        return f"Error querying LLM: {str(e)}"

# ===== MCP Tools =====

@mcp.tool()
def search_arxiv_papers(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search for academic papers on arXiv.
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return (default: 5)
        
    Returns:
        List of paper dictionaries with metadata
    """
    try:
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )
        
        results = []
        for paper in search.results():
            results.append({
                'id': paper.get_short_id(),
                'title': paper.title,
                'authors': [author.name for author in paper.authors],
                'published': str(paper.published.date()),
                'summary': paper.summary,
                'pdf_url': paper.pdf_url,
                'primary_category': paper.primary_category
            })
        
        return results
    except Exception as e:
        return [{"error": f"Failed to search arXiv: {str(e)}"}]

@mcp.tool()
def save_paper_info(topic: str, papers: List[Dict[str, Any]]) -> str:
    """
    Save paper information to a JSON file.
    
    Args:
        topic: Research topic (used for folder name)
        papers: List of paper dictionaries to save
        
    Returns:
        Path to the saved file or error message
    """
    try:
        # Create topic directory
        topic_dir = os.path.join(PAPER_DIR, topic.lower().replace(" ", "_"))
        os.makedirs(topic_dir, exist_ok=True)
        
        # Save papers to JSON file
        file_path = os.path.join(topic_dir, "papers_info.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(papers, f, indent=2, ensure_ascii=False)
        
        return f"Papers saved to: {file_path}"
    except Exception as e:
        return f"Error saving papers: {str(e)}"

# ===== MCP Resources =====

@mcp.resource("papers://list")
def list_saved_topics() -> str:
    """List all saved research topics with paper counts."""
    try:
        if not os.path.exists(PAPER_DIR):
            return "No topics found. Use the search_arxiv_papers tool to start collecting papers."
        
        topics = []
        for item in os.listdir(PAPER_DIR):
            topic_dir = os.path.join(PAPER_DIR, item)
            if os.path.isdir(topic_dir):
                json_file = os.path.join(topic_dir, "papers_info.json")
                if os.path.exists(json_file):
                    try:
                        with open(json_file, 'r', encoding='utf-8') as f:
                            papers = json.load(f)
                            topics.append(f"- {item.replace('_', ' ').title()}: {len(papers)} papers")
                    except json.JSONDecodeError:
                        topics.append(f"- {item.replace('_', ' ').title()}: [Corrupted data]")
        
        if not topics:
            return "No saved topics found."
            
        return "# Saved Research Topics\n\n" + "\n".join(topics)
    except Exception as e:
        return f"Error listing topics: {str(e)}"

# ===== MCP Prompts =====

@mcp.prompt()
def research_summary_prompt(topic: str, num_papers: int = 5) -> str:
    """Generate a prompt for summarizing research on a topic."""
    return f"""You are a research assistant analyzing academic papers on '{topic}'. 
    I will provide you with {num_papers} papers. For each paper, please:
    1. Extract key findings and methodologies
    2. Identify common themes across papers
    3. Note any contradictory findings
    4. Highlight important citations
    
    Then, provide a comprehensive summary of the current state of research in this area,
    including open questions and potential future directions.
    
    Papers will follow this message. Please analyze them carefully."""

# ===== Main Execution =====

def interactive_mode():
    """Run an interactive session to test the MCP server."""
    print("\nArXiv MCP Agent - Interactive Mode")
    print("Type 'exit' to quit\n")
    
    while True:
        try:
            cmd = input("\nCommand [search/save/list/llm/exit]: ").strip().lower()
            
            if cmd == 'exit':
                break
                
            elif cmd == 'search':
                query = input("Enter search query: ")
                max_results = int(input("Max results (default 3): ") or "3")
                print("\nSearching papers...")
                papers = search_arxiv_papers(query, max_results)
                for i, paper in enumerate(papers, 1):
                    print(f"\n{i}. {paper.get('title', 'No title')}")
                    print(f"   Authors: {', '.join(paper.get('authors', []))}")
                    print(f"   Published: {paper.get('published')}")
                    print(f"   URL: {paper.get('pdf_url', 'N/A')}")
            
            elif cmd == 'save':
                topic = input("Enter topic name: ").strip()
                if not topic:
                    print("Topic cannot be empty")
                    continue
                query = input("Search query for papers: ")
                max_results = int(input("Number of papers to save (default 3): ") or "3")
                print("\nSearching and saving papers...")
                papers = search_arxiv_papers(query, max_results)
                if papers and not (isinstance(papers, list) and papers and 'error' in papers[0]):
                    result = save_paper_info(topic, papers)
                    print(f"\n{result}")
                else:
                    print("Failed to fetch papers to save")
            
            elif cmd == 'list':
                print("\nSaved topics:")
                print("-" * 50)
                print(list_saved_topics())
            
            elif cmd == 'llm':
                prompt = input("Enter your prompt for Qwen 3 8B: ")
                print("\nGenerating response...")
                response = query_llm(prompt, "You are a helpful research assistant.")
                print("\nResponse:")
                print("-" * 50)
                print(response)
                print("-" * 50)
            
            else:
                print("\nAvailable commands:")
                print("- search: Search for papers on arXiv")
                print("- save: Save papers on a topic")
                print("- list: List saved topics")
                print("- llm: Test LLM directly")
                print("- exit: Quit interactive mode")
        
        except KeyboardInterrupt:
            print("\nUse 'exit' to quit")
        except Exception as e:
            print(f"\nError: {e}")

def main():
    """Run the MCP server with arXiv paper search capabilities."""
    print("""
    ArXiv MCP Agent with Qwen 3 8B via Ollama
    =======================================
    
    This MCP server provides tools for:
    - Searching arXiv for academic papers
    - Saving and organizing paper metadata
    - Analyzing research topics
    
    Available endpoints:
    - POST /tools/search_arxiv_papers - Search for papers
    - POST /tools/save_paper_info - Save paper information
    - GET /resources/papers://list - List saved topics
    
    Make sure Ollama is running with the 'qwen3:8b' model installed.
    
    Starting interactive mode...
    """)
    
    # Start interactive mode
    interactive_mode()

if __name__ == "__main__":
    main()

# ===== MCP and Agents: Key Concepts =====
"""
How MCP Streamlines AI Development:

1. **Modularity**:
   - Tools, resources, and prompts are decoupled
   - Easy to add/remove functionality without changing core logic

2. **Standardization**:
   - Consistent interface for different AI capabilities
   - Tools can be discovered and used dynamically

3. **Composability**:
   - Combine multiple MCP servers for complex workflows
   - Chain operations across different services

4. **Agent Integration**:
   - Agents can dynamically discover and use MCP capabilities
   - No hardcoded tool definitions needed
   - Enables flexible, context-aware tool selection

Example Agent Workflow with MCP:
1. Agent receives a research task
2. Discovers available MCP tools
3. Uses search_arxiv_papers to find relevant papers
4. Saves interesting papers with save_paper_info
5. Generates a summary using the research_summary_prompt
6. Uses Qwen 3 8B via Ollama to analyze and present findings

To use this in your projects:
1. Define clear tool interfaces
2. Use MCP's type system for validation
3. Implement error handling and fallbacks
4. Document your tools and resources thoroughly
5. Consider security implications of exposed functionality
"""
