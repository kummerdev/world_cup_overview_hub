/* ── Internationalisation ─────────────────────────────────────────────────── */

const COUNTRY_NAMES = {
  pt: {
    'Mexico': 'México', 'South Africa': 'África do Sul', 'South Korea': 'Coreia do Sul',
    'Czech Republic': 'República Tcheca', 'Canada': 'Canadá',
    'Bosnia & Herzegovina': 'Bósnia e Herzegovina', 'Qatar': 'Catar',
    'Switzerland': 'Suíça', 'Brazil': 'Brasil', 'Morocco': 'Marrocos',
    'Haiti': 'Haiti', 'Scotland': 'Escócia', 'USA': 'EUA',
    'Paraguay': 'Paraguai', 'Australia': 'Austrália', 'Turkey': 'Turquia',
    'Germany': 'Alemanha', 'Curacao': 'Curaçao', 'Ivory Coast': 'Costa do Marfim',
    'Ecuador': 'Equador', 'Netherlands': 'Holanda', 'Japan': 'Japão',
    'Sweden': 'Suécia', 'Tunisia': 'Tunísia', 'Belgium': 'Bélgica',
    'Egypt': 'Egito', 'Iran': 'Irã', 'New Zealand': 'Nova Zelândia',
    'Spain': 'Espanha', 'Cape Verde': 'Cabo Verde', 'Saudi Arabia': 'Arábia Saudita',
    'Uruguay': 'Uruguai', 'France': 'França', 'Senegal': 'Senegal',
    'Iraq': 'Iraque', 'Norway': 'Noruega', 'Argentina': 'Argentina',
    'Algeria': 'Argélia', 'Austria': 'Áustria', 'Jordan': 'Jordânia',
    'Portugal': 'Portugal', 'DR Congo': 'RD Congo', 'Uzbekistan': 'Uzbequistão',
    'Colombia': 'Colômbia', 'England': 'Inglaterra', 'Croatia': 'Croácia',
    'Ghana': 'Gana', 'Panama': 'Panamá',
  },
  es: {
    'Mexico': 'México', 'South Africa': 'Sudáfrica', 'South Korea': 'Corea del Sur',
    'Czech Republic': 'República Checa', 'Canada': 'Canadá',
    'Bosnia & Herzegovina': 'Bosnia y Herzegovina', 'Qatar': 'Catar',
    'Switzerland': 'Suiza', 'Brazil': 'Brasil', 'Morocco': 'Marruecos',
    'Haiti': 'Haití', 'Scotland': 'Escocia', 'USA': 'EE.UU.',
    'Paraguay': 'Paraguay', 'Australia': 'Australia', 'Turkey': 'Turquía',
    'Germany': 'Alemania', 'Curacao': 'Curazao', 'Ivory Coast': 'Costa de Marfil',
    'Ecuador': 'Ecuador', 'Netherlands': 'Países Bajos', 'Japan': 'Japón',
    'Sweden': 'Suecia', 'Tunisia': 'Túnez', 'Belgium': 'Bélgica',
    'Egypt': 'Egipto', 'Iran': 'Irán', 'New Zealand': 'Nueva Zelanda',
    'Spain': 'España', 'Cape Verde': 'Cabo Verde', 'Saudi Arabia': 'Arabia Saudita',
    'Uruguay': 'Uruguay', 'France': 'Francia', 'Senegal': 'Senegal',
    'Iraq': 'Irak', 'Norway': 'Noruega', 'Argentina': 'Argentina',
    'Algeria': 'Argelia', 'Austria': 'Austria', 'Jordan': 'Jordania',
    'Portugal': 'Portugal', 'DR Congo': 'RD Congo', 'Uzbekistan': 'Uzbekistán',
    'Colombia': 'Colombia', 'England': 'Inglaterra', 'Croatia': 'Croacia',
    'Ghana': 'Ghana', 'Panama': 'Panamá',
  },
};

const UI_STRINGS = {
  pt: {
    'nav-grupos':         'Fase de Grupos',
    'nav-classificacao':  'Classificação',
    'nav-playoffs':       'Mata-Mata',
    'nav-calendario':     'Calendário',
    'nav-artilheiros':    'Artilheiros',
    'nav-noticias':       'Notícias',
    'footer-text':        "Copa do Mundo 2026 · Pick'em pessoal",
    'label-group':        'Grupo',
    'phase-group':        'Fase de Grupos',
    'phase-round32':      'Rodada de 32',
    'phase-round16':      'Oitavas de Final',
    'phase-quarterfinal': 'Quartas de Final',
    'phase-semifinal':    'Semifinal',
    'phase-third_place':  'Disputa de 3º Lugar',
    'phase-final':        'Final',
    'th-team':            'Seleção',
    'th-mp':              'J',  'th-mp-title':  'Jogos',
    'th-w':               'V',  'th-w-title':   'Vitórias',
    'th-d':               'E',  'th-d-title':   'Empates',
    'th-l':               'D',  'th-l-title':   'Derrotas',
    'th-gf':              'GM', 'th-gf-title':  'Gols Marcados',
    'th-ga':              'GS', 'th-ga-title':  'Gols Sofridos',
    'th-gd':              'SG', 'th-gd-title':  'Saldo de Gols',
    'th-pts':             'Pts',
    'live-badge':         '● AO VIVO',
    'playoff-info':       'Os confrontos são definidos automaticamente conforme os times avançam na fase de grupos.',
    'artilheiros-empty':  'As estatísticas de artilharia estarão disponíveis em breve.',
    'legend-advance':     'Avança (1º e 2º)',
    'legend-third':       'Pode avançar (3º)',
  },
  en: {
    'nav-grupos':         'Group Stage',
    'nav-classificacao':  'Standings',
    'nav-playoffs':       'Knockout',
    'nav-calendario':     'Calendar',
    'nav-artilheiros':    'Top Scorers',
    'nav-noticias':       'News',
    'footer-text':        "FIFA World Cup 2026 · Personal Pick'em",
    'label-group':        'Group',
    'phase-group':        'Group Stage',
    'phase-round32':      'Round of 32',
    'phase-round16':      'Round of 16',
    'phase-quarterfinal': 'Quarter-finals',
    'phase-semifinal':    'Semi-finals',
    'phase-third_place':  '3rd Place Match',
    'phase-final':        'Final',
    'th-team':            'Team',
    'th-mp':              'P',  'th-mp-title':  'Played',
    'th-w':               'W',  'th-w-title':   'Wins',
    'th-d':               'D',  'th-d-title':   'Draws',
    'th-l':               'L',  'th-l-title':   'Losses',
    'th-gf':              'GF', 'th-gf-title':  'Goals For',
    'th-ga':              'GA', 'th-ga-title':  'Goals Against',
    'th-gd':              'GD', 'th-gd-title':  'Goal Difference',
    'th-pts':             'Pts',
    'live-badge':         '● LIVE',
    'playoff-info':       'Matchups are determined automatically as teams advance through the group stage.',
    'artilheiros-empty':  'Scoring statistics will be available shortly.',
    'legend-advance':     'Advances (1st and 2nd)',
    'legend-third':       'May advance (3rd)',
  },
  es: {
    'nav-grupos':         'Fase de Grupos',
    'nav-classificacao':  'Clasificación',
    'nav-playoffs':       'Eliminatorias',
    'nav-calendario':     'Calendario',
    'nav-artilheiros':    'Goleadores',
    'nav-noticias':       'Noticias',
    'footer-text':        "Copa del Mundo 2026 · Pronósticos personales",
    'label-group':        'Grupo',
    'phase-group':        'Fase de Grupos',
    'phase-round32':      'Ronda de 32',
    'phase-round16':      'Octavos de Final',
    'phase-quarterfinal': 'Cuartos de Final',
    'phase-semifinal':    'Semifinal',
    'phase-third_place':  'Tercer Puesto',
    'phase-final':        'Final',
    'th-team':            'Selección',
    'th-mp':              'PJ', 'th-mp-title':  'Partidos',
    'th-w':               'G',  'th-w-title':   'Ganados',
    'th-d':               'E',  'th-d-title':   'Empates',
    'th-l':               'P',  'th-l-title':   'Perdidos',
    'th-gf':              'GF', 'th-gf-title':  'Goles a Favor',
    'th-ga':              'GC', 'th-ga-title':  'Goles en Contra',
    'th-gd':              'DG', 'th-gd-title':  'Diferencia de Goles',
    'th-pts':             'Pts',
    'live-badge':         '● EN VIVO',
    'playoff-info':       'Los cruces se determinan automáticamente conforme los equipos avanzan en la fase de grupos.',
    'artilheiros-empty':  'Las estadísticas de goles estarán disponibles en breve.',
    'legend-advance':     'Avanza (1.º y 2.º)',
    'legend-third':       'Puede avanzar (3.º)',
  },
};

/* ── Timezone conversion ──────────────────────────────────────────────────── */

const USER_TZ = Intl.DateTimeFormat().resolvedOptions().timeZone;

function convertMatchTime(hora, utctz, date) {
  const m = utctz.match(/UTC([+-]\d+(?:\.\d+)?)/i);
  if (!m) return { time: hora, tz: utctz };

  const offsetH  = parseFloat(m[1]);
  const [day, month] = date.split('/').map(Number);
  const [h, min]     = hora.split(':').map(Number);

  const utcMs   = Date.UTC(2026, month - 1, day, h - offsetH, min);
  const d       = new Date(utcMs);

  const timeStr = d.toLocaleTimeString('en-GB', {
    hour: '2-digit', minute: '2-digit', timeZone: USER_TZ, hour12: false,
  });

  const tzShort = d.toLocaleTimeString('en-US', {
    timeZoneName: 'short', timeZone: USER_TZ,
  }).split(' ').pop();

  return { time: timeStr, tz: tzShort };
}

/* ── Apply language ───────────────────────────────────────────────────────── */

function applyLanguage(lang) {
  const t  = UI_STRINGS[lang] || UI_STRINGS.pt;
  const cn = COUNTRY_NAMES[lang]; // undefined for 'en' — keeps English originals

  // UI strings
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const val = t[el.dataset.i18n];
    if (val !== undefined) el.innerHTML = val;
  });

  // th title attributes
  document.querySelectorAll('[data-i18n-title]').forEach(el => {
    const val = t[el.dataset.i18nTitle];
    if (val !== undefined) el.title = val;
  });

  // Country names
  document.querySelectorAll('.country-name[data-en]').forEach(el => {
    el.textContent = (cn && cn[el.dataset.en]) || el.dataset.en;
  });

  // Match times → user's local timezone
  document.querySelectorAll('.match-time-block').forEach(block => {
    const { time, tz } = convertMatchTime(
      block.dataset.hora, block.dataset.utctz, block.dataset.date
    );
    const horaEl = block.querySelector('.hora-val');
    const tzEl   = block.querySelector('.tz-val');
    if (horaEl) horaEl.textContent = time;
    if (tzEl)   tzEl.textContent   = tz;
  });

  // Active lang button
  document.querySelectorAll('.lang-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.lang === lang);
  });

  document.documentElement.lang = lang === 'pt' ? 'pt-br' : lang;
  localStorage.setItem('wcp-lang', lang);
}

/* ── Live scores poller ─────────────────────────────────────────────────────
   Polls /livescores.json every 45 seconds while the page is visible.
   Updates match cards in place — no full page reload needed.
   ─────────────────────────────────────────────────────────────────────────── */

const POLL_INTERVAL = 20_000;

function buildScoreHTML(hs, as_, detail) {
  const min = detail ? `<span class="live-min">${detail}</span>` : '';
  return `
    <span class="resultado-oficial live-score">
      ${hs} <span class="placar-sep">&ndash;</span> ${as_}
    </span>
    ${min}
  `;
}

function applyLiveScores(games) {
  const lookup = {};
  for (const g of games) {
    lookup[`${g.home}|${g.away}`] = g;
  }

  document.querySelectorAll('.jogo[data-home]').forEach(card => {
    const home   = card.dataset.home;
    const away   = card.dataset.away;
    const game   = lookup[`${home}|${away}`];
    const placar = card.querySelector('.placar-centro');
    if (!placar) return;

    if (game) {
      placar.innerHTML = buildScoreHTML(game.home_score, game.away_score, game.detail);
      placar.classList.add('live-active');

      if (!card.querySelector('.live-badge')) {
        const badge = document.createElement('span');
        badge.className = 'live-badge';
        badge.dataset.i18n = 'live-badge';
        const lang = localStorage.getItem('wcp-lang') || 'pt';
        badge.textContent = (UI_STRINGS[lang] || UI_STRINGS.pt)['live-badge'];
        card.querySelector('.jogo-header').appendChild(badge);
      }
      card.classList.add('jogo-live');
      card.classList.remove('jogo-finalizado');
    } else {
      if (card.classList.contains('jogo-live')) {
        card.classList.remove('jogo-live', 'live-active');
        placar.classList.remove('live-active');
        card.querySelector('.live-badge')?.remove();
        window.location.reload();
      }
    }
  });
}

async function pollLiveScores() {
  try {
    const res   = await fetch('/livescores.json');
    const games = await res.json();
    if (Array.isArray(games) && games.length > 0) {
      applyLiveScores(games);
    } else {
      applyLiveScores([]);
    }
  } catch (e) {
    // Network error — silently skip
  }
}

/* ── Bootstrap ───────────────────────────────────────────────────────────── */

document.addEventListener('DOMContentLoaded', () => {
  // Language buttons
  document.querySelectorAll('.lang-btn').forEach(btn => {
    btn.addEventListener('click', () => applyLanguage(btn.dataset.lang));
  });

  // Restore saved language (default: pt)
  applyLanguage(localStorage.getItem('wcp-lang') || 'pt');

  // Live scores polling
  pollLiveScores();
  setInterval(pollLiveScores, POLL_INTERVAL);

  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') pollLiveScores();
  });
});
