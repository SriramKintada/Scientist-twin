"""
Enhanced Quiz Engine with 12-15 Comprehensive Questions
Covers personality, professional interests, career values, and opinions
"""

import google.generativeai as genai
from config import GEMINI_API_KEY, DOMAINS, IMPACT_STYLES
from rich.console import Console
from rich.prompt import Prompt, IntPrompt
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()
genai.configure(api_key=GEMINI_API_KEY)

class EnhancedQuizEngine:
    """
    Comprehensive quiz covering:
    - Core personality (5 questions)
    - Working style & professional approach (4 questions)
    - Career values & choices (3 questions)
    - Scientific philosophy & impact orientation (3 questions)
    """

    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.user_profile = {
            # Expanded dimensions matching our comprehensive scientist profiles
            "personality": {},
            "working_style": {},
            "career_values": {},
            "philosophy": {},
            "demographics": {}
        }
        self.domain = None
        self.impact_style = None

    def welcome(self):
        """Enhanced welcome message"""
        welcome_text = """
# 🔬 Scientist Twin 2.0 - Deep Profile Edition

*Discover your scientific kindred spirit among 500+ Indian scientists*

This comprehensive assessment analyzes:
- **Personality traits** - How you think and respond to challenges
- **Working style** - Your preferred approach to research and collaboration
- **Career values** - What drives your professional choices
- **Scientific philosophy** - Your beliefs about knowledge and impact

**15 thoughtful questions** • **10-15 minutes** • **Detailed matching**

This is a creative exploration using AI interpretation, not a clinical assessment.

Let's begin your journey...
        """
        console.print(Panel(Markdown(welcome_text), border_style="cyan", padding=(1, 2)))

    def select_domain(self):
        """Domain selection"""
        console.print("\n[bold cyan]Step 1: Your Scientific Domain[/bold cyan]\n")

        for i, (key, domain) in enumerate(DOMAINS.items(), 1):
            console.print(f"  [yellow]{i}.[/yellow] {domain['name']}")
            console.print(f"     [dim]{domain['description']}[/dim]\n")

        choice = IntPrompt.ask("Select domain", choices=[str(i) for i in range(1, len(DOMAINS)+1)])
        self.domain = list(DOMAINS.keys())[choice - 1]
        console.print(f"\n✓ Selected: [bold]{DOMAINS[self.domain]['name']}[/bold]\n")

    def select_impact_style(self):
        """Impact style selection"""
        console.print("\n[bold cyan]Step 2: Your Impact Style[/bold cyan]\n")

        for i, (key, style) in enumerate(IMPACT_STYLES.items(), 1):
            console.print(f"  [yellow]{i}.[/yellow] {style}\n")

        choice = IntPrompt.ask("Select impact style", choices=[str(i) for i in range(1, len(IMPACT_STYLES)+1)])
        self.impact_style = list(IMPACT_STYLES.keys())[choice - 1]
        console.print(f"\n✓ Selected: [bold]{IMPACT_STYLES[self.impact_style]}[/bold]\n")

    def get_comprehensive_questions(self):
        """15 questions across all dimensions"""

        questions = [
            # === PERSONALITY TRAITS (5 questions) ===
            {
                "category": "personality",
                "question": "You're working on a problem that's stumped you for weeks. How do you typically respond?",
                "options": [
                    {
                        "text": "Keep pushing through systematically until I break through",
                        "scores": {"persistence": 0.9, "resilience": 0.8, "approach": "methodical"}
                    },
                    {
                        "text": "Step back, get creative, and try a completely different angle",
                        "scores": {"creativity": 0.9, "intuition": 0.7, "approach": "innovative"}
                    },
                    {
                        "text": "Reach out to colleagues and brainstorm collaboratively",
                        "scores": {"collaboration": 0.9, "openness": 0.8, "approach": "social"}
                    },
                    {
                        "text": "Accept it might not work and pivot to a more promising direction",
                        "scores": {"adaptability": 0.9, "pragmatism": 0.8, "approach": "flexible"}
                    }
                ]
            },
            {
                "category": "personality",
                "question": "A controversial new theory challenges your field's foundational assumptions. Your reaction:",
                "options": [
                    {
                        "text": "Immediately dive deep to understand it, regardless of who proposed it",
                        "scores": {"intellectual_openness": 0.9, "curiosity": 0.9, "stance": "open"}
                    },
                    {
                        "text": "Carefully verify the evidence before considering implications",
                        "scores": {"skepticism": 0.8, "rigor": 0.9, "stance": "cautious"}
                    },
                    {
                        "text": "Defend the established framework until overwhelming evidence emerges",
                        "scores": {"conservatism": 0.8, "loyalty": 0.7, "stance": "traditional"}
                    },
                    {
                        "text": "See it as an opportunity to bridge old and new perspectives",
                        "scores": {"synthesis": 0.9, "diplomacy": 0.8, "stance": "integrative"}
                    }
                ]
            },
            {
                "category": "personality",
                "question": "When facing a major setback or failure in your work:",
                "options": [
                    {
                        "text": "I analyze what went wrong and methodically fix it",
                        "scores": {"analytical": 0.9, "persistence": 0.8, "response": "systematic"}
                    },
                    {
                        "text": "I feel it deeply but use it as fuel to prove myself",
                        "scores": {"resilience": 0.9, "determination": 0.9, "response": "driven"}
                    },
                    {
                        "text": "I reframe it as a learning opportunity and move forward",
                        "scores": {"growth_mindset": 0.9, "optimism": 0.8, "response": "adaptive"}
                    },
                    {
                        "text": "I talk it through with mentors and peers for perspective",
                        "scores": {"social_support": 0.9, "humility": 0.8, "response": "collaborative"}
                    }
                ]
            },
            {
                "category": "personality",
                "question": "You have a groundbreaking idea that others think is too risky. You:",
                "options": [
                    {
                        "text": "Pursue it anyway - the best discoveries require courage",
                        "scores": {"risk_taking": 0.9, "conviction": 0.9, "risk_stance": "bold"}
                    },
                    {
                        "text": "Test it on a small scale first to gather evidence",
                        "scores": {"calculated_risk": 0.8, "pragmatism": 0.8, "risk_stance": "measured"}
                    },
                    {
                        "text": "Work on it quietly in parallel with safer projects",
                        "scores": {"strategic": 0.8, "patience": 0.7, "risk_stance": "hedged"}
                    },
                    {
                        "text": "Build consensus and support before committing fully",
                        "scores": {"political_savvy": 0.8, "collaboration": 0.7, "risk_stance": "cautious"}
                    }
                ]
            },
            {
                "category": "personality",
                "question": "Your ideal work rhythm and environment:",
                "options": [
                    {
                        "text": "Long, focused sessions of deep solo work",
                        "scores": {"independence": 0.9, "depth": 0.9, "style": "solitary"}
                    },
                    {
                        "text": "Dynamic collaboration with frequent discussions",
                        "scores": {"collaboration": 0.9, "social_energy": 0.8, "style": "collaborative"}
                    },
                    {
                        "text": "Alternating between solo thinking and team interaction",
                        "scores": {"balance": 0.9, "flexibility": 0.8, "style": "hybrid"}
                    },
                    {
                        "text": "Short bursts of intense work with breaks for other interests",
                        "scores": {"breadth": 0.8, "integration": 0.8, "style": "varied"}
                    }
                ]
            },

            # === WORKING STYLE & PROFESSIONAL APPROACH (4 questions) ===
            {
                "category": "working_style",
                "question": "When approaching a new research problem, you typically:",
                "options": [
                    {
                        "text": "Start with theory and mathematical frameworks",
                        "scores": {"theoretical_orientation": 0.9, "abstract": 0.8, "method": "theoretical"}
                    },
                    {
                        "text": "Go straight to experiments and observations",
                        "scores": {"empirical_orientation": 0.9, "hands_on": 0.9, "method": "experimental"}
                    },
                    {
                        "text": "Survey what's been done and identify gaps",
                        "scores": {"scholarly": 0.8, "systematic": 0.8, "method": "comprehensive"}
                    },
                    {
                        "text": "Build prototypes or models to test ideas",
                        "scores": {"applied": 0.9, "pragmatic": 0.8, "method": "applied"}
                    }
                ]
            },
            {
                "category": "working_style",
                "question": "Your relationship with resources and constraints:",
                "options": [
                    {
                        "text": "I thrive with constraints - they force creative solutions",
                        "scores": {"resourcefulness": 0.9, "innovation": 0.9, "resource_attitude": "constraint_positive"}
                    },
                    {
                        "text": "I actively seek resources needed for ambitious goals",
                        "scores": {"ambition": 0.9, "networking": 0.8, "resource_attitude": "resource_seeking"}
                    },
                    {
                        "text": "I work within what's available and optimize efficiency",
                        "scores": {"pragmatism": 0.9, "efficiency": 0.8, "resource_attitude": "adaptive"}
                    },
                    {
                        "text": "I believe proper resources are essential for good science",
                        "scores": {"quality_focus": 0.9, "standards": 0.8, "resource_attitude": "resource_dependent"}
                    }
                ]
            },
            {
                "category": "working_style",
                "question": "How do you prefer to build knowledge in your field?",
                "options": [
                    {
                        "text": "Deep specialization in one area becoming a world expert",
                        "scores": {"specialization": 0.9, "depth": 0.9, "knowledge_style": "specialist"}
                    },
                    {
                        "text": "Broad exploration across related disciplines",
                        "scores": {"breadth": 0.9, "interdisciplinary": 0.9, "knowledge_style": "generalist"}
                    },
                    {
                        "text": "T-shaped: deep in one area, broad connections to others",
                        "scores": {"hybrid": 0.9, "strategic": 0.8, "knowledge_style": "t_shaped"}
                    },
                    {
                        "text": "Following interesting problems wherever they lead",
                        "scores": {"curiosity_driven": 0.9, "flexibility": 0.8, "knowledge_style": "opportunistic"}
                    }
                ]
            },
            {
                "category": "working_style",
                "question": "In collaborations, you naturally tend to:",
                "options": [
                    {
                        "text": "Lead and organize - I see the big picture and coordinate",
                        "scores": {"leadership": 0.9, "vision": 0.8, "collab_role": "leader"}
                    },
                    {
                        "text": "Execute brilliantly - I dive deep and deliver results",
                        "scores": {"execution": 0.9, "reliability": 0.8, "collab_role": "executor"}
                    },
                    {
                        "text": "Connect ideas - I find links others miss",
                        "scores": {"synthesis": 0.9, "creativity": 0.8, "collab_role": "connector"}
                    },
                    {
                        "text": "Actually prefer working solo and sharing results",
                        "scores": {"independence": 0.9, "autonomy": 0.9, "collab_role": "solo"}
                    }
                ]
            },

            # === CAREER VALUES & CHOICES (3 questions) ===
            {
                "category": "career_values",
                "question": "If you had to choose between these career outcomes:",
                "options": [
                    {
                        "text": "Major recognition and awards from the scientific community",
                        "scores": {"recognition_motivated": 0.9, "status": 0.7, "value": "achievement"}
                    },
                    {
                        "text": "Tangible impact improving millions of lives",
                        "scores": {"impact_motivated": 0.9, "altruism": 0.9, "value": "social_good"}
                    },
                    {
                        "text": "Discovering fundamental truths about the universe",
                        "scores": {"knowledge_motivated": 0.9, "curiosity": 0.9, "value": "truth"}
                    },
                    {
                        "text": "Building institutions or movements that outlast me",
                        "scores": {"legacy_motivated": 0.9, "institution_building": 0.9, "value": "legacy"}
                    }
                ]
            },
            {
                "category": "career_values",
                "question": "Regarding work-life balance and boundaries:",
                "options": [
                    {
                        "text": "Science is my life - I don't separate them",
                        "scores": {"work_dedication": 0.9, "single_focus": 0.9, "balance": "integrated"}
                    },
                    {
                        "text": "I maintain strict boundaries for family and personal time",
                        "scores": {"balance": 0.9, "family_priority": 0.8, "balance": "separated"}
                    },
                    {
                        "text": "It varies by project phase - intense then sustainable",
                        "scores": {"flexibility": 0.9, "strategic": 0.8, "balance": "cyclical"}
                    },
                    {
                        "text": "I integrate science with broad interests and activism",
                        "scores": {"breadth": 0.9, "engagement": 0.9, "balance": "multidimensional"}
                    }
                ]
            },
            {
                "category": "career_values",
                "question": "When making major career decisions, you prioritize:",
                "options": [
                    {
                        "text": "Intellectual freedom and interesting problems",
                        "scores": {"autonomy": 0.9, "intellectual_priority": 0.9, "career_driver": "intellectual"}
                    },
                    {
                        "text": "Resources and institutional support for ambitious work",
                        "scores": {"ambition": 0.9, "pragmatism": 0.8, "career_driver": "resources"}
                    },
                    {
                        "text": "Geographic location and staying close to roots",
                        "scores": {"rootedness": 0.9, "cultural_loyalty": 0.8, "career_driver": "geographic"}
                    },
                    {
                        "text": "Alignment with values and societal contribution",
                        "scores": {"values_driven": 0.9, "social_consciousness": 0.9, "career_driver": "values"}
                    }
                ]
            },

            # === SCIENTIFIC PHILOSOPHY & IMPACT (3 questions) ===
            {
                "category": "philosophy",
                "question": "Your view on the purpose of scientific research:",
                "options": [
                    {
                        "text": "Pure pursuit of knowledge for its own sake",
                        "scores": {"pure_science": 0.9, "intrinsic_motivation": 0.9, "purpose": "knowledge"}
                    },
                    {
                        "text": "Solving practical problems and improving lives",
                        "scores": {"applied_science": 0.9, "pragmatism": 0.9, "purpose": "application"}
                    },
                    {
                        "text": "National development and self-reliance",
                        "scores": {"patriotism": 0.9, "nation_building": 0.9, "purpose": "national"}
                    },
                    {
                        "text": "All knowledge eventually serves humanity - no false dichotomy",
                        "scores": {"holistic": 0.9, "long_term": 0.8, "purpose": "integrated"}
                    }
                ]
            },
            {
                "category": "philosophy",
                "question": "How should scientific knowledge be shared?",
                "options": [
                    {
                        "text": "Completely open - science belongs to humanity",
                        "scores": {"open_science": 0.9, "idealism": 0.9, "sharing": "fully_open"}
                    },
                    {
                        "text": "Strategic sharing - protect national/institutional interests",
                        "scores": {"strategic": 0.9, "pragmatism": 0.8, "sharing": "strategic"}
                    },
                    {
                        "text": "Through peer review and traditional academic channels",
                        "scores": {"conventional": 0.8, "quality_control": 0.9, "sharing": "traditional"}
                    },
                    {
                        "text": "Directly to public through multiple accessible formats",
                        "scores": {"public_engagement": 0.9, "accessibility": 0.9, "sharing": "public"}
                    }
                ]
            },
            {
                "category": "philosophy",
                "question": "The most important quality in a scientist is:",
                "options": [
                    {
                        "text": "Intellectual brilliance and insight",
                        "scores": {"intelligence_value": 0.9, "elitism": 0.6, "scientist_ideal": "genius"}
                    },
                    {
                        "text": "Persistence and resilience through challenges",
                        "scores": {"grit_value": 0.9, "determination": 0.9, "scientist_ideal": "persistent"}
                    },
                    {
                        "text": "Ethical integrity and honesty",
                        "scores": {"ethics_value": 0.9, "principles": 0.9, "scientist_ideal": "ethical"}
                    },
                    {
                        "text": "Creativity and ability to see differently",
                        "scores": {"creativity_value": 0.9, "innovation": 0.9, "scientist_ideal": "creative"}
                    }
                ]
            }
        ]

        return questions

    def conduct_comprehensive_quiz(self):
        """Run the full 15-question assessment"""

        questions = self.get_comprehensive_questions()

        console.print("\n[bold cyan]Step 3: Comprehensive Assessment (15 Questions)[/bold cyan]")
        console.print("[dim]Take your time - your thoughtful answers create better matches[/dim]\n")

        for i, q in enumerate(questions, 1):
            console.print(f"\n[bold yellow]Question {i}/15[/bold yellow]")
            console.print(f"[cyan]Category: {q['category'].replace('_', ' ').title()}[/cyan]")
            console.print(f"\n{q['question']}\n")

            for j, option in enumerate(q['options'], 1):
                console.print(f"  [cyan]{j}.[/cyan] {option['text']}")

            choice = IntPrompt.ask("\nYour answer", choices=['1', '2', '3', '4'])

            # Record response
            selected = q['options'][choice - 1]

            # Update profile
            category = q['category']
            if category not in self.user_profile:
                self.user_profile[category] = {}

            for dimension, score in selected['scores'].items():
                if dimension in self.user_profile[category]:
                    self.user_profile[category][dimension] += score
                else:
                    self.user_profile[category][dimension] = score

        # Normalize scores
        for category in self.user_profile:
            if isinstance(self.user_profile[category], dict):
                max_val = max(self.user_profile[category].values()) if self.user_profile[category] else 1
                for dim in self.user_profile[category]:
                    self.user_profile[category][dim] = round(
                        self.user_profile[category][dim] / max_val, 2
                    )

        console.print("\n[green]✓ Assessment complete![/green]\n")

    def get_profile(self):
        """Return complete user profile"""
        return {
            "domain": self.domain,
            "impact_style": self.impact_style,
            "profile": self.user_profile
        }
