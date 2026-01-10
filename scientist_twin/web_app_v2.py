"""
Scientist Twin 2.0 - Web Application v2
Uses 12 questions and 500 scientists for comprehensive matching
"""

from flask import Flask, render_template, request, jsonify, session
import secrets
import json
from questions_v2 import QUESTIONS, map_answer_to_trait, build_user_profile
from matching_engine_v2 import MatchingEngineV2

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Initialize matching engine with 500 scientists
matching_engine = MatchingEngineV2('scientist_db_500.json')

# Domain definitions
DOMAINS = {
    "cosmos": {
        "name": "The Cosmos",
        "description": "Astronomy, Astrophysics, Space, Physics"
    },
    "quantum": {
        "name": "Quantum Logic",
        "description": "Physics, Mathematics, Computer Science"
    },
    "life": {
        "name": "Life & Biology",
        "description": "Biology, Medicine, Neuroscience, Biochemistry"
    },
    "earth": {
        "name": "Earth & Environment",
        "description": "Ecology, Agriculture, Environmental Science"
    },
    "engineering": {
        "name": "Engineering Feats",
        "description": "Engineering, Technology, Innovation"
    }
}

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index_v2.html', domains=DOMAINS)

@app.route('/api/start-quiz', methods=['POST'])
def start_quiz():
    """Start a new quiz session"""
    data = request.json

    session['domain'] = data.get('domain', 'cosmos')
    session['answers'] = []
    session['current_question'] = 0

    # Get first question
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
    """Record answer and return next question"""
    data = request.json
    answer = data.get('answer', 0)

    # Store answer
    if 'answers' not in session:
        session['answers'] = []
    session['answers'].append(answer)
    session.modified = True

    current = len(session['answers'])

    if current >= len(QUESTIONS):
        return jsonify({"complete": True})

    # Return next question
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
    """Calculate and return matches"""
    answers = session.get('answers', [])
    domain = session.get('domain', 'cosmos')

    # Build user profile from answers
    user_profile = build_user_profile(answers)

    # Get matches
    matches = matching_engine.get_full_matches(user_profile, domain)

    return jsonify({
        "user_profile": user_profile,
        "matches": matches
    })

@app.route('/api/scientists/count')
def scientist_count():
    """Return count of scientists"""
    return jsonify({
        "count": len(matching_engine.scientists)
    })

if __name__ == '__main__':
    print(f"Loaded {len(matching_engine.scientists)} scientists")
    print("Starting Scientist Twin 2.0 v2...")
    print("Open http://127.0.0.1:5000 in your browser")
    app.run(debug=True, host='127.0.0.1', port=5000)
