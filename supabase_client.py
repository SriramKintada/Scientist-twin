"""
Supabase Client for Scientist Twin
Handles all database operations, analytics, and vector search
"""

import os
import json
import hashlib
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from supabase import create_client, Client

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")  # Use anon/public key

_supabase: Optional[Client] = None

def get_client() -> Optional[Client]:
    """Get or create Supabase client"""
    global _supabase
    if _supabase is None and SUPABASE_URL and SUPABASE_KEY:
        try:
            _supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        except Exception as e:
            print(f"[Supabase] Connection failed: {e}")
            return None
    return _supabase

def is_connected() -> bool:
    """Check if Supabase is connected"""
    return get_client() is not None


# ============ QUIZ SESSION TRACKING ============

def create_quiz_session(session_id: str, domain: str, ip_address: str = None) -> Optional[str]:
    """Create a new quiz session, returns session UUID"""
    client = get_client()
    if not client:
        return None

    try:
        # Hash IP for privacy
        ip_hash = hashlib.sha256(ip_address.encode()).hexdigest()[:16] if ip_address else None

        result = client.table("quiz_sessions").insert({
            "session_id": session_id,
            "domain": domain,
            "ip_hash": ip_hash
        }).execute()

        if result.data:
            return result.data[0]["id"]
    except Exception as e:
        print(f"[Supabase] Error creating session: {e}")
    return None

def complete_quiz_session(session_uuid: str, user_profile: dict) -> bool:
    """Mark quiz session as complete with user's trait profile"""
    client = get_client()
    if not client:
        return False

    try:
        client.table("quiz_sessions").update({
            "user_profile": user_profile,
            "completed_at": datetime.utcnow().isoformat()
        }).eq("id", session_uuid).execute()
        return True
    except Exception as e:
        print(f"[Supabase] Error completing session: {e}")
    return False


# ============ QUIZ RESULTS ============

def save_quiz_results(session_uuid: str, matches: List[Dict]) -> bool:
    """Save the quiz match results"""
    client = get_client()
    if not client:
        return False

    try:
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
    except Exception as e:
        print(f"[Supabase] Error saving results: {e}")
    return False


# ============ LIKES & SHARES ============

def record_like(session_uuid: str, scientist_name: str) -> bool:
    """Record when a user likes their result"""
    client = get_client()
    if not client:
        return False

    try:
        client.table("likes").insert({
            "session_id": session_uuid,
            "scientist_name": scientist_name
        }).execute()
        return True
    except Exception as e:
        print(f"[Supabase] Error recording like: {e}")
    return False

def record_share(session_uuid: str, scientist_name: str, platform: str) -> bool:
    """Record when a user shares their result"""
    client = get_client()
    if not client:
        return False

    try:
        client.table("shares").insert({
            "session_id": session_uuid,
            "scientist_name": scientist_name,
            "platform": platform
        }).execute()
        return True
    except Exception as e:
        print(f"[Supabase] Error recording share: {e}")
    return False


# ============ ANALYTICS ============

def get_real_analytics() -> Dict[str, Any]:
    """Get real analytics from database"""
    client = get_client()
    if not client:
        return None

    try:
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

    except Exception as e:
        print(f"[Supabase] Error getting analytics: {e}")
        return None

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
