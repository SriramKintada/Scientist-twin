#!/usr/bin/env python3
"""
Scientist Twin 2.0 - Simple Version (No Emojis for Windows)
"""

import sys
import os

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from quiz_engine import QuizEngine
from matching_engine import MatchingEngine
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()

def main():
    """Main application flow - simplified for Windows"""

    try:
        # Simple welcome
        console.print("\n" + "="*70)
        console.print("[bold cyan]SCIENTIST TWIN 2.0[/bold cyan]")
        console.print("="*70 + "\n")
        console.print("Discover your scientific kindred spirit among Indian scientists\n")

        # Initialize
        quiz = QuizEngine()
        matcher = MatchingEngine()

        # Domain selection
        console.print("[bold cyan]Step 1: Choose Your Scientific Domain[/bold cyan]\n")
        from config import DOMAINS
        for i, (key, domain) in enumerate(DOMAINS.items(), 1):
            console.print(f"  {i}. {domain['name']}")
            console.print(f"     {domain['description']}\n")

        domain_choice = input("Select domain (1-5): ")
        quiz.domain = list(DOMAINS.keys())[int(domain_choice) - 1]
        console.print(f"\nSelected: {DOMAINS[quiz.domain]['name']}\n")

        # Impact style
        console.print("[bold cyan]Step 2: Choose Your Impact Style[/bold cyan]\n")
        from config import IMPACT_STYLES
        for i, (key, style) in enumerate(IMPACT_STYLES.items(), 1):
            console.print(f"  {i}. {style}\n")

        impact_choice = input("Select impact style (1-4): ")
        quiz.impact_style = list(IMPACT_STYLES.keys())[int(impact_choice) - 1]
        console.print(f"\nSelected: {IMPACT_STYLES[quiz.impact_style]}\n")

        # Run quiz (use fallback questions to avoid API calls for now)
        console.print("[bold cyan]Step 3: Personality Assessment (6 Questions)[/bold cyan]\n")
        questions = quiz._get_fallback_questions()

        for i, q in enumerate(questions, 1):
            console.print(f"\n[bold yellow]Question {i}/{len(questions)}[/bold yellow]")
            console.print(f"{q['question']}\n")

            for j, option in enumerate(q['options'], 1):
                console.print(f"  {j}. {option['text']}")

            choice = input("\nYour answer (1-4): ")
            selected = q['options'][int(choice) - 1]

            # Update scores
            for trait, score in selected['traits'].items():
                quiz.user_profile[trait] += score

        # Normalize scores
        max_possible = len(questions) * 1.0
        for trait in quiz.user_profile:
            quiz.user_profile[trait] = round(quiz.user_profile[trait] / max_possible, 2)

        console.print("\n[green]Assessment complete![/green]\n")

        # Get profile
        user_profile = {
            "domain": quiz.domain,
            "impact_style": quiz.impact_style,
            "traits": quiz.user_profile,
            "top_traits": sorted(quiz.user_profile.items(), key=lambda x: x[1], reverse=True)[:3]
        }

        # Find matches
        console.print("[cyan]Finding your scientific twin...[/cyan]\n")
        matches = matcher.find_matches(user_profile, num_matches=3)

        # Display results
        console.print("\n" + "="*70)
        console.print("[bold green]YOUR SCIENTIFIC TWIN[/bold green]")
        console.print("="*70 + "\n")

        primary = matches[0]
        scientist = primary['scientist']
        match_data = primary['match_data']

        console.print(f"[bold]{scientist['name']}[/bold]")
        console.print(f"Match Quality: {match_data['match_quality']}")
        console.print(f"Archetype: {scientist['archetype']}\n")

        console.print("[bold]RESONANCES (Similarities):[/bold]")
        for res in match_data['resonances']:
            console.print(f"- {res['trait']}: {res['explanation']}")

        console.print(f"\n[bold]CONTRASTS (Differences):[/bold]")
        for con in match_data.get('contrasts', []):
            console.print(f"- {con['trait']}: {con['explanation']}")

        console.print(f"\n[bold]Working Style:[/bold] {match_data['working_style_summary']}")
        console.print(f"\n[bold]Character Moment:[/bold] {match_data['character_moment']}\n")

        # Alternative matches
        if len(matches) > 1:
            console.print("\n[bold cyan]ALTERNATIVE MATCHES:[/bold cyan]\n")
            for i, match in enumerate(matches[1:], 2):
                scientist = match['scientist']
                match_data = match['analysis'] if 'analysis' in match else match['match_data']
                console.print(f"{i}. {scientist['name']} - {scientist.get('archetype', 'Pioneer')}")

        # Trait summary
        console.print("\n" + "="*70)
        console.print("[bold]YOUR TRAIT PROFILE:[/bold]")
        console.print("="*70 + "\n")
        for trait, score in sorted(user_profile['traits'].items(), key=lambda x: x[1], reverse=True):
            bar = "#" * int(score * 20)
            console.print(f"{trait:20s} {score:.2f} {bar}")

        console.print("\n[green]Journey complete! Thank you for exploring Indian science![/green]\n")

    except KeyboardInterrupt:
        console.print("\n\n[yellow]Session interrupted. Come back anytime![/yellow]\n")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
