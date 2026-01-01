#!/usr/bin/env python3
"""
Scientist Twin 2.0 - Enhanced Deep Profile Edition

Comprehensive personality matching with 500+ Indian scientists
- 15-question deep assessment
- Rich biographical vector profiles
- Detailed match explanations (500-1000 words)
"""

import sys
from enhanced_quiz import EnhancedQuizEngine
from enhanced_matching import EnhancedMatcher
from enhanced_output import EnhancedOutputFormatter
from rich.console import Console

console = Console()

def main():
    """Enhanced application flow with comprehensive profiling"""

    try:
        # Initialize engines
        console.print("[dim]Initializing Scientist Twin 2.0 - Enhanced Edition...[/dim]\n")

        quiz = EnhancedQuizEngine()
        matcher = EnhancedMatcher()

        # Phase 1: Welcome
        quiz.welcome()

        # Phase 2: Domain & Impact Selection
        quiz.select_domain()
        quiz.select_impact_style()

        # Phase 3: Comprehensive 15-Question Assessment
        quiz.conduct_comprehensive_quiz()

        # Get detailed user profile
        user_profile = quiz.get_profile()

        # Phase 4: Deep Matching Against Database
        console.print("\n[bold cyan]🔍 Analyzing your profile against 500+ Indian scientists...[/bold cyan]")
        console.print("[dim]This may take 30-60 seconds as we perform deep comparisons...[/dim]\n")

        matches = matcher.find_deep_matches(user_profile, num_matches=3)

        if not matches:
            console.print("[yellow]No strong matches found. Try adjusting your responses or domain.[/yellow]")
            return

        # Phase 5: Display Comprehensive Results
        EnhancedOutputFormatter.display_comprehensive_match(matches, user_profile)

        # Closing
        console.print("\n[green]✨ Your scientific journey of discovery is complete![/green]")
        console.print("[dim]Thank you for exploring India's scientific heritage with us.[/dim]\n")

    except KeyboardInterrupt:
        console.print("\n\n[yellow]Session interrupted. Your scientific twin awaits - come back anytime![/yellow]\n")
        sys.exit(0)

    except Exception as e:
        console.print(f"\n[red]An error occurred: {e}[/red]")
        console.print("[dim]Please try again or contact support if the issue persists.[/dim]\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    console.print("""
[bold cyan]╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           🔬 SCIENTIST TWIN 2.0 - Enhanced Edition           ║
║                                                              ║
║          Discover Your Kindred Spirit in Indian Science      ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝[/bold cyan]
""")

    main()
