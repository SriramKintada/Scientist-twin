-- Run this in Supabase SQL Editor: https://supabase.com/dashboard/project/nlgcvxygeicujcqwomut/sql/new

CREATE EXTENSION IF NOT EXISTS vector;

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
    embedding vector(384),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS quiz_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id TEXT NOT NULL,
    domain TEXT,
    user_profile JSONB,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    ip_hash TEXT
);

CREATE TABLE IF NOT EXISTS quiz_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES quiz_sessions(id),
    scientist_name TEXT NOT NULL,
    match_score FLOAT,
    match_quality TEXT,
    rank INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS likes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES quiz_sessions(id),
    scientist_name TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS shares (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES quiz_sessions(id),
    scientist_name TEXT NOT NULL,
    platform TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE quiz_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE quiz_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE likes ENABLE ROW LEVEL SECURITY;
ALTER TABLE shares ENABLE ROW LEVEL SECURITY;
ALTER TABLE scientists ENABLE ROW LEVEL SECURITY;

-- Allow public access for the app
CREATE POLICY "Allow all" ON scientists FOR ALL USING (true);
CREATE POLICY "Allow all" ON quiz_sessions FOR ALL USING (true);
CREATE POLICY "Allow all" ON quiz_results FOR ALL USING (true);
CREATE POLICY "Allow all" ON likes FOR ALL USING (true);
CREATE POLICY "Allow all" ON shares FOR ALL USING (true);
