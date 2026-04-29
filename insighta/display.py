from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from typing import List, Dict

console = Console()


def print_profiles_table(profiles: list) -> None:
    """Prints a formatted table of profiles."""
    if not profiles:
        console.print("[yellow]No profiles found.[/yellow]")
        return

    table = Table(
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan",
        border_style="dim",
    )

    # Define columns
    table.add_column("Name", style="white", min_width=20)
    table.add_column("Gender", style="cyan", min_width=8)
    table.add_column("Age", style="green", min_width=5)
    table.add_column("Age Group", style="yellow", min_width=12)
    table.add_column("Country", style="blue", min_width=8)
    table.add_column("Country Name", style="dim white", min_width=15)

    for p in profiles:
        table.add_row(
            p.get("name", ""),
            p.get("gender", ""),
            str(p.get("age", "")),
            p.get("age_group", ""),
            p.get("country_id", ""),
            p.get("country_name", ""),
        )

    console.print(table)


def print_profile_detail(profile: dict) -> None:
    """Prints detailed view of a single profile."""
    content = (
        f"[bold]ID:[/bold] {profile.get('id', '')}\n"
        f"[bold]Name:[/bold] {profile.get('name', '')}\n"
        f"[bold]Gender:[/bold] {profile.get('gender', '')} "
        f"([dim]{profile.get('gender_probability', '')} confidence[/dim])\n"
        f"[bold]Age:[/bold] {profile.get('age', '')} "
        f"([dim]{profile.get('age_group', '')}[/dim])\n"
        f"[bold]Country:[/bold] {profile.get('country_name', '')} "
        f"([dim]{profile.get('country_id', '')}[/dim])\n"
        f"[bold]Country Probability:[/bold] {profile.get('country_probability', '')}\n"
        f"[bold]Created At:[/bold] {profile.get('created_at', '')}"
    )
    console.print(Panel(content, title="[bold cyan]Profile Detail[/bold cyan]", expand=False))


def print_pagination_info(page: int, limit: int, total: int, total_pages: int) -> None:
    """Prints pagination summary below the table."""
    console.print(
        f"\n[dim]Page {page} of {total_pages} "
        f"• {total} total records "
        f"• {limit} per page[/dim]"
    )


def print_user_info(user: dict) -> None:
    """Prints current user info (whoami command)."""
    content = (
        f"[bold]Username:[/bold] @{user.get('username', '')}\n"
        f"[bold]Email:[/bold] {user.get('email', 'Not provided')}\n"
        f"[bold]Role:[/bold] {user.get('role', '')}\n"
        f"[bold]Active:[/bold] {user.get('is_active', '')}\n"
        f"[bold]Last Login:[/bold] {user.get('last_login_at', 'Never')}\n"
        f"[bold]Member Since:[/bold] {user.get('created_at', '')}"
    )
    console.print(Panel(content, title="[bold cyan]Current User[/bold cyan]", expand=False))


def print_success(message: str) -> None:
    console.print(f"[bold green]✅ {message}[/bold green]")


def print_error(message: str) -> None:
    console.print(f"[bold red]❌ {message}[/bold red]")


def print_info(message: str) -> None:
    console.print(f"[dim]{message}[/dim]")