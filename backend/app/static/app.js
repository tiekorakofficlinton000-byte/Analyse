/**
 * QuantBet Terminal - Full Reactive Controller
 * Implements Open Match Analyzer, Daily Cote 2.00, Market Readability Ranker, Bankroll Mentor, Telegram VIP, and Mobile Money Checkout.
 */

let activeCurrency = "FCFA";
let userBankroll = 50000; // 50 000 FCFA default
let compoundChartInstance = null;

// Tab switcher
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

    if (tabId === 'tab-mentor' && !compoundChartInstance) {
        updateMentorSim();
    }
    if (tabId === 'tab-telegram') {
        loadTelegramPreview();
    }
    if (tabId === 'tab-readable') {
        scanMarketReadability();
    }
}

// Currency Switcher
function setCurrency(cur) {
    activeCurrency = cur;
    const btnFcfa = document.getElementById('btnCurFcfa');
    const btnEur = document.getElementById('btnCurEur');

    if (cur === 'FCFA') {
        userBankroll = 50000;
        btnFcfa.className = "px-2 py-0.5 rounded font-bold bg-emerald-500 text-black";
        btnEur.className = "px-2 py-0.5 rounded text-slate-400 hover:text-white";
        document.getElementById('headerBankrollText').innerText = "50 000 FCFA";
    } else {
        userBankroll = 1000;
        btnEur.className = "px-2 py-0.5 rounded font-bold bg-emerald-500 text-black";
        btnFcfa.className = "px-2 py-0.5 rounded text-slate-400 hover:text-white";
        document.getElementById('headerBankrollText').innerText = "1 000.00 €";
    }

    loadDailyCote2();
    if (!document.getElementById('tab-mentor').classList.contains('hidden')) {
        updateMentorSim();
    }
}

// Quick fill team suggestions
function setTeams(home, away) {
    document.getElementById('inputHomeTeam').value = home;
    document.getElementById('inputAwayTeam').value = away;
    runCustomAnalysis();
}

// --- PILLAR 1 & 2: LOAD DAILY COTE 2.00 ---
async function loadDailyCote2() {
    try {
        const res = await fetch('/api/v1/cote2/daily-ticket');
        const data = await res.json();

        document.getElementById('cote2TotalOdds').innerText = data.combined_odds.toFixed(2);
        document.getElementById('cote2Prob').innerText = `${data.joint_probability_pct}%`;
        document.getElementById('cote2Timestamp').innerText = data.generated_at;

        const container = document.getElementById('cote2LegsContainer');
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

        const stakeAmount = Math.round(userBankroll * 0.025);
        const gainAmount = Math.round(stakeAmount * data.combined_odds);
        const symbol = activeCurrency;
        document.getElementById('cote2StakeAdvice').innerText = `${stakeAmount.toLocaleString()} ${symbol}`;
        document.getElementById('cote2GainAdvice').innerText = `${gainAmount.toLocaleString()} ${symbol}`;

        if (data.alternative_single) {
            document.getElementById('altSingleTitle').innerText = `${data.alternative_single.match} — ${data.alternative_single.selection}`;
            document.getElementById('altSingleOdds').innerText = data.alternative_single.odds.toFixed(2);
        }

    } catch (err) {
        console.error("Error loading Cote 2 ticket:", err);
    }
}

function trackDailyCote2() {
    alert("✅ Ticket Cote 2.00 validé et consigné !\n\n• Règle respectée : 2.5% du capital misé.\n• Aucun combiné risqué de 10 matchs.\n• La patience crée la richesse.");
}

// --- SCAN MARKET READABILITY & RANKING ---
async function scanMarketReadability() {
    const home = document.getElementById('marketRankHome').value.trim() || "Real Madrid";
    const away = document.getElementById('marketRankAway').value.trim() || "Villarreal";
    const tbody = document.getElementById('marketRankTableBody');

    tbody.innerHTML = `<tr><td colspan="5" class="py-4 text-center text-slate-500 font-mono">Évaluation de la lisibilité des marchés en cours...</td></tr>`;

    try {
        const res = await fetch('/api/v1/readable/rank-markets', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ home_team: home, away_team: away })
        });
        const data = await res.json();

        tbody.innerHTML = data.all_ranked_markets.map(m => {
            let badgeStyle = "";
            if (m.badge_class === "diamond") {
                badgeStyle = "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 font-bold";
            } else if (m.badge_class === "gold") {
                badgeStyle = "bg-blue-500/20 text-blue-300 border border-blue-500/40 font-medium";
            } else if (m.badge_class === "silver") {
                badgeStyle = "bg-amber-500/20 text-amber-300 border border-amber-500/40";
            } else {
                badgeStyle = "bg-rose-500/20 text-rose-300 border border-rose-500/40 font-bold";
            }

            return `
                <tr class="hover:bg-slate-900/60 transition">
                    <td class="py-3 px-3">
                        <div class="font-bold text-white">${m.name}</div>
                        <div class="text-[11px] text-slate-400 mt-0.5">${m.why_readable}</div>
                    </td>
                    <td class="py-3 px-3 text-center font-mono font-bold text-sm text-white">
                        ${m.odds.toFixed(2)}
                    </td>
                    <td class="py-3 px-3 text-center font-mono text-emerald-400 font-bold">
                        ${m.win_prob_pct}%
                    </td>
                    <td class="py-3 px-3 text-center font-mono font-black text-sm">
                        ${m.readability_score} / 100
                    </td>
                    <td class="py-3 px-3">
                        <span class="px-2 py-0.5 rounded text-[11px] ${badgeStyle}">
                            ${m.tier_badge}
                        </span>
                        <div class="text-[10px] text-slate-400 mt-1">${m.recommended_role}</div>
                    </td>
                </tr>
            `;
        }).join('');

    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="5" class="py-4 text-center text-rose-400">Erreur lors de l'évaluation des marchés.</td></tr>`;
    }
}

// --- MENU SPÉCIAL : ANALYSEUR LIBRE DE N'IMPORTE QUEL MATCH ---
async function runCustomAnalysis() {
    const home = document.getElementById('inputHomeTeam').value.trim();
    const away = document.getElementById('inputAwayTeam').value.trim();

    if (!home || !away) {
        alert("Veuillez renseigner le nom des deux équipes.");
        return;
    }

    const output = document.getElementById('customVerdictOutput');
    output.innerHTML = `<div class="p-6 text-center text-xs font-mono text-slate-400">Calcul du verdict mathématique et détection des pièges pour ${home} vs ${away}...</div>`;

    try {
        const res = await fetch('/api/v1/analyzer/evaluate-match', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ home_team: home, away_team: away })
        });
        const data = await res.json();

        const badgeColor = data.verdict_status === 'SAFE_GREEN' 
            ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40' 
            : (data.verdict_status === 'BALANCED_YELLOW' ? 'bg-amber-500/20 text-amber-300 border-amber-500/40' : 'bg-rose-500/20 text-rose-300 border-rose-500/40');

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
                        <div class="text-[10px] text-slate-500 font-mono">xG : ${data.projected_xg.home} vs ${data.projected_xg.away}</div>
                    </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
                    <div class="p-4 rounded-xl bg-emerald-950/20 border border-emerald-500/40 space-y-2">
                        <div class="text-xs font-mono uppercase text-emerald-400 font-bold flex items-center gap-1.5">
                            <span>🛡️</span> Le Choix Blindé (Le Plus Sûr)
                        </div>
                        <div class="text-sm font-bold text-white">${data.safe_pick.title}</div>
                        <div class="flex items-center justify-between text-xs font-mono text-slate-300">
                            <span>Cote estimée : <strong class="text-emerald-400">@ ${data.safe_pick.estimated_odds}</strong></span>
                            <span>Fiabilité : <strong class="text-emerald-400">${data.safe_pick.win_probability_pct}%</strong></span>
                        </div>
                        <p class="text-[11px] text-slate-400 pt-1 border-t border-slate-800">${data.safe_pick.reason}</p>
                    </div>

                    <div class="p-4 rounded-xl bg-blue-950/20 border border-blue-500/40 space-y-2">
                        <div class="text-xs font-mono uppercase text-blue-400 font-bold flex items-center gap-1.5">
                            <span>🎯</span> Le Choix Équilibré (Cote ~2.00)
                        </div>
                        <div class="text-sm font-bold text-white">${data.value_pick.title}</div>
                        <div class="flex items-center justify-between text-xs font-mono text-slate-300">
                            <span>Cote estimée : <strong class="text-blue-400">@ ${data.value_pick.estimated_odds}</strong></span>
                            <span>Probabilité : <strong class="text-blue-400">${data.value_pick.win_probability_pct}%</strong></span>
                        </div>
                        <p class="text-[11px] text-slate-400 pt-1 border-t border-slate-800">${data.value_pick.reason}</p>
                    </div>

                    <div class="p-4 rounded-xl bg-rose-950/20 border border-rose-500/40 space-y-2">
                        <div class="text-xs font-mono uppercase text-rose-400 font-bold flex items-center gap-1.5">
                            <span>⚠️</span> Le Piège Bookmaker Détecté
                        </div>
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
        output.innerHTML = `<div class="p-4 text-center text-xs text-rose-400">Erreur lors de l'analyse du match.</div>`;
    }
}

// --- PILLAR 3: COMPOUND CAPITAL SIMULATOR ---
async function updateMentorSim() {
    const capitalSlider = document.getElementById('sliderCapital');
    const daysSlider = document.getElementById('sliderDays');

    const capital = parseFloat(capitalSlider?.value || 25000);
    const days = parseInt(daysSlider?.value || 60);

    const symbol = activeCurrency;
    document.getElementById('labelCapitalInput').innerText = `${capital.toLocaleString()} ${symbol}`;
    document.getElementById('labelDaysInput').innerText = `${days} Jours`;

    try {
        const res = await fetch(`/api/v1/mentor/compound-simulation?initial_capital=${capital}&currency=${symbol}&days=${days}&stake_pct=2.5&win_rate_pct=66.0`);
        const data = await res.json();

        document.getElementById('mentorFinalCapital').innerText = `${Math.round(data.final_capital).toLocaleString()} ${symbol}`;
        const avgStake = Math.round((data.initial_capital + data.final_capital) / 2 * 0.025);
        document.getElementById('mentorAvgStake').innerText = `${avgStake.toLocaleString()} ${symbol}`;

        const labels = data.trajectory.map(t => `Jour ${t.day}`);
        const quantValues = data.trajectory.map(t => t.quant_capital);
        const casualValues = data.trajectory.map(t => t.casual_capital);

        const ctx = document.getElementById('compoundChart').getContext('2d');
        if (compoundChartInstance) {
            compoundChartInstance.destroy();
        }

        compoundChartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Abonné Discipliné (Cote 2 Sécurisée + Gestion 2.5%)',
                        data: quantValues,
                        borderColor: '#10b981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        borderWidth: 2.5,
                        fill: true,
                        tension: 0.2
                    },
                    {
                        label: 'Parieur Combinés de 10 Matchs (Perte)',
                        data: casualValues,
                        borderColor: '#f43f5e',
                        borderDash: [5, 5],
                        backgroundColor: 'transparent',
                        borderWidth: 2,
                        tension: 0.1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { labels: { color: '#94a3b8', font: { family: 'monospace', size: 11 } } }
                },
                scales: {
                    x: {
                        grid: { color: 'rgba(255, 255, 255, 0.04)' },
                        ticks: { color: '#64748b', font: { family: 'monospace', size: 10 } }
                    },
                    y: {
                        grid: { color: 'rgba(255, 255, 255, 0.04)' },
                        ticks: {
                            color: '#94a3b8',
                            font: { family: 'monospace', size: 10 },
                            callback: (v) => `${v.toLocaleString()} ${symbol}`
                        }
                    }
                }
            }
        });

    } catch (err) {
        console.error(err);
    }
}

// --- TELEGRAM BROADCAST PREVIEW ---
async function loadTelegramPreview() {
    try {
        const res = await fetch('/api/v1/telegram/preview-daily-alert');
        const data = await res.json();
        document.getElementById('telegramMessagePreview').innerText = data.raw_message;
    } catch (err) {
        console.error(err);
    }
}

function copyTelegramMessage() {
    const text = document.getElementById('telegramMessagePreview').innerText;
    navigator.clipboard.writeText(text);
    alert("✅ Message Telegram copié dans le presse-papier !");
}

function simulateTelegramBroadcast() {
    alert("🚀 Message diffusé avec succès aux 1 024 abonnés du canal VIP Telegram !\n\nChaque abonné a reçu sur son téléphone le ticket Cote 2.00 avec la mise exacte à jouer.");
}

// --- PAYMENT CHECKOUT SIMULATION ---
async function simulatePaymentCheckout() {
    const provider = document.getElementById('paymentProviderSelect').value;
    const contact = document.getElementById('paymentCustomerContact').value;
    const resultBox = document.getElementById('paymentResultBox');

    resultBox.innerHTML = `<div class="p-3 bg-slate-950 rounded border border-slate-800 text-slate-400">Génération du lien de paiement ${provider}...</div>`;

    try {
        const res = await fetch('/api/v1/payments/checkout', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                customer_phone_or_email: contact,
                provider_id: provider,
                currency: activeCurrency
            })
        });
        const data = await res.json();

        // Simulate immediate confirmation callback
        const confirmRes = await fetch(`/api/v1/payments/simulate-webhook/${data.transaction_id}`, { method: 'POST' });
        const confirmData = await confirmRes.json();

        resultBox.innerHTML = `
            <div class="p-3 bg-emerald-950/40 border border-emerald-500/40 rounded-lg text-emerald-300 space-y-1">
                <div class="font-bold flex items-center gap-1.5">
                    <span>✅ Paiement Validé avec Succès !</span>
                </div>
                <div>Opérateur : <strong>${data.provider}</strong> • Montant : <strong>${data.amount.toLocaleString()} ${data.currency}</strong></div>
                <div class="text-[11px] text-slate-300">Abonnement PRO activé pour 30 jours. L'utilisateur a reçu son lien vers le canal VIP Telegram.</div>
            </div>
        `;

    } catch (err) {
        resultBox.innerHTML = `<div class="p-3 bg-rose-950/40 border border-rose-500/40 rounded text-rose-300">Erreur de paiement.</div>`;
    }
}

// --- BUSINESS SCALE SLIDER ---
function updateBizProjections() {
    const slider = document.getElementById('sliderBizSubscribers');
    const count = parseInt(slider.value);
    document.getElementById('bizSubscribersCountText').innerText = `${count.toLocaleString()} Abonnés`;

    const priceFcfa = 15000;
    const priceEur = 22.86;

    const mrrFcfa = count * priceFcfa;
    const mrrEur = Math.round(count * priceEur);
    const arrFcfa = mrrFcfa * 12;
    const arrEur = Math.round(arrFcfa * (priceEur / priceFcfa));

    document.getElementById('bizMrrFcfa').innerText = `${mrrFcfa.toLocaleString()} FCFA`;
    document.getElementById('bizMrrEur').innerText = `≈ ${mrrEur.toLocaleString()} € / mois`;
    document.getElementById('bizArrFcfa').innerText = `${arrFcfa.toLocaleString()} FCFA`;
    document.getElementById('bizArrEur').innerText = `≈ ${arrEur.toLocaleString()} € / an`;
}

// Bootstrap
window.addEventListener('DOMContentLoaded', () => {
    loadDailyCote2();
    runCustomAnalysis();
    scanMarketReadability();
});
