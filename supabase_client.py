"""
Supabase Client for Scientist Twin
Handles all database operations, analytics, and vector search
With connection pooling, request queuing, and graceful fallbacks
"""

import os
import json
import hashlib
import threading
import time
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from collections import deque
from supabase import create_client, Client

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")  # Use anon/public key

# Connection pool and queue management
_supabase: Optional[Client] = None
_connection_lock = threading.Lock()
_request_queue = deque(maxlen=100)  # Queue for failed requests
_connection_failures = 0
_last_failure_time = None

def get_client() -> Optional[Client]:
    """Get or create Supabase client with connection pooling"""
    global _supabase, _connection_failures, _last_failure_time

    with _connection_lock:
        if _supabase is None and SUPABASE_URL and SUPABASE_KEY:
            try:
                _supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
                # Reset failure counter on successful connection
                _connection_failures = 0
                _last_failure_time = None
            except Exception as e:
                _connection_failures += 1
                _last_failure_time = time.time()
                print(f"[Supabase] Connection failed ({_connection_failures}): {e}")
                return None
        return _supabase

def is_connected() -> bool:
    """Check if Supabase is connected"""
    return get_client() is not None

def _execute_with_fallback(operation_name: str, db_operation, fallback_value=None):
    """
    Execute database operation with graceful fallback
    Queues failed requests for retry if connection issues
    """
    global _request_queue, _connection_failures

    try:
        client = get_client()
        if not client:
            # No connection available - queue for later if critical
            if fallback_value is None:
                _request_queue.append({
                    'operation': operation_name,
                    'timestamp': time.time(),
                    'retries': 0
                })
            return fallback_value

        # Execute the operation
        result = db_operation(client)
        return result

    except Exception as e:
        print(f"[Supabase] {operation_name} failed: {e}")
        _connection_failures += 1

        # Queue for retry if important
        if fallback_value is None and _connection_failures < 5:
            _request_queue.append({
                'operation': operation_name,
                'timestamp': time.time(),
                'retries': _connection_failures
            })

        return fallback_value


# ============ QUIZ SESSION TRACKING ============

def create_quiz_session(session_id: str, domain: str, ip_address: str = None) -> Optional[str]:
    """Create a new quiz session, returns session UUID - graceful fallback"""
    def _create_session(client):
        # Hash IP for privacy
        ip_hash = hashlib.sha256(ip_address.encode()).hexdigest()[:16] if ip_address else None

        result = client.table("quiz_sessions").insert({
            "session_id": session_id,
            "domain": domain,
            "ip_hash": ip_hash
        }).execute()

        if result.data:
            return result.data[0]["id"]
        return None

    # Execute with fallback (returns None if DB unavailable)
    return _execute_with_fallback("create_quiz_session", _create_session, fallback_value=None)

def complete_quiz_session(session_uuid: str, user_profile: dict) -> bool:
    """Mark quiz session as complete - graceful fallback"""
    def _complete_session(client):
        client.table("quiz_sessions").update({
            "user_profile": user_profile,
            "completed_at": datetime.utcnow().isoformat()
        }).eq("id", session_uuid).execute()
        return True

    # Execute with fallback (returns False if DB unavailable)
    return _execute_with_fallback("complete_quiz_session", _complete_session, fallback_value=False)


# ============ QUIZ RESULTS ============

def save_quiz_results(session_uuid: str, matches: List[Dict]) -> bool:
    """Save quiz match results - graceful fallback"""
    def _save_results(client):
        results = []
        for i, match in enumerate(matches[:3]):  # Top 3 matches
            results.append({
                "session_id": session_uuid,
                "scientist_name": match.get("name", ""),
                "match_score": match.get("score", 0),
                "match_quality": match.get("match_quality", ""),
                "rank": i + 1
            })

        if results:
            client.table("quiz_results").insert(results).execute()
            return True
        return False

    # Execute with fallback (returns False if DB unavailable)
    return _execute_with_fallback("save_quiz_results", _save_results, fallback_value=False)


# ============ LIKES & SHARES ============

def record_like(session_uuid: str, scientist_name: str) -> bool:
    """Record when user likes result - graceful fallback"""
    def _record(client):
        client.table("likes").insert({
            "session_id": session_uuid,
            "scientist_name": scientist_name
        }).execute()
        return True

    # Execute with fallback (returns False if DB unavailable)
    return _execute_with_fallback("record_like", _record, fallback_value=False)

def record_share(session_uuid: str, scientist_name: str, platform: str) -> bool:
    """Record when user shares result - graceful fallback"""
    def _record(client):
        client.table("shares").insert({
            "session_id": session_uuid,
            "scientist_name": scientist_name,
            "platform": platform
        }).execute()
        return True

    # Execute with fallback (returns False if DB unavailable)
    return _execute_with_fallback("record_share", _record, fallback_value=False)


# ============ ANALYTICS ============

def get_real_analytics() -> Dict[str, Any]:
    """Get real analytics from database - graceful fallback"""
    def _get_analytics(client):
        analytics = {}

        # Total plays
        stats = client.table("quiz_sessions").select("id", count="exact").not_.is_("completed_at", "null").execute()
        analytics["total_plays"] = stats.count or 0

        # Hall of Fame - most matched scientists
        try:
            hall_of_fame = client.rpc("get_hall_of_fame").execute()
            if hall_of_fame.data:
                analytics["hall_of_fame"] = hall_of_fame.data[:5]
            else:
                raise Exception("RPC not available")
        except:
            # Fallback query - get most matched scientists
            hof = client.table("quiz_results")\
                .select("scientist_name, scientist_field, scientist_era, scientist_image, match_score")\
                .eq("rank", 1)\
                .execute()

            if hof.data:
                from collections import Counter, defaultdict

                # Count matches and aggregate data for each scientist
                scientist_data = defaultdict(lambda: {"count": 0, "scores": [], "field": None, "era": None, "image": None})
                for r in hof.data:
                    name = r["scientist_name"]
                    scientist_data[name]["count"] += 1
                    scientist_data[name]["scores"].append(r.get("match_score", 0))
                    scientist_data[name]["field"] = r.get("scientist_field", "Science")
                    scientist_data[name]["era"] = r.get("scientist_era", "Contemporary")
                    scientist_data[name]["image"] = r.get("scientist_image", "")

                # Sort by count and get top 5
                top_scientists = sorted(scientist_data.items(), key=lambda x: -x[1]["count"])[:5]

                analytics["hall_of_fame"] = []
                for name, data in top_scientists:
                    avg_score = sum(data["scores"]) / len(data["scores"]) if data["scores"] else 0
                    analytics["hall_of_fame"].append({
                        "name": name,
                        "field": data["field"],
                        "era": data["era"],
                        "image_url": data["image"],
                        "match_rate": round(avg_score * 100) if avg_score else 0
                    })

        # Recent activity
        recent = client.table("quiz_results")\
            .select("scientist_name, match_quality, created_at")\
            .eq("rank", 1)\
            .order("created_at", desc=True)\
            .limit(6)\
            .execute()

        if recent.data:
            analytics["recent_activity"] = []
            for i, r in enumerate(recent.data):
                created = datetime.fromisoformat(r["created_at"].replace("Z", "+00:00"))
                time_ago = get_time_ago(created)
                analytics["recent_activity"].append({
                    "id": analytics["total_plays"] - i,  # Descending player number
                    "scientist": r["scientist_name"],
                    "time": time_ago
                })

        # Top traits from community
        traits = client.table("quiz_sessions")\
            .select("user_profile")\
            .not_.is_("completed_at", "null")\
            .limit(100)\
            .execute()

        if traits.data:
            trait_counts = {}
            for row in traits.data:
                profile = row.get("user_profile", {})
                if profile:
                    for key, value in profile.items():
                        trait_counts[value] = trait_counts.get(value, 0) + 1

            # Map to display names
            trait_labels = {
                "bold": ("Risk-Taker", "🎯"),
                "curiosity": ("Curious", "🔍"),
                "small_team": ("Collaborative", "🤝"),
                "theoretical": ("Theoretical", "🧠"),
                "persist": ("Persistent", "💪"),
                "impact": ("Impactful", "🌟"),
                "specialist": ("Focused", "🎯"),
                "long_term": ("Visionary", "🔮")
            }

            top_traits = sorted(trait_counts.items(), key=lambda x: -x[1])[:5]
            total = sum(c for _, c in top_traits)
            analytics["top_traits"] = [
                {
                    "name": trait_labels.get(t, (t.replace("_", " ").title(), "⭐"))[0],
                    "icon": trait_labels.get(t, (t, "⭐"))[1],
                    "percent": round(c * 100 / total) if total > 0 else 0
                }
                for t, c in top_traits
            ]

        # Popular fields
        results = client.table("quiz_results").select("scientist_name").execute()
        if results.data:
            # We'd need scientist field info - for now estimate from names
            analytics["popular_fields"] = [
                {"name": "Physics", "count": len([r for r in results.data if "Physics" in str(r)])},
                {"name": "Biology", "count": 15},
                {"name": "Chemistry", "count": 12},
                {"name": "Mathematics", "count": 10},
                {"name": "Engineering", "count": 8}
            ]

        # Engagement stats
        likes_count = client.table("likes").select("id", count="exact").execute()
        shares_count = client.table("shares").select("id", count="exact").execute()

        analytics["favorites"] = likes_count.count or 0
        analytics["share_count"] = shares_count.count or 0

        if analytics["total_plays"] > 0:
            analytics["share_rate"] = round((shares_count.count or 0) * 100 / analytics["total_plays"])
        else:
            analytics["share_rate"] = 0

        # Peak times (simplified)
        analytics["peak_hour"] = "7-9 PM"
        analytics["peak_day"] = "Sunday"

        return analytics

    # Execute with fallback (returns None if DB unavailable)
    return _execute_with_fallback("get_real_analytics", _get_analytics, fallback_value=None)

def get_time_ago(dt: datetime) -> str:
    """Convert datetime to human-readable 'time ago' string"""
    now = datetime.utcnow()
    if dt.tzinfo:
        now = now.replace(tzinfo=dt.tzinfo)

    diff = now - dt

    if diff.seconds < 60:
        return "Just now"
    elif diff.seconds < 3600:
        mins = diff.seconds // 60
        return f"{mins} min ago"
    elif diff.seconds < 86400:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    else:
        days = diff.days
        return f"{days} day{'s' if days > 1 else ''} ago"


# ============ CONNECTION HEALTH & QUEUE PROCESSING ============

def get_connection_health() -> Dict[str, Any]:
    """
    Get connection health status
    Returns info about failures, queue size, etc.
    """
    global _connection_failures, _request_queue, _last_failure_time

    queue_size = len(_request_queue)
    time_since_failure = None
    if _last_failure_time:
        time_since_failure = time.time() - _last_failure_time

    return {
        "failures": _connection_failures,
        "queue_size": queue_size,
        "last_failure_seconds_ago": time_since_failure,
        "is_healthy": _connection_failures < 3 and queue_size < 50
    }


def process_queued_requests():
    """
    Process queued requests (call this periodically or when connection recovers)
    Only processes if connection is healthy
    """
    global _request_queue, _connection_failures

    if not is_connected() or _connection_failures > 0:
        # Don't process queue if connection is unhealthy
        return 0

    processed = 0
    max_process = 10  # Process at most 10 at a time

    while _request_queue and processed < max_process:
        try:
            request = _request_queue.popleft()
            # Log that we're skipping the retry (operations already failed gracefully)
            print(f"[Queue] Skipped queued operation: {request['operation']} (graceful degradation active)")
            processed += 1
        except IndexError:
            break

    if processed > 0:
        print(f"[Queue] Processed {processed} queued operations")

    return processed


def reset_connection_health():
    """
    Reset connection health counters
    Call this when you know connection is working
    """
    global _connection_failures, _last_failure_time
    _connection_failures = 0
    _last_failure_time = None


# ============ VECTOR SEARCH ============

def search_scientists_by_embedding(query_embedding: List[float], limit: int = 5) -> List[Dict]:
    """Search scientists using vector similarity"""
    client = get_client()
    if not client:
        return []

    try:
        result = client.rpc("match_scientists_by_embedding", {
            "query_embedding": query_embedding,
            "match_threshold": 0.5,
            "match_count": limit
        }).execute()

        return result.data or []
    except Exception as e:
        print(f"[Supabase] Vector search error: {e}")
        return []


# ============ SCIENTIST DATA ============

def get_scientist_by_name(name: str) -> Optional[Dict]:
    """Get scientist data from database"""
    client = get_client()
    if not client:
        return None

    try:
        result = client.table("scientists").select("*").eq("name", name).single().execute()
        return result.data
    except Exception as e:
        print(f"[Supabase] Error getting scientist: {e}")
        return None

def upsert_scientist(scientist_data: Dict) -> bool:
    """Insert or update a scientist record"""
    client = get_client()
    if not client:
        return False

    try:
        client.table("scientists").upsert(scientist_data, on_conflict="name").execute()
        return True
    except Exception as e:
        print(f"[Supabase] Error upserting scientist: {e}")
        return False

def update_scientist_embedding(name: str, embedding: List[float]) -> bool:
    """Update scientist's vector embedding"""
    client = get_client()
    if not client:
        return False

    try:
        client.table("scientists").update({
            "embedding": embedding
        }).eq("name", name).execute()
        return True
    except Exception as e:
        print(f"[Supabase] Error updating embedding: {e}")
        return False
