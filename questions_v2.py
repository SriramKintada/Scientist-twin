"""
12 Carefully Designed Questions for Scientist Twin 2.0
Each question maps to specific trait dimensions that differentiate 500 scientists
"""

QUESTIONS = [
    # Q1: Problem-Solving Approach (Theoretical vs Experimental vs Applied)
    {
        "id": 1,
        "dimension": "approach",
        "text": "When facing a complex problem, what's your natural first instinct?",
        "options": [
            {"text": "Sit with pen and paper, work through the logic and mathematics", "maps_to": "theoretical"},
            {"text": "Design an experiment or prototype to test my ideas", "maps_to": "experimental"},
            {"text": "Look for practical applications and real-world impact first", "maps_to": "applied"},
            {"text": "Gather data and observe patterns before theorizing", "maps_to": "observational"}
        ],
        "rationale": "Differentiates theorists (Ramanujan, Chandrasekhar) from experimentalists (Raman, Bose) from applied scientists (Kalam, Sarabhai)"
    },

    # Q2: Working Style (Solo vs Collaborative vs Leadership)
    {
        "id": 2,
        "dimension": "collaboration",
        "text": "In your ideal work environment, how do you prefer to operate?",
        "options": [
            {"text": "Deep solitary focus - my best work comes when I'm alone", "maps_to": "solo"},
            {"text": "Small trusted team - a few brilliant minds working together", "maps_to": "small_team"},
            {"text": "Large collaborative projects - orchestrating many contributors", "maps_to": "large_team"},
            {"text": "Mentoring others - teaching while researching", "maps_to": "mentor"}
        ],
        "rationale": "Ramanujan (solo) vs Bhabha (institution builder) vs Swaminathan (community-oriented)"
    },

    # Q3: Risk Tolerance (Conservative vs Calculated vs Bold)
    {
        "id": 3,
        "dimension": "risk",
        "text": "When presented with an unconventional idea that might fail, you typically:",
        "options": [
            {"text": "Need strong evidence before investing time - I prefer proven paths", "maps_to": "conservative"},
            {"text": "Carefully weigh risks and rewards before committing", "maps_to": "calculated"},
            {"text": "Get excited and dive in - breakthrough requires bold moves", "maps_to": "bold"},
            {"text": "Test it quietly on the side while maintaining safer work", "maps_to": "hedged"}
        ],
        "rationale": "Differentiates risk-takers (Kalam's missile program) from methodical researchers (Khorana)"
    },

    # Q4: Motivation Source (Curiosity vs Impact vs Recognition vs Duty)
    {
        "id": 4,
        "dimension": "motivation",
        "text": "What drives you most in your work?",
        "options": [
            {"text": "Pure curiosity - understanding how things work is its own reward", "maps_to": "curiosity"},
            {"text": "Making a tangible difference in people's lives", "maps_to": "impact"},
            {"text": "Proving myself and gaining recognition for excellence", "maps_to": "recognition"},
            {"text": "Serving my country or community - duty and responsibility", "maps_to": "duty"}
        ],
        "rationale": "Ramanujan (pure math) vs Swaminathan (hunger) vs Raman (Nobel) vs Kalam (nation)"
    },

    # Q5: Response to Adversity (Persist vs Pivot vs Fight vs Accept)
    {
        "id": 5,
        "dimension": "adversity",
        "text": "When facing major obstacles or rejection, your typical response is:",
        "options": [
            {"text": "Double down and persist - obstacles only strengthen my resolve", "maps_to": "persist"},
            {"text": "Adapt and find alternative routes to my goal", "maps_to": "pivot"},
            {"text": "Challenge the system directly - fight for what's right", "maps_to": "fight"},
            {"text": "Accept setbacks philosophically and focus on what I can control", "maps_to": "accept"}
        ],
        "rationale": "Raman built own lab (persist), Sarabhai pivoted to space (pivot), Bhabha fought bureaucracy (fight)"
    },

    # Q6: Knowledge Style (Deep Specialist vs Broad Generalist vs Interdisciplinary)
    {
        "id": 6,
        "dimension": "breadth",
        "text": "How do you prefer to develop your expertise?",
        "options": [
            {"text": "Go extremely deep in one area - mastery requires focus", "maps_to": "specialist"},
            {"text": "Learn broadly across many fields - connections spark innovation", "maps_to": "generalist"},
            {"text": "Bridge two or three fields - work at the intersections", "maps_to": "interdisciplinary"},
            {"text": "Start deep, then gradually expand outward over time", "maps_to": "expanding"}
        ],
        "rationale": "Chandrasekhar (deep astrophysics) vs JC Bose (physics+biology) vs Ramachandran (neuro+psychology)"
    },

    # Q7: Relationship with Authority (Independent vs Institutional vs Revolutionary)
    {
        "id": 7,
        "dimension": "authority",
        "text": "Your relationship with established institutions and authorities is typically:",
        "options": [
            {"text": "I work best outside traditional structures - independence matters", "maps_to": "independent"},
            {"text": "I build and strengthen institutions - they're essential for progress", "maps_to": "institutional"},
            {"text": "I challenge outdated norms while working within the system", "maps_to": "reformer"},
            {"text": "I create entirely new frameworks when existing ones fail", "maps_to": "revolutionary"}
        ],
        "rationale": "Raman (independent), Bhabha (institution builder), Sarabhai (reformer)"
    },

    # Q8: Communication Style (Reserved vs Charismatic vs Written vs Action)
    {
        "id": 8,
        "dimension": "communication",
        "text": "How do you prefer to share your ideas and influence others?",
        "options": [
            {"text": "Through my work itself - let results speak for themselves", "maps_to": "reserved"},
            {"text": "Engaging presentations and discussions - I enjoy explaining ideas", "maps_to": "charismatic"},
            {"text": "Detailed written documentation - precision matters", "maps_to": "written"},
            {"text": "By building things and demonstrating possibilities", "maps_to": "demonstrative"}
        ],
        "rationale": "Ramanujan (reserved), Kalam (charismatic), Chandrasekhar (written), Sarabhai (demonstrative)"
    },

    # Q9: Time Horizon (Immediate vs Medium vs Long-term vs Eternal)
    {
        "id": 9,
        "dimension": "time_horizon",
        "text": "When planning your work, you typically think in terms of:",
        "options": [
            {"text": "Immediate problems that need solving now", "maps_to": "immediate"},
            {"text": "Medium-term goals achievable in a few years", "maps_to": "medium"},
            {"text": "Long-term vision spanning decades", "maps_to": "long_term"},
            {"text": "Timeless questions that transcend any era", "maps_to": "eternal"}
        ],
        "rationale": "Kalam (mission deadlines) vs Sarabhai (decade vision) vs Ramanujan (eternal math)"
    },

    # Q10: Resource Philosophy (Frugal vs Adequate vs Abundant)
    {
        "id": 10,
        "dimension": "resources",
        "text": "Your approach to resources and funding for your work:",
        "options": [
            {"text": "I can achieve great things with minimal resources - constraints spark creativity", "maps_to": "frugal"},
            {"text": "I need adequate resources but avoid excess - efficiency matters", "maps_to": "adequate"},
            {"text": "Big problems need big resources - I'll secure what's necessary", "maps_to": "abundant"},
            {"text": "I focus on ideas first, resources follow good work", "maps_to": "ideas_first"}
        ],
        "rationale": "Raman (built spectrograph from scraps) vs Bhabha (atomic program funding)"
    },

    # Q11: Legacy Orientation (Knowledge vs People vs Institutions vs Movement)
    {
        "id": 11,
        "dimension": "legacy",
        "text": "What kind of legacy matters most to you?",
        "options": [
            {"text": "Discoveries and knowledge that outlast me", "maps_to": "knowledge"},
            {"text": "The students and people I've influenced and trained", "maps_to": "people"},
            {"text": "Institutions and systems that continue my work", "maps_to": "institutions"},
            {"text": "A movement or change in how society thinks", "maps_to": "movement"}
        ],
        "rationale": "Ramanujan (theorems), Raman (students), Bhabha (TIFR/BARC), Swaminathan (green revolution)"
    },

    # Q12: Failure Philosophy (Learn vs Persist vs Reframe vs Avoid)
    {
        "id": 12,
        "dimension": "failure",
        "text": "When a project fails or hypothesis is disproven, you typically:",
        "options": [
            {"text": "Analyze what went wrong - failures are data points", "maps_to": "analytical"},
            {"text": "Try again with modifications - persistence wins", "maps_to": "persistent"},
            {"text": "Look for unexpected discoveries in the 'failure'", "maps_to": "serendipitous"},
            {"text": "Move on quickly to more promising directions", "maps_to": "pragmatic"}
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
