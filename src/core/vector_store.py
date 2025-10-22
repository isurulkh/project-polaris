"""
Supabase PGVector Vector Store Implementation
Connects to n8n-created Supabase vector database
"""

import logging
from src.core.supabase_vector_store import SupabaseVectorStoreWrapper

logger = logging.getLogger(__name__)


class SupabasePGVectorStore(SupabaseVectorStoreWrapper):
    """
    Main vector store class - uses Supabase native implementation
    Compatible with n8n Supabase Vector Store node
    """
    pass