-- Project Polaris Database Setup Script
-- Run this script in your Supabase SQL editor to create the required tables

-- Enable pgvector extension (if not already enabled)
CREATE EXTENSION IF NOT EXISTS vector;

-- Create the collection table (used by LangChain to organize document collections)
CREATE TABLE IF NOT EXISTS langchain_pg_collection (
    uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR NOT NULL,
    cmetadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create unique index on collection name
CREATE UNIQUE INDEX IF NOT EXISTS idx_langchain_pg_collection_name 
ON langchain_pg_collection (name);

-- Create the embedding table (stores document chunks and their vector embeddings)
CREATE TABLE IF NOT EXISTS langchain_pg_embedding (
    uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    collection_id UUID NOT NULL REFERENCES langchain_pg_collection(uuid) ON DELETE CASCADE,
    embedding VECTOR(768),  -- Gemini embedding dimension is 768
    document TEXT NOT NULL,
    cmetadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for optimal performance
-- Vector similarity search index (HNSW for fast approximate nearest neighbor)
CREATE INDEX IF NOT EXISTS idx_langchain_pg_embedding_vector 
ON langchain_pg_embedding USING hnsw (embedding vector_cosine_ops);

-- Full-text search index for hybrid search
CREATE INDEX IF NOT EXISTS idx_langchain_pg_embedding_document_gin 
ON langchain_pg_embedding USING gin(to_tsvector('english', document));

-- Collection ID index for filtering
CREATE INDEX IF NOT EXISTS idx_langchain_pg_embedding_collection_id 
ON langchain_pg_embedding (collection_id);

-- Metadata index for filtering by metadata
CREATE INDEX IF NOT EXISTS idx_langchain_pg_embedding_metadata 
ON langchain_pg_embedding USING gin(cmetadata);

-- Create the default collection for Google Drive documents
INSERT INTO langchain_pg_collection (name, cmetadata) 
VALUES ('google_drive_documents', '{"description": "Documents from Google Drive via n8n workflow"}')
ON CONFLICT (name) DO NOTHING;

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers to automatically update the updated_at column
CREATE TRIGGER update_langchain_pg_collection_updated_at 
    BEFORE UPDATE ON langchain_pg_collection 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_langchain_pg_embedding_updated_at 
    BEFORE UPDATE ON langchain_pg_embedding 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Grant necessary permissions (adjust as needed for your setup)
-- These are typically handled by Supabase automatically, but included for completeness
-- GRANT ALL ON langchain_pg_collection TO authenticated;
-- GRANT ALL ON langchain_pg_embedding TO authenticated;

-- Display setup completion message
DO $$
BEGIN
    RAISE NOTICE 'Project Polaris database setup completed successfully!';
    RAISE NOTICE 'Tables created: langchain_pg_collection, langchain_pg_embedding';
    RAISE NOTICE 'Indexes created for optimal vector and text search performance';
    RAISE NOTICE 'Default collection "google_drive_documents" created';
END $$;