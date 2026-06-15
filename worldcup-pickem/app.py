from __future__ import annotations

import json
import logging
import os
import re
import time
from datetime import date, timedelta

from flask import Flask, jsonify, render_template, g
from markupsafe import Markup

import worldcup_api as wc_api

# ── App setup ─────────────────────────────────────────────────────────────────

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or __import__("secrets").token_hex(32)

logger = logging.getLogger(__name__)

BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
MATCHES_FILE = os.path.join(BASE_DIR, "data", "matches.json")

# ── Constants ─────────────────────────────────────────────────────────────────

FASE_LABELS: dict[str, str] = {
    "group":        "Fase de Grupos",
    "round32":      "Rodada de 32",
    "round16":      "Oitavas de Final",
    "quarterfinal": "Quartas de Final",
    "semifinal":    "Semifinal",
    "third_place":  "Disputa de 3º Lugar",
    "final":        "Final",
}

FASE_ORDER = ["group", "round32", "round16", "quarterfinal", "semifinal", "third_place", "final"]

FLAGS: dict[str, str] = {
    "Mexico":               "mx",
    "South Africa":         "za",
    "South Korea":          "kr",
    "Czech Republic":       "cz",
    "Canada":               "ca",
    "Bosnia & Herzegovina": "ba",
    "Qatar":                "qa",
    "Switzerland":          "ch",
    "Brazil":               "br",
    "Morocco":              "ma",
    "Haiti":                "ht",
    "Scotland":             "gb-sct",
    "USA":                  "us",
    "Paraguay":             "py",
    "Australia":            "au",
    "Turkey":               "tr",
    "Germany":              "de",
    "Curacao":              "cw",
    "Ivory Coast":          "ci",
    "Ecuador":              "ec",
    "Netherlands":          "nl",
    "Japan":                "jp",
    "Sweden":               "se",
    "Tunisia":              "tn",
    "Belgium":              "be",
    "Egypt":                "eg",
    "Iran":                 "ir",
    "New Zealand":          "nz",
    "Spain":                "es",
    "Cape Verde":           "cv",
    "Saudi Arabia":         "sa",
    "Uruguay":              "uy",
    "France":               "fr",
    "Senegal":              "sn",
    "Iraq":                 "iq",
    "Norway":               "no",
    "Argentina":            "ar",
    "Algeria":              "dz",
    "Austria":              "at",
    "Jordan":               "jo",
    "Portugal":             "pt",
    "DR Congo":             "cd",
    "Uzbekistan":           "uz",
    "Colombia":             "co",
    "England":              "gb-eng",
    "Croatia":              "hr",
    "Ghana":                "gh",
    "Panama":               "pa",
}

THIRD_PLACE_SLOTS: dict[int, set[str]] = {
    74: {"A", "B", "C", "D", "F"},
    77: {"C", "D", "F", "G", "H"},
    79: {"C", "E", "F", "H", "I"},
    80: {"E", "H", "I", "J", "K"},
    81: {"B", "E", "F", "I", "J"},
    82: {"A", "E", "H", "I", "J"},
    85: {"E", "F", "G", "I", "J"},
    87: {"D", "E", "I", "J", "L"},
}

# ── Template filters ──────────────────────────────────────────────────────────

@app.template_filter("flag")
def flag_filter(name: str) -> Markup | str:
    if not name:
        return name
    name = wc_api.normalize(name)
    code = FLAGS.get(name)
    name_span = f'<span class="country-name" data-en="{name}">{name}</span>'
    if not code:
        return Markup(name_span)
    img = f'<img src="https://flagcdn.com/w20/{code}.png" class="flag-img" alt="{name}">'
    return Markup(f"{img} {name_span}")


# ── File I/O ──────────────────────────────────────────────────────────────────

def load_json(filepath: str) -> list | dict:
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(filepath: str, data: list | dict) -> None:
    """Atomic write — uses a temp file + os.replace() to prevent corruption."""
    tmp = filepath + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, filepath)


def get_matches() -> list:
    if "matches" not in g:
        g.matches = load_json(MATCHES_FILE)
    return g.matches


# ── Display helpers ───────────────────────────────────────────────────────────

def get_display_name(match: dict, side: str) -> str:
    return match.get(side) or match.get(f"{side}_placeholder", "?")


def set_display_names(matches: list) -> None:
    for match in matches:
        match["home_display"] = get_display_name(match, "home")
        match["away_display"] = get_display_name(match, "away")


# ── Group standings ───────────────────────────────────────────────────────────

def calcular_classificacao(group_matches: list) -> dict:
    groups: dict[str, dict] = {}

    for m in group_matches:
        grp = m["grupo"]
        row = groups.setdefault(grp, {})
        for side in ("home", "away"):
            team = m.get(side)
            if team and team not in row:
                row[team] = {"mp": 0, "w": 0, "d": 0, "l": 0,
                             "gf": 0, "ga": 0, "gd": 0, "pts": 0}

        if m["home_score"] is None or m["away_score"] is None:
            continue
        home, away = m["home"], m["away"]
        if not home or not away:
            continue

        hs, as_ = m["home_score"], m["away_score"]
        for team, gf, ga in ((home, hs, as_), (away, as_, hs)):
            groups[grp][team]["mp"] += 1
            groups[grp][team]["gf"] += gf
            groups[grp][team]["ga"] += ga

        if hs > as_:
            groups[grp][home]["w"] += 1
            groups[grp][home]["pts"] += 3
            groups[grp][away]["l"] += 1
        elif hs < as_:
            groups[grp][away]["w"] += 1
            groups[grp][away]["pts"] += 3
            groups[grp][home]["l"] += 1
        else:
            groups[grp][home]["d"] += 1
            groups[grp][home]["pts"] += 1
            groups[grp][away]["d"] += 1
            groups[grp][away]["pts"] += 1

    result = {}
    for grp in sorted(groups):
        for name, s in groups[grp].items():
            s["gd"] = s["gf"] - s["ga"]
            s["name"] = name
        result[grp] = sorted(
            groups[grp].values(),
            key=lambda t: (-t["pts"], -t["gd"], -t["gf"], t["name"]),
        )
    return result


def get_complete_groups(group_matches: list) -> set[str]:
    counts: dict[str, dict] = {}
    for m in group_matches:
        grp = m["grupo"]
        c = counts.setdefault(grp, {"total": 0, "done": 0})
        c["total"] += 1
        if m["home_score"] is not None and m["away_score"] is not None:
            c["done"] += 1
    return {grp for grp, c in counts.items() if c["total"] > 0 and c["total"] == c["done"]}


# ── Playoff resolution ────────────────────────────────────────────────────────

def get_best_third_place(standings: dict) -> list:
    third = []
    for grp, teams in standings.items():
        if len(teams) >= 3:
            t = dict(teams[2])
            t["group"] = grp
            third.append(t)
    third.sort(key=lambda t: (-t["pts"], -t["gd"], -t["gf"], t["name"]))
    return third[:8]


def assign_third_place(qualifying_third: list) -> dict[int, str]:
    qual_groups = {t["group"]: t for t in qualifying_third}
    slots = sorted(THIRD_PLACE_SLOTS.items(), key=lambda kv: len(kv[1] & set(qual_groups)))
    assignment: dict[int, str] = {}
    used: set[str] = set()
    for match_id, allowed in slots:
        available = (allowed & set(qual_groups)) - used
        for team in qualifying_third:
            if team["group"] in available:
                assignment[match_id] = team["name"]
                used.add(team["group"])
                break
    return assignment


def _resolve_team(placeholder: str, standings: dict, third_assignment: dict,
                  resolved: dict, match_id: int, complete_groups: set) -> str:
    if not placeholder:
        return "?"

    m = re.match(r"^([1-4])([A-L])$", placeholder)
    if m:
        pos, grp = int(m.group(1)), m.group(2)
        if grp not in complete_groups:
            return placeholder
        teams = standings.get(grp, [])
        return teams[pos - 1]["name"] if len(teams) >= pos else placeholder

    if re.match(r"^3[A-L](/[A-L])+$", placeholder):
        return placeholder if len(complete_groups) < 12 else third_assignment.get(match_id, placeholder)

    m = re.match(r"^([WL])(\d+)$", placeholder)
    if m:
        kind, ref_id = m.group(1), int(m.group(2))
        ref = resolved.get(ref_id)
        if ref and ref["home_score"] is not None:
            hs, as_ = ref["home_score"], ref["away_score"]
            winner = ref["home"] if hs >= as_ else ref["away"]
            return winner if kind == "W" else (ref["away"] if hs >= as_ else ref["home"])
        return placeholder

    return placeholder


def resolve_playoff_displays(playoff_matches: list, standings: dict, complete_groups: set) -> None:
    best_third   = get_best_third_place(standings)
    third_assign = assign_third_place(best_third)
    phase_rank   = {f: i for i, f in enumerate(FASE_ORDER)}
    ordered      = sorted(playoff_matches, key=lambda m: (phase_rank.get(m["fase"], 99), m["id"]))
    resolved: dict = {}

    for match in ordered:
        for side in ("home", "away"):
            if not match.get(side):
                ph   = match.get(f"{side}_placeholder", "?")
                name = _resolve_team(ph, standings, third_assign, resolved,
                                     match["id"], complete_groups)
                match[f"{side}_display"] = name
                if name != ph:
                    match[side] = name
        resolved[match["id"]] = {
            "home":       match.get("home_display", "?"),
            "away":       match.get("away_display", "?"),
            "home_score": match.get("home_score"),
            "away_score": match.get("away_score"),
        }


# ── Leaders cache ─────────────────────────────────────────────────────────────

_ATHLETE_CACHE_TTL = 6 * 3600   # 6 hours
_LEADERS_CACHE_TTL = 600         # 10 minutes

_athlete_cache: dict[str, tuple[dict, float]] = {}   # url -> (data, timestamp)
_leaders_cache: dict = {"data": None, "ts": 0.0}


def _resolve_athlete(ref_url: str) -> dict:
    entry = _athlete_cache.get(ref_url)
    if entry and time.time() - entry[1] < _ATHLETE_CACHE_TTL:
        return entry[0]
    try:
        data = wc_api.resolve_ref(ref_url)
    except Exception:
        data = {}
    _athlete_cache[ref_url] = (data, time.time())
    return data


def _get_leaders_data() -> list:
    now = time.time()
    if _leaders_cache["data"] is not None and now - _leaders_cache["ts"] < _LEADERS_CACHE_TTL:
        return _leaders_cache["data"]

    try:
        raw = wc_api.get_leaders()
    except Exception as e:
        logger.warning("Leaders API error: %s", e)
        _leaders_cache.update({"data": [], "ts": now})
        return []

    # ESPN returns some categories twice: verbose ("Matches: 1, Goals: 2") and
    # simple ("2"). Skip verbose duplicates; deduplicate by category name.
    seen: set[str] = set()
    categories = []

    for cat in raw.get("categories", []):
        cat_name  = cat.get("displayName") or cat.get("name", "")
        first_val = (cat.get("leaders") or [{}])[0].get("displayValue", "")
        if "Matches:" in first_val or cat_name in seen:
            continue
        seen.add(cat_name)

        leaders = []
        for entry in cat.get("leaders", [])[:10]:
            ath_raw  = entry.get("athlete", {})
            team_raw = entry.get("team", {})
            value    = entry.get("displayValue", "0")

            ath = _resolve_athlete(ath_raw["$ref"]) if "$ref" in ath_raw else ath_raw or {}

            if "$ref" in team_raw:
                td   = _resolve_athlete(team_raw["$ref"])
                team = wc_api.normalize(td.get("name") or td.get("displayName") or ath.get("citizenship", ""))
            else:
                team = wc_api.normalize(ath.get("citizenship", ""))

            leaders.append({
                "name":     ath.get("displayName", "?"),
                "value":    value,
                "headshot": (ath.get("headshot") or {}).get("href", ""),
                "team":     team,
            })

        if leaders and any(e["name"] != "?" for e in leaders):
            categories.append({"name": cat_name, "leaders": leaders})

    _leaders_cache.update({"data": categories, "ts": now})
    return categories


# ── ESPN auto-sync ────────────────────────────────────────────────────────────

_SYNC_COOLDOWN = 15   # seconds — avoids hammering ESPN on rapid page refreshes
_sync_last_run: float = 0.0


def _sync_today_silent() -> int:
    """
    Pull ESPN results into matches.json on every page load.

    A 15-second cooldown prevents hammering ESPN when the user refreshes
    rapidly — data is at most 15 s stale, live scores still update via the
    JS poller every 20 s regardless.

    On first call, also sweeps past dates that still have null scores so
    previously missed games are caught automatically.
    """
    global _sync_last_run

    today = date.today()
    if today < wc_api.WC_START or today > wc_api.WC_END:
        return 0

    now = time.time()
    if now - _sync_last_run < _SYNC_COOLDOWN:
        return 0
    _sync_last_run = now

    matches  = load_json(MATCHES_FILE)
    espn_map = {m["espn_event_id"]: m for m in matches if m.get("espn_event_id")}

    dates_needed: set[date] = {today, today - timedelta(days=1)}
    for m in matches:
        if m["home_score"] is None and m.get("home"):
            try:
                day, month = map(int, m["data"].split("/"))
                match_date = date(2026, month, day)
                if wc_api.WC_START <= match_date < today:
                    dates_needed.add(match_date)
            except Exception:
                pass

    all_events: list = []
    for d in sorted(dates_needed):
        if not (wc_api.WC_START <= d <= wc_api.WC_END):
            continue
        try:
            data = wc_api.get_scoreboard(d.strftime("%Y%m%d"))
            all_events.extend(data.get("events", []))
        except Exception as e:
            logger.warning("Scoreboard fetch failed for %s: %s", d, e)

    updated = 0
    for ev in all_events:
        if not wc_api.is_finished(ev) and not wc_api.is_live(ev):
            continue

        home_c, away_c = wc_api.extract_competitors(ev)
        home = wc_api.extract_team_name(home_c)
        away = wc_api.extract_team_name(away_c)
        hs   = wc_api.extract_score(home_c)
        as_  = wc_api.extract_score(away_c)
        if hs is None or as_ is None:
            continue

        match = espn_map.get(ev["id"]) or next(
            (m for m in matches if m.get("home") == home and m.get("away") == away), None
        )
        if not match:
            continue

        if match["home_score"] != hs or match["away_score"] != as_:
            match["home_score"] = hs
            match["away_score"] = as_
            updated += 1

    if updated:
        save_json(MATCHES_FILE, matches)

    return updated


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    _sync_today_silent()
    matches       = get_matches()
    group_matches = [m for m in matches if m["fase"] == "group"]
    set_display_names(group_matches)
    grupos: dict = {}
    for m in group_matches:
        grupos.setdefault(m["grupo"], []).append(m)
    return render_template("index.html", grupos=grupos, active_tab="grupos")


@app.route("/classificacao")
def classificacao():
    _sync_today_silent()
    group_matches = [m for m in get_matches() if m["fase"] == "group"]
    standings     = calcular_classificacao(group_matches)
    return render_template("standings.html", standings=standings, active_tab="classificacao")


@app.route("/playoffs")
def playoffs():
    _sync_today_silent()
    matches         = get_matches()
    group_matches   = [m for m in matches if m["fase"] == "group"]
    playoff_matches = [m for m in matches if m["fase"] != "group"]
    standings       = calcular_classificacao(group_matches)
    complete_groups = get_complete_groups(group_matches)
    resolve_playoff_displays(playoff_matches, standings, complete_groups)
    fases: dict = {}
    for m in playoff_matches:
        fase = m["fase"]
        fases.setdefault(fase, {"label": FASE_LABELS[fase], "matches": []})["matches"].append(m)
    return render_template(
        "playoffs.html",
        fases=fases,
        fase_order=[f for f in FASE_ORDER if f != "group"],
        active_tab="playoffs",
    )


@app.route("/calendario")
def calendario():
    _sync_today_silent()
    matches = get_matches()
    set_display_names(matches)
    by_date: dict = {}
    for m in matches:
        by_date.setdefault(m["data"], []).append(m)
    sorted_dates = sorted(by_date, key=lambda d: (int(d[3:5]), int(d[0:2])))
    return render_template(
        "calendar.html",
        by_date=by_date,
        sorted_dates=sorted_dates,
        active_tab="calendario",
        FASE_LABELS=FASE_LABELS,
    )


@app.route("/livescores.json")
def livescores_json():
    try:
        events = wc_api.get_scoreboard().get("events", [])
    except Exception as e:
        return jsonify({"error": str(e)}), 502

    scores = []
    for ev in events:
        if not wc_api.is_live(ev):
            continue
        home_c, away_c = wc_api.extract_competitors(ev)
        status      = ev.get("status", {})
        status_type = status.get("type", {})
        scores.append({
            "home":       wc_api.extract_team_name(home_c),
            "away":       wc_api.extract_team_name(away_c),
            "home_score": wc_api.extract_score(home_c),
            "away_score": wc_api.extract_score(away_c),
            "detail":     status_type.get("detail", ""),
            "clock":      status.get("displayClock", ""),
            "period":     status.get("period", 1),
        })
    return jsonify(scores)


@app.route("/artilheiros")
def artilheiros():
    categories = _get_leaders_data()
    return render_template("artilheiros.html", categories=categories, active_tab="artilheiros")


@app.route("/noticias")
def noticias():
    try:
        articles = wc_api.get_news(limit=20).get("articles", [])
        error    = None
    except Exception as e:
        articles, error = [], str(e)
    return render_template("noticias.html", articles=articles, error=error, active_tab="noticias")


if __name__ == "__main__":
    app.run(debug=True)
