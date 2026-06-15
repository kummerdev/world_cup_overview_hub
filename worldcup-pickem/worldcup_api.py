"""
ESPN public API client for FIFA World Cup 2026.
No API key required — completely free.

Base URLs:
  Site API  → https://site.api.espn.com
  Core API  → https://sports.core.api.espn.com
"""

import requests
from datetime import date, timedelta

SITE  = "https://site.api.espn.com"
CORE  = "https://sports.core.api.espn.com"
SPORT = "soccer"
LEAGUE = "fifa.world"

# World Cup 2026 date range
WC_START = date(2026, 6, 11)
WC_END   = date(2026, 7, 19)

# ESPN may use different names for some nations
ESPN_NAME_ALIASES = {
    "United States":       "USA",
    "Korea Republic":      "South Korea",
    "IR Iran":             "Iran",
    "Côte d'Ivoire":       "Ivory Coast",
    "Cote d'Ivoire":       "Ivory Coast",
    "Czechia":             "Czech Republic",
    "Bosnia-Herzegovina":  "Bosnia & Herzegovina",
    "Türkiye":             "Turkey",
    "Curaçao":             "Curacao",
    "Curacao":             "Curacao",
}


def _get(url: str, **params) -> dict:
    r = requests.get(url, params=params, timeout=15,
                     headers={"User-Agent": "WCP-PickEm/1.0"})
    r.raise_for_status()
    return r.json()


def normalize(name: str) -> str:
    return ESPN_NAME_ALIASES.get(name, name)


# ── Scoreboard ────────────────────────────────────────────────────────────────

def get_scoreboard(day: str = None) -> dict:
    """
    Fetch the FIFA World Cup scoreboard.
    day — 'YYYYMMDD' string; omit for today's matches.
    Returns the raw ESPN response dict.
    """
    url = f"{SITE}/apis/site/v2/sports/{SPORT}/{LEAGUE}/scoreboard"
    params = {"limit": 50}
    if day:
        params["dates"] = day
    return _get(url, **params)


def get_all_wc_events() -> list:
    """
    Iterate every day of WC 2026 and collect all ESPN events.
    Returns a flat list of raw ESPN event dicts.
    """
    events = []
    seen   = set()
    current = WC_START
    while current <= WC_END:
        try:
            data = get_scoreboard(current.strftime("%Y%m%d"))
            for ev in data.get("events", []):
                if ev["id"] not in seen:
                    seen.add(ev["id"])
                    events.append(ev)
        except Exception:
            pass
        current += timedelta(days=1)
    return events


# ── Standings ─────────────────────────────────────────────────────────────────

def get_standings() -> dict:
    """Group-stage standings (full table)."""
    url = f"{SITE}/apis/v2/sports/{SPORT}/{LEAGUE}/standings"
    return _get(url)


# ── Match summary ─────────────────────────────────────────────────────────────

def get_match_summary(event_id: str) -> dict:
    """Full match report: goals, cards, lineups, box score."""
    url = f"{SITE}/apis/site/v2/sports/{SPORT}/{LEAGUE}/summary"
    return _get(url, event=event_id)


# ── News ──────────────────────────────────────────────────────────────────────

def get_news(limit: int = 15) -> dict:
    """Latest FIFA World Cup news from ESPN."""
    url = f"{SITE}/apis/site/v2/sports/{SPORT}/{LEAGUE}/news"
    return _get(url, limit=limit)


# ── Statistical leaders ───────────────────────────────────────────────────────

def get_leaders() -> dict:
    """Top scorers and statistical leaders for WC 2026."""
    url = f"{CORE}/v2/sports/{SPORT}/leagues/{LEAGUE}/seasons/2026/types/1/leaders"
    return _get(url)


def resolve_ref(ref_url: str) -> dict:
    """Fetch any ESPN $ref URL directly (used for leaders athlete resolution)."""
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


def extract_score(competitor: dict):
    """Return score as int or None."""
    s = competitor.get("score")
    try:
        return int(s) if s is not None else None
    except (ValueError, TypeError):
        return None


def is_finished(event: dict) -> bool:
    status = event.get("status", {}).get("type", {})
    return bool(status.get("completed")) or status.get("state") == "post"


def is_live(event: dict) -> bool:
    status = event.get("status", {}).get("type", {})
    return status.get("state") == "in"


def event_to_teams_scores(event: dict) -> tuple:
    """
    Returns (home_name, away_name, home_score, away_score).
    Scores are None when the match hasn't been played.
    """
    home_c, away_c = extract_competitors(event)
    return (
        extract_team_name(home_c),
        extract_team_name(away_c),
        extract_score(home_c) if is_finished(event) else None,
        extract_score(away_c) if is_finished(event) else None,
    )


def build_event_lookup(events: list) -> tuple[dict, dict]:
    """
    Returns:
      by_id    — { espn_event_id -> event }
      by_teams — { (home_name, away_name) -> event }
    """
    by_id, by_teams = {}, {}
    for ev in events:
        home_c, away_c = extract_competitors(ev)
        home = extract_team_name(home_c)
        away = extract_team_name(away_c)
        by_id[ev["id"]] = ev
        if home and away:
            by_teams[(home, away)] = ev
    return by_id, by_teams
