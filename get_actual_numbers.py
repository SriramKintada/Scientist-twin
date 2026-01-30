"""
Get ACTUAL ISF event numbers - direct from Supabase
"""
import supabase_client as db

print("="*70)
print("  ISF EVENT - ACTUAL NUMBERS")
print("="*70)

client = db.get_client()
if not client:
    print("ERROR: Could not connect to Supabase")
    exit(1)

print("\nConnected to Supabase. Fetching data...\n")

# 1. Total people who played (completed quiz)
total_completed = client.table("quiz_sessions")\
    .select("id", count="exact")\
    .not_.is_("completed_at", "null")\
    .execute()

print(f"TOTAL PEOPLE WHO PLAYED: {total_completed.count}")
print(f"  (People who completed the full quiz)\n")

# 2. Total sessions started (including incomplete)
total_started = client.table("quiz_sessions")\
    .select("id", count="exact")\
    .execute()

incomplete = total_started.count - total_completed.count
print(f"Total sessions started: {total_started.count}")
print(f"Incomplete (didn't finish): {incomplete}")
print(f"Completion rate: {(total_completed.count / total_started.count * 100):.1f}%\n")

# 3. Get all completed sessions to analyze
print("Fetching all session details...")
all_sessions = client.table("quiz_sessions")\
    .select("id, session_id, domain, user_profile, completed_at")\
    .not_.is_("completed_at", "null")\
    .execute()

print(f"Retrieved {len(all_sessions.data)} completed sessions\n")

# 4. Domain breakdown
domain_counts = {}
for session in all_sessions.data:
    domain = session.get('domain', 'unknown')
    domain_counts[domain] = domain_counts.get(domain, 0) + 1

print("-"*70)
print("DOMAIN BREAKDOWN:")
print("-"*70)
for domain, count in sorted(domain_counts.items(), key=lambda x: -x[1]):
    pct = (count / total_completed.count * 100) if total_completed.count > 0 else 0
    print(f"  {domain:15} : {count:3} users ({pct:5.1f}%)")

# 5. Most matched scientists
print("\n" + "-"*70)
print("TOP MATCHED SCIENTISTS:")
print("-"*70)

results = client.table("quiz_results")\
    .select("scientist_name, scientist_field")\
    .eq("rank", 1)\
    .execute()

scientist_counts = {}
for result in results.data:
    name = result.get('scientist_name', 'Unknown')
    scientist_counts[name] = scientist_counts.get(name, 0) + 1

top_scientists = sorted(scientist_counts.items(), key=lambda x: -x[1])[:15]
for i, (name, count) in enumerate(top_scientists, 1):
    pct = (count / total_completed.count * 100) if total_completed.count > 0 else 0
    print(f"  {i:2}. {name:30} : {count:3} users ({pct:5.1f}%)")

# 6. Likes and shares
print("\n" + "-"*70)
print("ENGAGEMENT:")
print("-"*70)

likes = client.table("likes").select("id", count="exact").execute()
shares = client.table("shares").select("id", count="exact").execute()

print(f"  Total likes (favorites): {likes.count}")
print(f"  Total shares: {shares.count}")
if total_completed.count > 0:
    print(f"  Like rate: {(likes.count / total_completed.count * 100):.1f}%")
    print(f"  Share rate: {(shares.count / total_completed.count * 100):.1f}%")

# 7. Check for duplicates
print("\n" + "-"*70)
print("DUPLICATE CHECK:")
print("-"*70)

session_ids = [s['session_id'] for s in all_sessions.data]
unique_session_ids = len(set(session_ids))
duplicates = len(session_ids) - unique_session_ids

print(f"  Total session records: {len(session_ids)}")
print(f"  Unique session IDs: {unique_session_ids}")
print(f"  Duplicate records: {duplicates}")

if duplicates > 0:
    print(f"\n  NOTE: {duplicates} duplicate records found.")
    print(f"  Actual unique users: ~{unique_session_ids}")
    print(f"  Some users may have taken the quiz multiple times.")

print("\n" + "="*70)
print(f"  SUMMARY: {total_completed.count} people played the quiz at ISF")
if duplicates > 0:
    print(f"  (Approximately {unique_session_ids} unique users)")
print("="*70)
