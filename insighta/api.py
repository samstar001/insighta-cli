import httpx
import typer
from typing import Optional
from insighta.config import (
    get_api_url,
    load_credentials,
    save_credentials,
    clear_credentials,
)

# Standard headers sent with every API request
API_HEADERS = {
    "X-API-Version": "1",
    "Content-Type": "application/json",
}


def get_auth_headers() -> dict:
    """
    Returns headers with the current access token.
    Raises error if not logged in.
    """
    creds = load_credentials()
    if not creds:
        typer.echo("❌ Not logged in. Run: insighta login")
        raise typer.Exit(1)

    return {
        **API_HEADERS,
        "Authorization": f"Bearer {creds['access_token']}"
    }


def refresh_access_token() -> bool:
    """
    Tries to refresh the access token using the refresh token.
    Returns True if successful, False if refresh token is also expired.
    """
    creds = load_credentials()
    if not creds or not creds.get("refresh_token"):
        return False

    try:
        response = httpx.post(
            f"{get_api_url()}/auth/refresh",
            json={"refresh_token": creds["refresh_token"]},
            timeout=30.0
        )

        if response.status_code == 200:
            data = response.json()
            # Save the new tokens
            save_credentials(
                access_token=data["access_token"],
                refresh_token=data["refresh_token"],
                username=creds["username"],
                role=creds["role"],
            )
            return True
        return False
    except Exception:
        return False


def make_request(
    method: str,
    endpoint: str,
    params: Optional[dict] = None,
    json_data: Optional[dict] = None,
    retry: bool = True,
) -> Optional[dict]:
    """
    Makes an authenticated HTTP request to the backend.
    Automatically retries once with a refreshed token if 401 is returned.

    Args:
        method: "GET", "POST", "DELETE"
        endpoint: e.g. "/api/profiles"
        params: URL query parameters
        json_data: Request body for POST
        retry: Whether to retry after token refresh

    Returns:
        Response JSON as dict, or None on error
    """
    url = f"{get_api_url()}{endpoint}"
    headers = get_auth_headers()

    try:
        response = httpx.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=json_data,
            timeout=30.0,
            follow_redirects=True,
        )

        # Token expired — try to refresh automatically
        if response.status_code == 401 and retry:
            typer.echo("⏳ Token expired. Refreshing...")
            if refresh_access_token():
                # Retry the original request with new token
                return make_request(method, endpoint, params, json_data, retry=False)
            else:
                typer.echo("❌ Session expired. Please login again: insighta login")
                clear_credentials()
                raise typer.Exit(1)

        return response

    except httpx.ConnectError:
        typer.echo(f"❌ Cannot connect to server. Check your internet connection.")
        raise typer.Exit(1)
    except httpx.TimeoutException:
        typer.echo(f"❌ Request timed out. Try again.")
        raise typer.Exit(1)