/**
 * DuoSecur Pro — Client Controller
 */

function switchTab(tabId) {
    document.querySelectorAll('.tab-panel').forEach(panel => panel.classList.add('hidden'));
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('border-emerald-500', 'text-emerald-400');
        btn.classList.add('border-transparent', 'text-slate-400');
    });

    const activePanel = document.getElementById(tabId);
    if (activePanel) activePanel.classList.remove('hidden');

    const btnId = tabId.replace('tab-', 'nav-');
    const activeBtn = document.getElementById(btnId);
    if (activeBtn) {
        activeBtn.classList.remove('border-transparent', 'text-slate-400');
        activeBtn.classList.add('border-emerald-500', 'text-emerald-400');
    }

    if (tabId === 'tab-readable') {
        scanMarketReadability();
    }
}

function setTeams(home, away) {
    document.getElementById('inputHomeTeam').value = home;
    document.getElementById('inputAwayTeam').value = away;
    runCustomAnalysis();
}

async function loadDailyCote2() {
    try {
        const res = await fetch('/api/v1/cote2/daily-ticket');
        const data = await res.json();

        const totalOddsEl = document.getElementById('cote2TotalOdds');
        const probEl = document.getElementById('cote2Prob');
        const timeEl = document.getElementById('cote2Timestamp');

        if (totalOddsEl) totalOddsEl.innerText = data.combined_odds.toFixed(2);
        if (probEl) probEl.innerText = `${data.joint_probability_pct}%`;
        if (timeEl) timeEl.innerText = data.generated_at;

        const container = document.getElementById('cote2LegsContainer');
        if (container) {
            container.innerHTML = data.legs.map((leg, index) => {
                return `
                    <div class="bg-slate-900/90 border border-slate-800 p-4 rounded-xl space-y-3 relative hover:border-emerald-500/40 transition">
                        <div class="flex items-center justify-between">
                            <span class="text-xs font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 font-bold uppercase">Événement #${index + 1} Ultra-Lisible</span>
                            <span class="text-xs text-slate-400 font-mono">${leg.competition} • ${leg.time}</span>
                        </div>

                        <div>
                            <h4 class="text-base font-bold text-white">${leg.match}</h4>
                            <div class="mt-1 flex items-center justify-between">
                                <span class="text-sm font-semibold text-emerald-300">${leg.selection}</span>
                                <span class="text-lg font-mono font-black text-white px-2 py-0.5 rounded bg-slate-800 border border-slate-700">@ ${leg.odds.toFixed(2)}</span>
                            </div>
                        </div>

                        <div class="p-2.5 rounded-lg bg-slate-950/70 border border-slate-800/80 text-xs text-slate-300 space-y-1">
                            <div class="text-[11px] font-mono text-emerald-400 font-bold">POURQUOI CE CHOIX :</div>
                            <p>${leg.why_this_pick}</p>
                        </div>

                        <div class="p-2 rounded-lg bg-rose-950/20 border border-rose-500/30 text-xs text-rose-300 flex items-start gap-1.5">
                            <span class="font-bold shrink-0">🚫 Piège Évité :</span>
                            <span>${leg.trap_avoided}</span>
                        </div>
                    </div>
                `;
            }).join('');
        }

        if (data.alternative_single) {
            const altTitle = document.getElementById('altSingleTitle');
            const altOdds = document.getElementById('altSingleOdds');
            if (altTitle) altTitle.innerText = `${data.alternative_single.match} — ${data.alternative_single.selection}`;
            if (altOdds) altOdds.innerText = data.alternative_single.odds.toFixed(2);
        }

    } catch (err) {
        console.error("Error loading Cote 2 ticket:", err);
    }
}

async function scanMarketReadability() {
    const homeInput = document.getElementById('marketRankHome');
    const awayInput = document.getElementById('marketRankAway');
    const tbody = document.getElementById('marketRankTableBody');
    if (!tbody) return;

    const home = (homeInput ? homeInput.value.trim() : "") || "Real Madrid";
    const away = (awayInput ? awayInput.value.trim() : "") || "Villarreal";

    tbody.innerHTML = `<tr><td colspan="5" class="py-4 text-center text-slate-500 font-mono">Évaluation de la lisibilité des marchés en cours...</td></tr>`;

    try {
        const res = await fetch('/api/v1/readable/rank-markets', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ home_team: home, away_team: away })
        });
        const data = await res.json();

        tbody.innerHTML = data.all_ranked_markets.map(m => {
            let badgeStyle = m.badge_class === "diamond" ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 font-bold" : (m.badge_class === "gold" ? "bg-blue-500/20 text-blue-300 border border-blue-500/40" : (m.badge_class === "silver" ? "bg-amber-500/20 text-amber-300 border border-amber-500/40" : "bg-rose-500/20 text-rose-300 border border-rose-500/40 font-bold"));

            return `
                <tr class="hover:bg-slate-900/60 transition">
                    <td class="py-3 px-3">
                        <div class="font-bold text-white">${m.name}</div>
                        <div class="text-[11px] text-slate-400 mt-0.5">${m.why_readable}</div>
                    </td>
                    <td class="py-3 px-3 text-center font-mono font-bold text-sm text-white">${m.odds.toFixed(2)}</td>
                    <td class="py-3 px-3 text-center font-mono text-emerald-400 font-bold">${m.win_prob_pct}%</td>
                    <td class="py-3 px-3 text-center font-mono font-black text-sm">${m.readability_score} / 100</td>
                    <td class="py-3 px-3">
                        <span class="px-2 py-0.5 rounded text-[11px] ${badgeStyle}">${m.tier_badge}</span>
                        <div class="text-[10px] text-slate-400 mt-1">${m.recommended_role}</div>
                    </td>
                </tr>
            `;
        }).join('');

    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="5" class="py-4 text-center text-rose-400">Erreur lors de l'évaluation des marchés.</td></tr>`;
    }
}

async function runCustomAnalysis() {
    const homeInput = document.getElementById('inputHomeTeam');
    const awayInput = document.getElementById('inputAwayTeam');
    const home = homeInput ? homeInput.value.trim() : "";
    const away = awayInput ? awayInput.value.trim() : "";

    if (!home || !away) {
        alert("Veuillez renseigner le nom des deux équipes.");
        return;
    }

    const output = document.getElementById('customVerdictOutput');
    if (!output) return;
    output.innerHTML = `<div class="p-6 text-center text-xs font-mono text-slate-400">Calcul du verdict mathématique et détection des pièges pour ${home} vs ${away}...</div>`;

    try {
        const res = await fetch('/api/v1/analyzer/evaluate-match', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ home_team: home, away_team: away })
        });
        const data = await res.json();

        const badgeColor = data.verdict_status === 'SAFE_GREEN' ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40' : (data.verdict_status === 'BALANCED_YELLOW' ? 'bg-amber-500/20 text-amber-300 border-amber-500/40' : 'bg-rose-500/20 text-rose-300 border-rose-500/40');

        output.innerHTML = `
            <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
                <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
                    <div>
                        <div class="flex items-center gap-2">
                            <span class="text-xs font-mono px-2 py-0.5 rounded border font-bold ${badgeColor}">${data.verdict_badge}</span>
                            <span class="text-xs text-slate-400 font-mono">Indice de Lisibilité : <strong class="text-white">${data.readability_score} / 100</strong></span>
                        </div>
                        <h3 class="text-lg font-black text-white mt-1">${data.home_team} vs ${data.away_team}</h3>
                        <p class="text-xs text-slate-300 mt-0.5">${data.verdict_desc}</p>
                    </div>
                    <div class="text-right shrink-0">
                        <div class="text-[11px] font-mono text-slate-400">Score le plus probable</div>
                        <div class="text-xl font-black text-emerald-400 font-mono">${Math.round(data.projected_xg.home)} - ${Math.round(data.projected_xg.away)}</div>
                    </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
                    <div class="p-4 rounded-xl bg-emerald-950/20 border border-emerald-500/40 space-y-2">
                        <div class="text-xs font-mono uppercase text-emerald-400 font-bold">🛡️ Le Choix Blindé (Le Plus Sûr)</div>
                        <div class="text-sm font-bold text-white">${data.safe_pick.title}</div>
                        <div class="flex items-center justify-between text-xs font-mono text-slate-300">
                            <span>Cote estimée : <strong class="text-emerald-400">@ ${data.safe_pick.estimated_odds}</strong></span>
                            <span>Fiabilité : <strong class="text-emerald-400">${data.safe_pick.win_probability_pct}%</strong></span>
                        </div>
                        <p class="text-[11px] text-slate-400 pt-1 border-t border-slate-800">${data.safe_pick.reason}</p>
                    </div>

                    <div class="p-4 rounded-xl bg-blue-950/20 border border-blue-500/40 space-y-2">
                        <div class="text-xs font-mono uppercase text-blue-400 font-bold">🎯 Le Choix Équilibré (Cote ~2.00)</div>
                        <div class="text-sm font-bold text-white">${data.value_pick.title}</div>
                        <div class="flex items-center justify-between text-xs font-mono text-slate-300">
                            <span>Cote estimée : <strong class="text-blue-400">@ ${data.value_pick.estimated_odds}</strong></span>
                            <span>Probabilité : <strong class="text-blue-400">${data.value_pick.win_probability_pct}%</strong></span>
                        </div>
                        <p class="text-[11px] text-slate-400 pt-1 border-t border-slate-800">${data.value_pick.reason}</p>
                    </div>

                    <div class="p-4 rounded-xl bg-rose-950/20 border border-rose-500/40 space-y-2">
                        <div class="text-xs font-mono uppercase text-rose-400 font-bold">⚠️ Le Piège Bookmaker Détecté</div>
                        <div class="text-sm font-bold text-rose-300">${data.trap_warning.trap_market}</div>
                        <p class="text-[11px] text-slate-300">${data.trap_warning.why_its_a_trap}</p>
                        <p class="text-[11px] text-rose-400 font-semibold border-t border-slate-800 pt-1">Conseil : ${data.trap_warning.recommendation}</p>
                    </div>
                </div>

                <div class="p-3 bg-slate-950 rounded-lg border border-slate-800 text-xs text-slate-400 flex items-center justify-between">
                    <span>💡 ${data.advice_rule}</span>
                    <span class="font-mono text-emerald-400 font-bold">Mise max conseillée : ${data.recommended_stake_pct}%</span>
                </div>
            </div>
        `;

    } catch (err) {
        if (output) output.innerHTML = `<div class="p-4 text-center text-xs text-rose-400">Erreur lors de l'analyse du match.</div>`;
    }
}

window.addEventListener('DOMContentLoaded', () => {
    loadDailyCote2();
    runCustomAnalysis();
    scanMarketReadability();
});
