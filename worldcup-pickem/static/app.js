/* ── Live scores poller ─────────────────────────────────────────────────────
   Polls /livescores.json every 45 seconds while the page is visible.
   Updates match cards in place — no full page reload needed.
   ─────────────────────────────────────────────────────────────────────────── */

const POLL_INTERVAL = 45_000; // ms

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
  // Build a lookup: "HomeTeam|AwayTeam" -> game data
  const lookup = {};
  for (const g of games) {
    lookup[`${g.home}|${g.away}`] = g;
  }

  // Find every match card on the page
  document.querySelectorAll('.jogo[data-home]').forEach(card => {
    const home  = card.dataset.home;
    const away  = card.dataset.away;
    const game  = lookup[`${home}|${away}`];
    const placar = card.querySelector('.placar-centro');
    if (!placar) return;

    if (game) {
      // Live match — inject score + live badge
      placar.innerHTML = buildScoreHTML(game.home_score, game.away_score, game.detail);
      placar.classList.add('live-active');

      if (!card.querySelector('.live-badge')) {
        const badge = document.createElement('span');
        badge.className = 'live-badge';
        badge.textContent = '● AO VIVO';
        card.querySelector('.jogo-header').appendChild(badge);
      }
      card.classList.add('jogo-live');
      card.classList.remove('jogo-finalizado');
    } else {
      // Remove live state if game ended between polls
      if (card.classList.contains('jogo-live')) {
        card.classList.remove('jogo-live', 'live-active');
        placar.classList.remove('live-active');
        card.querySelector('.live-badge')?.remove();
        // Reload to show final score
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
      // No live games — clear any stale live state
      applyLiveScores([]);
    }
  } catch (e) {
    // Network error — silently skip this poll
  }
}

// Start polling as soon as the page loads
document.addEventListener('DOMContentLoaded', () => {
  pollLiveScores();                        // immediate first check
  setInterval(pollLiveScores, POLL_INTERVAL);

  // Pause polling when tab is hidden, resume when visible again
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') pollLiveScores();
  });
});
