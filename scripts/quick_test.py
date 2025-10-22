"""
Quick functionality test for Project Polaris
Tests end-to-end query and summarization
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
import time

console = Console()


def test_query_agent():
    """Test query agent with sample question"""
    console.print("\n[bold blue]Testing Query Agent...[/bold blue]")
    
    try:
        from src.core.embeddings import get_gemini_embeddings
        from src.core.llm import get_gemini_llm
        from src.core.vector_store import SupabasePGVectorStore
        from src.rag.retriever import AdvancedRAGRetriever
        from src.agents.query_agent import QueryAgent
        
        # Initialize components
        console.print("  Initializing components...")
        embeddings = get_gemini_embeddings()
        llm = get_gemini_llm()
        vector_store = SupabasePGVectorStore(embedding_function=embeddings)
        retriever = AdvancedRAGRetriever(vector_store=vector_store)
        
        # Create query agent
        query_agent = QueryAgent(
            llm=llm.get_flash_model(),
            retriever=retriever
        )
        
        # Test query
        test_query = "What are the main topics in the documents?"
        console.print(f"\n  Query: [cyan]{test_query}[/cyan]")
        
        start_time = time.time()
        result = query_agent.execute({
            "query": test_query
        })
        execution_time = time.time() - start_time
        
        if result.success:
            console.print(f"\n  [green]✅ Query successful in {execution_time:.2f}s[/green]")
            
            # Display answer
            answer = result.data["answer"]
            console.print(Panel(
                Markdown(answer[:500] + "..." if len(answer) > 500 else answer),
                title="[bold green]Answer[/bold green]",
                border_style="green"
            ))
            
            # Display stats
            console.print(f"\n  Sources used: {result.data['num_sources']}")
            if result.data.get('followup_questions'):
                console.print(f"  Follow-up questions: {len(result.data['followup_questions'])}")
            
            return True
        else:
            console.print(f"  [red]❌ Query failed: {result.error}[/red]")
            return False
            
    except Exception as e:
        console.print(f"  [red]❌ Test failed: {str(e)}[/red]")
        import traceback
        traceback.print_exc()
        return False


def test_summary_agent():
    """Test summary agent"""
    console.print("\n[bold blue]Testing Summary Agent...[/bold blue]")
    
    try:
        from src.core.embeddings import get_gemini_embeddings
        from src.core.llm import get_gemini_llm
        from src.core.vector_store import SupabasePGVectorStore
        from src.rag.retriever import AdvancedRAGRetriever
        from src.agents.summary_agent import SummaryAgent
        
        # Initialize components
        console.print("  Initializing components...")
        embeddings = get_gemini_embeddings()
        llm = get_gemini_llm()
        vector_store = SupabasePGVectorStore(embedding_function=embeddings)
        retriever = AdvancedRAGRetriever(vector_store=vector_store)
        
        # Create summary agent
        summary_agent = SummaryAgent(
            llm=llm.get_pro_model(),
            retriever=retriever
        )
        
        # Test summary
        test_topic = "Provide an overview of all documents"
        console.print(f"\n  Topic: [cyan]{test_topic}[/cyan]")
        
        start_time = time.time()
        result = summary_agent.execute({
            "query": test_topic,
            "summary_type": "brief",
            "max_docs": 5
        })
        execution_time = time.time() - start_time
        
        if result.success:
            console.print(f"\n  [green]✅ Summary generated in {execution_time:.2f}s[/green]")
            
            # Display summary
            summary = result.data["summary"]
            console.print(Panel(
                Markdown(summary[:500] + "..." if len(summary) > 500 else summary),
                title="[bold green]Summary[/bold green]",
                border_style="green"
            ))
            
            # Display key points
            key_points = result.data.get("key_points", [])
            if key_points:
                console.print("\n  [bold]Key Points:[/bold]")
                for i, point in enumerate(key_points[:3], 1):
                    console.print(f"    {i}. {point}")
            
            console.print(f"\n  Documents analyzed: {result.data['num_documents_analyzed']}")
            
            return True
        else:
            console.print(f"  [red]❌ Summary failed: {result.error}[/red]")
            return False
            
    except Exception as e:
        console.print(f"  [red]❌ Test failed: {str(e)}[/red]")
        import traceback
        traceback.print_exc()
        return False


def test_router_agent():
    """Test router agent"""
    console.print("\n[bold blue]Testing Router Agent...[/bold blue]")
    
    try:
        from src.core.llm import get_gemini_llm
        from src.agents.router_agent import RouterAgent
        
        # Initialize components
        llm = get_gemini_llm()
        router_agent = RouterAgent(llm=llm.get_flash_model())
        
        # Test different query types
        test_queries = [
            "What does the document say about sales?",
            "Summarize the Q4 report",
            "How many documents are about marketing?"
        ]
        
        for query in test_queries:
            result = router_agent.execute({"query": query})
            if result.success:
                category = result.data["category"]
                target = result.data["target_agent"]
                console.print(f"  ✅ '{query[:40]}...' → {category} → {target}")
            else:
                console.print(f"  ❌ Routing failed for: {query}")
                return False
        
        return True
        
    except Exception as e:
        console.print(f"  [red]❌ Test failed: {str(e)}[/red]")
        return False


def test_advanced_rag():
    """Test advanced RAG features"""
    console.print("\n[bold blue]Testing Advanced RAG Features...[/bold blue]")
    
    try:
        from src.core.embeddings import get_gemini_embeddings
        from src.core.vector_store import SupabasePGVectorStore
        from src.rag.retriever import AdvancedRAGRetriever
        
        embeddings = get_gemini_embeddings()
        vector_store = SupabasePGVectorStore(embedding_function=embeddings)
        
        # Test with different strategies
        retriever = AdvancedRAGRetriever(
            vector_store=vector_store,
            enable_hyde=True,
            enable_reranking=True,
            enable_hybrid=True
        )
        
        console.print("  Testing retrieval strategies...")
        
        # Simple retrieval
        docs = retriever.retrieve("test query", retrieval_strategy="simple")
        console.print(f"  ✅ Simple retrieval: {len(docs)} docs")
        
        # Hybrid retrieval
        docs = retriever.retrieve("test query", retrieval_strategy="hybrid")
        console.print(f"  ✅ Hybrid retrieval: {len(docs)} docs")
        
        # Advanced retrieval
        docs = retriever.retrieve("test query", retrieval_strategy="advanced")
        console.print(f"  ✅ Advanced retrieval: {len(docs)} docs")
        
        # Get stats
        stats = retriever.get_retriever_stats()
        console.print(f"\n  Configuration:")
        console.print(f"    HyDE: {stats['enable_hyde']}")
        console.print(f"    Reranking: {stats['enable_reranking']}")
        console.print(f"    Hybrid: {stats['enable_hybrid']}")
        
        return True
        
    except Exception as e:
        console.print(f"  [red]❌ Test failed: {str(e)}[/red]")
        return False


def main():
    """Run quick tests"""
    console.print("\n[bold green]" + "="*60 + "[/bold green]")
    console.print("[bold green]Project Polaris - Quick Functionality Test[/bold green]")
    console.print("[bold green]" + "="*60 + "[/bold green]")
    
    # Check if documents exist
    from src.core.embeddings import get_gemini_embeddings
    from src.core.vector_store import SupabasePGVectorStore
    
    embeddings = get_gemini_embeddings()
    vector_store = SupabasePGVectorStore(embedding_function=embeddings)
    stats = vector_store.get_collection_stats()
    
    if stats.get('total_documents', 0) == 0:
        console.print("\n[bold yellow]⚠️  Warning: No documents found in vector store![/bold yellow]")
        console.print("Please ensure your n8n workflow has processed some documents first.")
        return 1
    
    console.print(f"\n[bold]Vector Store Status:[/bold]")
    console.print(f"  Documents: {stats['total_documents']}")
    console.print(f"  Unique files: {stats['unique_files']}")
    
    # Run tests
    results = {
        "Router Agent": test_router_agent(),
        "Advanced RAG": test_advanced_rag(),
        "Query Agent": test_query_agent(),
        "Summary Agent": test_summary_agent(),
    }
    
    # Summary
    console.print("\n[bold blue]Test Results:[/bold blue]")
    for test, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        console.print(f"  {status} - {test}")
    
    all_passed = all(results.values())
    if all_passed:
        console.print("\n[bold green]🎉 All tests passed! System is fully functional.[/bold green]")
        return 0
    else:
        console.print("\n[bold red]❌ Some tests failed.[/bold red]")
        return 1


if __name__ == "__main__":
    exit(main())