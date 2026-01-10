"""Beautiful output formatting for match results"""

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

console = Console()

class OutputFormatter:
    @staticmethod
    def display_matches(matches: list, user_profile: dict):
        """Display the final match results"""

        console.print("\n\n")
        console.print("="*80, style="bold cyan")
        console.print("\n")

        # Display primary match
        primary = matches[0]
        OutputFormatter._display_primary_match(primary, user_profile)

        # Display alternative matches
        if len(matches) > 1:
            console.print("\n\n")
            OutputFormatter._display_alternative_matches(matches[1:])

        # Display technical transparency
        OutputFormatter._display_trait_vector(user_profile)

    @staticmethod
    def _display_primary_match(match: dict, user_profile: dict):
        """Display the top match in detail"""
        scientist = match['scientist']
        match_data = match['match_data']
        wiki = match.get('wikipedia', {})

        # Header
        header = f"# 🏆 Your Scientific Twin: {scientist['name']}\n"
        header += f"**Match Strength: {match_data['match_quality']}**\n\n"
        header += f"*{scientist['archetype']} • {scientist['era']} • {scientist['sub_domain']}*"

        console.print(Panel(Markdown(header), border_style="bold green", padding=(1, 2)))

        # Resonance section
        console.print("\n")
        resonance_md = "### 🧬 The Resonance (Similarities)\n\n"
        for res in match_data['resonances']:
            resonance_md += f"**{res['trait']}:** {res['explanation']}\n\n"

        console.print(Panel(Markdown(resonance_md), border_style="green", title="[bold]What You Share[/bold]"))

        # Contrast section
        if match_data.get('contrasts'):
            console.print("\n")
            contrast_md = "### ⚡ The Contrast (Differences)\n\n"
            for con in match_data['contrasts']:
                contrast_md += f"**{con['trait']}:** {con['explanation']}\n\n"

            console.print(Panel(Markdown(contrast_md), border_style="yellow", title="[bold]Where You Differ[/bold]"))

        # Reasoning cards
        console.print("\n")
        reasoning_md = "### 📚 Deeper Insights\n\n"
        reasoning_md += f"**Working Style:** {match_data['working_style_summary']}\n\n"
        reasoning_md += f"**Character Moment:** {match_data['character_moment']}\n\n"

        console.print(Panel(Markdown(reasoning_md), border_style="blue", title="[bold]Understanding the Connection[/bold]"))

        # Wikipedia link
        if wiki:
            console.print(f"\n[dim]Learn more: {wiki.get('url', '')}[/dim]")

    @staticmethod
    def _display_alternative_matches(matches: list):
        """Display alternative matches"""
        console.print(Panel("[bold cyan]🌐 Alternative Matches[/bold cyan]", border_style="cyan"))
        console.print()

        for i, match in enumerate(matches, 2):
            scientist = match['scientist']
            match_data = match['match_data']

            alt_md = f"### {i}. {scientist['name']} - {match_data['match_quality']}\n\n"
            alt_md += f"*{scientist['archetype']} • {scientist['sub_domain']}*\n\n"

            if match_data['resonances']:
                alt_md += f"**Key Resonance:** {match_data['resonances'][0]['explanation']}\n\n"

            wiki = match.get('wikipedia', {})
            if wiki:
                alt_md += f"[Learn more]({wiki.get('url', '')})\n"

            console.print(Markdown(alt_md))
            if i < len(matches) + 1:
                console.print("---\n")

    @staticmethod
    def _display_trait_vector(user_profile: dict):
        """Display the technical trait breakdown"""
        console.print("\n\n")

        table = Table(title="🔬 Technical Transparency: Your Trait Profile", border_style="dim")
        table.add_column("Trait", style="cyan", no_wrap=True)
        table.add_column("Score", style="magenta", justify="right")
        table.add_column("Bar", style="green")

        traits = user_profile['traits']
        for trait, score in sorted(traits.items(), key=lambda x: x[1], reverse=True):
            bar = "█" * int(score * 20)
            table.add_row(trait, f"{score:.2f}", bar)

        console.print(table)

        # Domain info
        from config import DOMAINS, IMPACT_STYLES
        console.print(f"\n[dim]Domain: {DOMAINS[user_profile['domain']]['name']}[/dim]")
        console.print(f"[dim]Impact Style: {IMPACT_STYLES[user_profile['impact_style']]}[/dim]")

        console.print("\n[dim italic]This matching is an AI-powered creative interpretation,")
        console.print("not a clinical psychological assessment.[/dim italic]\n")
