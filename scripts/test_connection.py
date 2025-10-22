"""
Test Database and API Connections
Run this script to verify your setup before starting the application
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from rich.console import Console
from rich.table import Table
from rich import print as rprint
import time

console = Console()


def test_imports():
    """Test if all required packages are installed"""
    console.print("\n[bold blue]Testing Python Imports...[/bold blue]")
    
    required_packages = [
        ('langchain', 'LangChain'),
        ('langchain_google_genai', 'Google GenAI'),
        ('sqlalchemy', 'SQLAlchemy'),
        ('fastapi', 'FastAPI'),
        ('streamlit', 'Streamlit'),
        ('sentence_transformers', 'Sentence Transformers'),
    ]
    
    all_good = True
    for package, name in required_packages:
        try:
            __import__(package)
            console.print(f"  ✅ {name}")
        except ImportError as e:
            console.print(f"  ❌ {name} - {str(e)}")
            all_good = False
    
    return all_good


def test_environment():
    """Test if environment variables are set"""
    console.print("\n[bold blue]Testing Environment Variables...[/bold blue]")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = [
        ('GOOGLE_API_KEY', 'Google API Key'),
        ('DATABASE_URL', 'Database URL'),
    ]
    
    all_good = True
    for var, name in required_vars:
        value = os.getenv(var)
        if value:
            masked_value = value[:10] + "..." if len(value) > 10 else "***"
            console.print(f"  ✅ {name}: {masked_value}")
        else:
            console.print(f"  ❌ {name}: Not set")
            all_good = False
    
    return all_good


def test_database_connection():
    """Test connection to Supabase/PostgreSQL"""
    console.print("\n[bold blue]Testing Database Connection...[/bold blue]")
    
    try:
        from config.settings import settings
        from sqlalchemy import create_engine, text
        
        # Create engine
        engine = create_engine(settings.database_url, pool_pre_ping=True)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            console.print(f"  ✅ Connected to PostgreSQL")
            console.print(f"     Version: {version[:50]}...")
            
            # Check pgvector extension
            result = conn.execute(text("SELECT * FROM pg_extension WHERE extname = 'vector';"))
            if result.fetchone():
                console.print(f"  ✅ PGVector extension installed")
            else:
                console.print(f"  ⚠️  PGVector extension not found")
                return False
            
            # Check if collection exists
            result = conn.execute(text(
                f"SELECT COUNT(*) FROM langchain_pg_collection WHERE name = '{settings.collection_name}';"
            ))
            count = result.fetchone()[0]
            console.print(f"  ✅ Collection '{settings.collection_name}' exists")
            
            # Count documents
            if count > 0:
                result = conn.execute(text("""
                    SELECT COUNT(*) FROM langchain_pg_embedding 
                    WHERE collection_id = (
                        SELECT uuid FROM langchain_pg_collection 
                        WHERE name = :collection_name
                    );
                """), {"collection_name": settings.collection_name})
                doc_count = result.fetchone()[0]
                console.print(f"  ✅ Found {doc_count} embedded documents")
        
        return True
        
    except Exception as e:
        console.print(f"  ❌ Database connection failed: {str(e)}")
        return False


def test_gemini_api():
    """Test Google Gemini API connection"""
    console.print("\n[bold blue]Testing Google Gemini API...[/bold blue]")
    
    try:
        from config.settings import settings
        import google.generativeai as genai
        
        # Configure API
        genai.configure(api_key=settings.google_api_key)
        
        # Test Flash model
        console.print(f"  Testing {settings.gemini_model_flash}...")
        model = genai.GenerativeModel(settings.gemini_model_flash)
        response = model.generate_content("Say 'Hello'")
        console.print(f"  ✅ Flash model working")
        
        # Test Pro model
        console.print(f"  Testing {settings.gemini_model_pro}...")
        model = genai.GenerativeModel(settings.gemini_model_pro)
        response = model.generate_content("Say 'Hello'")
        console.print(f"  ✅ Pro model working")
        
        # Test embeddings
        console.print(f"  Testing {settings.gemini_embedding_model}...")
        result = genai.embed_content(
            model=settings.gemini_embedding_model,
            content="test",
            task_type="retrieval_document"
        )
        console.print(f"  ✅ Embeddings working (dimension: {len(result['embedding'])})")
        
        return True
        
    except Exception as e:
        console.print(f"  ❌ Gemini API test failed: {str(e)}")
        return False


def test_vector_store():
    """Test vector store initialization"""
    console.print("\n[bold blue]Testing Vector Store...[/bold blue]")
    
    try:
        from src.core.embeddings import get_gemini_embeddings
        from src.core.vector_store import SupabasePGVectorStore
        
        # Initialize embeddings
        embeddings = get_gemini_embeddings()
        console.print(f"  ✅ Embeddings initialized")
        
        # Initialize vector store
        vector_store = SupabasePGVectorStore(embedding_function=embeddings)
        console.print(f"  ✅ Vector store connected")
        
        # Get stats
        stats = vector_store.get_collection_stats()
        console.print(f"  ✅ Collection stats retrieved:")
        console.print(f"     Total documents: {stats.get('total_documents', 0)}")
        console.print(f"     Unique files: {stats.get('unique_files', 0)}")
        
        return True
        
    except Exception as e:
        console.print(f"  ❌ Vector store test failed: {str(e)}")
        return False


def test_complete_system():
    """Test complete system initialization"""
    console.print("\n[bold blue]Testing Complete System...[/bold blue]")
    
    try:
        from src.core.embeddings import get_gemini_embeddings
        from src.core.llm import get_gemini_llm
        from src.core.vector_store import SupabasePGVectorStore
        from src.rag.retriever import AdvancedRAGRetriever
        
        # Initialize components
        embeddings = get_gemini_embeddings()
        console.print(f"  ✅ Embeddings ready")
        
        llm = get_gemini_llm()
        console.print(f"  ✅ LLM ready")
        
        vector_store = SupabasePGVectorStore(embedding_function=embeddings)
        console.print(f"  ✅ Vector store ready")
        
        retriever = AdvancedRAGRetriever(vector_store=vector_store)
        console.print(f"  ✅ RAG retriever ready")
        
        # Test simple query if documents exist
        stats = vector_store.get_collection_stats()
        if stats.get('total_documents', 0) > 0:
            console.print(f"\n  Testing retrieval with sample query...")
            docs = retriever.retrieve("test query", top_k=3)
            console.print(f"  ✅ Retrieved {len(docs)} documents")
        
        return True
        
    except Exception as e:
        console.print(f"  ❌ System test failed: {str(e)}")
        return False


def main():
    """Run all tests"""
    console.print("\n[bold green]" + "="*60 + "[/bold green]")
    console.print("[bold green]Project Polaris - System Connection Tests[/bold green]")
    console.print("[bold green]" + "="*60 + "[/bold green]")
    
    results = {
        "Imports": test_imports(),
        "Environment": test_environment(),
        "Database": test_database_connection(),
        "Gemini API": test_gemini_api(),
        "Vector Store": test_vector_store(),
        "Complete System": test_complete_system(),
    }
    
    # Summary table
    console.print("\n[bold blue]Test Summary[/bold blue]")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Test", style="cyan")
    table.add_column("Status", justify="center")
    
    for test, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        table.add_row(test, status)
    
    console.print(table)
    
    # Final result
    all_passed = all(results.values())
    if all_passed:
        console.print("\n[bold green]🎉 All tests passed! System is ready.[/bold green]")
        console.print("\n[bold]Next steps:[/bold]")
        console.print("  1. Start API: uvicorn src.api.main:app --reload")
        console.print("  2. Start UI: streamlit run ui/streamlit_app.py")
        console.print("  3. Access docs: http://localhost:8000/docs")
        return 0
    else:
        console.print("\n[bold red]❌ Some tests failed. Please fix the issues above.[/bold red]")
        return 1


if __name__ == "__main__":
    exit(main())