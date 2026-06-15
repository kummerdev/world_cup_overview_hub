"""
ESPN public API client for FIFA World Cup 2026.
No API key required — completely free.

Base URLs:
  Site API  → https://site.api.espn.com
  Core API  → https://sports.core.api.espn.com
"""

from datetime import date
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

SITE   = "https://site.api.espn.com"
CORE   = "https://sports.core.api.espn.com"
SPORT  = "soccer"
LEAGUE = "fifa.world"

WC_START = date(2026, 6, 11)
WC_END   = date(2026, 7, 19)

ESPN_NAME_ALIASES: dict[str, str] = {
    "United States":       "USA",
    "Korea Republic":      "South Korea",
    "IR Iran":             "Iran",
    "Côte d'Ivoire":       "Ivory Coast",
    "Cote d'Ivoire":       "Ivory Coast",
    "Czechia":             "Czech Republic",
    "Bosnia-Herzegovina":  "Bosnia & Herzegovina",
    "Türkiye":             "Turkey",
    "Curaçao":             "Curacao",
}

# Shared HTTP session with automatic retry on transient failures
_session = Session()
_retry = Retry(total=3, backoff_factor=0.4, status_forcelist={500, 502, 503, 504})
_session.mount("https://", HTTPAdapter(max_retries=_retry))
_session.headers.update({"User-Agent": "WCP-PickEm/1.0"})


def _get(url: str, **params) -> dict:
    r = _session.get(url, params=params or None, timeout=12)
    r.raise_for_status()
    return r.json()


def normalize(name: str) -> str:
    if not name:
        return name
    return ESPN_NAME_ALIASES.get(name, name)


# ── Scoreboard ────────────────────────────────────────────────────────────────

def get_scoreboard(day: str | None = None) -> dict:
    """
    Fetch the FIFA World Cup scoreboard.
    day — 'YYYYMMDD' string; omit for today's matches.
    """
    url = f"{SITE}/apis/site/v2/sports/{SPORT}/{LEAGUE}/scoreboard"
    params: dict = {"limit": 50}
    if day:
        params["dates"] = day
    return _get(url, **params)


# ── News ──────────────────────────────────────────────────────────────────────

def get_news(limit: int = 20) -> dict:
    """Latest FIFA World Cup news from ESPN."""
    url = f"{SITE}/apis/site/v2/sports/{SPORT}/{LEAGUE}/news"
    return _get(url, limit=limit)


# ── Statistical leaders ───────────────────────────────────────────────────────

def get_leaders() -> dict:
    """Top scorers and statistical leaders for WC 2026."""
    url = f"{CORE}/v2/sports/{SPORT}/leagues/{LEAGUE}/seasons/2026/types/1/leaders"
    return _get(url)


def resolve_ref(ref_url: str) -> dict:
    """Fetch any ESPN $ref URL directly."""
    return _get(ref_url)


# ── Helpers ───────────────────────────────────────────────────────────────────

def extract_competitors(event: dict) -> tuple[dict, dict]:
    """Return (home_competitor, away_competitor) from an ESPN event."""
    competitors = event.get("competitions", [{}])[0].get("competitors", [])
    home = next((c for c in competitors if c.get("homeAway") == "home"), {})
    away = next((c for c in competitors if c.get("homeAway") == "away"), {})
    return home, away


def extract_team_name(competitor: dict) -> str:
    return normalize(competitor.get("team", {}).get("name", ""))


def extract_score(competitor: dict) -> int | None:
    s = competitor.get("score")
    try:
        return int(s) if s is not None else None
    except (ValueError, TypeError):
        return None


def is_finished(event: dict) -> bool:
    status = event.get("status", {}).get("type", {})
    return bool(status.get("completed")) or status.get("state") == "post"


def is_live(event: dict) -> bool:
    return event.get("status", {}).get("type", {}).get("state") == "in"
