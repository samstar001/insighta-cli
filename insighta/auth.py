import webbrowser
import httpx
import typer
from rich.console import Console
from insighta.config import get_api_url, save_credentials, clear_credentials

console = Console()


def login() -> bool:
    """
    Simple GitHub OAuth login flow:
    1. Opens browser to backend login URL
    2. User logs in on GitHub
    3. Browser shows JSON with tokens
    4. User pastes tokens into terminal
    """
    api_url = get_api_url()

    # Direct URL — no PKCE for simplicity
    login_url = f"{api_url}/auth/github?source=cli"

    console.print("\n[bold cyan]🔐 Insighta Labs Login[/bold cyan]")
    console.print("\nOpening your browser to GitHub login...")
    console.print(f"\n[dim]If browser doesn't open automatically, paste this URL in your browser:[/dim]")
    console.print(f"[bold yellow]{login_url}[/bold yellow]\n")

    # Open browser
    webbrowser.open(login_url)

    console.print("[dim]After logging in with GitHub, you will see a JSON response in your browser.[/dim]")
    console.print("[dim]Copy the access_token and refresh_token values and paste them below.[/dim]\n")

    # Get tokens from user
    access_token = typer.prompt("Paste your access_token here").strip()
    if not access_token:
        console.print("[red]❌ Login cancelled — no token provided.[/red]")
        return False

    refresh_token = typer.prompt("Paste your refresh_token here").strip()
    if not refresh_token:
        console.print("[red]❌ Login cancelled — no refresh token provided.[/red]")
        return False

    # Verify token by calling /auth/me
    console.print("\n[dim]Verifying token...[/dim]")
    try:
        response = httpx.get(
            f"{api_url}/auth/me",
            headers={
                "Authorization": f"Bearer {access_token}",
                "X-API-Version": "1"
            },
            timeout=30.0,
            follow_redirects=True,
        )

        if response.status_code == 200:
            user_data = response.json().get("data", {})
            username = user_data.get("username", "unknown")
            role = user_data.get("role", "analyst")

            save_credentials(access_token, refresh_token, username, role)
            console.print(f"\n[bold green]✅ Logged in as @{username} ({role})[/bold green]\n")
            return True

        elif response.status_code == 401:
            console.print("[red]❌ Token is invalid or expired. Please try again.[/red]")
            return False

        else:
            console.print(f"[red]❌ Verification failed with status {response.status_code}[/red]")
            return False

    except httpx.ConnectError:
        console.print("[red]❌ Cannot connect to the server. Check your internet.[/red]")
        return False
    except httpx.TimeoutException:
        console.print("[red]❌ Request timed out. Try again.[/red]")
        return False
    except Exception as e:
        console.print(f"[red]❌ Unexpected error: {e}[/red]")
        return False