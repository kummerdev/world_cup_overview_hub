from flask import Flask, render_template, g, jsonify
from markupsafe import Markup
import json
import os
import re
import time
import worldcup_api as wc_api

app = Flask(__name__)
_secret = os.environ.get('SECRET_KEY')
if not _secret:
    import secrets as _s
    _secret = _s.token_hex(32)   # random per process — fine for local dev
app.secret_key = _secret

BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
MATCHES_FILE = os.path.join(BASE_DIR, 'data', 'matches.json')

FASE_LABELS = {
    'group':        'Fase de Grupos',
    'round32':      'Rodada de 32',
    'round16':      'Oitavas de Final',
    'quarterfinal': 'Quartas de Final',
    'semifinal':    'Semifinal',
    'third_place':  'Disputa de 3º Lugar',
    'final':        'Final',
}

FASE_ORDER = ['group', 'round32', 'round16', 'quarterfinal', 'semifinal', 'third_place', 'final']

FLAGS = {
    'Mexico':               'mx',
    'South Africa':         'za',
    'South Korea':          'kr',
    'Czech Republic':       'cz',
    'Canada':               'ca',
    'Bosnia & Herzegovina': 'ba',
    'Qatar':                'qa',
    'Switzerland':          'ch',
    'Brazil':               'br',
    'Morocco':              'ma',
    'Haiti':                'ht',
    'Scotland':             'gb-sct',
    'USA':                  'us',
    'Paraguay':             'py',
    'Australia':            'au',
    'Turkey':               'tr',
    'Germany':              'de',
    'Curacao':              'cw',
    'Ivory Coast':          'ci',
    'Ecuador':              'ec',
    'Netherlands':          'nl',
    'Japan':                'jp',
    'Sweden':               'se',
    'Tunisia':              'tn',
    'Belgium':              'be',
    'Egypt':                'eg',
    'Iran':                 'ir',
    'New Zealand':          'nz',
    'Spain':                'es',
    'Cape Verde':           'cv',
    'Saudi Arabia':         'sa',
    'Uruguay':              'uy',
    'France':               'fr',
    'Senegal':              'sn',
    'Iraq':                 'iq',
    'Norway':               'no',
    'Argentina':            'ar',
    'Algeria':              'dz',
    'Austria':              'at',
    'Jordan':               'jo',
    'Portugal':             'pt',
    'DR Congo':             'cd',
    'Uzbekistan':           'uz',
    'Colombia':             'co',
    'England':              'gb-eng',
    'Croatia':              'hr',
    'Ghana':                'gh',
    'Panama':               'pa',
}


@app.template_filter('flag')
def flag_filter(name):
    if not name:
        return name
    name = wc_api.normalize(name)
    code = FLAGS.get(name)
    if not code:
        return Markup(name)
    img = f'<img src="https://flagcdn.com/w20/{code}.png" class="flag-img" alt="{name}">'
    return Markup(f'{img} {name}')


def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_matches():
    if 'matches' not in g:
        g.matches = load_json(MATCHES_FILE)
    return g.matches


def get_display_name(match, side):
    name = match.get(side)
    return name if name else match.get(f'{side}_placeholder', '?')


def set_display_names(matches):
    """Set home_display / away_display on every match."""
    for match in matches:
        match['home_display'] = get_display_name(match, 'home')
        match['away_display'] = get_display_name(match, 'away')


def get_complete_groups(group_matches):
    counts = {}
    for m in group_matches:
        grp = m['grupo']
        if grp not in counts:
            counts[grp] = {'total': 0, 'done': 0}
        counts[grp]['total'] += 1
        if m['home_score'] is not None and m['away_score'] is not None:
            counts[grp]['done'] += 1
    return {grp for grp, c in counts.items() if c['total'] > 0 and c['total'] == c['done']}


THIRD_PLACE_SLOTS = {
    74: {'A', 'B', 'C', 'D', 'F'},
    77: {'C', 'D', 'F', 'G', 'H'},
    79: {'C', 'E', 'F', 'H', 'I'},
    80: {'E', 'H', 'I', 'J', 'K'},
    81: {'B', 'E', 'F', 'I', 'J'},
    82: {'A', 'E', 'H', 'I', 'J'},
    85: {'E', 'F', 'G', 'I', 'J'},
    87: {'D', 'E', 'I', 'J', 'L'},
}


def get_best_third_place(standings):
    third = []
    for grp, teams in standings.items():
        if len(teams) >= 3:
            t = dict(teams[2])
            t['group'] = grp
            third.append(t)
    third.sort(key=lambda t: (-t['pts'], -t['gd'], -t['gf'], t['name']))
    return third[:8]


def assign_third_place(qualifying_third):
    qual_groups = {t['group']: t for t in qualifying_third}
    slots = sorted(
        THIRD_PLACE_SLOTS.items(),
        key=lambda kv: len(kv[1] & set(qual_groups))
    )
    assignment = {}
    used = set()
    for match_id, allowed in slots:
        available = (allowed & set(qual_groups)) - used
        for team in qualifying_third:
            if team['group'] in available:
                assignment[match_id] = team['name']
                used.add(team['group'])
                break
    return assignment


def _resolve_team(placeholder, standings, third_assignment, resolved, match_id, complete_groups):
    if not placeholder:
        return '?'
    m = re.match(r'^([1-4])([A-L])$', placeholder)
    if m:
        pos, grp = int(m.group(1)), m.group(2)
        if grp not in complete_groups:
            return placeholder
        teams = standings.get(grp, [])
        if len(teams) >= pos:
            return teams[pos - 1]['name']
        return placeholder
    if re.match(r'^3[A-L](/[A-L])+$', placeholder):
        if len(complete_groups) < 12:
            return placeholder
        return third_assignment.get(match_id, placeholder)
    m = re.match(r'^([WL])(\d+)$', placeholder)
    if m:
        kind, ref_id = m.group(1), int(m.group(2))
        ref = resolved.get(ref_id)
        if ref and ref['home_score'] is not None:
            hs, as_ = ref['home_score'], ref['away_score']
            if kind == 'W':
                return ref['home'] if hs >= as_ else ref['away']
            else:
                return ref['home'] if hs < as_ else ref['away']
        return placeholder
    return placeholder


def resolve_playoff_displays(playoff_matches, standings, complete_groups):
    best_third   = get_best_third_place(standings)
    third_assign = assign_third_place(best_third)
    phase_rank   = {f: i for i, f in enumerate(FASE_ORDER)}
    ordered      = sorted(playoff_matches, key=lambda m: (phase_rank.get(m['fase'], 99), m['id']))
    resolved     = {}
    for match in ordered:
        for side in ('home', 'away'):
            if not match.get(side):
                ph   = match.get(f'{side}_placeholder', '?')
                name = _resolve_team(ph, standings, third_assign, resolved,
                                     match['id'], complete_groups)
                match[f'{side}_display'] = name
                if name != ph:
                    match[side] = name
        resolved[match['id']] = {
            'home':       match.get('home_display', '?'),
            'away':       match.get('away_display', '?'),
            'home_score': match.get('home_score'),
            'away_score': match.get('away_score'),
        }


def calcular_classificacao(group_matches):
    groups = {}
    for m in group_matches:
        grp = m['grupo']
        if grp not in groups:
            groups[grp] = {}
        for side in ('home', 'away'):
            team = m.get(side)
            if team and team not in groups[grp]:
                groups[grp][team] = {'mp': 0, 'w': 0, 'd': 0, 'l': 0,
                                     'gf': 0, 'ga': 0, 'gd': 0, 'pts': 0}
        if m['home_score'] is None or m['away_score'] is None:
            continue
        home, away = m['home'], m['away']
        if not home or not away:
            continue
        hs, as_ = m['home_score'], m['away_score']
        groups[grp][home]['mp'] += 1
        groups[grp][away]['mp'] += 1
        groups[grp][home]['gf'] += hs;  groups[grp][home]['ga'] += as_
        groups[grp][away]['gf'] += as_; groups[grp][away]['ga'] += hs
        if hs > as_:
            groups[grp][home]['w'] += 1; groups[grp][home]['pts'] += 3
            groups[grp][away]['l'] += 1
        elif hs < as_:
            groups[grp][away]['w'] += 1; groups[grp][away]['pts'] += 3
            groups[grp][home]['l'] += 1
        else:
            groups[grp][home]['d'] += 1; groups[grp][home]['pts'] += 1
            groups[grp][away]['d'] += 1; groups[grp][away]['pts'] += 1

    result = {}
    for grp in sorted(groups):
        for name, s in groups[grp].items():
            s['gd'] = s['gf'] - s['ga']
            s['name'] = name
        result[grp] = sorted(
            groups[grp].values(),
            key=lambda t: (-t['pts'], -t['gd'], -t['gf'], t['name'])
        )
    return result


# ── Leaders cache ─────────────────────────────────────────────────────────────

_athlete_cache: dict = {}
_leaders_cache: dict = {'data': None, 'ts': 0.0}


def _resolve_athlete(ref_url: str) -> dict:
    if ref_url not in _athlete_cache:
        try:
            _athlete_cache[ref_url] = wc_api.resolve_ref(ref_url)
        except Exception:
            _athlete_cache[ref_url] = {}
    return _athlete_cache[ref_url]


def _get_leaders_data():
    now = time.time()
    if _leaders_cache['data'] is not None and now - _leaders_cache['ts'] < 600:
        return _leaders_cache['data']

    try:
        raw = wc_api.get_leaders()
    except Exception:
        _leaders_cache.update({'data': [], 'ts': now})
        return []

    categories = []
    for cat in raw.get('items', []):
        cat_name = cat.get('displayName') or cat.get('name', '')
        leaders = []
        for entry in cat.get('leaders', [])[:10]:
            ath_raw = entry.get('athlete', {})
            value   = entry.get('displayValue', '0')

            if isinstance(ath_raw, dict) and '$ref' in ath_raw:
                ath = _resolve_athlete(ath_raw['$ref'])
            else:
                ath = ath_raw or {}

            name     = ath.get('displayName', '?')
            headshot = (ath.get('headshot') or {}).get('href', '')
            team     = wc_api.normalize(ath.get('citizenship', '') or '')
            leaders.append({'name': name, 'value': value,
                            'headshot': headshot, 'team': team})

        if leaders and any(e['name'] != '?' for e in leaders):
            categories.append({'name': cat_name, 'leaders': leaders})

    _leaders_cache.update({'data': categories, 'ts': now})
    return categories


# ── ESPN auto-sync ────────────────────────────────────────────────────────────

def _sync_today_silent():
    """
    Silently pull today's ESPN results and update matches.json.
    Called automatically on each page load during the tournament.
    Returns the number of matches updated.
    """
    from datetime import date, timedelta
    today = date.today()
    if today < wc_api.WC_START or today > wc_api.WC_END:
        return 0

    try:
        dates_to_check = [today - timedelta(days=1), today]
        all_events = []
        for d in dates_to_check:
            if wc_api.WC_START <= d <= wc_api.WC_END:
                data = wc_api.get_scoreboard(d.strftime('%Y%m%d'))
                all_events.extend(data.get('events', []))
    except Exception:
        return 0

    matches  = load_json(MATCHES_FILE)
    espn_map = {m['espn_event_id']: m for m in matches if m.get('espn_event_id')}
    updated  = 0

    for ev in all_events:
        if not wc_api.is_finished(ev):
            continue
        home_c, away_c = wc_api.extract_competitors(ev)
        home = wc_api.extract_team_name(home_c)
        away = wc_api.extract_team_name(away_c)
        hs   = wc_api.extract_score(home_c)
        as_  = wc_api.extract_score(away_c)
        if hs is None or as_ is None:
            continue

        match = espn_map.get(ev['id']) or next(
            (m for m in matches if m.get('home') == home and m.get('away') == away), None
        )
        if not match:
            continue
        if match['home_score'] != hs or match['away_score'] != as_:
            match['home_score'] = hs
            match['away_score'] = as_
            updated += 1

    if updated:
        save_json(MATCHES_FILE, matches)
    return updated


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route('/classificacao')
def classificacao():
    _sync_today_silent()
    group_matches = [m for m in get_matches() if m['fase'] == 'group']
    standings = calcular_classificacao(group_matches)
    return render_template('standings.html', standings=standings, active_tab='classificacao')


@app.route('/')
def index():
    _sync_today_silent()
    matches = get_matches()
    group_matches = [m for m in matches if m['fase'] == 'group']
    set_display_names(group_matches)
    grupos = {}
    for m in group_matches:
        grupos.setdefault(m['grupo'], []).append(m)
    return render_template('index.html', grupos=grupos, active_tab='grupos')


@app.route('/playoffs')
def playoffs():
    _sync_today_silent()
    matches = get_matches()
    group_matches   = [m for m in matches if m['fase'] == 'group']
    playoff_matches = [m for m in matches if m['fase'] != 'group']
    standings       = calcular_classificacao(group_matches)
    complete_groups = get_complete_groups(group_matches)
    resolve_playoff_displays(playoff_matches, standings, complete_groups)
    fases = {}
    for m in playoff_matches:
        fase = m['fase']
        if fase not in fases:
            fases[fase] = {'label': FASE_LABELS[fase], 'matches': []}
        fases[fase]['matches'].append(m)
    return render_template(
        'playoffs.html',
        fases=fases,
        fase_order=[f for f in FASE_ORDER if f != 'group'],
        active_tab='playoffs',
    )


@app.route('/calendario')
def calendario():
    _sync_today_silent()
    matches = get_matches()
    set_display_names(matches)
    by_date = {}
    for m in matches:
        by_date.setdefault(m['data'], []).append(m)
    sorted_dates = sorted(by_date, key=lambda d: (int(d[3:5]), int(d[0:2])))
    return render_template(
        'calendar.html',
        by_date=by_date,
        sorted_dates=sorted_dates,
        active_tab='calendario',
        FASE_LABELS=FASE_LABELS,
    )


# ── ESPN integration ──────────────────────────────────────────────────────────


@app.route('/livescores.json')
def livescores_json():
    try:
        data   = wc_api.get_scoreboard()
        events = data.get('events', [])
    except Exception as e:
        return jsonify({'error': str(e)}), 502

    scores = []
    for ev in events:
        if not wc_api.is_live(ev):
            continue
        home_c, away_c  = wc_api.extract_competitors(ev)
        status           = ev.get('status', {})
        status_type      = status.get('type', {})
        scores.append({
            'home':       wc_api.extract_team_name(home_c),
            'away':       wc_api.extract_team_name(away_c),
            'home_score': wc_api.extract_score(home_c),
            'away_score': wc_api.extract_score(away_c),
            'detail':     status_type.get('detail', ''),       # e.g. "45'"
            'clock':      status.get('displayClock', ''),      # e.g. "45:00"
            'period':     status.get('period', 1),             # 1 or 2
        })
    return jsonify(scores)



@app.route('/artilheiros')
def artilheiros():
    categories = _get_leaders_data()
    return render_template('artilheiros.html', categories=categories,
                           active_tab='artilheiros')


@app.route('/noticias')
def noticias():
    try:
        data     = wc_api.get_news(limit=20)
        articles = data.get('articles', [])
        error    = None
    except Exception as e:
        articles, error = [], str(e)
    return render_template('noticias.html', articles=articles,
                           error=error, active_tab='noticias')


if __name__ == '__main__':
    app.run(debug=True)
