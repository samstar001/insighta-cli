import typer
from typing import Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from insighta.auth import login
from insighta.config import (
    load_credentials,
    clear_credentials,
    is_logged_in,
)
from insighta.api import make_request
from insighta.display import (
    print_profiles_table,
    print_profile_detail,
    print_pagination_info,
    print_user_info,
    print_success,
    print_error,
    print_info,
    console,
)

# Create the main app and profiles sub-app
app = typer.Typer(
    name="insighta",
    help="Insighta Labs CLI — Profile Intelligence Service",
    no_args_is_help=True,
)
profiles_app = typer.Typer(help="Manage profiles")
app.add_typer(profiles_app, name="profiles")


# ─── AUTH COMMANDS ────────────────────────────────────────────────────────────

@app.command("login")
def login_cmd():
    """Login with GitHub OAuth."""
    login()

# Register as 'insighta login'
app.command("login")(login_cmd)


@app.command()
def logout():
    """Logout and clear stored credentials."""
    if not is_logged_in():
        print_info("You are not logged in.")
        return

    clear_credentials()
    print_success("Logged out successfully.")


@app.command()
def whoami():
    """Show current logged in user."""
    if not is_logged_in():
        print_error("Not logged in. Run: insighta login")
        raise typer.Exit(1)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task("Fetching user info...", total=None)
        response = make_request("GET", "/auth/me")

    if response and response.status_code == 200:
        user = response.json().get("data", {})
        print_user_info(user)
    else:
        print_error("Failed to fetch user info.")


# ─── PROFILES COMMANDS ────────────────────────────────────────────────────────

@profiles_app.command("list")
def profiles_list(
    gender: Optional[str] = typer.Option(None, "--gender", "-g", help="Filter by gender"),
    country: Optional[str] = typer.Option(None, "--country", "-c", help="Filter by country code (e.g. NG)"),
    age_group: Optional[str] = typer.Option(None, "--age-group", help="Filter by age group"),
    min_age: Optional[int] = typer.Option(None, "--min-age", help="Minimum age"),
    max_age: Optional[int] = typer.Option(None, "--max-age", help="Maximum age"),
    sort_by: Optional[str] = typer.Option(None, "--sort-by", help="Sort by: age, created_at, gender_probability"),
    order: Optional[str] = typer.Option("asc", "--order", help="Sort order: asc or desc"),
    page: int = typer.Option(1, "--page", "-p", help="Page number"),
    limit: int = typer.Option(10, "--limit", "-l", help="Results per page (max 50)"),
):
    """List profiles with optional filters and sorting."""
    if not is_logged_in():
        print_error("Not logged in. Run: insighta login")
        raise typer.Exit(1)

    params = {"page": page, "limit": limit, "order": order}
    if gender:
        params["gender"] = gender
    if country:
        params["country_id"] = country
    if age_group:
        params["age_group"] = age_group
    if min_age is not None:
        params["min_age"] = min_age
    if max_age is not None:
        params["max_age"] = max_age
    if sort_by:
        params["sort_by"] = sort_by

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task("Fetching profiles...", total=None)
        response = make_request("GET", "/api/profiles", params=params)

    if response and response.status_code == 200:
        data = response.json()
        profiles = data.get("data", [])
        print_profiles_table(profiles)
        print_pagination_info(
            page=data.get("page", 1),
            limit=data.get("limit", 10),
            total=data.get("total", 0),
            total_pages=data.get("total_pages", 1),
        )
    else:
        error_msg = "Failed to fetch profiles."
        if response:
            detail = response.json().get("detail", {})
            error_msg = detail.get("message", error_msg) if isinstance(detail, dict) else str(detail)
        print_error(error_msg)


@profiles_app.command("get")
def profiles_get(
    profile_id: str = typer.Argument(..., help="Profile UUID"),
):
    """Get a single profile by ID."""
    if not is_logged_in():
        print_error("Not logged in. Run: insighta login")
        raise typer.Exit(1)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task("Fetching profile...", total=None)
        response = make_request("GET", f"/api/profiles/{profile_id}")

    if response and response.status_code == 200:
        profile = response.json().get("data", {})
        print_profile_detail(profile)
    elif response and response.status_code == 404:
        print_error("Profile not found.")
    else:
        print_error("Failed to fetch profile.")


@profiles_app.command("search")
def profiles_search(
    query: str = typer.Argument(..., help='Natural language query e.g. "young males from nigeria"'),
    page: int = typer.Option(1, "--page", "-p", help="Page number"),
    limit: int = typer.Option(10, "--limit", "-l", help="Results per page"),
):
    """Search profiles using natural language."""
    if not is_logged_in():
        print_error("Not logged in. Run: insighta login")
        raise typer.Exit(1)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(f'Searching for "{query}"...', total=None)
        response = make_request(
            "GET",
            "/api/profiles/search",
            params={"q": query, "page": page, "limit": limit}
        )

    if response and response.status_code == 200:
        data = response.json()
        profiles = data.get("data", [])
        console.print(f"\n[bold]Results for:[/bold] [cyan]\"{query}\"[/cyan]")
        print_profiles_table(profiles)
        print_pagination_info(
            page=data.get("page", 1),
            limit=data.get("limit", 10),
            total=data.get("total", 0),
            total_pages=data.get("total_pages", 1),
        )
    elif response and response.status_code == 400:
        detail = response.json().get("detail", {})
        msg = detail.get("message", "Invalid query") if isinstance(detail, dict) else str(detail)
        print_error(msg)
    else:
        print_error("Search failed.")


@profiles_app.command("create")
def profiles_create(
    name: str = typer.Option(..., "--name", "-n", help="Person's name"),
):
    """Create a new profile (admin only)."""
    if not is_logged_in():
        print_error("Not logged in. Run: insighta login")
        raise typer.Exit(1)

    creds = load_credentials()
    if creds and creds.get("role") != "admin":
        print_error("Access denied. Only admins can create profiles.")
        raise typer.Exit(1)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(f"Creating profile for {name}...", total=None)
        response = make_request("POST", "/api/profiles", json_data={"name": name})

    if response and response.status_code in (200, 201):
        data = response.json()
        profile = data.get("data", {})
        msg = data.get("message", "")
        if msg:
            print_info(msg)
        print_profile_detail(profile)
    elif response and response.status_code == 403:
        print_error("Access denied. Admin role required.")
    elif response and response.status_code == 502:
        detail = response.json().get("detail", {})
        msg = detail.get("message", "External API error") if isinstance(detail, dict) else str(detail)
        print_error(f"External API error: {msg}")
    else:
        print_error("Failed to create profile.")


@profiles_app.command("export")
def profiles_export(
    format: str = typer.Option("csv", "--format", "-f", help="Export format (csv)"),
    gender: Optional[str] = typer.Option(None, "--gender", "-g"),
    country: Optional[str] = typer.Option(None, "--country", "-c"),
    age_group: Optional[str] = typer.Option(None, "--age-group"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output filename"),
):
    """Export profiles to CSV file."""
    if not is_logged_in():
        print_error("Not logged in. Run: insighta login")
        raise typer.Exit(1)

    params = {"format": format}
    if gender:
        params["gender"] = gender
    if country:
        params["country_id"] = country
    if age_group:
        params["age_group"] = age_group

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task("Exporting profiles...", total=None)
        response = make_request("GET", "/api/profiles/export", params=params)

    if response and response.status_code == 200:
        # Save to current directory
        from datetime import datetime
        filename = output or f"profiles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        with open(filename, "w", encoding="utf-8") as f:
            f.write(response.text)

        print_success(f"Exported to {filename}")
        console.print(f"[dim]Saved in current directory: {filename}[/dim]")
    else:
        print_error("Export failed.")


# ─── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app()