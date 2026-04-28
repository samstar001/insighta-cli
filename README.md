# Insighta CLI

Command-line interface for the Insighta Labs Profile Intelligence Service.

## Installation

```bash
pip install -e .
```

## Usage

### Authentication
```bash
insighta login       # Login with GitHub OAuth
insighta logout      # Logout
insighta whoami      # Show current user
```

### Profiles
```bash
insighta profiles list                          # List all profiles
insighta profiles list --gender male            # Filter by gender
insighta profiles list --country NG             # Filter by country
insighta profiles list --age-group adult        # Filter by age group
insighta profiles list --min-age 25 --max-age 40
insighta profiles list --sort-by age --order desc
insighta profiles list --page 2 --limit 20
insighta profiles get <id>                      # Get single profile
insighta profiles search "young males from nigeria"
insighta profiles create --name "Harriet Tubman"  # Admin only
insighta profiles export --format csv
insighta profiles export --format csv --gender male --country NG
```

## Token Storage

Credentials stored at `~/.insighta/credentials.json`

Tokens auto-refresh when expired. If refresh also expires, re-login is prompted.

## Backend URL

Configured in `insighta/config.py`:
```
DEFAULT_API_URL = "https://profile-intelligence-service-rcl7.vercel.app"
```