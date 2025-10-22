"""
Project Polaris Streamlit User Interface
Modern, production-ready UI for document querying with enhanced UX
"""

import streamlit as st
import requests
from typing import List, Dict, Any
import time
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Project Polaris - Document Intelligence",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #1f77b4;
        --secondary-color: #ff7f0e;
        --success-color: #2ecc71;
        --warning-color: #f39c12;
        --danger-color: #e74c3c;
        --light-bg: #f8f9fa;
        --border-color: #e0e0e0;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Main header styling */
    .main-header {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #1f77b4 0%, #2ecc71 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        letter-spacing: -0.5px;
    }
    
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    /* Enhanced source box */
    .source-box {
        background: linear-gradient(to right, #f0f2f6 0%, #ffffff 100%);
        padding: 1.2rem;
        border-radius: 0.75rem;
        border-left: 4px solid var(--primary-color);
        margin: 0.8rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    
    .source-box:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    
    .source-header {
        font-weight: 600;
        color: var(--primary-color);
        margin-bottom: 0.5rem;
        font-size: 0.95rem;
    }
    
    .source-content {
        color: #555;
        line-height: 1.6;
        font-size: 0.9rem;
    }
    
    .source-meta {
        color: #999;
        font-size: 0.85rem;
        margin-top: 0.5rem;
        display: flex;
        gap: 1rem;
    }
    
    /* Clickable follow-up questions */
    .followup-question {
        background: linear-gradient(135deg, #e8f4f8 0%, #f0f8ff 100%);
        padding: 0.75rem 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        cursor: pointer;
        border: 1px solid #d0e8f0;
        transition: all 0.2s ease;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .followup-question:hover {
        background: linear-gradient(135deg, #d0e8f0 0%, #e0f0f8 100%);
        border-color: var(--primary-color);
        transform: translateX(5px);
    }
    
    /* Stat boxes */
    .stat-box {
        background: white;
        padding: 1.5rem;
        border-radius: 0.75rem;
        text-align: center;
        border: 1px solid var(--border-color);
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    
    .stat-box:hover {
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        transform: translateY(-3px);
    }
    
    /* Chat message styling */
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.75rem;
        margin-bottom: 1rem;
    }
    
    /* Buttons */
    .stButton>button {
        border-radius: 0.5rem;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* Info badges */
    .info-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.85rem;
        font-weight: 500;
        margin: 0.25rem;
    }
    
    .badge-success {
        background-color: #d4edda;
        color: #155724;
    }
    
    .badge-info {
        background-color: #d1ecf1;
        color: #0c5460;
    }
    
    .badge-warning {
        background-color: #fff3cd;
        color: #856404;
    }
    
    /* Loading animation */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .loading-indicator {
        animation: pulse 1.5s ease-in-out infinite;
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.3rem;
        font-weight: 600;
        color: #333;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid var(--primary-color);
    }
    
    /* Response time indicator */
    .response-time {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.4rem 0.8rem;
        background-color: #f0f8ff;
        border-radius: 0.5rem;
        font-size: 0.85rem;
        color: #555;
        margin-top: 0.5rem;
    }
    
    /* Welcome message */
    .welcome-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 1rem;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
    }
    
    .welcome-title {
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .welcome-text {
        font-size: 1rem;
        opacity: 0.95;
    }
    
    /* Quick action cards */
    .quick-action-card {
        background: white;
        border: 2px solid var(--border-color);
        border-radius: 0.75rem;
        padding: 1.5rem;
        cursor: pointer;
        transition: all 0.3s ease;
        height: 100%;
    }
    
    .quick-action-card:hover {
        border-color: var(--primary-color);
        box-shadow: 0 4px 16px rgba(31, 119, 180, 0.2);
        transform: translateY(-5px);
    }
    
    .quick-action-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    
    .quick-action-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #333;
        margin-bottom: 0.5rem;
    }
    
    .quick-action-desc {
        font-size: 0.9rem;
        color: #666;
    }
</style>
""", unsafe_allow_html=True)


# API Configuration
API_BASE_URL = st.secrets.get("API_URL", "http://localhost:8000/api/v1")


# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "api_status" not in st.session_state:
    st.session_state.api_status = None
if "show_welcome" not in st.session_state:
    st.session_state.show_welcome = True


def call_query_api(query: str, chat_history: List[tuple] = None) -> Dict[str, Any]:
    """Call the query API endpoint with improved error handling"""
    try:
        with st.spinner("🔍 Searching through your documents..."):
            response = requests.post(
                f"{API_BASE_URL}/query",
                json={
                    "query": query,
                    "chat_history": chat_history or [],
                    "include_sources": True,
                    "include_followup": True
                },
                timeout=60
            )
            response.raise_for_status()
            return response.json()
    except requests.exceptions.Timeout:
        st.error("⏱️ Request timed out. Please try again.")
        return None
    except requests.exceptions.ConnectionError:
        st.error("🔌 Unable to connect to the API. Please check if the server is running.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"❌ API Error: {str(e)}")
        return None


def call_summary_api(query: str, summary_type: str = "comprehensive") -> Dict[str, Any]:
    """Call the summary API endpoint with improved error handling"""
    try:
        with st.spinner(f"📊 Generating {summary_type} summary..."):
            response = requests.post(
                f"{API_BASE_URL}/summarize",
                json={
                    "query": query,
                    "summary_type": summary_type,
                    "max_docs": 10
                },
                timeout=90
            )
            response.raise_for_status()
            return response.json()
    except requests.exceptions.Timeout:
        st.error("⏱️ Summary generation timed out. Please try again.")
        return None
    except requests.exceptions.ConnectionError:
        st.error("🔌 Unable to connect to the API. Please check if the server is running.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"❌ API Error: {str(e)}")
        return None


def get_system_info() -> Dict[str, Any]:
    """Get system information with caching"""
    try:
        response = requests.get(
            f"{API_BASE_URL.replace('/api/v1', '')}/api/v1/system/info", 
            timeout=10
        )
        response.raise_for_status()
        st.session_state.api_status = "online"
        return response.json()
    except:
        st.session_state.api_status = "offline"
        return None


def render_source_box(source: Dict[str, Any], index: int):
    """Render an enhanced source box"""
    metadata = source.get('metadata', {})
    filename = metadata.get('filename', 'Unknown')
    content = source.get('content', '')
    score = source.get('score', 0)
    
    st.markdown(f"""
    <div class="source-box">
        <div class="source-header">
            📄 Source {index + 1}: {filename}
        </div>
        <div class="source-content">
            {content[:300]}{'...' if len(content) > 300 else ''}
        </div>
        <div class="source-meta">
            <span>📊 Relevance: {score:.2%}</span>
            <span>📏 Length: {len(content)} chars</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_followup_questions(questions: List[str]):
    """Render clickable follow-up questions"""
    if questions:
        st.markdown("**💡 Suggested follow-up questions:**")
        for i, question in enumerate(questions):
            # Use columns to create a clickable area
            if st.button(f"💬 {question}", key=f"followup_{i}_{time.time()}", use_container_width=True):
                # Add the question to chat
                st.session_state.messages.append({"role": "user", "content": question})
                st.rerun()


# Sidebar with enhanced design
with st.sidebar:
    # Header
    st.markdown("## 🚀 Project Polaris")
    st.markdown("### Document Intelligence")
    
    # API Status indicator
    if st.session_state.api_status:
        status_color = "🟢" if st.session_state.api_status == "online" else "🔴"
        status_text = "Online" if st.session_state.api_status == "online" else "Offline"
        st.markdown(f"{status_color} **API Status:** {status_text}")
    
    st.markdown("---")
    
    # Mode selection with icons
    mode = st.radio(
        "Navigation",
        ["💬 Chat", "📄 Summarize", "📊 System Info"],
        index=0,
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Mode-specific settings
    if mode == "📄 Summarize":
        st.markdown("#### Summary Settings")
        summary_type = st.selectbox(
            "Type",
            ["comprehensive", "brief", "executive"],
            index=0,
            help="Choose the level of detail for your summary"
        )
        
        st.markdown("**Summary Types:**")
        st.markdown("- **Comprehensive**: Detailed analysis")
        st.markdown("- **Brief**: Quick overview")
        st.markdown("- **Executive**: High-level insights")
    
    st.markdown("---")
    
    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.messages = []
            st.session_state.chat_history = []
            st.session_state.show_welcome = True
            st.rerun()
    
    with col2:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    
    st.markdown("---")
    
    # Quick Stats
    st.markdown("#### 📊 Quick Stats")
    
    sys_info = get_system_info()
    if sys_info:
        vector_stats = sys_info.get("vector_store", {})
        
        # Display metrics with better formatting
        st.metric(
            "Documents", 
            vector_stats.get("total_documents", 0),
            delta=None,
            help="Total number of document chunks"
        )
        st.metric(
            "Unique Files", 
            vector_stats.get("unique_files", 0),
            delta=None,
            help="Number of source files"
        )
        
        # Storage info if available
        if "storage_size" in vector_stats:
            st.metric("Storage", vector_stats["storage_size"])
    else:
        st.warning("⚠️ Unable to load stats")
    
    st.markdown("---")
    
    # Help section
    with st.expander("ℹ️ Help & Tips"):
        st.markdown("""
        **Chat Mode:**
        - Ask questions in natural language
        - Click suggested follow-ups
        - View source documents
        
        **Summarize Mode:**
        - Request document summaries
        - Choose summary depth
        - Get key insights
        
        **System Info:**
        - Check system health
        - View configuration
        - Monitor resources
        """)


# Main content area
st.markdown('<div class="main-header">🚀 Project Polaris</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Intelligent Document Management & Retrieval System</div>', 
            unsafe_allow_html=True)


# Chat Mode
if mode == "💬 Chat":
    # Welcome message for first-time users
    if st.session_state.show_welcome and len(st.session_state.messages) == 0:
        st.markdown("""
        <div class="welcome-box">
            <div class="welcome-title">👋 Welcome to Project Polaris!</div>
            <div class="welcome-text">
                Ask me anything about your documents. I can help you find information, 
                summarize content, and answer complex questions using advanced AI.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick action cards
        st.markdown("#### 🚀 Quick Start")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Analyze Data", use_container_width=True):
                st.session_state.messages.append({
                    "role": "user", 
                    "content": "What are the key metrics in my documents?"
                })
                st.session_state.show_welcome = False
                st.rerun()
        
        with col2:
            if st.button("🔍 Find Info", use_container_width=True):
                st.session_state.messages.append({
                    "role": "user", 
                    "content": "What documents do you have access to?"
                })
                st.session_state.show_welcome = False
                st.rerun()
        
        with col3:
            if st.button("📝 Summarize", use_container_width=True):
                st.session_state.messages.append({
                    "role": "user", 
                    "content": "Give me a summary of all available documents"
                })
                st.session_state.show_welcome = False
                st.rerun()
        
        st.markdown("---")
    
    # Display chat history
    for idx, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Display sources if available
            if "sources" in message and message["sources"]:
                with st.expander(f"📚 View {len(message['sources'])} sources", expanded=False):
                    for i, source in enumerate(message["sources"]):
                        render_source_box(source, i)
            
            # Display response time if available
            if "response_time" in message:
                st.markdown(f"""
                <div class="response-time">
                    ⚡ Response time: {message['response_time']:.2f}s
                </div>
                """, unsafe_allow_html=True)
            
            # Display follow-up questions with clickable buttons
            if "followup" in message and message["followup"]:
                render_followup_questions(message["followup"])
    
    # Chat input
    if prompt := st.chat_input("💬 Ask a question about your documents...", key="chat_input"):
        # Hide welcome message
        st.session_state.show_welcome = False
        
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            start_time = time.time()
            
            # Call API
            result = call_query_api(prompt, st.session_state.chat_history)
            
            if result and result.get("success"):
                answer = result["answer"]
                sources = result.get("sources", [])
                followup = result.get("followup_questions", [])
                exec_time = time.time() - start_time
                
                # Display answer
                st.markdown(answer)
                
                # Display response time
                st.markdown(f"""
                <div class="response-time">
                    ⚡ Response time: {exec_time:.2f}s | 📄 Sources: {len(sources)}
                </div>
                """, unsafe_allow_html=True)
                
                # Display sources
                if sources:
                    with st.expander(f"📚 View {len(sources)} sources", expanded=False):
                        for i, source in enumerate(sources):
                            render_source_box(source, i)
                
                # Display follow-up questions
                if followup:
                    render_followup_questions(followup)
                
                # Save to history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources,
                    "followup": followup,
                    "response_time": exec_time
                })
                st.session_state.chat_history.append((prompt, answer))
            else:
                st.error("❌ Failed to get response. Please try again.")


# Summarize Mode
elif mode == "📄 Summarize":
    st.markdown("### Generate Document Summaries")
    
    # Summary type info
    st.info("""
    💡 **Tips for better summaries:**
    - Be specific about what you want to summarize
    - Use filters like date ranges or document types
    - Choose the appropriate summary type for your needs
    """)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        summary_query = st.text_area(
            "What would you like to summarize?",
            placeholder="E.g., 'Summarize all Q4 financial reports' or 'Overview of client feedback from last month'",
            height=120,
            help="Describe the documents you want to summarize and any specific focus areas"
        )
    
    with col2:
        st.markdown("#### ⚙️ Settings")
        summary_type = st.selectbox(
            "Summary Type",
            ["comprehensive", "brief", "executive"],
            index=0,
            help="Select the level of detail"
        )
        
        # Additional options
        include_quotes = st.checkbox("Include quotes", value=True)
        include_stats = st.checkbox("Include statistics", value=True)
    
    # Generate button
    if st.button("🎯 Generate Summary", type="primary", use_container_width=True):
        if summary_query:
            start_time = time.time()
            result = call_summary_api(summary_query, summary_type)
            exec_time = time.time() - start_time
            
            if result and result.get("success"):
                # Success message
                st.success(f"✅ Summary generated in {exec_time:.2f}s")
                
                # Main summary
                st.markdown('<div class="section-header">📝 Summary</div>', unsafe_allow_html=True)
                st.markdown(result["summary"])
                
                # Create tabs for additional information
                tab1, tab2, tab3 = st.tabs(["🎯 Key Points", "💡 Insights", "📚 Sources"])
                
                with tab1:
                    if result.get("key_points"):
                        for i, point in enumerate(result["key_points"], 1):
                            st.markdown(f"**{i}.** {point}")
                    else:
                        st.info("No key points extracted")
                
                with tab2:
                    if result.get("insights"):
                        for insight in result["insights"]:
                            st.markdown(f"💡 {insight}")
                    else:
                        st.info("No insights generated")
                
                with tab3:
                    st.metric("Documents Analyzed", result.get('num_documents_analyzed', 0))
                    st.markdown("---")
                    
                    doc_sources = result.get("document_sources", [])
                    if doc_sources:
                        for doc in doc_sources:
                            st.markdown(f"- 📄 {doc.get('filename', 'Unknown')}")
                    else:
                        st.info("No source information available")
                
                # Download options
                st.markdown("---")
                st.markdown("#### 💾 Export Options")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.download_button(
                        "📥 Download as Text",
                        data=result["summary"],
                        file_name=f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain"
                    )
            else:
                st.error("❌ Failed to generate summary. Please try again.")
        else:
            st.warning("⚠️ Please enter a summary topic or question.")


# System Info Mode
elif mode == "📊 System Info":
    st.markdown("### System Status & Information")
    
    # Refresh button
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()
    
    sys_info = get_system_info()
    
    if sys_info:
        # System Overview
        st.markdown('<div class="section-header">🖥️ System Overview</div>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="stat-box">', unsafe_allow_html=True)
            st.metric("Status", "🟢 Online")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="stat-box">', unsafe_allow_html=True)
            st.metric("Environment", sys_info["system"]["environment"])
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="stat-box">', unsafe_allow_html=True)
            st.metric("Version", sys_info["system"]["version"])
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="stat-box">', unsafe_allow_html=True)
            current_time = datetime.now().strftime("%H:%M:%S")
            st.metric("Time", current_time)
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Vector Store Stats
        st.markdown('<div class="section-header">📦 Vector Store</div>', unsafe_allow_html=True)
        vector_stats = sys_info.get("vector_store", {})
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Documents", 
                f"{vector_stats.get('total_documents', 0):,}",
                help="Total number of document chunks in the vector store"
            )
        
        with col2:
            st.metric(
                "Unique Files", 
                vector_stats.get("unique_files", 0),
                help="Number of source files processed"
            )
        
        with col3:
            st.metric(
                "Collection", 
                vector_stats.get("collection_name", "N/A"),
                help="Active collection name"
            )
        
        with col4:
            # Calculate average chunks per file
            total_docs = vector_stats.get('total_documents', 0)
            unique_files = vector_stats.get("unique_files", 1)
            avg_chunks = total_docs / unique_files if unique_files > 0 else 0
            st.metric(
                "Avg Chunks/File",
                f"{avg_chunks:.1f}",
                help="Average number of chunks per file"
            )
        
        st.markdown("---")
        
        # Models Info
        st.markdown('<div class="section-header">🤖 AI Models</div>', unsafe_allow_html=True)
        models = sys_info.get("models", {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Language Models:**")
            st.markdown(f"- ⚡ Flash: `{models.get('flash', 'N/A')}`")
            st.markdown(f"- 🎯 Pro: `{models.get('pro', 'N/A')}`")
        
        with col2:
            st.markdown("**Embeddings:**")
            st.markdown(f"- 📊 Model: `{models.get('embeddings', 'N/A')}`")
        
        st.markdown("---")
        
        # RAG Configuration
        st.markdown('<div class="section-header">🔍 RAG Configuration</div>', unsafe_allow_html=True)
        retriever = sys_info.get("retriever", {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Search Features:**")
            hyde_status = "✅ Enabled" if retriever.get('enable_hyde') else "❌ Disabled"
            hybrid_status = "✅ Enabled" if retriever.get('enable_hybrid') else "❌ Disabled"
            st.markdown(f"- HyDE: {hyde_status}")
            st.markdown(f"- Hybrid Search: {hybrid_status}")
        
        with col2:
            st.markdown("**Retrieval Settings:**")
            rerank_status = "✅ Enabled" if retriever.get('enable_reranking') else "❌ Disabled"
            st.markdown(f"- Reranking: {rerank_status}")
            st.markdown(f"- Top-K Results: {retriever.get('top_k_final', 'N/A')}")
        
        # Performance metrics
        if "performance" in sys_info:
            st.markdown("---")
            st.markdown('<div class="section-header">⚡ Performance Metrics</div>', unsafe_allow_html=True)
            perf = sys_info["performance"]
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Avg Query Time", f"{perf.get('avg_query_time', 0):.2f}s")
            with col2:
                st.metric("Total Queries", f"{perf.get('total_queries', 0):,}")
            with col3:
                st.metric("Cache Hit Rate", f"{perf.get('cache_hit_rate', 0):.1%}")
        
    else:
        st.error("❌ Failed to load system information. Please check your API connection.")
        
        # Troubleshooting tips
        with st.expander("🔧 Troubleshooting"):
            st.markdown("""
            **Common issues:**
            1. Check if the API server is running
            2. Verify the API_URL in your secrets/config
            3. Ensure network connectivity
            4. Check firewall settings
            
            **Current API URL:**  
            `{}`
            """.format(API_BASE_URL))


# Footer
st.markdown("---")
footer_col1, footer_col2, footer_col3 = st.columns([1, 2, 1])

with footer_col2:
    st.markdown(
        '<div style="text-align: center; color: #666; font-size: 0.9rem;">'
        '🚀 Project Polaris v1.0 - Advanced Document Intelligence System<br>'
        f'<small>Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</small>'
        '</div>',
        unsafe_allow_html=True
    )