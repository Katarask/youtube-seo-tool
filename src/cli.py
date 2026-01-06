"""Command-line interface for YouTube SEO Tool."""

import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich import print as rprint
from pathlib import Path

from .core.analyzer import KeywordAnalyzer
from .core.autocomplete import scrape_autocomplete
from .exporters.csv_export import export_to_csv, generate_csv_filename
from .exporters.json_export import export_to_json, generate_json_filename
from .exporters.notion import NotionExporter
from .utils.config import config

console = Console()


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """🎯 YouTube SEO Research Tool - Find content opportunities."""
    pass


@cli.command()
@click.argument("keywords", nargs=-1, required=True)
@click.option("--expand", "-e", is_flag=True, help="Expand with prefix/suffix")
@click.option("--notion", "-n", is_flag=True, help="Export to Notion")
@click.option("--csv", "-c", type=click.Path(), help="Export to CSV file")
@click.option("--json", "-j", type=click.Path(), help="Export to JSON file")
@click.option("--no-cache", is_flag=True, help="Disable caching")
def analyze(keywords, expand, notion, csv, json, no_cache):
    """Analyze keywords for content opportunities."""
    
    # Check API key
    if not config.youtube_api_key:
        console.print("[red]Error: YOUTUBE_API_KEY not set in .env[/red]")
        console.print("Get one at: https://console.cloud.google.com")
        return
    
    analyzer = KeywordAnalyzer()
    results = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Analyzing keywords...", total=len(keywords))
        
        for keyword in keywords:
            progress.update(task, description=f"Analyzing: {keyword}")
            
            analysis = analyzer.analyze_keyword(
                keyword,
                include_suggestions=True,
                expand_suggestions=expand,
                use_cache=not no_cache
            )
            results.append(analysis)
            progress.advance(task)
    
    # Sort by gap score
    results.sort(key=lambda x: x.gap_score, reverse=True)
    
    # Display results
    _display_results(results)
    
    # Export if requested
    if csv:
        path = export_to_csv(results, csv)
        console.print(f"\n[green]✓ Exported to CSV: {path}[/green]")
    
    if json:
        path = export_to_json(results, json)
        console.print(f"[green]✓ Exported to JSON: {path}[/green]")
    
    if notion:
        _export_to_notion(results)
    
    # Show quota usage
    console.print(f"\n[dim]YouTube API quota used: ~{analyzer.quota_used} units[/dim]")


@cli.command()
@click.argument("keyword")
@click.option("--expand", "-e", is_flag=True, help="Expand with prefix/suffix")
@click.option("--depth", "-d", default=1, help="Recursion depth for related searches")
def autocomplete(keyword, expand, depth):
    """Get autocomplete suggestions (no API quota)."""
    
    with console.status(f"Fetching suggestions for '{keyword}'..."):
        if expand:
            suggestions = scrape_autocomplete(keyword, expand=True)
        else:
            suggestions = scrape_autocomplete(keyword, expand=False)
    
    table = Table(title=f"Autocomplete: {keyword}")
    table.add_column("#", style="dim")
    table.add_column("Keyword", style="cyan")
    table.add_column("Position", style="green")
    
    for i, s in enumerate(suggestions[:50], 1):
        table.add_row(str(i), s.keyword, str(s.position))
    
    console.print(table)
    console.print(f"\n[dim]Total: {len(suggestions)} suggestions[/dim]")


@cli.command()
@click.argument("seed_keyword")
@click.option("--min-score", "-m", default=5.0, help="Minimum gap score")
@click.option("--max-results", "-r", default=20, help="Maximum results")
@click.option("--notion", "-n", is_flag=True, help="Export to Notion")
@click.option("--csv", "-c", type=click.Path(), help="Export to CSV")
def opportunities(seed_keyword, min_score, max_results, notion, csv):
    """Find keyword opportunities from a seed keyword."""
    
    if not config.youtube_api_key:
        console.print("[red]Error: YOUTUBE_API_KEY not set[/red]")
        return
    
    analyzer = KeywordAnalyzer()
    
    with console.status(f"Finding opportunities for '{seed_keyword}'..."):
        results = analyzer.find_opportunities(
            seed_keyword,
            min_gap_score=min_score,
            max_results=max_results
        )
    
    if not results:
        console.print(f"[yellow]No opportunities found with gap score >= {min_score}[/yellow]")
        return
    
    _display_results(results)
    
    if csv:
        path = export_to_csv(results, csv)
        console.print(f"\n[green]✓ Exported to CSV: {path}[/green]")
    
    if notion:
        _export_to_notion(results)


@cli.command()
def cache_stats():
    """Show cache statistics."""
    from .data.cache import cache
    
    stats = cache.get_stats()
    
    console.print(Panel.fit(
        f"Total entries: {stats['total_entries']}\n"
        f"Expired: {stats['expired_entries']}\n"
        f"By type: {stats['by_type']}",
        title="Cache Statistics"
    ))


@cli.command()
@click.confirmation_option(prompt="Clear all cached data?")
def cache_clear():
    """Clear all cached data."""
    from .data.cache import cache

    cache.clear_all()
    console.print("[green]✓ Cache cleared[/green]")


@cli.command()
def interactive():
    """Interactive mode with menu-driven analysis."""
    console.print(Panel.fit(
        "[bold red]YOUTUBE[/bold red] SEO Tool\n"
        "[dim]Interaktiver Modus[/dim]",
        border_style="red"
    ))

    while True:
        console.print("\n[bold]Was moechtest du tun?[/bold]\n")
        console.print("  [cyan]1[/cyan] - Keywords analysieren")
        console.print("  [cyan]2[/cyan] - Autocomplete Vorschlaege")
        console.print("  [cyan]3[/cyan] - Opportunities finden")
        console.print("  [cyan]4[/cyan] - Cache Status")
        console.print("  [cyan]q[/cyan] - Beenden\n")

        choice = Prompt.ask("Auswahl", choices=["1", "2", "3", "4", "q"], default="1")

        if choice == "q":
            console.print("[dim]Auf Wiedersehen![/dim]")
            break

        elif choice == "1":
            _interactive_analyze()

        elif choice == "2":
            _interactive_autocomplete()

        elif choice == "3":
            _interactive_opportunities()

        elif choice == "4":
            cache_stats.callback()


def _interactive_analyze():
    """Interactive keyword analysis."""
    if not config.youtube_api_key:
        console.print("[red]Error: YOUTUBE_API_KEY nicht gesetzt[/red]")
        return

    console.print("\n[bold]Keywords eingeben[/bold] (kommagetrennt oder Enter fuer einzeln):")
    keywords_input = Prompt.ask("Keywords")

    if not keywords_input.strip():
        return

    # Parse keywords
    if "," in keywords_input:
        keywords = [k.strip() for k in keywords_input.split(",") if k.strip()]
    else:
        keywords = [keywords_input.strip()]

    # Options
    expand = Confirm.ask("Keywords erweitern?", default=False)
    export_notion = Confirm.ask("Nach Notion exportieren?", default=False) if config.notion_api_key else False

    analyzer = KeywordAnalyzer()
    results = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Analysiere...", total=len(keywords))

        for keyword in keywords:
            progress.update(task, description=f"[cyan]{keyword}[/cyan]")

            analysis = analyzer.analyze_keyword(
                keyword,
                include_suggestions=True,
                expand_suggestions=expand,
            )
            results.append(analysis)
            progress.advance(task)

    results.sort(key=lambda x: x.gap_score, reverse=True)
    _display_results(results)

    # Export options
    if export_notion and results:
        _export_to_notion(results)

    if Confirm.ask("\nAls CSV speichern?", default=False):
        filename = generate_csv_filename(keywords[0] if keywords else "analysis")
        path = export_to_csv(results, filename)
        console.print(f"[green]✓ Gespeichert: {path}[/green]")

    # Copy to clipboard option
    if results and Confirm.ask("Bestes Keyword kopieren?", default=False):
        try:
            import subprocess
            best = results[0].keyword
            subprocess.run(['xclip', '-selection', 'clipboard'], input=best.encode(), check=True)
            console.print(f"[green]✓ Kopiert: {best}[/green]")
        except Exception:
            console.print(f"[yellow]Kopieren nicht moeglich. Bestes Keyword: {results[0].keyword}[/yellow]")

    console.print(f"\n[dim]API Quota: ~{analyzer.quota_used} Einheiten[/dim]")


def _interactive_autocomplete():
    """Interactive autocomplete."""
    keyword = Prompt.ask("\n[bold]Seed Keyword[/bold]")
    if not keyword.strip():
        return

    expand = Confirm.ask("Erweitern (Prefix/Suffix)?", default=False)

    with console.status(f"Lade Vorschlaege fuer '{keyword}'..."):
        suggestions = scrape_autocomplete(keyword, expand=expand)

    if not suggestions:
        console.print("[yellow]Keine Vorschlaege gefunden[/yellow]")
        return

    table = Table(title=f"Vorschlaege fuer: {keyword}")
    table.add_column("#", style="dim", width=4)
    table.add_column("Keyword", style="cyan")
    table.add_column("Position", style="green", justify="right")

    for i, s in enumerate(suggestions[:30], 1):
        table.add_row(str(i), s.keyword, str(s.position))

    console.print(table)
    console.print(f"\n[dim]Gesamt: {len(suggestions)} Vorschlaege[/dim]")

    # Option to analyze selected ones
    if Confirm.ask("\nVorschlaege analysieren?", default=False):
        indices = Prompt.ask("Nummern (kommagetrennt, z.B. 1,3,5)", default="1")
        try:
            selected = [int(i.strip()) - 1 for i in indices.split(",")]
            selected_keywords = [suggestions[i].keyword for i in selected if 0 <= i < len(suggestions)]
            if selected_keywords and config.youtube_api_key:
                analyzer = KeywordAnalyzer()
                results = [analyzer.analyze_keyword(kw) for kw in selected_keywords]
                results.sort(key=lambda x: x.gap_score, reverse=True)
                _display_results(results)
        except (ValueError, IndexError):
            console.print("[red]Ungueltige Eingabe[/red]")


def _interactive_opportunities():
    """Interactive opportunity finder."""
    if not config.youtube_api_key:
        console.print("[red]Error: YOUTUBE_API_KEY nicht gesetzt[/red]")
        return

    seed = Prompt.ask("\n[bold]Seed Keyword[/bold]")
    if not seed.strip():
        return

    min_score = float(Prompt.ask("Minimum Gap Score", default="5.0"))
    max_results = int(Prompt.ask("Max Ergebnisse", default="20"))

    analyzer = KeywordAnalyzer()

    with console.status(f"Suche Opportunities fuer '{seed}'..."):
        results = analyzer.find_opportunities(
            seed,
            min_gap_score=min_score,
            max_results=max_results
        )

    if not results:
        console.print(f"[yellow]Keine Opportunities mit Score >= {min_score}[/yellow]")
        return

    _display_results(results)

    if Confirm.ask("\nNach Notion exportieren?", default=False) and config.notion_api_key:
        _export_to_notion(results)


def _display_results(results):
    """Display analysis results in a table."""
    table = Table(title="Keyword Analysis Results")
    table.add_column("Keyword", style="cyan", max_width=40)
    table.add_column("Gap", justify="right")
    table.add_column("Rating")
    table.add_column("Demand", justify="right")
    table.add_column("Supply", justify="right")
    table.add_column("Trend")
    table.add_column("Videos/30d", justify="right")
    
    for r in results:
        gap_color = "green" if r.gap_score >= 7 else "yellow" if r.gap_score >= 4 else "red"
        
        table.add_row(
            r.keyword[:40],
            f"[{gap_color}]{r.gap_score:.1f}[/{gap_color}]",
            r.gap_emoji,
            f"{r.demand.demand_score:.1f}" if r.demand else "-",
            f"{r.supply.supply_score:.1f}" if r.supply else "-",
            r.trend_data.trend_emoji if r.trend_data else "-",
            str(r.supply.videos_last_30_days) if r.supply else "-",
        )
    
    console.print(table)
    
    # Show top insights
    if results and results[0].insights:
        console.print(f"\n[bold]💡 Top Opportunity: {results[0].keyword}[/bold]")
        for insight in results[0].insights[:3]:
            console.print(f"  • {insight}")


def _export_to_notion(results):
    """Export results to Notion."""
    if not config.notion_api_key:
        console.print("[red]Error: NOTION_API_KEY not set[/red]")
        return
    
    if not config.notion_database_id:
        console.print("[yellow]NOTION_DATABASE_ID not set. Create database first.[/yellow]")
        return
    
    try:
        exporter = NotionExporter()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Exporting to Notion...", total=len(results))
            
            def callback(current, total, keyword):
                progress.update(task, description=f"Exporting: {keyword}")
                progress.advance(task)
            
            page_ids = exporter.export_multiple(results, progress_callback=callback)
        
        console.print(f"[green]✓ Exported {len(page_ids)} keywords to Notion[/green]")
        
    except Exception as e:
        console.print(f"[red]Error exporting to Notion: {e}[/red]")


if __name__ == "__main__":
    cli()
