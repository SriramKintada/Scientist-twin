"""
Scientist Twin 3.0 - Rich Biographical Matching with Supabase
Real analytics, persistent data, and vector similarity search
"""

from flask import Flask, render_template, request, jsonify, session, redirect
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

# Performance optimizations
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000  # Cache static files for 1 year
app.config['JSON_SORT_KEYS'] = False  # Faster JSON serialization

# Allow embedding in iframes (for SciRio website)
@app.after_request
def add_header(response):
    # Allow embedding from scirio.in and localhost
    response.headers['X-Frame-Options'] = 'ALLOW-FROM https://www.scirio.in'
    response.headers['Content-Security-Policy'] = "frame-ancestors 'self' https://www.scirio.in https://scirio.in"
    return response

# Try to enable compression
try:
    from flask_compress import Compress
    Compress(app)
    print("[Performance] Gzip compression enabled")
except ImportError:
    print("[Performance] flask-compress not available - install with: pip install flask-compress")

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


@app.route('/embed-code')
def embed_code():
    """Provide embed code for SciRio website"""
    # Get the current deployment URL (Vercel or local)
    base_url = request.host_url.rstrip('/')

    embed_snippet = f'''<!-- SciRio Scientist Twin Quiz Embed Code -->
<div id="scirio-scientist-twin" style="width: 100%; max-width: 1200px; margin: 0 auto;">
    <iframe
        src="{base_url}/"
        width="100%"
        height="800"
        frameborder="0"
        scrolling="auto"
        allow="clipboard-write"
        style="border: none; border-radius: 20px; box-shadow: 0 10px 40px rgba(0,0,0,0.1);"
        title="Curious Minds Club - Find Your Indian Scientist Twin">
    </iframe>
</div>

<!-- Optional: Make iframe responsive -->
<script>
    (function() {{
        const iframe = document.querySelector('#scirio-scientist-twin iframe');

        // Auto-resize iframe based on content
        window.addEventListener('message', function(e) {{
            if (e.origin === '{base_url}') {{
                if (e.data.height) {{
                    iframe.style.height = e.data.height + 'px';
                }}
            }}
        }});

        // Responsive sizing
        function resizeIframe() {{
            const container = document.getElementById('scirio-scientist-twin');
            const width = container.offsetWidth;

            if (width < 640) {{
                iframe.style.height = '900px'; // Mobile
            }} else {{
                iframe.style.height = '800px'; // Desktop
            }}
        }}

        resizeIframe();
        window.addEventListener('resize', resizeIframe);
    }})();
</script>'''

    return f'''<!DOCTYPE html>
<html>
<head>
    <title>Scientist Twin - Embed Code</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 900px; margin: 40px auto; padding: 20px; background: #f5f5f5; }}
        .container {{ background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }}
        h1 {{ color: #f87171; margin-bottom: 10px; }}
        .subtitle {{ color: #6b7280; margin-bottom: 30px; }}
        pre {{ background: #1f2937; color: #f3f4f6; padding: 20px; border-radius: 8px; overflow-x: auto; font-size: 13px; line-height: 1.6; }}
        .copy-btn {{ background: #f87171; color: white; border: none; padding: 12px 24px; border-radius: 8px; cursor: pointer; font-size: 16px; margin-top: 10px; font-weight: 600; }}
        .copy-btn:hover {{ background: #ef4444; }}
        .info {{ background: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px 20px; margin: 20px 0; border-radius: 4px; }}
        .success {{ background: #d1fae5; border-left: 4px solid #10b981; padding: 15px 20px; margin: 20px 0; border-radius: 4px; display: none; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🧪 Scientist Twin Quiz - Embed Code</h1>
        <p class="subtitle">Copy and paste this code into your SciRio website</p>
        <div class="info">
            <strong>📋 Instructions:</strong>
            <ol style="margin: 10px 0 0 0; padding-left: 20px;">
                <li>Click "Copy Embed Code" below</li>
                <li>Paste into your HTML where you want the quiz to appear</li>
                <li>The quiz will automatically fit the container width</li>
            </ol>
        </div>
        <pre id="embed-code">{embed_snippet}</pre>
        <button class="copy-btn" onclick="copyCode()">📋 Copy Embed Code</button>
        <div class="success" id="success-msg">✅ <strong>Copied!</strong> Paste this code into your website.</div>
        <div class="info" style="margin-top: 30px;">
            <strong>🔧 Features:</strong><br>
            ✓ Fully responsive (mobile & desktop)<br>
            ✓ Auto-height adjustment<br>
            ✓ Clean styling with rounded corners<br>
            ✓ Secure iframe embedding<br>
            ✓ Works ONLY on scirio.in domains
        </div>
        <div class="info" style="background: #dbeafe; border-left: 4px solid #3b82f6;">
            <strong>🔒 Security Note:</strong><br>
            This quiz is configured to work <strong>ONLY on https://www.scirio.in/</strong> and related SciRio domains.<br>
            It will NOT work if embedded on other websites (security restriction to prevent unauthorized use).
        </div>
    </div>
    <script>
        function copyCode() {{
            const code = document.getElementById('embed-code').textContent;
            navigator.clipboard.writeText(code).then(function() {{
                document.getElementById('success-msg').style.display = 'block';
                setTimeout(function() {{
                    document.getElementById('success-msg').style.display = 'none';
                }}, 3000);
            }});
        }}
    </script>
</body>
</html>'''


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
    import time
    start_time = time.time()

    answers = session.get('answers', [])
    domain = session.get('domain', 'cosmos')

    user_profile = build_user_profile(answers)
    print(f"[Performance] Profile built in {time.time() - start_time:.3f}s")

    # Anti-repetition: Get recently shown scientists from session
    # Keep track of last 9 scientists shown (3 attempts × 3 matches)
    recently_shown = session.get('recently_shown_scientists', [])

    # Get matches with anti-repetition
    match_start = time.time()
    matches = matching_engine.get_full_matches(user_profile, domain, recently_shown=recently_shown)
    print(f"[Performance] Matching took {time.time() - match_start:.3f}s")

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

    # Save to Supabase (async to avoid blocking response)
    if SUPABASE_AVAILABLE and db:
        session_uuid = session.get('db_session_uuid')
        if session_uuid:
            db_start = time.time()
            try:
                # Complete the session
                db.complete_quiz_session(session_uuid, user_profile)
                # Save match results
                db.save_quiz_results(session_uuid, matches)
                print(f"[Performance] Supabase save took {time.time() - db_start:.3f}s")
            except Exception as e:
                print(f"[Warning] Supabase save failed: {e}")

    # Store result in session for "Back to results" functionality
    session['last_result'] = {
        "user_profile": user_profile,
        "trait_percentages": trait_percentages,
        "matches": matches
    }
    session.modified = True

    print(f"[Performance] Total request time: {time.time() - start_time:.3f}s")

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

                # Calculate summary stats from the data we already have
                total_completed = len(sessions.data) if sessions.data else 0

                # Count likes and shares
                likes = client.table("likes").select("id", count="exact").execute()
                shares = client.table("shares").select("id", count="exact").execute()

                detailed_stats['summary'] = {
                    'total_plays': total_completed,
                    'favorites': likes.count or 0,
                    'share_count': shares.count or 0,
                    'share_rate': round((shares.count or 0) * 100 / total_completed) if total_completed > 0 else 0
                }

            except Exception as e:
                print(f"Dashboard error: {e}")
                detailed_stats['error'] = str(e)
                # Provide fallback summary
                detailed_stats['summary'] = {
                    'total_plays': 0,
                    'favorites': 0,
                    'share_count': 0
                }

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

    # Calculate total plays first (needed for player IDs)
    total_plays = random.randint(1200, 2500)

    # Recent activity
    recent_activity = []
    activity_scientists = random.sample(scientists, min(6, len(scientists)))
    times = ["Just now", "2 min ago", "5 min ago", "12 min ago", "23 min ago", "1 hour ago"]
    for i, s in enumerate(activity_scientists):
        recent_activity.append({
            "id": total_plays - i,  # Descending order from total_plays
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
        "total_plays": total_plays,
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


@app.route('/results')
def view_results():
    """Display the last quiz result - bulletproof version"""
    try:
        last_result = session.get('last_result')

        if not last_result:
            # No result in session, redirect to home
            return redirect('/')

        # Validate result has required fields
        if not isinstance(last_result, dict) or 'matches' not in last_result:
            # Invalid result format, clear and redirect
            session.pop('last_result', None)
            return redirect('/')

        # Return stored result as JSON for client-side rendering
        return render_template('index_v3.html', stored_result=json.dumps(last_result))

    except Exception as e:
        # Log error and redirect to home
        print(f"[ERROR] /results route failed: {e}")
        session.pop('last_result', None)
        return redirect('/')


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


@app.route('/api/analytics-live')
def analytics_live():
    """Live analytics data for auto-refresh"""
    if SUPABASE_AVAILABLE and db:
        try:
            # Get just the live data that changes frequently
            client = db.get_client()

            # Total plays
            stats = client.table("quiz_sessions").select("id", count="exact").not_.is_("completed_at", "null").execute()
            total_plays = stats.count or 0

            # Recent activity (last 6)
            recent = client.table("quiz_results")\
                .select("scientist_name, created_at")\
                .eq("rank", 1)\
                .order("created_at", desc=True)\
                .limit(6)\
                .execute()

            recent_activity = []
            if recent.data:
                for i, r in enumerate(recent.data):
                    from datetime import datetime
                    created = datetime.fromisoformat(r["created_at"].replace("Z", "+00:00"))
                    time_ago = db.get_time_ago(created)
                    recent_activity.append({
                        "id": total_plays - i,
                        "scientist": r["scientist_name"],
                        "time": time_ago
                    })

            return jsonify({
                "total_plays": total_plays,
                "recent_activity": recent_activity
            })

        except Exception as e:
            print(f"[Error] Analytics live refresh failed: {e}")
            return jsonify({"error": str(e)}), 500

    return jsonify({"total_plays": 0, "recent_activity": []})


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
