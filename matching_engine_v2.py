"""
Matching Engine v2 for 500 Scientists
Uses 12-dimensional trait vectors for precise matching
"""

import json
import google.generativeai as genai
from config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)

class MatchingEngineV2:
    """
    Match users to scientists based on 12-dimensional trait profiles
    """

    def __init__(self, database_path='scientist_db_500.json'):
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.load_database(database_path)

    def load_database(self, path):
        """Load the scientist database"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                self.scientists = json.load(f)
            print(f"Loaded {len(self.scientists)} scientists")
        except FileNotFoundError:
            print(f"Database not found at {path}, using default")
            self.scientists = []

    def calculate_match_score(self, user_profile: dict, scientist: dict) -> tuple:
        """
        Calculate match score between user and scientist
        Returns (score, matching_traits, differing_traits)
        """
        matching_traits = []
        differing_traits = []

        scientist_traits = scientist.get('traits', {})

        for dimension, user_value in user_profile.items():
            scientist_value = scientist_traits.get(dimension)

            if scientist_value == user_value:
                matching_traits.append({
                    "dimension": dimension,
                    "value": user_value,
                    "match_type": "exact"
                })
            elif self._are_related(dimension, user_value, scientist_value):
                matching_traits.append({
                    "dimension": dimension,
                    "user_value": user_value,
                    "scientist_value": scientist_value,
                    "match_type": "related"
                })
            else:
                differing_traits.append({
                    "dimension": dimension,
                    "user_value": user_value,
                    "scientist_value": scientist_value
                })

        # Calculate score
        exact_matches = sum(1 for t in matching_traits if t.get('match_type') == 'exact')
        related_matches = sum(1 for t in matching_traits if t.get('match_type') == 'related')

        score = (exact_matches * 1.0 + related_matches * 0.5) / len(user_profile) if user_profile else 0

        return score, matching_traits, differing_traits

    def _are_related(self, dimension: str, val1: str, val2: str) -> bool:
        """Check if two trait values are somewhat related"""
        if val1 is None or val2 is None:
            return False

        related_pairs = {
            "approach": [("theoretical", "observational"), ("experimental", "applied")],
            "collaboration": [("solo", "small_team"), ("large_team", "mentor")],
            "risk": [("calculated", "hedged"), ("bold", "calculated")],
            "motivation": [("curiosity", "recognition"), ("impact", "duty")],
            "adversity": [("persist", "fight"), ("pivot", "accept")],
            "breadth": [("generalist", "interdisciplinary"), ("specialist", "expanding")],
            "authority": [("independent", "reformer"), ("institutional", "reformer")],
            "communication": [("written", "reserved"), ("charismatic", "demonstrative")],
            "time_horizon": [("medium", "long_term"), ("long_term", "eternal")],
            "resources": [("frugal", "adequate"), ("adequate", "abundant")],
            "legacy": [("knowledge", "people"), ("institutions", "movement")],
            "failure": [("analytical", "pragmatic"), ("persistent", "serendipitous")]
        }

        pairs = related_pairs.get(dimension, [])
        return (val1, val2) in pairs or (val2, val1) in pairs

    def find_matches(self, user_profile: dict, domain_filter: str = None, top_n: int = 3) -> list:
        """
        Find top N matching scientists for a user profile
        """
        candidates = self.scientists

        # Filter by domain if specified
        if domain_filter:
            domain_map = {
                "cosmos": ["Physics", "Space Science", "Astrophysics", "Astronomy"],
                "quantum": ["Physics", "Mathematics", "Computer Science"],
                "life": ["Biology", "Medicine", "Biochemistry", "Neuroscience"],
                "earth": ["Environmental Science", "Agriculture", "Ecology", "Environment"],
                "engineering": ["Engineering", "Technology", "Aerospace", "Computer Science"]
            }
            allowed_fields = domain_map.get(domain_filter, [])
            if allowed_fields:
                candidates = [s for s in candidates if s.get('field') in allowed_fields]

        # Score all candidates
        scored = []
        for scientist in candidates:
            score, matching, differing = self.calculate_match_score(user_profile, scientist)
            scored.append({
                "scientist": scientist,
                "score": score,
                "matching_traits": matching,
                "differing_traits": differing
            })

        # Sort by score
        scored.sort(key=lambda x: x['score'], reverse=True)

        return scored[:top_n]

    def generate_match_narrative(self, user_profile: dict, match: dict) -> dict:
        """
        Generate detailed narrative explanation for a match
        """
        scientist = match['scientist']

        prompt = f"""You are explaining why a user matches with scientist {scientist['name']}.

SCIENTIST PROFILE:
Name: {scientist['name']}
Field: {scientist['field']} - {scientist.get('subfield', '')}
Era: {scientist.get('era', 'Unknown')}
Achievements: {scientist.get('achievements', '')}
Archetype: {scientist.get('archetype', '')}
Summary: {scientist.get('summary', '')}
Key Moments: {scientist.get('moments', [])}

MATCHING TRAITS ({len(match['matching_traits'])} matches):
{json.dumps(match['matching_traits'], indent=2)}

DIFFERING TRAITS:
{json.dumps(match['differing_traits'], indent=2)}

USER PROFILE:
{json.dumps(user_profile, indent=2)}

Generate a response in this EXACT JSON format:
{{
    "match_quality": "Deep Resonance" or "Parallel Paths" or "Kindred Spirit" or "Complementary Match",
    "resonances": [
        {{"trait": "trait_name", "explanation": "2-3 sentence explanation of similarity"}},
        {{"trait": "trait_name", "explanation": "2-3 sentence explanation of similarity"}},
        {{"trait": "trait_name", "explanation": "2-3 sentence explanation of similarity"}}
    ],
    "contrasts": [
        {{"trait": "trait_name", "explanation": "1-2 sentence explanation of productive difference"}}
    ],
    "working_style": "3-4 sentences about how this scientist worked and how the user might work similarly",
    "character_moment": "A specific story or moment from the scientist's life that illustrates the connection"
}}

Return ONLY valid JSON, no markdown or explanation."""

        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()

            # Clean up response
            if text.startswith('```'):
                text = text.split('```')[1]
                if text.startswith('json'):
                    text = text[4:]
            text = text.strip()

            result = json.loads(text)
            return result

        except Exception as e:
            print(f"Error generating narrative: {e}")
            # Return fallback
            return {
                "match_quality": "Kindred Spirit" if match['score'] > 0.6 else "Parallel Paths",
                "resonances": [
                    {"trait": t['dimension'], "explanation": f"You share a similar approach to {t['dimension']}"}
                    for t in match['matching_traits'][:3]
                ],
                "contrasts": [
                    {"trait": t['dimension'], "explanation": f"Different approach to {t['dimension']} could be complementary"}
                    for t in match['differing_traits'][:1]
                ],
                "working_style": scientist.get('summary', f"{scientist['name']} was known for their work in {scientist['field']}"),
                "character_moment": scientist.get('moments', ['A defining moment'])[0] if scientist.get('moments') else "A key moment in their career"
            }

    def get_full_matches(self, user_profile: dict, domain: str = None) -> list:
        """
        Get full match results with narratives
        """
        matches = self.find_matches(user_profile, domain)

        results = []
        for match in matches:
            narrative = self.generate_match_narrative(user_profile, match)

            results.append({
                "name": match['scientist']['name'],
                "field": match['scientist']['field'],
                "subfield": match['scientist'].get('subfield', ''),
                "archetype": match['scientist'].get('archetype', ''),
                "score": match['score'],
                "match_quality": narrative.get('match_quality', 'Kindred Spirit'),
                "resonances": narrative.get('resonances', []),
                "contrasts": narrative.get('contrasts', []),
                "working_style": narrative.get('working_style', ''),
                "character_moment": narrative.get('character_moment', ''),
                "achievements": match['scientist'].get('achievements', ''),
                "era": match['scientist'].get('era', '')
            })

        return results


# Test
if __name__ == "__main__":
    engine = MatchingEngineV2()

    # Sample user profile
    test_profile = {
        "approach": "theoretical",
        "collaboration": "solo",
        "risk": "bold",
        "motivation": "curiosity",
        "adversity": "persist",
        "breadth": "specialist",
        "authority": "independent",
        "communication": "reserved",
        "time_horizon": "eternal",
        "resources": "frugal",
        "legacy": "knowledge",
        "failure": "persistent"
    }

    print("Finding matches for theoretical, solo researcher...")
    matches = engine.get_full_matches(test_profile, domain="cosmos")

    for m in matches:
        print(f"\n{m['name']} ({m['match_quality']})")
        print(f"  Field: {m['field']}")
        print(f"  Score: {m['score']:.2f}")
        print(f"  Archetype: {m['archetype']}")
