#!/usr/bin/env python3
"""
Scientist Twin 2.0
A psychological sorting hat for the India Science Fest

Matches users to Indian scientists through interpretive AI-powered analysis.
"""

import sys
from quiz_engine import QuizEngine
from matching_engine import MatchingEngine
from output_formatter import OutputFormatter
from rich.console import Console

console = Console()

def main():
    """Main application flow"""
    try:
        # Initialize engines
        quiz = QuizEngine()
        matcher = MatchingEngine()

        # Phase 1: Welcome
        quiz.welcome()

        # Phase 2: Domain & Impact Selection
        quiz.select_domain()
        quiz.select_impact_style()

        # Phase 3: Psychological Profiling
        quiz.conduct_quiz()

        # Get user profile
        user_profile = quiz.get_profile()

        # Phase 4: Matching
        console.print("\n[bold cyan]🔍 Finding your scientific twin...[/bold cyan]\n")
        matches = matcher.find_matches(user_profile, num_matches=3)

        # Phase 5: Enrich with Wikipedia
        matches = matcher.enrich_with_wikipedia(matches)

        # Phase 6: Display Results
        OutputFormatter.display_matches(matches, user_profile)

        console.print("\n[green]✨ Journey complete! Thank you for exploring science with us.[/green]\n")

    except KeyboardInterrupt:
        console.print("\n\n[yellow]Session interrupted. Come back anytime![/yellow]\n")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]An error occurred: {e}[/red]\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
