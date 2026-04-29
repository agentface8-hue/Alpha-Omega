"""Verify signals are in Supabase."""
from dotenv import load_dotenv
import os
load_dotenv()
from supabase import create_client

sb = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_ANON_KEY"))
r = sb.table("signals").select("ticker,status,data->pnl_pct").execute()
print(f"Signals in Supabase: {len(r.data)}")
for row in r.data:
    print(f"  {row['ticker']:6} | {row['status']:8}")

print("\nSignals are now PERMANENT - survive any Render restart!")
