"""
Enhanced Output Formatter - Detailed Match Presentations
Displays long-form explanations with similarities and differences
"""

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.columns import Columns

console = Console()

class EnhancedOutputFormatter:
    """Display detailed match results with long-form narratives"""

    @staticmethod
    def display_comprehensive_match(matches: list, user_profile: dict):
        """Display full match results with detailed explanations"""

        console.print("\n\n")
        console.print("="*100, style="bold cyan")
        console.print("\n")

        # Primary match - Full detail
        if matches:
            EnhancedOutputFormatter._display_primary_match_detailed(matches[0], user_profile)

        # Alternative matches - Medium detail
        if len(matches) > 1:
            console.print("\n\n")
            EnhancedOutputFormatter._display_alternative_matches_detailed(matches[1:])

        # User profile summary
        EnhancedOutputFormatter._display_user_profile_summary(user_profile)

    @staticmethod
    def _display_primary_match_detailed(match: dict, user_profile: dict):
        """Display primary match with full 800-1000 word analysis"""

        scientist = match['scientist']
        analysis = match['analysis']

        # === HEADER ===
        header_md = f"""# 🏆 Your Scientific Twin: **{scientist['name']}**

**Match Quality: {analysis['match_quality_label']}** • Score: {analysis['overall_score']}/100

*{scientist.get('archetype', 'Scientific Pioneer')} • {scientist.get('domain', '').title()} • Era: {scientist.get('era', 'Modern')}*

---

{analysis.get('match_explanation', '')}
"""
        console.print(Panel(
            Markdown(header_md),
            border_style="bold green",
            padding=(1, 2)
        ))

        # === THE MATCH STORY ===
        console.print("\n")
        story_md = f"""## 🎭 The Match Story

{analysis.get('match_story', 'A compelling connection across time and circumstance.')}
"""
        console.print(Panel(
            Markdown(story_md),
            border_style="cyan",
            title="[bold cyan]Why You Match[/bold cyan]",
            padding=(1, 2)
        ))

        # === DEEP SIMILARITIES ===
        console.print("\n")
        similarities_md = "## 🧬 Deep Similarities - Where Your Spirits Align\n\n"

        for i, sim in enumerate(analysis.get('deep_similarities', []), 1):
            similarities_md += f"""### {i}. {sim.get('dimension', 'Shared Trait')}

**Your Trait:** {sim.get('user_trait', '')}

**How {scientist['name']} Lived This:**

{sim.get('connection_narrative', '')}

**Specific Examples from Their Life:**
"""
            for example in sim.get('specific_examples', []):
                similarities_md += f"- {example}\n"

            similarities_md += "\n---\n\n"

        console.print(Panel(
            Markdown(similarities_md),
            border_style="green",
            title="[bold green]What You Share[/bold green]",
            padding=(1, 2),
            expand=False
        ))

        # === MEANINGFUL DIFFERENCES ===
        console.print("\n")
        differences_md = "## ⚡ Meaningful Differences - Productive Tensions\n\n"
        differences_md += "*These differences offer opportunities for learning and growth*\n\n"

        for i, diff in enumerate(analysis.get('meaningful_differences', []), 1):
            differences_md += f"""### {i}. {diff.get('dimension', 'Contrasting Approach')}

**{scientist['name']}'s Approach:** {diff.get('scientist_approach', '')}

**Your Approach:** {diff.get('user_approach', '')}

**The Productive Tension:**

{diff.get('explanation', '')}

*What you can learn:* {diff.get('productive_tension', '')}

---

"""

        console.print(Panel(
            Markdown(differences_md),
            border_style="yellow",
            title="[bold yellow]Where You Differ[/bold yellow]",
            padding=(1, 2),
            expand=False
        ))

        # === WORKING STYLE & KEY MOMENT ===
        console.print("\n")
        insights_md = f"""## 📚 Final Insights

### Working Style Parallel
{analysis.get('working_style_parallel', 'Similar approaches to research and problem-solving.')}

### A Life Moment That Resonates
{analysis.get('life_moment_that_resonates', 'A defining moment in their journey.')}

"""

        if scientist.get('wikipedia_url'):
            insights_md += f"\n### Learn More\n[Read full biography on Wikipedia]({scientist['wikipedia_url']})\n"

        console.print(Panel(
            Markdown(insights_md),
            border_style="blue",
            title="[bold blue]Deeper Understanding[/bold blue]",
            padding=(1, 2)
        ))

    @staticmethod
    def _display_alternative_matches_detailed(matches: list):
        """Display alternative matches with medium detail"""

        console.print(Panel(
            "[bold cyan]🌐 Alternative Matches - Other Kindred Spirits[/bold cyan]",
            border_style="cyan"
        ))
        console.print()

        for i, match in enumerate(matches, 2):
            scientist = match['scientist']
            analysis = match['analysis']

            alt_md = f"""## {i}. {scientist['name']} • {analysis.get('match_quality_label', 'Strong Match')}

**Score: {analysis.get('overall_score', 0)}/100** • *{scientist.get('archetype', '')} • {scientist.get('domain', '').title()}*

### Why This Match Works

{analysis.get('match_explanation', '')}

### Key Similarity

"""
            # Add first similarity if available
            if analysis.get('deep_similarities'):
                first_sim = analysis['deep_similarities'][0]
                alt_md += f"**{first_sim.get('dimension', '')}**: {first_sim.get('connection_narrative', '')[:200]}...\n\n"

            # Add first difference
            if analysis.get('meaningful_differences'):
                first_diff = analysis['meaningful_differences'][0]
                alt_md += f"### An Interesting Difference\n\n**{first_diff.get('dimension', '')}**: {first_diff.get('explanation', '')[:200]}...\n\n"

            if scientist.get('wikipedia_url'):
                alt_md += f"[Learn more about {scientist['name']}]({scientist['wikipedia_url']})\n"

            console.print(Markdown(alt_md))

            if i < len(matches) + 1:
                console.print("\n" + "─" * 100 + "\n")

    @staticmethod
    def _display_user_profile_summary(user_profile: dict):
        """Display user's profile dimensions"""

        console.print("\n\n")
        console.print("="*100, style="dim")
        console.print()

        profile_md = f"""## 🔬 Your Profile Summary

**Domain:** {user_profile.get('domain', '').replace('_', ' ').title()}
**Impact Style:** {user_profile.get('impact_style', '').replace('_', ' ').title()}

### Your Top Traits Across Dimensions
"""

        # Display top traits from each category
        profile_data = user_profile.get('profile', {})

        for category, traits in profile_data.items():
            if isinstance(traits, dict) and traits:
                profile_md += f"\n**{category.replace('_', ' ').title()}:**  \n"
                # Get top 3 traits in this category
                sorted_traits = sorted(traits.items(), key=lambda x: x[1], reverse=True)[:3]
                for trait, score in sorted_traits:
                    bar = "█" * int(score * 10)
                    profile_md += f"- {trait.replace('_', ' ').title()}: {bar} ({score:.2f})  \n"

        profile_md += "\n\n"
        console.print(Markdown(profile_md))

        # Transparency note
        console.print(Panel(
            """[dim italic]This matching uses AI to interpretively compare your responses
with biographical narratives of Indian scientists. It's a creative
exploration tool, not a clinical psychological assessment.

The similarities and differences highlighted are based on our analysis
of their documented life stories and how they might resonate with
your preferences and values.[/dim italic]""",
            border_style="dim",
            padding=(1, 2)
        ))

        console.print("\n")
