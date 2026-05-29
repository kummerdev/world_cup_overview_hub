#!/usr/bin/env python
"""
Sync FIFA World Cup 2026 results from ESPN into matches.json.
No API key required.

Commands
--------
link   One-time: fetch all ESPN events and store their IDs in matches.json.
sync   Pull latest finished scores into matches.json.
live   Print currently live matches (no file changes).

Usage
-----
  python sync_matches.py link
  python sync_matches.py sync
  python sync_matches.py live
"""

import sys
import json
import os
from datetime import date, timedelta

import worldcup_api as api

BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
MATCHES_FILE = os.path.join(BASE_DIR, "data", "matches.json")


def _load():
    with open(MATCHES_FILE, encoding="utf-8") as f:
        return json.load(f)


def _save(matches):
    with open(MATCHES_FILE, "w", encoding="utf-8") as f:
        json.dump(matches, f, ensure_ascii=False, indent=2)


# ── Commands ──────────────────────────────────────────────────────────────────

def cmd_link():
    """
    Fetch every day of the World Cup from ESPN and map ESPN event IDs
    to local matches by home + away team names.
    Run this once before the tournament starts.
    """
    print("Fetching all WC 2026 events from ESPN…")
    print(f"  Scanning {api.WC_START} → {api.WC_END} (this may take ~30 s)")

    try:
        events = api.get_all_wc_events()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    _, by_teams = api.build_event_lookup(events)
    print(f"  Found {len(events)} ESPN events.")

    local = _load()
    linked = skipped = 0

    for match in local:
        home = match.get("home") or ""
        away = match.get("away") or ""
        if not home or not away:
            skipped += 1
            continue
        ev = by_teams.get((home, away))
        if ev:
            match["espn_event_id"] = ev["id"]
            linked += 1
        else:
            print(f"  No ESPN event: {home} vs {away}")
            skipped += 1

    _save(local)
    print(f"Done — linked {linked} matches, {skipped} skipped.")


def cmd_sync():
    """
    Sync finished match scores from ESPN into matches.json.
    Uses stored espn_event_id when available; falls back to team-name matching.
    Only fetches dates from the last 3 days onward to stay efficient.
    """
    local   = _load()
    by_local_id = {m["id"]: m for m in local}

    # Determine date range: WC start up to today
    today   = date.today()
    start   = max(api.WC_START, today - timedelta(days=3))
    end     = min(api.WC_END, today)

    if start > end:
        print("No past WC dates to sync yet.")
        return

    print(f"Fetching ESPN scores from {start} to {end}…")
    all_events = []
    current = start
    while current <= end:
        try:
            data = api.get_scoreboard(current.strftime("%Y%m%d"))
            all_events.extend(data.get("events", []))
        except Exception as e:
            print(f"  Warning: could not fetch {current}: {e}")
        current += timedelta(days=1)

    by_id, by_teams = api.build_event_lookup(all_events)

    # Build reverse map: espn_event_id -> local match
    espn_to_local = {
        m["espn_event_id"]: m
        for m in local if m.get("espn_event_id")
    }

    updated = 0
    for ev in all_events:
        if not api.is_finished(ev):
            continue

        home_c, away_c = api.extract_competitors(ev)
        home = api.extract_team_name(home_c)
        away = api.extract_team_name(away_c)
        hs   = api.extract_score(home_c)
        as_  = api.extract_score(away_c)

        if hs is None or as_ is None:
            continue

        # Try ID match first, then team-name match
        match = espn_to_local.get(ev["id"])
        if not match:
            match = next(
                (m for m in local
                 if m.get("home") == home and m.get("away") == away),
                None
            )

        if not match:
            continue

        if match["home_score"] != hs or match["away_score"] != as_:
            match["home_score"] = hs
            match["away_score"] = as_
            print(f"  Updated: {home} {hs}-{as_} {away}")
            updated += 1

    _save(local)
    print(f"Sync complete — {updated} match(es) updated.")


def cmd_live():
    """Print currently live matches (no file changes)."""
    try:
        data = api.get_scoreboard()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    events = data.get("events", [])
    live   = [ev for ev in events if api.is_live(ev)]

    if not live:
        print("No live matches right now.")
        return

    for ev in live:
        home_c, away_c = api.extract_competitors(ev)
        home = api.extract_team_name(home_c)
        away = api.extract_team_name(away_c)
        hs   = api.extract_score(home_c)
        as_  = api.extract_score(away_c)
        detail = ev.get("status", {}).get("type", {}).get("detail", "")
        print(f"  {home} {hs} - {as_} {away}  [{detail}]")


# ── Entry point ───────────────────────────────────────────────────────────────

COMMANDS = {"link": cmd_link, "sync": cmd_sync, "live": cmd_live}

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "sync"
    fn  = COMMANDS.get(cmd)
    if not fn:
        print(f"Unknown command '{cmd}'. Choose from: {', '.join(COMMANDS)}")
        sys.exit(1)
    fn()
