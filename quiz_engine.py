"""Quiz engine for psychological profiling"""

import google.generativeai as genai
from config import GEMINI_API_KEY, TRAITS, DOMAINS, IMPACT_STYLES
from rich.console import Console
from rich.prompt import Prompt, IntPrompt
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()

class QuizEngine:
    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.user_profile = {trait: 0.0 for trait in TRAITS}
        self.domain = None
        self.impact_style = None

    def welcome(self):
        """Display welcome message"""
        welcome_text = """
# 🔬 Welcome to Scientist Twin 2.0

*A psychological sorting hat for the India Science Fest*

We'll match you with Indian scientists by analyzing your personality,
working style, and scientific inclinations. This is a creative exploration,
not a clinical assessment.

Let's discover your scientific kindred spirit...
        """
        console.print(Panel(Markdown(welcome_text), border_style="cyan"))

    def select_domain(self):
        """Let user select their scientific domain"""
        console.print("\n[bold cyan]Step 1: Choose Your Scientific Domain[/bold cyan]\n")

        for i, (key, domain) in enumerate(DOMAINS.items(), 1):
            console.print(f"  [yellow]{i}.[/yellow] {domain['name']}")
            console.print(f"     [dim]{domain['description']}[/dim]\n")

        choice = IntPrompt.ask("Select domain", choices=[str(i) for i in range(1, len(DOMAINS)+1)])
        self.domain = list(DOMAINS.keys())[choice - 1]
        console.print(f"\n✓ Selected: [bold]{DOMAINS[self.domain]['name']}[/bold]\n")

    def select_impact_style(self):
        """Let user select their impact style"""
        console.print("\n[bold cyan]Step 2: Choose Your Impact Style[/bold cyan]\n")

        for i, (key, style) in enumerate(IMPACT_STYLES.items(), 1):
            console.print(f"  [yellow]{i}.[/yellow] {style}\n")

        choice = IntPrompt.ask("Select impact style", choices=[str(i) for i in range(1, len(IMPACT_STYLES)+1)])
        self.impact_style = list(IMPACT_STYLES.keys())[choice - 1]
        console.print(f"\n✓ Selected: [bold]{IMPACT_STYLES[self.impact_style]}[/bold]\n")

    def generate_questions(self):
        """Generate tailored questions using Gemini"""
        console.print("\n[bold cyan]Generating your personalized assessment...[/bold cyan]\n")

        domain_name = DOMAINS[self.domain]['name']
        impact_style = IMPACT_STYLES[self.impact_style]

        prompt = f"""Generate 6 psychological scenario questions for someone interested in {domain_name} who wants to create {impact_style}.

Each question should present a realistic scenario with 4 distinct options that map to these traits:
{', '.join(TRAITS)}

Format as JSON:
[
  {{
    "question": "scenario question here",
    "options": [
      {{"text": "option 1", "traits": {{"Persistence": 0.8, "Logic": 0.6}}}},
      {{"text": "option 2", "traits": {{"Creativity": 0.9, "Risk-Taking": 0.7}}}},
      {{"text": "option 3", "traits": {{"Collaboration": 0.8, "Social Impact": 0.7}}}},
      {{"text": "option 4", "traits": {{"Resilience": 0.9, "Intuition": 0.6}}}}
    ]
  }}
]

Make scenarios specific to {domain_name} context. Each option should emphasize 2-3 different traits with values 0.0-1.0."""

        try:
            response = self.model.generate_content(prompt)
            # Parse JSON from response
            import json
            import re

            # Extract JSON from response
            text = response.text
            json_match = re.search(r'\[.*\]', text, re.DOTALL)
            if json_match:
                questions_data = json.loads(json_match.group())
                return questions_data
            else:
                # Fallback to hardcoded questions if generation fails
                return self._get_fallback_questions()
        except Exception as e:
            console.print(f"[yellow]Note: Using fallback questions[/yellow]")
            return self._get_fallback_questions()

    def _get_fallback_questions(self):
        """Fallback questions if generation fails"""
        return [
            {
                "question": "You're leading a research project with limited funding. How do you proceed?",
                "options": [
                    {"text": "Work with what you have and innovate with limited resources",
                     "traits": {"Persistence": 0.9, "Creativity": 0.8, "Resilience": 0.7}},
                    {"text": "Collaborate with other institutions to pool resources",
                     "traits": {"Collaboration": 0.9, "Social Impact": 0.6}},
                    {"text": "Take a calculated risk and pursue unconventional funding",
                     "traits": {"Risk-Taking": 0.8, "Intuition": 0.7}},
                    {"text": "Systematically analyze the most efficient allocation of funds",
                     "traits": {"Logic": 0.9, "Persistence": 0.6}}
                ]
            },
            {
                "question": "A groundbreaking discovery contradicts your previous work. What's your reaction?",
                "options": [
                    {"text": "Immediately pivot and explore this new direction",
                     "traits": {"Risk-Taking": 0.8, "Creativity": 0.7}},
                    {"text": "Carefully verify the findings before changing course",
                     "traits": {"Logic": 0.9, "Persistence": 0.6}},
                    {"text": "Use this to collaborate and bridge different perspectives",
                     "traits": {"Collaboration": 0.8, "Social Impact": 0.7}},
                    {"text": "Trust your instinct that there's more to discover",
                     "traits": {"Intuition": 0.9, "Resilience": 0.6}}
                ]
            },
            {
                "question": "You have a chance to work on a high-risk, high-reward problem. Do you?",
                "options": [
                    {"text": "Absolutely, breakthrough science requires bold moves",
                     "traits": {"Risk-Taking": 0.9, "Creativity": 0.8}},
                    {"text": "Only if I can build a collaborative safety net",
                     "traits": {"Collaboration": 0.8, "Logic": 0.6}},
                    {"text": "Yes, but with systematic planning and fallbacks",
                     "traits": {"Logic": 0.8, "Persistence": 0.7}},
                    {"text": "If it aligns with societal benefit, I'll take the risk",
                     "traits": {"Social Impact": 0.9, "Resilience": 0.7}}
                ]
            },
            {
                "question": "Your research hits a major obstacle that could delay results by years. You:",
                "options": [
                    {"text": "Persist through it - great discoveries take time",
                     "traits": {"Persistence": 0.9, "Resilience": 0.8}},
                    {"text": "Creatively reframe the problem from a new angle",
                     "traits": {"Creativity": 0.9, "Intuition": 0.7}},
                    {"text": "Bring in collaborators with different expertise",
                     "traits": {"Collaboration": 0.9, "Logic": 0.6}},
                    {"text": "Use the obstacle to pivot toward broader impact",
                     "traits": {"Social Impact": 0.8, "Resilience": 0.7}}
                ]
            },
            {
                "question": "How do you approach sharing your findings with the world?",
                "options": [
                    {"text": "Academic rigor first - precise, peer-reviewed publications",
                     "traits": {"Logic": 0.9, "Persistence": 0.7}},
                    {"text": "Public engagement - make science accessible to everyone",
                     "traits": {"Social Impact": 0.9, "Collaboration": 0.7}},
                    {"text": "Creative formats - books, talks, multimedia",
                     "traits": {"Creativity": 0.9, "Risk-Taking": 0.6}},
                    {"text": "Build networks and collaborative research communities",
                     "traits": {"Collaboration": 0.9, "Social Impact": 0.7}}
                ]
            },
            {
                "question": "What drives your scientific curiosity most?",
                "options": [
                    {"text": "Solving fundamental mysteries of the universe",
                     "traits": {"Logic": 0.8, "Creativity": 0.8, "Persistence": 0.7}},
                    {"text": "Creating tangible improvements in people's lives",
                     "traits": {"Social Impact": 0.9, "Collaboration": 0.7}},
                    {"text": "Pushing boundaries others think impossible",
                     "traits": {"Risk-Taking": 0.9, "Resilience": 0.8}},
                    {"text": "Following intuition to unexplored territories",
                     "traits": {"Intuition": 0.9, "Creativity": 0.8}}
                ]
            }
        ]

    def conduct_quiz(self):
        """Run the quiz and calculate trait scores"""
        questions = self.generate_questions()

        console.print("\n[bold cyan]Step 3: Personality Assessment[/bold cyan]")
        console.print("[dim]Answer honestly - there are no wrong answers[/dim]\n")

        for i, q in enumerate(questions, 1):
            console.print(f"\n[bold yellow]Question {i}/{len(questions)}[/bold yellow]")
            console.print(f"{q['question']}\n")

            for j, option in enumerate(q['options'], 1):
                console.print(f"  [cyan]{j}.[/cyan] {option['text']}")

            choice = IntPrompt.ask("\nYour answer", choices=[str(j) for j in range(1, 5)])

            # Update trait scores
            selected_option = q['options'][choice - 1]
            for trait, score in selected_option['traits'].items():
                self.user_profile[trait] += score

        # Normalize scores
        max_possible = len(questions) * 1.0
        for trait in self.user_profile:
            self.user_profile[trait] = round(self.user_profile[trait] / max_possible, 2)

        console.print("\n[green]✓ Assessment complete![/green]\n")

    def get_profile(self):
        """Return the complete user profile"""
        return {
            "domain": self.domain,
            "impact_style": self.impact_style,
            "traits": self.user_profile,
            "top_traits": sorted(self.user_profile.items(), key=lambda x: x[1], reverse=True)[:3]
        }
