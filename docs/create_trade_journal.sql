-- Run this in Supabase Dashboard > SQL Editor
CREATE TABLE IF NOT EXISTS trade_journal (
    id BIGSERIAL PRIMARY KEY,
    scanned_at TIMESTAMPTZ DEFAULT NOW(),
    ticker VARCHAR(10) NOT NULL,
    price_at_scan NUMERIC(12,2),
    conviction_pct INTEGER,
    heat VARCHAR(10),
    hard_fail BOOLEAN DEFAULT FALSE,
    hard_fail_reason TEXT DEFAULT '',
    trend VARCHAR(10),
    tas VARCHAR(5),
    ma150_position VARCHAR(10),
    rr NUMERIC(6,2),
    sl NUMERIC(12,2),
    tp1 NUMERIC(12,2),
    entry_low NUMERIC(12,2),
    entry_high NUMERIC(12,2),
    regime VARCHAR(30),
    pillar_scores JSONB DEFAULT '{}',
    ta_note TEXT DEFAULT '',
    price_5d NUMERIC(12,2),
    price_10d NUMERIC(12,2),
    price_30d NUMERIC(12,2),
    outcome VARCHAR(20)
);

ALTER TABLE trade_journal ENABLE ROW LEVEL SECURITY;
CREATE POLICY "allow_all_trade_journal" ON trade_journal FOR ALL USING (true) WITH CHECK (true);
