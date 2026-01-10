"""Configuration for Scientist Twin 2.0"""
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# The 8 personality traits we track
TRAITS = [
    "Persistence",
    "Risk-Taking",
    "Intuition",
    "Logic",
    "Collaboration",
    "Social Impact",
    "Resilience",
    "Creativity"
]

# Scientific domains
DOMAINS = {
    "cosmos": {
        "name": "The Cosmos",
        "description": "Astronomy, Astrophysics, Space Exploration",
        "keywords": ["astronomy", "astrophysics", "space", "cosmology", "ISRO"]
    },
    "life": {
        "name": "Life & Biology",
        "description": "Biology, Medicine, Genetics, Ecology",
        "keywords": ["biology", "medicine", "genetics", "botany", "zoology"]
    },
    "quantum": {
        "name": "Quantum Logic",
        "description": "Physics, Mathematics, Computer Science",
        "keywords": ["physics", "mathematics", "computer science", "quantum"]
    },
    "earth": {
        "name": "Earth & Environment",
        "description": "Geology, Climate, Environmental Science",
        "keywords": ["geology", "environment", "climate", "meteorology"]
    },
    "engineering": {
        "name": "Engineering Feats",
        "description": "Mechanical, Electrical, Chemical Engineering",
        "keywords": ["engineering", "technology", "innovation", "design"]
    }
}

# Impact styles
IMPACT_STYLES = {
    "theoretical": "Theoretical Discovery",
    "societal": "Societal Change",
    "engineering": "Engineering Feats",
    "education": "Education & Mentorship"
}
