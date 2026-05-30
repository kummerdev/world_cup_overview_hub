# Copa do Mundo 2026 — Tracker

A Personal Learning Project,Used for help me watch and keep track off the 2026 world cup,Created Using Claude as the Main Helping Agent

A live **FIFA World Cup 2026** tracker built with Flask and the free ESPN public API. Scores update automatically — no API key, no manual entry required.

---

## Features

- **Live scores** — JavaScript polls ESPN every 45 seconds and updates match cards in place with a blinking **AO VIVO** badge and current minute
- **Auto-sync** — every page load silently fetches today's finished results from ESPN and writes them to the fixture list
- **Group standings** — automatically ranked by points, goal difference, and goals scored
- **Knockout bracket** — auto-populated as teams advance from the group stage, all the way from the Round of 32 to the Final
- **Best 3rd-place logic** — the 8 best third-place teams are ranked and assigned to the correct bracket slots following the official FIFA rules
- **News tab** — latest World Cup articles pulled directly from ESPN
- **Calendar view** — all 104 matches organized by date across the full tournament
- **Flag icons** — 48 national flags via [flagcdn.com](https://flagcdn.com)

---

## Tech Stack

| Layer | Tech |
|---|---|
| Backend | Python 3 · Flask |
| Data source | [ESPN Public API](https://site.api.espn.com) — free, no key |
| Frontend | Vanilla JS · CSS (dark theme) |
| Storage | JSON flat files (no database) |

---

## Project Structure

```
worldcup-pickem/
├── app.py               # Flask routes & bracket logic
├── worldcup_api.py      # ESPN API client
├── sync_matches.py      # CLI: link local matches to ESPN IDs
├── data/
│   └── matches.json     # 104 fixtures (groups + knockout)
├── templates/
│   ├── base.html
│   ├── index.html       # Group stage
│   ├── standings.html   # Group standings
│   ├── playoffs.html    # Knockout bracket
│   ├── calendar.html    # Full schedule by date
│   ├── noticias.html    # News
│   └── macros.html      # Reusable match card
└── static/
    ├── style.css
    └── app.js           # Live score poller
```

---

## Setup

```bash
# 1. Install dependencies
pip install flask python-dotenv requests

# 2. Run
python app.py
```

No API key required. The ESPN API is completely public.

---

## One-time fixture linking (optional)

Before the tournament starts, run the link step to map each local match to its ESPN event ID. This makes syncing faster and more reliable during the tournament:

```bash
python sync_matches.py link   # maps local matches -> ESPN event IDs
python sync_matches.py sync   # manually pull latest results
python sync_matches.py live   # print current live scores to stdout
```

---

## How the bracket auto-populates

1. ESPN sync writes scores into `matches.json` as games finish
2. `calcular_classificacao()` ranks each group by FIFA tiebreaker rules (pts → GD → GF)
3. `resolve_playoff_displays()` reads those rankings and fills placeholders like `1A`, `2B`, `3A/B/C/D/F`, `W74`, `L88` — all the way from the Round of 32 to the Final
4. The standings page and knockout bracket always reflect the current state

---

## Tournament Coverage

- **48 teams** · **12 groups** (A–L) · **104 matches**
- Group stage → Round of 32 → Round of 16 → Quarterfinals → Semifinals → Third-place play-off → Final
- Host nations: Canada · USA · Mexico
