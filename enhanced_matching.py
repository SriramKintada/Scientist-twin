"""
Enhanced Matching Engine - Deep Profile Comparison
Generates detailed explanations of matches, similarities, and differences
"""

import json
import google.generativeai as genai
from config import GEMINI_API_KEY
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()
genai.configure(api_key=GEMINI_API_KEY)

class EnhancedMatcher:
    """
    Deep matching using comprehensive profiles
    Generates 500-1000 word explanations of why they match
    """

    def __init__(self, database_file='scientist_db_comprehensive.json'):
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.database = self._load_database(database_file)

    def _load_database(self, filename):
        """Load comprehensive scientist database"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            console.print(f"[yellow]Database {filename} not found, using basic database[/yellow]")
            # Fallback to basic database
            with open('scientist_db.json', 'r', encoding='utf-8') as f:
                return json.load(f)

    def find_deep_matches(self, user_profile: dict, num_matches: int = 3):
        """
        Find matching scientists using comprehensive profile comparison
        Returns detailed match analysis
        """

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:

            task = progress.add_task("[cyan]Analyzing your profile against 500+ scientists...", total=None)

            # Filter by domain if possible
            domain = user_profile.get('domain')
            candidates = [s for s in self.database if s.get('domain') == domain]

            # If not enough, use all
            if len(candidates) < 10:
                candidates = self.database

            # Perform deep matching
            matches = []
            for scientist in candidates[:100]:  # Analyze top 100 for performance
                match_analysis = self._deep_compare(user_profile, scientist)
                if match_analysis:
                    matches.append({
                        'scientist': scientist,
                        'analysis': match_analysis
                    })

            # Sort by match quality
            matches.sort(key=lambda x: x['analysis']['overall_score'], reverse=True)

            progress.update(task, completed=True)

        return matches[:num_matches]

    def _deep_compare(self, user_profile: dict, scientist: dict):
        """
        Generate comprehensive match analysis comparing user to scientist
        Returns detailed explanation with similarities and differences
        """

        # Extract user dimensions
        personality = user_profile.get('profile', {}).get('personality', {})
        working_style = user_profile.get('profile', {}).get('working_style', {})
        career_values = user_profile.get('profile', {}).get('career_values', {})
        philosophy = user_profile.get('profile', {}).get('philosophy', {})

        # Extract scientist dimensions
        scientist_profile = scientist.get('comprehensive_profile', {})
        scientist_name = scientist.get('name', 'Unknown')

        prompt = f"""You are an expert at deep psychological and professional profiling.

Compare this USER PROFILE with this SCIENTIST'S life and generate a comprehensive match analysis.

USER PROFILE:
Domain: {user_profile.get('domain')}
Impact Style: {user_profile.get('impact_style')}

Personality Dimensions: {json.dumps(personality, indent=2)}
Working Style: {json.dumps(working_style, indent=2)}
Career Values: {json.dumps(career_values, indent=2)}
Philosophy: {json.dumps(philosophy, indent=2)}

SCIENTIST: {scientist_name}
Comprehensive Profile: {json.dumps(scientist_profile, indent=2)[:4000]}
Summary: {scientist.get('personality_summary', '')}
Archetype: {scientist.get('archetype', '')}
Key Moments: {json.dumps(scientist.get('key_life_moments', []), indent=2)}

TASK:
Generate a DETAILED match analysis (500-800 words) covering:

1. OVERALL MATCH QUALITY (score 0-100):
   - Calculate how well this scientist matches the user across all dimensions
   - Consider personality, working style, values, and philosophy

2. DEEP SIMILARITIES (300-400 words):
   - Identify 3-5 profound similarities
   - For EACH similarity:
     * Name the dimension (e.g., "Response to Adversity", "Resource Constraints")
     * Explain HOW the scientist's life demonstrates this trait
     * Provide SPECIFIC examples from their biography
     * Connect to HOW the user answered similar questions
   - Write narratively, making it compelling and personal

3. MEANINGFUL DIFFERENCES (200-300 words):
   - Identify 2-3 significant differences
   - For EACH difference:
     * Name the dimension
     * Explain the scientist's approach
     * Contrast with the user's profile
     * Frame as "productive tension" - what the user can learn

4. THE MATCH STORY (100-150 words):
   - A narrative synthesis
   - "You and {scientist_name} share a..."
   - Paint a vivid picture of the connection
   - Make it emotionally resonant

Return ONLY valid JSON:
{{
  "overall_score": 85,
  "match_quality_label": "Deep Resonance",
  "match_explanation": "One paragraph explaining the score",

  "deep_similarities": [
    {{
      "dimension": "Response to Adversity",
      "user_trait": "Resilient and persistent",
      "scientist_manifestation": "How scientist showed this in their life",
      "specific_examples": ["Example 1 from their biography", "Example 2"],
      "connection_narrative": "200-300 word story connecting user to scientist on this dimension"
    }},
    {{...}},
    {{...}}
  ],

  "meaningful_differences": [
    {{
      "dimension": "Collaboration Style",
      "scientist_approach": "Worked primarily solo",
      "user_approach": "Prefers collaborative environments",
      "productive_tension": "How this difference offers learning",
      "explanation": "100-150 words"
    }},
    {{...}}
  ],

  "match_story": "500-word narrative synthesis of the overall match",

  "working_style_parallel": "2-3 sentences on shared working style",
  "life_moment_that_resonates": "A specific biographical moment that mirrors user's traits"
}}

Be specific, evidence-based, and narratively compelling."""

        try:
            response = self.model.generate_content(prompt)
            import re
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)

            if json_match:
                analysis = json.loads(json_match.group())
                return analysis
            else:
                # Fallback simple analysis
                return {
                    "overall_score": 50,
                    "match_quality_label": "Kindred Spirits",
                    "match_explanation": "Basic compatibility detected",
                    "deep_similarities": [],
                    "meaningful_differences": [],
                    "match_story": f"You and {scientist_name} share interesting parallels.",
                    "working_style_parallel": "Similar approaches to problem-solving",
                    "life_moment_that_resonates": "Their dedication mirrors yours"
                }

        except Exception as e:
            console.print(f"[yellow]Matching error for {scientist_name}: {e}[/yellow]")
            return None
