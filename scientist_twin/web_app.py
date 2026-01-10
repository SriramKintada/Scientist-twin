"""
Simple Web Interface for Scientist Twin 2.0
Flask-based web app for testing with Playwright
"""

from flask import Flask, render_template, request, jsonify, session
import secrets
from quiz_engine import QuizEngine
from matching_engine import MatchingEngine
from config import DOMAINS, IMPACT_STYLES

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

@app.route('/')
def index():
    """Landing page"""
    return render_template('index.html', domains=DOMAINS, impact_styles=IMPACT_STYLES)

@app.route('/api/start-quiz', methods=['POST'])
def start_quiz():
    """Initialize quiz with domain and impact style"""
    data = request.json
    session['domain'] = data.get('domain')
    session['impact_style'] = data.get('impact_style')
    session['current_question'] = 0
    session['answers'] = []

    # Get questions
    quiz = QuizEngine()
    quiz.domain = session['domain']
    quiz.impact_style = session['impact_style']

    questions = quiz._get_fallback_questions()
    session['total_questions'] = len(questions)

    return jsonify({
        'success': True,
        'total_questions': len(questions),
        'question': {
            'number': 1,
            'text': questions[0]['question'],
            'options': [opt['text'] for opt in questions[0]['options']]
        }
    })

@app.route('/api/answer-question', methods=['POST'])
def answer_question():
    """Record answer and get next question"""
    data = request.json
    answer_index = data.get('answer')

    # Record answer
    if 'answers' not in session:
        session['answers'] = []
    session['answers'].append(answer_index)

    quiz = QuizEngine()
    quiz.domain = session['domain']
    quiz.impact_style = session['impact_style']
    questions = quiz._get_fallback_questions()

    session['current_question'] += 1

    if session['current_question'] < len(questions):
        # More questions
        q_num = session['current_question']
        return jsonify({
            'success': True,
            'complete': False,
            'question': {
                'number': q_num + 1,
                'text': questions[q_num]['question'],
                'options': [opt['text'] for opt in questions[q_num]['options']]
            }
        })
    else:
        # Quiz complete
        return jsonify({
            'success': True,
            'complete': True
        })

@app.route('/api/get-matches', methods=['POST'])
def get_matches():
    """Calculate and return matches"""
    quiz = QuizEngine()
    quiz.domain = session['domain']
    quiz.impact_style = session['impact_style']
    questions = quiz._get_fallback_questions()

    # Calculate scores
    for i, answer_idx in enumerate(session['answers']):
        selected = questions[i]['options'][answer_idx]
        for trait, score in selected['traits'].items():
            quiz.user_profile[trait] += score

    # Normalize
    max_possible = len(questions) * 1.0
    for trait in quiz.user_profile:
        quiz.user_profile[trait] = round(quiz.user_profile[trait] / max_possible, 2)

    user_profile = {
        "domain": quiz.domain,
        "impact_style": quiz.impact_style,
        "traits": quiz.user_profile,
        "top_traits": sorted(quiz.user_profile.items(), key=lambda x: x[1], reverse=True)[:3]
    }

    # Find matches
    matcher = MatchingEngine()
    matches = matcher.find_matches(user_profile, num_matches=3)

    # Format results
    results = []
    for match in matches:
        scientist = match['scientist']
        match_data = match['match_data']

        results.append({
            'name': scientist['name'],
            'archetype': scientist['archetype'],
            'match_quality': match_data['match_quality'],
            'resonances': match_data['resonances'],
            'contrasts': match_data.get('contrasts', []),
            'working_style': match_data['working_style_summary'],
            'character_moment': match_data['character_moment']
        })

    return jsonify({
        'success': True,
        'matches': results,
        'user_profile': user_profile
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
