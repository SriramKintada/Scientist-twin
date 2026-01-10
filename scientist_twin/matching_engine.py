"""Matching engine using Gemini AI for interpretive matching"""

import json
import google.generativeai as genai
from config import GEMINI_API_KEY, TRAITS, DOMAINS
from wikipedia_service import WikipediaService
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

class MatchingEngine:
    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.wiki_service = WikipediaService()
        self.scientist_db = self._load_scientist_database()

    def _load_scientist_database(self):
        """Load pre-curated scientist database"""
        try:
            with open('scientist_db.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            console.print("[red]Error: scientist_db.json not found[/red]")
            return []

    def filter_candidates(self, user_profile: dict) -> list:
        """Filter scientists by domain"""
        domain = user_profile['domain']
        candidates = [s for s in self.scientist_db if s['domain'] == domain]

        # If not enough in exact domain, expand search
        if len(candidates) < 5:
            candidates = self.scientist_db

        return candidates

    def calculate_match_score(self, user_profile: dict, scientist: dict) -> dict:
        """Use Gemini to interpretively match user to scientist"""

        user_traits = user_profile['traits']
        top_user_traits = user_profile['top_traits']

        prompt = f"""You are analyzing the match between a user's personality profile and a scientist's biography.

USER PROFILE:
- Domain Interest: {DOMAINS[user_profile['domain']]['name']}
- Impact Style: {user_profile['impact_style']}
- Top Personality Traits:
  {chr(10).join([f"  • {trait}: {score:.2f}" for trait, score in top_user_traits])}

SCIENTIST: {scientist['name']}
- Era: {scientist['era']}
- Field: {scientist['sub_domain']}
- Archetype: {scientist['archetype']}
- Personality Summary: {scientist['personality_summary']}
- Trait Indicators:
  {chr(10).join([f"  • {trait}: {desc}" for trait, desc in scientist['trait_summary'].items()])}
- Key Moments:
  {chr(10).join([f"  • {moment}" for moment in scientist['key_moments']])}

TASK:
1. Analyze how well this scientist matches the user's personality
2. Identify 2-3 strong resonances (similarities)
3. Identify 1-2 interesting contrasts (differences)
4. Rate the overall match quality: "Deep Resonance", "Parallel Paths", or "Kindred Spirits"

Return ONLY valid JSON in this exact format:
{{
  "match_quality": "Deep Resonance",
  "resonances": [
    {{"trait": "Persistence", "explanation": "Both show unwavering commitment..."}},
    {{"trait": "Creativity", "explanation": "Similar innovative approaches..."}}
  ],
  "contrasts": [
    {{"trait": "Collaboration", "explanation": "While user values collaboration, {scientist['name']} often worked in isolation..."}}
  ],
  "working_style_summary": "Two sentences about shared approach",
  "character_moment": "A specific anecdote from their life that mirrors user's traits"
}}"""

        try:
            response = self.model.generate_content(prompt)
            # Extract JSON from response
            import re
            text = response.text

            # Try to extract JSON
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                match_data = json.loads(json_match.group())
                return match_data
            else:
                # Fallback
                return self._create_fallback_match(user_profile, scientist)

        except Exception as e:
            console.print(f"[yellow]Note: Using simplified matching for {scientist['name']}[/yellow]")
            return self._create_fallback_match(user_profile, scientist)

    def _create_fallback_match(self, user_profile: dict, scientist: dict):
        """Simple fallback matching logic"""
        top_traits = [t[0] for t in user_profile['top_traits']]
        scientist_traits = list(scientist['trait_summary'].keys())

        common_traits = set(top_traits) & set(scientist_traits)

        return {
            "match_quality": "Parallel Paths" if len(common_traits) >= 2 else "Kindred Spirits",
            "resonances": [
                {"trait": trait, "explanation": scientist['trait_summary'][trait]}
                for trait in list(common_traits)[:2]
            ],
            "contrasts": [
                {"trait": "Background", "explanation": f"Different approaches to {scientist['sub_domain']}"}
            ],
            "working_style_summary": scientist['personality_summary'][:150],
            "character_moment": scientist['key_moments'][0] if scientist['key_moments'] else "Notable achievement"
        }

    def find_matches(self, user_profile: dict, num_matches: int = 3):
        """Find top matching scientists"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Analyzing scientists...", total=None)

            candidates = self.filter_candidates(user_profile)

            # Calculate matches for all candidates
            matches = []
            for scientist in candidates:
                match_data = self.calculate_match_score(user_profile, scientist)
                matches.append({
                    'scientist': scientist,
                    'match_data': match_data
                })

            # Sort by match quality
            quality_order = {"Deep Resonance": 3, "Parallel Paths": 2, "Kindred Spirits": 1}
            matches.sort(
                key=lambda x: (
                    quality_order.get(x['match_data']['match_quality'], 0),
                    len(x['match_data']['resonances'])
                ),
                reverse=True
            )

            progress.update(task, completed=True)

        return matches[:num_matches]

    def enrich_with_wikipedia(self, matches: list):
        """Fetch full Wikipedia articles for top matches"""
        console.print("\n[cyan]Fetching detailed biographies...[/cyan]\n")

        for match in matches:
            scientist = match['scientist']
            wiki_title = scientist.get('wikipedia_title', scientist['name'].replace(' ', '_'))

            article = self.wiki_service.get_article(wiki_title)
            if article:
                match['wikipedia'] = article
            else:
                match['wikipedia'] = {
                    'extract': scientist['personality_summary'],
                    'url': f"https://en.wikipedia.org/wiki/{wiki_title}"
                }

        return matches
