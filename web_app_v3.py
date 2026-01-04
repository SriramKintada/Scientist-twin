"""
Scientist Twin 3.0 - Rich Biographical Matching with Supabase
Real analytics, persistent data, and vector similarity search
"""

from flask import Flask, render_template, request, jsonify, session
import secrets
import json
import random
import hashlib
from datetime import datetime, timedelta
from questions_v3_simplified import QUESTIONS, map_answer_to_trait, build_user_profile
from matching_engine_v3 import MatchingEngineV3

# Try to import Supabase client
try:
    import supabase_client as db
    SUPABASE_AVAILABLE = db.is_connected()
    if SUPABASE_AVAILABLE:
        print("[Supabase] Connected - using real analytics")
    else:
        print("[Supabase] Not configured - using fallback analytics")
except ImportError:
    SUPABASE_AVAILABLE = False
    db = None
    print("[Supabase] Client not available - using fallback analytics")

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Initialize with rich database
matching_engine = MatchingEngineV3('scientist_db_rich.json')

DOMAINS = {
    "cosmos": {
        "name": "The Cosmos",
        "description": "Physics, Astrophysics, Space Science",
        "icon": "stars"
    },
    "quantum": {
        "name": "Quantum & Math",
        "description": "Physics, Mathematics, Computer Science",
        "icon": "atom"
    },
    "chemistry": {
        "name": "Chemistry",
        "description": "Chemical Science, Material Science, Organic & Inorganic Chemistry",
        "icon": "flask"
    },
    "life": {
        "name": "Life Sciences",
        "description": "Biology, Medicine, Genetics",
        "icon": "dna"
    },
    "earth": {
        "name": "Earth & Environment",
        "description": "Ecology, Agriculture, Environmental Science",
        "icon": "leaf"
    },
    "engineering": {
        "name": "Engineering & Tech",
        "description": "Engineering, Technology, Innovation",
        "icon": "cog"
    }
}


def get_client_ip():
    """Get client IP address (works behind proxies)"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr


@app.route('/')
def index():
    return render_template('index_v3.html', domains=DOMAINS)


@app.route('/api/start-quiz', methods=['POST'])
def start_quiz():
    data = request.json
    domain = data.get('domain', 'cosmos')

    # Initialize session
    session['domain'] = domain
    session['answers'] = []
    session['current_question'] = 0
    session['quiz_session_id'] = secrets.token_hex(8)

    # Track in Supabase
    if SUPABASE_AVAILABLE and db:
        session_uuid = db.create_quiz_session(
            session_id=session['quiz_session_id'],
            domain=domain,
            ip_address=get_client_ip()
        )
        if session_uuid:
            session['db_session_uuid'] = session_uuid

    question = QUESTIONS[0]
    return jsonify({
        "total_questions": len(QUESTIONS),
        "question": {
            "number": 1,
            "text": question['text'],
            "options": [opt['text'] for opt in question['options']],
            "dimension": question['dimension']
        }
    })


@app.route('/api/answer-question', methods=['POST'])
def answer_question():
    data = request.json
    answer = data.get('answer', 0)

    if 'answers' not in session:
        session['answers'] = []
    session['answers'].append(answer)
    session.modified = True

    current = len(session['answers'])

    if current >= len(QUESTIONS):
        return jsonify({"complete": True})

    question = QUESTIONS[current]
    return jsonify({
        "complete": False,
        "question": {
            "number": current + 1,
            "text": question['text'],
            "options": [opt['text'] for opt in question['options']],
            "dimension": question['dimension']
        }
    })


@app.route('/api/get-matches', methods=['POST'])
def get_matches():
    answers = session.get('answers', [])
    domain = session.get('domain', 'cosmos')

    user_profile = build_user_profile(answers)

    # Anti-repetition: Get recently shown scientists from session
    # Keep track of last 9 scientists shown (3 attempts × 3 matches)
    recently_shown = session.get('recently_shown_scientists', [])

    # Get matches with anti-repetition
    matches = matching_engine.get_full_matches(user_profile, domain, recently_shown=recently_shown)

    # Update recently shown list with current matches
    current_scientists = [m['name'] for m in matches]
    recently_shown.extend(current_scientists)

    # Keep only the last 9 entries (prevent list from growing indefinitely)
    # This gives variety across ~3 quiz attempts
    recently_shown = recently_shown[-9:]
    session['recently_shown_scientists'] = recently_shown
    session.modified = True

    # Calculate trait percentages based on answer positions
    # Each answer (0-3) maps to different intensity levels
    trait_percentages = {}
    for i, answer in enumerate(answers):
        if i < len(QUESTIONS):
            dim = QUESTIONS[i]['dimension']
            # Map answer position to percentage (visual representation)
            # Answer 0=95%, 1=82%, 2=68%, 3=55% (first answer = strongest expression)
            percent_map = {0: 95, 1: 82, 2: 68, 3: 55}
            trait_percentages[dim] = percent_map.get(answer, 75)

    # Save to Supabase
    if SUPABASE_AVAILABLE and db:
        session_uuid = session.get('db_session_uuid')
        if session_uuid:
            # Complete the session
            db.complete_quiz_session(session_uuid, user_profile)
            # Save match results
            db.save_quiz_results(session_uuid, matches)

    return jsonify({
        "user_profile": user_profile,
        "trait_percentages": trait_percentages,
        "matches": matches
    })


@app.route('/api/scientists/count')
def scientist_count():
    return jsonify({
        "count": len(matching_engine.scientists)
    })


@app.route('/dashboard')
def dashboard():
    """Backend dashboard for Suchitha - detailed analytics with password protection"""
    from flask import request, redirect, url_for, session as flask_session

    # Simple password protection
    if not flask_session.get('dashboard_auth'):
        password = request.args.get('password', '')
        if password == 'SciRio2025':
            flask_session['dashboard_auth'] = True
        else:
            return '''
            <html><body style="font-family: Arial; max-width: 500px; margin: 100px auto; text-align: center;">
            <h2>🔐 Backend Dashboard Access</h2>
            <form>
                <input type="password" name="password" placeholder="Enter password" style="padding: 12px; width: 250px; font-size: 16px;"><br><br>
                <button type="submit" style="padding: 12px 24px; font-size: 16px; cursor: pointer;">Access Dashboard</button>
            </form>
            <p style="color: #666; margin-top: 32px;">Contact admin for password</p>
            </body></html>
            '''

    # Get detailed analytics
    detailed_stats = {}

    if SUPABASE_AVAILABLE and db:
        client = db.get_client()
        if client:
            try:
                # Get all sessions with user profiles
                sessions = client.table("quiz_sessions")\
                    .select("*")\
                    .not_.is_("completed_at", "null")\
                    .order("completed_at", desc=True)\
                    .limit(50)\
                    .execute()

                detailed_stats['recent_sessions'] = sessions.data if sessions.data else []

                # Domain distribution
                domain_counts = {}
                trait_counts = {}

                for session in (sessions.data or []):
                    domain = session.get('domain', 'unknown')
                    domain_counts[domain] = domain_counts.get(domain, 0) + 1

                    # Collect trait data
                    profile = session.get('user_profile', {})
                    for dim, value in profile.items():
                        key = f"{dim}:{value}"
                        trait_counts[key] = trait_counts.get(key, 0) + 1

                detailed_stats['domain_distribution'] = [
                    {"domain": d, "count": c}
                    for d, c in sorted(domain_counts.items(), key=lambda x: -x[1])
                ]

                detailed_stats['trait_distribution'] = [
                    {"trait": t, "count": c}
                    for t, c in sorted(trait_counts.items(), key=lambda x: -x[1])[:20]
                ]

                # All quiz results for detailed view
                results = client.table("quiz_results")\
                    .select("*")\
                    .order("id", desc=True)\
                    .limit(100)\
                    .execute()

                detailed_stats['all_results'] = results.data if results.data else []

            except Exception as e:
                print(f"Dashboard error: {e}")
                detailed_stats['error'] = str(e)

    # Also get regular analytics
    if SUPABASE_AVAILABLE and db:
        detailed_stats['summary'] = db.get_real_analytics()

    detailed_stats['total_scientists'] = len(matching_engine.scientists)

    return render_template('dashboard.html', stats=detailed_stats, is_admin=True)


@app.route('/analytics')
def analytics():
    """Analytics dashboard with real or fallback stats"""

    # Try to get real analytics from Supabase
    if SUPABASE_AVAILABLE and db:
        real_stats = db.get_real_analytics()
        if real_stats and real_stats.get('total_plays', 0) > 0:
            return render_template('analytics.html', stats=real_stats, is_real=True)

    # Fallback to generated stats
    scientists = matching_engine.scientists

    # Hall of Fame - top matched scientists (sample from database)
    sample_scientists = random.sample(scientists, min(5, len(scientists)))
    hall_of_fame = []
    match_rates = [87, 72, 68, 54, 49]
    for i, s in enumerate(sample_scientists):
        hall_of_fame.append({
            "name": s["name"],
            "field": s["field"],
            "era": s.get("era", "Modern"),
            "match_rate": match_rates[i] if i < len(match_rates) else random.randint(30, 50),
            "image_url": s.get("image_url", "")
        })

    # Recent activity
    recent_activity = []
    activity_scientists = random.sample(scientists, min(6, len(scientists)))
    times = ["Just now", "2 min ago", "5 min ago", "12 min ago", "23 min ago", "1 hour ago"]
    for i, s in enumerate(activity_scientists):
        recent_activity.append({
            "id": random.randint(1000, 9999),
            "scientist": s["name"],
            "time": times[i] if i < len(times) else f"{random.randint(1, 12)} hours ago"
        })

    # Top traits
    top_traits = [
        {"name": "Curious", "icon": "🔍", "percent": 78},
        {"name": "Collaborative", "icon": "🤝", "percent": 65},
        {"name": "Risk-Taker", "icon": "🎯", "percent": 58},
        {"name": "Visionary", "icon": "🌟", "percent": 52},
        {"name": "Methodical", "icon": "📊", "percent": 47}
    ]

    # Popular fields
    field_counts = {}
    for s in scientists:
        field = s["field"]
        field_counts[field] = field_counts.get(field, 0) + random.randint(5, 25)

    popular_fields = [
        {"name": field, "count": count}
        for field, count in sorted(field_counts.items(), key=lambda x: -x[1])[:5]
    ]

    stats = {
        "total_plays": random.randint(1200, 2500),
        "hall_of_fame": hall_of_fame,
        "recent_activity": recent_activity,
        "top_traits": top_traits,
        "popular_fields": popular_fields,
        "share_rate": random.randint(35, 55),
        "retake_rate": random.randint(20, 40),
        "favorites": random.randint(150, 400),
        "peak_hour": "7-9 PM",
        "peak_day": "Sunday"
    }

    return render_template('analytics.html', stats=stats, is_real=False)


@app.route('/api/like', methods=['POST'])
def like_result():
    """Track when users like their result"""
    data = request.json
    scientist_name = data.get('scientist', '')

    # Save to Supabase
    if SUPABASE_AVAILABLE and db:
        session_uuid = session.get('db_session_uuid')
        if session_uuid:
            db.record_like(session_uuid, scientist_name)

    return jsonify({"success": True, "message": f"Liked {scientist_name}!"})


@app.route('/api/share', methods=['POST'])
def share_result():
    """Track when users share their result"""
    data = request.json
    scientist_name = data.get('scientist', '')
    platform = data.get('platform', 'unknown')

    # Save to Supabase
    if SUPABASE_AVAILABLE and db:
        session_uuid = session.get('db_session_uuid')
        if session_uuid:
            db.record_share(session_uuid, scientist_name, platform)

    return jsonify({"success": True})


@app.route('/api/stats')
def get_stats():
    """API endpoint for real-time stats"""
    if SUPABASE_AVAILABLE and db:
        stats = db.get_real_analytics()
        if stats:
            return jsonify({"success": True, "stats": stats, "is_real": True})

    # Fallback
    return jsonify({
        "success": True,
        "stats": {
            "total_plays": random.randint(1200, 2500),
            "favorites": random.randint(150, 400)
        },
        "is_real": False
    })


if __name__ == '__main__':
    print(f"Loaded {len(matching_engine.scientists)} scientists with rich profiles")
    print(f"Supabase: {'Connected' if SUPABASE_AVAILABLE else 'Not configured (using fallback)'}")
    print("Starting Scientist Twin 3.0...")
    print("Open http://127.0.0.1:5000 in your browser")
    app.run(debug=True, host='127.0.0.1', port=5000)
