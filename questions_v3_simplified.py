"""
12 Simplified Questions for Scientist Twin 3.0
Kid-friendly but NOT dumbed down - accessible to all ages while maintaining sophistication
Each question maps to specific trait dimensions that differentiate scientists
"""

QUESTIONS = [
    # Q1: Problem-Solving Approach (Theoretical vs Experimental vs Applied)
    {
        "id": 1,
        "dimension": "approach",
        "text": "When you encounter a tricky problem, what do you naturally do first?",
        "options": [
            {"text": "Think it through step by step on paper or in your head", "maps_to": "theoretical"},
            {"text": "Try things out and see what happens", "maps_to": "experimental"},
            {"text": "Think about how it connects to everyday life", "maps_to": "applied"},
            {"text": "Watch closely and notice patterns before deciding", "maps_to": "observational"}
        ],
        "rationale": "Differentiates theorists (Ramanujan, Chandrasekhar) from experimentalists (Raman, Bose) from applied scientists (Kalam, Sarabhai)"
    },

    # Q2: Working Style (Solo vs Collaborative vs Leadership)
    {
        "id": 2,
        "dimension": "collaboration",
        "text": "How do you like to work on projects or solve challenges?",
        "options": [
            {"text": "By myself - I do my best thinking alone", "maps_to": "solo"},
            {"text": "With a small group of close friends or teammates", "maps_to": "small_team"},
            {"text": "With lots of people all working together", "maps_to": "large_team"},
            {"text": "Teaching others while I learn and work", "maps_to": "mentor"}
        ],
        "rationale": "Ramanujan (solo) vs Bhabha (institution builder) vs Swaminathan (community-oriented)"
    },

    # Q3: Risk Tolerance (Conservative vs Calculated vs Bold)
    {
        "id": 3,
        "dimension": "risk",
        "text": "When you hear about a new, unusual idea that might not work, you:",
        "options": [
            {"text": "Want to see proof it works before trying it", "maps_to": "conservative"},
            {"text": "Think carefully about the good and bad before deciding", "maps_to": "calculated"},
            {"text": "Get excited and want to jump in right away", "maps_to": "bold"},
            {"text": "Try it secretly while still doing what usually works", "maps_to": "hedged"}
        ],
        "rationale": "Differentiates risk-takers (Kalam's missile program) from methodical researchers (Khorana)"
    },

    # Q4: Motivation Source (Curiosity vs Impact vs Recognition vs Duty)
    {
        "id": 4,
        "dimension": "motivation",
        "text": "What makes you most excited about doing something?",
        "options": [
            {"text": "Finding out how things work - curiosity is the best reward", "maps_to": "curiosity"},
            {"text": "Making life better for people around me", "maps_to": "impact"},
            {"text": "Being really good at it and getting recognized", "maps_to": "recognition"},
            {"text": "Helping my family, community, or country", "maps_to": "duty"}
        ],
        "rationale": "Ramanujan (pure math) vs Swaminathan (hunger) vs Raman (Nobel) vs Kalam (nation)"
    },

    # Q5: Response to Adversity (Persist vs Pivot vs Fight vs Accept)
    {
        "id": 5,
        "dimension": "adversity",
        "text": "When something goes wrong or doesn't work out, you usually:",
        "options": [
            {"text": "Keep trying harder - challenges make me stronger", "maps_to": "persist"},
            {"text": "Find a different way to reach my goal", "maps_to": "pivot"},
            {"text": "Stand up and fight to change what's unfair", "maps_to": "fight"},
            {"text": "Accept it calmly and focus on what I can control", "maps_to": "accept"}
        ],
        "rationale": "Raman built own lab (persist), Sarabhai pivoted to space (pivot), Bhabha fought bureaucracy (fight)"
    },

    # Q6: Knowledge Style (Deep Specialist vs Broad Generalist vs Interdisciplinary)
    {
        "id": 6,
        "dimension": "breadth",
        "text": "How do you try to learn something new?",
        "options": [
            {"text": "Go really deep into one thing until I master it completely", "maps_to": "specialist"},
            {"text": "Learn a little bit about many different things", "maps_to": "generalist"},
            {"text": "Connect ideas from two or three different areas", "maps_to": "interdisciplinary"},
            {"text": "Start with one thing, then slowly explore related topics", "maps_to": "expanding"}
        ],
        "rationale": "Chandrasekhar (deep astrophysics) vs JC Bose (physics+biology) vs Ramachandran (neuro+psychology)"
    },

    # Q7: Relationship with Authority (Independent vs Institutional vs Revolutionary)
    {
        "id": 7,
        "dimension": "authority",
        "text": "How do you feel about rules and the way things are usually done?",
        "options": [
            {"text": "I like doing things my own way, even if it's different", "maps_to": "independent"},
            {"text": "I work well with teams and organizations - they help us achieve more", "maps_to": "institutional"},
            {"text": "I follow rules but try to improve the ones that don't work", "maps_to": "reformer"},
            {"text": "I create completely new ways of doing things when needed", "maps_to": "revolutionary"}
        ],
        "rationale": "Raman (independent), Bhabha (institution builder), Sarabhai (reformer)"
    },

    # Q8: Communication Style (Reserved vs Charismatic vs Written vs Action)
    {
        "id": 8,
        "dimension": "communication",
        "text": "If you had a brilliant new idea and want others to get interested, what would you do?",
        "options": [
            {"text": "Just work on it and let my results show others", "maps_to": "reserved"},
            {"text": "Excitedly tell people about it and explain why it's cool", "maps_to": "charismatic"},
            {"text": "Write it down carefully so others can understand it fully", "maps_to": "written"},
            {"text": "Build or create something to show them how it works", "maps_to": "demonstrative"}
        ],
        "rationale": "Ramanujan (reserved), Kalam (charismatic), Chandrasekhar (written), Sarabhai (demonstrative)"
    },

    # Q9: Time Horizon (Immediate vs Medium vs Long-term vs Eternal)
    {
        "id": 9,
        "dimension": "time_horizon",
        "text": "When you're working on something important, how far ahead do you think?",
        "options": [
            {"text": "What needs to be done right now or this week", "maps_to": "immediate"},
            {"text": "What I can finish this year or in a couple of years", "maps_to": "medium"},
            {"text": "What might happen many years from now", "maps_to": "long_term"},
            {"text": "Big questions that matter no matter when", "maps_to": "eternal"}
        ],
        "rationale": "Kalam (mission deadlines) vs Sarabhai (decade vision) vs Ramanujan (eternal math)"
    },

    # Q10: Resource Philosophy (Frugal vs Adequate vs Abundant)
    {
        "id": 10,
        "dimension": "resources",
        "text": "When you want to do something amazing, how do you think about what you need?",
        "options": [
            {"text": "I can do great things with very little - limits make me creative", "maps_to": "frugal"},
            {"text": "I need enough to do it well, but not too much extra", "maps_to": "adequate"},
            {"text": "Big dreams need big support - I'll get what's necessary", "maps_to": "abundant"},
            {"text": "I focus on the idea first, the rest will follow", "maps_to": "ideas_first"}
        ],
        "rationale": "Raman (built spectrograph from scraps) vs Bhabha (atomic program funding)"
    },

    # Q11: Legacy Orientation (Knowledge vs People vs Institutions vs Movement)
    {
        "id": 11,
        "dimension": "legacy",
        "text": "What would make you feel most proud when you look back at your life?",
        "options": [
            {"text": "Discovering something new that people remember", "maps_to": "knowledge"},
            {"text": "Helping and inspiring the people I've worked with", "maps_to": "people"},
            {"text": "Creating groups or systems that keep going after me", "maps_to": "institutions"},
            {"text": "Starting a change in how people think about the world", "maps_to": "movement"}
        ],
        "rationale": "Ramanujan (theorems), Raman (students), Bhabha (TIFR/BARC), Swaminathan (green revolution)"
    },

    # Q12: Failure Philosophy (Learn vs Persist vs Reframe vs Avoid)
    {
        "id": 12,
        "dimension": "failure",
        "text": "When something you tried doesn't work the way you hoped, you:",
        "options": [
            {"text": "Figure out what went wrong so I can learn from it", "maps_to": "analytical"},
            {"text": "Try again with some changes until it works", "maps_to": "persistent"},
            {"text": "Look for the unexpected good things that came out of it", "maps_to": "serendipitous"},
            {"text": "Move on to something more likely to succeed", "maps_to": "pragmatic"}
        ],
        "rationale": "Different scientists have different relationships with failure"
    }
]

# Trait dimensions mapped by questions
TRAIT_DIMENSIONS = {
    "approach": ["theoretical", "experimental", "applied", "observational"],
    "collaboration": ["solo", "small_team", "large_team", "mentor"],
    "risk": ["conservative", "calculated", "bold", "hedged"],
    "motivation": ["curiosity", "impact", "recognition", "duty"],
    "adversity": ["persist", "pivot", "fight", "accept"],
    "breadth": ["specialist", "generalist", "interdisciplinary", "expanding"],
    "authority": ["independent", "institutional", "reformer", "revolutionary"],
    "communication": ["reserved", "charismatic", "written", "demonstrative"],
    "time_horizon": ["immediate", "medium", "long_term", "eternal"],
    "resources": ["frugal", "adequate", "abundant", "ideas_first"],
    "legacy": ["knowledge", "people", "institutions", "movement"],
    "failure": ["analytical", "persistent", "serendipitous", "pragmatic"]
}

def get_questions():
    """Return formatted questions for the quiz"""
    return [{
        "id": q["id"],
        "text": q["text"],
        "options": [opt["text"] for opt in q["options"]],
        "dimension": q["dimension"]
    } for q in QUESTIONS]

def map_answer_to_trait(question_id: int, answer_index: int) -> tuple:
    """Map an answer to its trait dimension and value"""
    question = QUESTIONS[question_id - 1]
    dimension = question["dimension"]
    value = question["options"][answer_index]["maps_to"]
    return (dimension, value)

def build_user_profile(answers: list) -> dict:
    """Build user profile from list of answers (0-3 for each of 12 questions)"""
    profile = {}
    for q_id, answer in enumerate(answers, 1):
        dimension, value = map_answer_to_trait(q_id, answer)
        profile[dimension] = value
    return profile
