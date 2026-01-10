-- Scientist Twin - Supabase Schema
-- Run this in Supabase SQL Editor

-- Enable pgvector extension for semantic search
CREATE EXTENSION IF NOT EXISTS vector;

-- Scientists table with vector embeddings
CREATE TABLE IF NOT EXISTS scientists (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT UNIQUE NOT NULL,
    field TEXT NOT NULL,
    subfield TEXT,
    era TEXT,
    archetype TEXT,
    summary TEXT,
    achievements TEXT,
    working_style TEXT,
    traits JSONB,
    moments JSONB,
    wiki_title TEXT,
    embedding vector(384),  -- For semantic search (all-MiniLM-L6-v2 produces 384-dim)
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Quiz sessions - tracks each quiz attempt
CREATE TABLE IF NOT EXISTS quiz_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id TEXT NOT NULL,  -- Browser session identifier
    domain TEXT,
    user_profile JSONB,  -- Their trait answers
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    ip_hash TEXT  -- Hashed IP for rough geo (privacy-safe)
);

-- Quiz results - stores match results
CREATE TABLE IF NOT EXISTS quiz_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES quiz_sessions(id),
    scientist_name TEXT NOT NULL,
    scientist_id UUID REFERENCES scientists(id),
    match_score FLOAT,
    match_quality TEXT,
    rank INTEGER,  -- 1 = primary match, 2 = second, 3 = third
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Likes - when users heart their result
CREATE TABLE IF NOT EXISTS likes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES quiz_sessions(id),
    scientist_name TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Shares - track social shares
CREATE TABLE IF NOT EXISTS shares (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES quiz_sessions(id),
    scientist_name TEXT NOT NULL,
    platform TEXT,  -- twitter, whatsapp, linkedin, copy
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_quiz_sessions_completed ON quiz_sessions(completed_at) WHERE completed_at IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_quiz_results_scientist ON quiz_results(scientist_name);
CREATE INDEX IF NOT EXISTS idx_quiz_results_created ON quiz_results(created_at);
CREATE INDEX IF NOT EXISTS idx_likes_scientist ON likes(scientist_name);
CREATE INDEX IF NOT EXISTS idx_scientists_embedding ON scientists USING ivfflat (embedding vector_cosine_ops) WITH (lists = 20);

-- Views for analytics

-- Hall of Fame: Most matched scientists
CREATE OR REPLACE VIEW hall_of_fame AS
SELECT
    scientist_name,
    COUNT(*) as match_count,
    ROUND(AVG(match_score) * 100) as avg_match_percent,
    COUNT(*) FILTER (WHERE rank = 1) as primary_matches
FROM quiz_results
GROUP BY scientist_name
ORDER BY match_count DESC
LIMIT 10;

-- Recent activity feed
CREATE OR REPLACE VIEW recent_activity AS
SELECT
    qr.scientist_name,
    qs.session_id,
    qr.match_quality,
    qr.created_at
FROM quiz_results qr
JOIN quiz_sessions qs ON qr.session_id = qs.id
WHERE qr.rank = 1
ORDER BY qr.created_at DESC
LIMIT 20;

-- Trait distribution in community
CREATE OR REPLACE VIEW trait_distribution AS
SELECT
    trait_key,
    trait_value,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY trait_key), 1) as percentage
FROM quiz_sessions,
LATERAL jsonb_each_text(user_profile) AS traits(trait_key, trait_value)
WHERE completed_at IS NOT NULL
GROUP BY trait_key, trait_value
ORDER BY trait_key, count DESC;

-- Popular domains
CREATE OR REPLACE VIEW popular_domains AS
SELECT
    domain,
    COUNT(*) as play_count
FROM quiz_sessions
WHERE completed_at IS NOT NULL
GROUP BY domain
ORDER BY play_count DESC;

-- Overall stats
CREATE OR REPLACE VIEW overall_stats AS
SELECT
    COUNT(*) FILTER (WHERE completed_at IS NOT NULL) as total_plays,
    COUNT(DISTINCT session_id) as unique_sessions,
    COUNT(*) FILTER (WHERE completed_at IS NOT NULL AND completed_at > NOW() - INTERVAL '24 hours') as plays_today,
    (SELECT COUNT(*) FROM likes) as total_likes,
    (SELECT COUNT(*) FROM shares) as total_shares
FROM quiz_sessions;

-- Function for vector similarity search
CREATE OR REPLACE FUNCTION match_scientists_by_embedding(
    query_embedding vector(384),
    match_threshold float DEFAULT 0.7,
    match_count int DEFAULT 5
)
RETURNS TABLE (
    id UUID,
    name TEXT,
    field TEXT,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        s.id,
        s.name,
        s.field,
        1 - (s.embedding <=> query_embedding) as similarity
    FROM scientists s
    WHERE s.embedding IS NOT NULL
    AND 1 - (s.embedding <=> query_embedding) > match_threshold
    ORDER BY s.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Row Level Security (optional but recommended)
ALTER TABLE quiz_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE quiz_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE likes ENABLE ROW LEVEL SECURITY;
ALTER TABLE shares ENABLE ROW LEVEL SECURITY;

-- Allow anonymous inserts (for quiz tracking)
CREATE POLICY "Allow anonymous inserts" ON quiz_sessions FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow anonymous inserts" ON quiz_results FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow anonymous inserts" ON likes FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow anonymous inserts" ON shares FOR INSERT WITH CHECK (true);

-- Allow public reads for analytics
CREATE POLICY "Allow public reads" ON quiz_sessions FOR SELECT USING (true);
CREATE POLICY "Allow public reads" ON quiz_results FOR SELECT USING (true);
