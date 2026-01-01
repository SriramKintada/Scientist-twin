"""
Scientist Twin 3.0 - Rich Biographical Matching
Uses detailed scientist profiles for meaningful matches
"""

from flask import Flask, render_template, request, jsonify, session
import secrets
import json
import random
from datetime import datetime, timedelta
from questions_v2 import QUESTIONS, map_answer_to_trait, build_user_profile
from matching_engine_v3 import MatchingEngineV3

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
    "life": {
        "name": "Life Sciences",
        "description": "Biology, Medicine, Chemistry",
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

@app.route('/')
def index():
    return render_template('index_v3.html', domains=DOMAINS)

@app.route('/api/start-quiz', methods=['POST'])
def start_quiz():
    data = request.json
    session['domain'] = data.get('domain', 'cosmos')
    session['answers'] = []
    session['current_question'] = 0

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
    matches = matching_engine.get_full_matches(user_profile, domain)

    return jsonify({
        "user_profile": user_profile,
        "matches": matches
    })

@app.route('/api/scientists/count')
def scientist_count():
    return jsonify({
        "count": len(matching_engine.scientists)
    })

@app.route('/analytics')
def analytics():
    """Analytics dashboard with community stats"""
    # Generate realistic mock stats based on actual scientist data
    scientists = matching_engine.scientists

    # Hall of Fame - top matched scientists (sample from database)
    sample_scientists = random.sample(scientists, min(5, len(scientists)))
    hall_of_fame = []
    match_rates = [87, 72, 68, 54, 49]  # Decreasing match rates
    for i, s in enumerate(sample_scientists):
        hall_of_fame.append({
            "name": s["name"],
            "field": s["field"],
            "era": s.get("era", "Modern"),
            "match_rate": match_rates[i] if i < len(match_rates) else random.randint(30, 50)
        })

    # Recent activity (mock data with realistic timing)
    recent_activity = []
    activity_scientists = random.sample(scientists, min(6, len(scientists)))
    times = ["Just now", "2 min ago", "5 min ago", "12 min ago", "23 min ago", "1 hour ago"]
    for i, s in enumerate(activity_scientists):
        recent_activity.append({
            "id": random.randint(1000, 9999),
            "scientist": s["name"],
            "time": times[i] if i < len(times) else f"{random.randint(1, 12)} hours ago"
        })

    # Top traits in community
    top_traits = [
        {"name": "Curious", "icon": "🔍", "percent": 78},
        {"name": "Collaborative", "icon": "🤝", "percent": 65},
        {"name": "Risk-Taker", "icon": "🎯", "percent": 58},
        {"name": "Visionary", "icon": "🌟", "percent": 52},
        {"name": "Methodical", "icon": "📊", "percent": 47}
    ]

    # Popular fields from actual database
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

    return render_template('analytics.html', stats=stats)

@app.route('/api/like', methods=['POST'])
def like_result():
    """Track when users like their result"""
    data = request.json
    scientist_name = data.get('scientist', '')
    # In a real app, store this in a database
    return jsonify({"success": True, "message": f"Liked {scientist_name}!"})

if __name__ == '__main__':
    print(f"Loaded {len(matching_engine.scientists)} scientists with rich profiles")
    print("Starting Scientist Twin 3.0...")
    print("Open http://127.0.0.1:5000 in your browser")
    app.run(debug=True, host='127.0.0.1', port=5000)
