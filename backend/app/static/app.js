/**
 * DuoSecur Pro — Client Controller
 * Multi-Tier Combos (Cote 2, Cote 3, Cote 5), Weekly Alternatives & Advanced Quant Indicators
 * Features:
 * - Full Dixon-Coles bivariate Poisson modeling
 * - Advanced Tactical Indicators: xG, npxG, xGA, PPDA, Field Tilt, Direct Speed
 * - Zero-Vig Fair Odds & True Probabilities Table
 * - Top Exact Score Matrix
 * - Quarter-Kelly Capital Sizing & EV%
 */

let currentUser = null;
let allTicketsData = {};
let allPremiumMatches = [];
let activeTier = 'cote2';
let activeLeagueFilter = 'ALL';
let activeModalPlan = 'PREMIUM';

// --- AUTH & SESSION MANAGEMENT ---
function initUserSession() {
    const stored = localStorage.getItem('duosecur_user');
    if (stored) {
        try {
            currentUser = JSON.parse(stored);
        } catch (e) {
            currentUser = null;
        }
    } else {
        currentUser = {
            email: "invite@duosecur.io",
            tier: "FREE_TRIAL",
            trial_days_remaining: 3,
            daily_analysis_count: 0,
            max_analyses: 5,
            analyses_remaining: 5,
            max_alternatives: 1,
            has_cote2: true,
            has_cote3: false,
            has_cote5: false,
            is_guest: true
        };
    }
    updateUIForUser();
}

function updateUIForUser() {
    const guestArea = document.getElementById('headerGuestArea');
    const userArea = document.getElementById('headerUserArea');
    const emailEl = document.getElementById('headerUserEmail');
    const badgeEl = document.getElementById('headerUserBadge');
    const upgradeBtn = document.getElementById('headerUpgradeBtn');
    const bannerStatusTag = document.getElementById('bannerTrialStatusTag');
    const bannerStatusText = document.getElementById('bannerTrialStatusText');
    const quotaDisplay = document.getElementById('quotaDisplayTag');
    const altHeaderBadge = document.getElementById('alternativesHeaderBadge');

    if (!currentUser || currentUser.is_guest) {
        if (guestArea) guestArea.classList.remove('hidden');
        if (userArea) userArea.classList.add('hidden');
        if (bannerStatusTag) bannerStatusTag.innerText = "🎁 ESSAI 3 JOURS GRATUITS";
        if (bannerStatusText) bannerStatusText.innerText = "Inscrivez-vous pour activer vos 3 jours gratuits (Cote 2 + 1 alternative + 5 analyses/j).";
        if (quotaDisplay) quotaDisplay.innerText = "5 / 5 analyses restantes";
        if (altHeaderBadge) altHeaderBadge.innerText = "1 Match (Essai / Simple) • 5 Matchs (Pro)";
        return;
    }

    if (guestArea) guestArea.classList.add('hidden');
    if (userArea) userArea.classList.remove('hidden');
    if (emailEl) emailEl.innerText = currentUser.email;

    const isPro = currentUser.tier === 'PREMIUM' || currentUser.tier === 'PRO';
    const isSimple = currentUser.tier === 'SIMPLE';

    if (isPro) {
        if (badgeEl) badgeEl.innerText = "👑 Membre Pro VIP";
        if (upgradeBtn) upgradeBtn.classList.add('hidden');
        if (bannerStatusTag) {
            bannerStatusTag.className = "px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 font-mono font-bold";
            bannerStatusTag.innerText = "👑 COMPTE PRO VIP ACTIF";
        }
        if (bannerStatusText) bannerStatusText.innerText = "Accès intégral débloqué : Cotes 2, 3 et 5, 5 événements en alternative et analyses illimitées.";
        if (quotaDisplay) {
            quotaDisplay.innerText = "⚡ Analyses Illimitées (Pro)";
            quotaDisplay.className = "text-sm font-black font-mono text-amber-400";
        }
        if (altHeaderBadge) altHeaderBadge.innerText = "5 Matchs en Alternative Débloqués (Pro)";
    } else if (isSimple) {
        if (badgeEl) badgeEl.innerText = "🟢 Abonné Simple (1 000 F)";
        if (upgradeBtn) {
            upgradeBtn.classList.remove('hidden');
            upgradeBtn.innerText = "👑 Passer Pro (2 000 F)";
        }
        if (bannerStatusTag) {
            bannerStatusTag.className = "px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-mono font-bold";
            bannerStatusTag.innerText = "🟢 ABONNEMENT SIMPLE ACTIF";
        }
        if (bannerStatusText) bannerStatusText.innerText = "Formule Simple active (Cote 2 + 1 alternative + 5 analyses/j). Passez au Pro pour les cotes 3, 5 et 5 alternatives.";
        const rem = currentUser.analyses_remaining !== undefined ? currentUser.analyses_remaining : 5;
        if (quotaDisplay) {
            quotaDisplay.innerText = `${rem} / 5 analyses restantes`;
            quotaDisplay.className = "text-sm font-black font-mono text-emerald-400";
        }
        if (altHeaderBadge) altHeaderBadge.innerText = "1 Match en Alternative (Formule Simple)";
    } else {
        const daysLeft = currentUser.trial_days_remaining || 3;
        if (badgeEl) badgeEl.innerText = `🎁 Essai Gratuit (${daysLeft}j)`;
        if (upgradeBtn) {
            upgradeBtn.classList.remove('hidden');
            upgradeBtn.innerText = "👑 Passer Pro (2 000 F)";
        }
        if (bannerStatusTag) {
            bannerStatusTag.className = "px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-mono font-bold";
            bannerStatusTag.innerText = `🎁 ESSAI GRATUIT (${daysLeft} JOURS)`;
        }
        if (bannerStatusText) bannerStatusText.innerText = `Vos ${daysLeft} jours d'essai gratuits sont actifs (Cote 2 + 1 alternative + 5 analyses/j).`;
        const rem = currentUser.analyses_remaining !== undefined ? currentUser.analyses_remaining : 5;
        if (quotaDisplay) {
            quotaDisplay.innerText = `${rem} / 5 analyses restantes`;
            quotaDisplay.className = "text-sm font-black font-mono text-emerald-400";
        }
        if (altHeaderBadge) altHeaderBadge.innerText = "1 Match (Essai 3j) • 5 Matchs (Pro)";
    }

    renderActiveTicket();
    renderFilteredAlternatives();
}

// --- AUTH MODAL FUNCTIONS ---
function openAuthModal(defaultTab = 'register') {
    const modal = document.getElementById('authModal');
    if (modal) {
        modal.classList.remove('hidden');
        switchAuthTab(defaultTab);
    }
}

function closeAuthModal() {
    const modal = document.getElementById('authModal');
    if (modal) modal.classList.add('hidden');
}

function switchAuthTab(tab) {
    const btnReg = document.getElementById('tabBtnRegister');
    const btnLog = document.getElementById('tabBtnLogin');
    const formReg = document.getElementById('formRegister');
    const formLog = document.getElementById('formLogin');

    if (tab === 'register') {
        if (btnReg) btnReg.className = "text-sm font-black text-emerald-400 border-b-2 border-emerald-500 pb-1";
        if (btnLog) btnLog.className = "text-sm font-bold text-slate-400 hover:text-white pb-1";
        if (formReg) formReg.classList.remove('hidden');
        if (formLog) formLog.classList.add('hidden');
    } else {
        if (btnLog) btnLog.className = "text-sm font-black text-emerald-400 border-b-2 border-emerald-500 pb-1";
        if (btnReg) btnReg.className = "text-sm font-bold text-slate-400 hover:text-white pb-1";
        if (formLog) formLog.classList.remove('hidden');
        if (formReg) formReg.classList.add('hidden');
    }
}

async function handleRegisterSubmit(e) {
    e.preventDefault();
    const email = document.getElementById('regEmail').value.trim();
    const password = document.getElementById('regPassword').value;
    const resultBox = document.getElementById('authRegisterResult');
    const btn = document.getElementById('btnSubmitRegister');

    if (!email || !password) return;
    btn.disabled = true;
    resultBox.innerHTML = `<span class="text-slate-400 font-mono">Création du compte & activation des 3 jours gratuits...</span>`;

    try {
        const res = await fetch('/api/v1/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: email, password: password })
        });
        const data = await res.json();

        if (!res.ok) {
            resultBox.innerHTML = `<span class="text-rose-400">${data.detail || "Erreur d'inscription."}</span>`;
            btn.disabled = false;
            return;
        }

        currentUser = {
            email: data.email,
            tier: data.tier,
            trial_days_remaining: data.trial_days_remaining,
            analyses_remaining: data.analyses_remaining,
            max_analyses: data.max_analyses,
            max_alternatives: data.max_alternatives,
            token: data.access_token,
            is_guest: false
        };
        localStorage.setItem('duosecur_user', JSON.stringify(currentUser));
        localStorage.setItem('duosecur_token', data.access_token);

        resultBox.innerHTML = `<span class="text-emerald-400 font-bold">✅ Compte créé ! Vos 3 jours gratuits sont actifs.</span>`;
        setTimeout(() => {
            closeAuthModal();
            updateUIForUser();
        }, 1200);

    } catch (err) {
        resultBox.innerHTML = `<span class="text-rose-400">Erreur réseau lors de l'inscription.</span>`;
        btn.disabled = false;
    }
}

async function handleLoginSubmit(e) {
    e.preventDefault();
    const email = document.getElementById('loginEmail').value.trim();
    const password = document.getElementById('loginPassword').value;
    const resultBox = document.getElementById('authLoginResult');
    const btn = document.getElementById('btnSubmitLogin');

    if (!email || !password) return;
    btn.disabled = true;
    resultBox.innerHTML = `<span class="text-slate-400 font-mono">Connexion sécurisée en cours...</span>`;

    try {
        const res = await fetch('/api/v1/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: email, password: password })
        });
        const data = await res.json();

        if (!res.ok) {
            resultBox.innerHTML = `<span class="text-rose-400">${data.detail || "Email ou mot de passe incorrect."}</span>`;
            btn.disabled = false;
            return;
        }

        currentUser = {
            email: data.email,
            tier: data.tier,
            trial_days_remaining: data.trial_days_remaining,
            analyses_remaining: data.analyses_remaining,
            max_analyses: data.max_analyses,
            max_alternatives: data.max_alternatives,
            token: data.access_token,
            is_guest: false
        };
        localStorage.setItem('duosecur_user', JSON.stringify(currentUser));
        localStorage.setItem('duosecur_token', data.access_token);

        resultBox.innerHTML = `<span class="text-emerald-400 font-bold">✅ Connexion réussie !</span>`;
        setTimeout(() => {
            closeAuthModal();
            updateUIForUser();
        }, 900);

    } catch (err) {
        resultBox.innerHTML = `<span class="text-rose-400">Erreur réseau lors de la connexion.</span>`;
        btn.disabled = false;
    }
}

function quickFillLogin(email, password) {
    switchAuthTab('login');
    document.getElementById('loginEmail').value = email;
    document.getElementById('loginPassword').value = password;
    const fakeEvent = { preventDefault: () => {} };
    handleLoginSubmit(fakeEvent);
}

function logoutUser() {
    localStorage.removeItem('duosecur_user');
    localStorage.removeItem('duosecur_token');
    currentUser = null;
    initUserSession();
}

// --- TICKET TIER SELECTION (COTE 2, COTE 3, COTE 5) ---
function selectTicketTier(tier) {
    activeTier = tier;

    const btnCote2 = document.getElementById('btnTierCote2');
    const btnCote3 = document.getElementById('btnTierCote3');
    const btnCote5 = document.getElementById('btnTierCote5');

    const inactiveClass = "flex-1 sm:flex-initial py-2 px-4 rounded-lg text-xs font-black transition flex items-center justify-center gap-1.5 text-slate-400 hover:text-white";
    const activeClass = "flex-1 sm:flex-initial py-2 px-4 rounded-lg text-xs font-black transition flex items-center justify-center gap-1.5 bg-emerald-500 text-black shadow";

    if (btnCote2) btnCote2.className = tier === 'cote2' ? activeClass : inactiveClass;
    if (btnCote3) btnCote3.className = tier === 'cote3' ? activeClass : inactiveClass;
    if (btnCote5) btnCote5.className = tier === 'cote5' ? activeClass : inactiveClass;

    renderActiveTicket();
}

function renderActiveTicket() {
    const ticket = allTicketsData[activeTier];
    if (!ticket) return;

    const totalOddsEl = document.getElementById('cote2TotalOdds');
    const probEl = document.getElementById('cote2Prob');
    const titleEl = document.getElementById('ticketTitleText');
    const descEl = document.getElementById('ticketDescText');
    const badgeEl = document.getElementById('ticketBadgeText');

    if (totalOddsEl) totalOddsEl.innerText = ticket.combined_odds.toFixed(2);
    if (probEl) probEl.innerText = `${ticket.joint_probability_pct}%`;
    if (titleEl) titleEl.innerText = ticket.title;
    if (descEl) descEl.innerText = ticket.description;
    if (badgeEl) badgeEl.innerText = ticket.badge;

    const isPro = currentUser && (currentUser.tier === 'PREMIUM' || currentUser.tier === 'PRO');
    const container = document.getElementById('cote2LegsContainer');
    if (!container) return;

    // RULE: Cote 2.00 is visible to all. Cote 3 & 5 are strictly for Pro.
    if (activeTier !== 'cote2' && !isPro) {
        container.innerHTML = `
            <div class="col-span-full p-8 rounded-2xl bg-gradient-to-br from-amber-950/30 via-slate-900 to-slate-900 border border-amber-500/50 text-center space-y-4 shadow-xl">
                <div class="w-12 h-12 mx-auto rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/40 flex items-center justify-center text-xl font-bold">
                    🔒
                </div>
                <div>
                    <span class="text-xs font-mono font-black px-2.5 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/40 uppercase">EXCLUSIVITÉ ABONNEMENT PRO (2 000 FCFA / MOIS)</span>
                    <h3 class="text-lg font-black text-white mt-2">Le Ticket ${ticket.title} est réservé aux Membres Pro</h3>
                    <p class="text-xs text-slate-300 max-w-lg mx-auto mt-1 leading-relaxed">
                        Votre formule actuelle inclut la <strong>Cote 2.00</strong>. Pour débloquer la Cote 3.00, la Cote 5.00, 5 événements en alternative et les analyses illimitées, passez au Pack Pro.
                    </p>
                </div>
                <div class="pt-2">
                    <button onclick="openSubscriptionModal('PREMIUM')" class="px-5 py-3 bg-gradient-to-r from-amber-500 to-yellow-400 hover:from-amber-400 hover:to-yellow-300 text-black font-black text-xs rounded-xl transition shadow-lg shadow-amber-500/20">
                        👑 Débloquer le Pack Pro VIP (2 000 F / mois) →
                    </button>
                </div>
            </div>
        `;
        return;
    }

    container.innerHTML = ticket.legs.map((leg, index) => {
        const adv = leg.advanced || {};
        return `
            <div class="bg-slate-900/90 border border-slate-800 p-4 rounded-xl space-y-3 relative hover:border-emerald-500/40 transition shadow-lg">
                <div class="flex items-center justify-between">
                    <span class="text-xs font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 font-bold uppercase">Événement #${index + 1}</span>
                    <span class="text-xs text-slate-400 font-mono">${leg.competition} • ${leg.time}</span>
                </div>

                <div>
                    <h4 class="text-base font-bold text-white">${leg.match}</h4>
                    <div class="mt-1 flex items-center justify-between">
                        <span class="text-sm font-semibold text-emerald-300">${leg.selection}</span>
                        <span class="text-lg font-mono font-black text-white px-2 py-0.5 rounded bg-slate-800 border border-slate-700">@ ${leg.odds.toFixed(2)}</span>
                    </div>
                </div>

                ${adv.xg_home ? `
                    <div class="grid grid-cols-3 gap-1.5 p-2 bg-slate-950/80 rounded-lg border border-slate-800/80 text-[10px] font-mono">
                        <div>
                            <span class="text-slate-400 block">xG Projeté</span>
                            <strong class="text-amber-400">${adv.xg_home} - ${adv.xg_away}</strong>
                        </div>
                        <div>
                            <span class="text-slate-400 block">Field Tilt</span>
                            <strong class="text-emerald-400">${adv.field_tilt}%</strong>
                        </div>
                        <div>
                            <span class="text-slate-400 block">Edge EV</span>
                            <strong class="text-blue-400">+${adv.edge_ev_pct}%</strong>
                        </div>
                    </div>
                ` : ''}

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

// --- ALTERNATIVE MATCHES (1 FOR SIMPLE VS 5 FOR PRO) ---
function filterPremiumMatches(league) {
    activeLeagueFilter = league;

    document.querySelectorAll('.premium-filter-btn').forEach(btn => {
        if (btn.innerText.trim().toUpperCase() === league.toUpperCase() || (league === 'ALL' && btn.innerText.trim() === 'Tous')) {
            btn.className = "premium-filter-btn px-2.5 py-1 rounded-lg bg-emerald-500 text-black font-bold";
        } else {
            btn.className = "premium-filter-btn px-2.5 py-1 rounded-lg text-slate-400 hover:text-white";
        }
    });

    renderFilteredAlternatives();
}

function renderFilteredAlternatives() {
    const container = document.getElementById('premiumMatchesContainer');
    const lockNotice = document.getElementById('lockedAlternativesNotice');
    if (!container) return;

    const filtered = activeLeagueFilter === 'ALL' ? allPremiumMatches : allPremiumMatches.filter(m => m.competition.toLowerCase().includes(activeLeagueFilter.toLowerCase()));
    const isPro = currentUser && (currentUser.tier === 'PREMIUM' || currentUser.tier === 'PRO');

    const visibleList = isPro ? filtered : filtered.slice(0, 1);

    if (visibleList.length === 0) {
        container.innerHTML = `<div class="p-8 text-center text-slate-500 font-mono text-xs">Aucun match trouvé pour ce championnat.</div>`;
        if (lockNotice) lockNotice.classList.add('hidden');
        return;
    }

    container.innerHTML = visibleList.map(m => {
        const adv = m.advanced || {};
        return `
            <div class="bg-cardbg border border-slate-800 hover:border-amber-500/40 transition rounded-2xl p-5 space-y-4 shadow-xl">
                
                <!-- Match Header -->
                <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-3">
                    <div class="flex items-center gap-2 flex-wrap">
                        <span class="px-2.5 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30 text-[11px] font-mono font-bold uppercase">${m.competition}</span>
                        <span class="text-xs text-slate-400 font-mono">${m.date} • ${m.time}</span>
                        <span class="text-xs text-slate-500">• ${m.stadium}</span>
                    </div>
                    <div class="flex items-center gap-2">
                        <span class="text-xs font-mono text-slate-400">Indice de Lisibilité :</span>
                        <span class="text-xs font-mono font-black px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">${m.readability_score} / 100</span>
                    </div>
                </div>

                <!-- Match Teams & Key Indicators -->
                <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div>
                        <h3 class="text-lg font-black text-white">${m.match}</h3>
                        <p class="text-xs text-slate-300 mt-1 leading-relaxed">${m.tactical_analysis}</p>
                    </div>
                    <div class="bg-slate-950/80 p-3 rounded-xl border border-slate-800 text-center shrink-0 min-w-[150px]">
                        <div class="text-[10px] font-mono uppercase text-slate-400">xG Projeté (Dixon-Coles)</div>
                        <div class="text-xl font-mono font-black text-amber-400 mt-0.5">${m.xg_home} - ${m.xg_away}</div>
                        ${adv.top_score ? `<div class="text-[10px] font-mono text-slate-400 mt-1">Score : <strong class="text-white">${adv.top_score}</strong></div>` : ''}
                    </div>
                </div>

                <!-- Tactical Metrics Strip -->
                ${adv.ppda ? `
                    <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 p-2.5 bg-slate-950/90 rounded-xl border border-slate-800 text-xs font-mono">
                        <div class="border-r border-slate-800/80 pr-2">
                            <span class="text-[10px] text-slate-400 block uppercase">PPDA (Pressing)</span>
                            <span class="text-white font-bold">${adv.ppda.home} vs ${adv.ppda.away}</span>
                        </div>
                        <div class="border-r border-slate-800/80 pr-2">
                            <span class="text-[10px] text-slate-400 block uppercase">Field Tilt</span>
                            <span class="text-emerald-400 font-bold">${adv.field_tilt_pct.home}% - ${adv.field_tilt_pct.away}%</span>
                        </div>
                        <div class="border-r border-slate-800/80 pr-2">
                            <span class="text-[10px] text-slate-400 block uppercase">xPoints (xPts)</span>
                            <span class="text-amber-400 font-bold">${adv.xpts.home} vs ${adv.xpts.away}</span>
                        </div>
                        <div>
                            <span class="text-[10px] text-slate-400 block uppercase">Transition</span>
                            <span class="text-blue-400 font-bold">${adv.direct_speed_mps.home} m/s</span>
                        </div>
                    </div>
                ` : ''}

                <!-- 3 Actionable Picks Breakdown -->
                <div class="grid grid-cols-1 md:grid-cols-3 gap-3.5 pt-1">
                    
                    <!-- 1. Le Choix Blindé -->
                    <div class="p-3.5 rounded-xl bg-emerald-950/20 border border-emerald-500/40 space-y-2">
                        <div class="flex items-center justify-between">
                            <span class="text-xs font-mono uppercase text-emerald-400 font-bold">🛡️ Le Choix Blindé (Ultra-Sûr)</span>
                            <span class="text-[11px] font-mono font-black text-emerald-300">${m.safe_pick.win_prob_pct}%</span>
                        </div>
                        <div class="text-sm font-bold text-white">${m.safe_pick.market}</div>
                        <div class="text-xs font-mono text-slate-300">Cote : <strong class="text-emerald-400">@ ${m.safe_pick.odds.toFixed(2)}</strong></div>
                        <p class="text-[11px] text-slate-400 border-t border-slate-800/80 pt-1.5 leading-snug">${m.safe_pick.reason}</p>
                    </div>

                    <!-- 2. Le Choix Rentable -->
                    <div class="p-3.5 rounded-xl bg-blue-950/20 border border-blue-500/40 space-y-2">
                        <div class="flex items-center justify-between">
                            <span class="text-xs font-mono uppercase text-blue-400 font-bold">🎯 Choix Rentable (Value Pick)</span>
                            <span class="text-[11px] font-mono font-black text-blue-300">${m.value_pick.win_prob_pct}%</span>
                        </div>
                        <div class="text-sm font-bold text-white">${m.value_pick.market}</div>
                        <div class="flex items-center justify-between text-xs font-mono text-slate-300">
                            <span>Cote : <strong class="text-blue-400">@ ${m.value_pick.odds.toFixed(2)}</strong></span>
                            ${m.value_pick.ev_pct ? `<span class="text-emerald-400 font-bold font-mono">+${m.value_pick.ev_pct}% EV</span>` : ''}
                        </div>
                        <p class="text-[11px] text-slate-400 border-t border-slate-800/80 pt-1.5 leading-snug">${m.value_pick.reason}</p>
                    </div>

                    <!-- 3. Le Piège Détecté -->
                    <div class="p-3.5 rounded-xl bg-rose-950/20 border border-rose-500/40 space-y-2">
                        <div class="text-xs font-mono uppercase text-rose-400 font-bold">🚫 Le Piège Détecté</div>
                        <div class="text-sm font-bold text-rose-300">${m.trap_warning.trap_market}</div>
                        <p class="text-[11px] text-slate-300 leading-snug">${m.trap_warning.why_its_a_trap}</p>
                        <p class="text-[11px] text-rose-400 font-semibold border-t border-slate-800/80 pt-1.5 leading-snug">Conseil : ${m.trap_warning.recommendation}</p>
                    </div>

                </div>

            </div>
        `;
    }).join('');

    if (lockNotice) {
        if (!isPro && filtered.length > 1) {
            lockNotice.classList.remove('hidden');
        } else {
            lockNotice.classList.add('hidden');
        }
    }
}

// --- DATA INITIALIZATION ---
async function loadDailyCote2() {
    try {
        const res = await fetch('/api/v1/cote2/daily-ticket');
        const data = await res.json();

        const timeEl = document.getElementById('cote2Timestamp');
        if (timeEl) timeEl.innerText = data.generated_at;

        if (data.all_tickets) {
            allTicketsData = data.all_tickets;
        }
        if (data.premium_week_matches) {
            allPremiumMatches = data.premium_week_matches;
        }

        renderActiveTicket();
        renderFilteredAlternatives();

    } catch (err) {
        console.error("Error loading tickets & alternatives:", err);
    }
}

// --- SUBSCRIPTION CHECKOUT MODAL LOGIC ---
function openSubscriptionModal(defaultPlan = 'PREMIUM') {
    const modal = document.getElementById('subscriptionModal');
    if (!modal) return;
    setModalPlan(defaultPlan);
    modal.classList.remove('hidden');
}

function closeSubscriptionModal() {
    const modal = document.getElementById('subscriptionModal');
    if (modal) modal.classList.add('hidden');
    const resultBox = document.getElementById('modalResultBox');
    if (resultBox) resultBox.innerHTML = '';
}

function setModalPlan(plan) {
    activeModalPlan = plan;
    const btnSimple = document.getElementById('modalBtnPlanSimple');
    const btnPremium = document.getElementById('modalBtnPlanPremium');
    const titleEl = document.getElementById('modalPlanTitle');
    const amountEl = document.getElementById('modalAmountDisplay');

    if (plan === 'SIMPLE') {
        if (btnSimple) btnSimple.className = "py-2 px-3 rounded-lg text-xs font-bold transition bg-emerald-500 text-black shadow";
        if (btnPremium) btnPremium.className = "py-2 px-3 rounded-lg text-xs font-bold transition text-slate-400";
        if (titleEl) titleEl.innerText = "Activer l'Abonnement Simple (1 000 F)";
        if (amountEl) amountEl.innerText = "1 000 FCFA / mois";
    } else {
        if (btnPremium) btnPremium.className = "py-2 px-3 rounded-lg text-xs font-bold transition bg-gradient-to-r from-amber-500 to-yellow-400 text-black shadow";
        if (btnSimple) btnSimple.className = "py-2 px-3 rounded-lg text-xs font-bold transition text-slate-400";
        if (titleEl) titleEl.innerText = "Activer l'Abonnement Pro VIP (2 000 F)";
        if (amountEl) amountEl.innerText = "2 000 FCFA / mois";
    }
}

async function submitSubscriptionCheckout() {
    const provider = document.getElementById('modalProviderSelect').value;
    const contact = document.getElementById('modalCustomerContact').value.trim();
    const resultBox = document.getElementById('modalResultBox');
    const submitBtn = document.getElementById('modalSubmitBtn');

    if (!contact) {
        alert("Veuillez renseigner votre numéro Mobile Money ou email.");
        return;
    }

    const planPriceText = activeModalPlan === 'SIMPLE' ? "1 000 FCFA" : "2 000 FCFA";
    resultBox.innerHTML = `<div class="p-3 bg-slate-950 rounded-xl border border-slate-800 text-slate-400 font-mono">Connexion sécurisée avec l'opérateur ${provider.toUpperCase()} pour ${planPriceText}...</div>`;
    submitBtn.disabled = true;

    try {
        const userEmail = currentUser ? currentUser.email : contact;
        const res = await fetch('/api/v1/payments/checkout', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                customer_phone_or_email: contact,
                provider_id: provider,
                plan_tier: activeModalPlan,
                user_email: userEmail,
                currency: "FCFA"
            })
        });
        const data = await res.json();

        // Simulate instant webhook confirmation and database upgrade
        const confirmRes = await fetch(`/api/v1/payments/simulate-webhook/${data.transaction_id}?plan_tier=${activeModalPlan}&user_email=${encodeURIComponent(userEmail)}`, { method: 'POST' });
        const confirmData = await confirmRes.json();

        if (!currentUser) {
            currentUser = { email: contact, is_guest: false };
        }
        currentUser.tier = activeModalPlan === 'SIMPLE' ? 'SIMPLE' : 'PREMIUM';
        currentUser.is_guest = false;
        currentUser.trial_days_remaining = 0;
        if (currentUser.tier === 'PREMIUM') {
            currentUser.analyses_remaining = 9999;
            currentUser.max_analyses = 9999;
            currentUser.max_alternatives = 5;
        } else {
            currentUser.analyses_remaining = 5;
            currentUser.max_analyses = 5;
            currentUser.max_alternatives = 1;
        }
        localStorage.setItem('duosecur_user', JSON.stringify(currentUser));

        resultBox.innerHTML = `
            <div class="p-4 bg-emerald-950/40 border border-emerald-500/50 rounded-xl text-emerald-300 space-y-2 mt-2">
                <div class="font-black text-sm flex items-center gap-1.5 text-white">
                    <span>✅ Paiement Confirmé avec Succès !</span>
                </div>
                <div class="text-xs">
                    Formule activée : <strong class="text-amber-300">${confirmData.plan_name}</strong>
                </div>
                <div class="text-xs text-slate-300">
                    Débit de <strong>${data.amount.toLocaleString()} FCFA</strong> effectué via <strong>${data.provider}</strong>.
                </div>
                <div class="text-[11px] font-mono text-emerald-400 pt-1 border-t border-emerald-500/30">
                    Accès actif pour 30 jours sur votre compte : ${contact}
                </div>
            </div>
        `;

        submitBtn.disabled = false;
        updateUIForUser();

    } catch (err) {
        resultBox.innerHTML = `<div class="p-3 bg-rose-950/40 border border-rose-500/40 rounded-xl text-rose-300 text-xs">Erreur lors de la validation du paiement.</div>`;
        submitBtn.disabled = false;
    }
}

// --- SECTION MANUELLE DES ÉQUIPES : CALCUL AVEC TOUS LES INDICATEURS AVANCÉS ---
function setTeams(home, away) {
    document.getElementById('inputHomeTeam').value = home;
    document.getElementById('inputAwayTeam').value = away;
    runCustomAnalysis();
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
    const btn = document.getElementById('btnRunAnalysis');
    if (!output) return;

    output.innerHTML = `<div class="p-8 text-center text-xs font-mono text-slate-400 space-y-2">
        <div class="animate-spin inline-block w-6 h-6 border-2 border-emerald-500 border-t-transparent rounded-full"></div>
        <div>Modélisation bivariée Dixon-Coles & calcul de tous les indicateurs avancés pour ${home} vs ${away}...</div>
    </div>`;
    if (btn) btn.disabled = true;

    try {
        const userEmail = currentUser ? currentUser.email : "guest";
        const res = await fetch('/api/v1/analyzer/evaluate-match', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                home_team: home,
                away_team: away,
                user_email: userEmail
            })
        });
        const data = await res.json();
        if (btn) btn.disabled = false;

        // If Quota exceeded for Simple or Trial user
        if (data.quota_exceeded) {
            output.innerHTML = `
                <div class="p-6 rounded-2xl bg-amber-950/30 border border-amber-500/50 space-y-3 text-center">
                    <div class="text-2xl">⚠️</div>
                    <h3 class="text-base font-black text-white">Quota de 5 analyses atteint pour aujourd'hui</h3>
                    <p class="text-xs text-slate-300 max-w-md mx-auto">
                        La formule Simple autorise <strong>5 analyses par jour</strong> sur la section manuelle. Passez à la formule <strong>Pro (2 000 FCFA / mois)</strong> pour analyser autant de matchs que vous le souhaitez en illimité !
                    </p>
                    <div class="pt-1">
                        <button onclick="openSubscriptionModal('PREMIUM')" class="px-5 py-2.5 bg-gradient-to-r from-amber-500 to-yellow-400 text-black font-black text-xs rounded-xl shadow-lg shadow-amber-500/20">
                            👑 Passer au Pack Pro pour l'Illimité (2 000 F) →
                        </button>
                    </div>
                </div>
            `;
            return;
        }

        // Update remaining analyses in UI
        if (currentUser && !data.is_unlimited) {
            currentUser.analyses_remaining = data.analyses_remaining;
            localStorage.setItem('duosecur_user', JSON.stringify(currentUser));
            const quotaDisplay = document.getElementById('quotaDisplayTag');
            if (quotaDisplay) quotaDisplay.innerText = `${data.analyses_remaining} / 5 analyses restantes`;
        }

        const badgeColor = data.verdict_status === 'SAFE_GREEN' ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40' : (data.verdict_status === 'BALANCED_YELLOW' ? 'bg-amber-500/20 text-amber-300 border-amber-500/40' : 'bg-rose-500/20 text-rose-300 border-rose-500/40');
        const adv = data.advanced_metrics || {};
        const probs = data.true_probabilities || {};
        const fair = data.fair_odds || {};
        const topScores = data.top_exact_scores || {};

        output.innerHTML = `
            <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-6 shadow-2xl">
                
                <!-- 1. Header Verdict Summary -->
                <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
                    <div>
                        <div class="flex items-center gap-2 flex-wrap">
                            <span class="text-xs font-mono px-2 py-0.5 rounded border font-bold ${badgeColor}">${data.verdict_badge}</span>
                            <span class="text-xs text-slate-400 font-mono">Indice de Lisibilité : <strong class="text-white">${data.readability_score} / 100</strong></span>
                            <span class="text-xs text-slate-500 font-mono">• Modèle Dixon-Coles (ρ = -0.11)</span>
                        </div>
                        <h3 class="text-xl font-black text-white mt-1.5">${data.home_team} vs ${data.away_team}</h3>
                        <p class="text-xs text-slate-300 mt-1 leading-relaxed">${data.verdict_desc}</p>
                    </div>
                    <div class="bg-slate-950 p-3 rounded-xl border border-slate-800 text-center shrink-0 min-w-[150px]">
                        <div class="text-[10px] font-mono uppercase text-slate-400">Score le plus probable</div>
                        <div class="text-2xl font-black text-amber-400 font-mono mt-0.5">${data.most_likely_score || '1-0'}</div>
                        <div class="text-[10px] font-mono text-emerald-400 mt-0.5">xG : ${adv.xg ? adv.xg.home + ' - ' + adv.xg.away : ''}</div>
                    </div>
                </div>

                <!-- 2. Dashboard des Indicateurs Avancés (Metrics Grid) -->
                <div>
                    <h4 class="text-xs font-mono uppercase text-slate-400 font-bold mb-2.5 flex items-center gap-1.5">
                        <span>📊</span>
                        <span>Indicateurs Tactiques & Physiques Avancés</span>
                    </h4>
                    <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2.5 text-xs font-mono">
                        <div class="p-3 bg-slate-950 rounded-xl border border-slate-800">
                            <span class="text-[10px] text-slate-400 block uppercase">xG (Hors Penalty)</span>
                            <div class="text-sm font-black text-white mt-0.5">${adv.npxg ? adv.npxg.home + ' vs ' + adv.npxg.away : '-'}</div>
                            <span class="text-[9px] text-slate-500">npxG généré</span>
                        </div>
                        <div class="p-3 bg-slate-950 rounded-xl border border-slate-800">
                            <span class="text-[10px] text-slate-400 block uppercase">Solidité (xGA)</span>
                            <div class="text-sm font-black text-emerald-400 mt-0.5">${adv.xga ? adv.xga.home + ' vs ' + adv.xga.away : '-'}</div>
                            <span class="text-[9px] text-slate-500">xG concédé/m</span>
                        </div>
                        <div class="p-3 bg-slate-950 rounded-xl border border-slate-800">
                            <span class="text-[10px] text-slate-400 block uppercase">PPDA (Pressing)</span>
                            <div class="text-sm font-black text-amber-400 mt-0.5">${adv.ppda ? adv.ppda.home + ' vs ' + adv.ppda.away : '-'}</div>
                            <span class="text-[9px] text-slate-500">Pression haute</span>
                        </div>
                        <div class="p-3 bg-slate-950 rounded-xl border border-slate-800">
                            <span class="text-[10px] text-slate-400 block uppercase">Field Tilt</span>
                            <div class="text-sm font-black text-cyan-400 mt-0.5">${adv.field_tilt_pct ? adv.field_tilt_pct.home + '% - ' + adv.field_tilt_pct.away + '%' : '-'}</div>
                            <span class="text-[9px] text-slate-500">Dernier tiers</span>
                        </div>
                        <div class="p-3 bg-slate-950 rounded-xl border border-slate-800">
                            <span class="text-[10px] text-slate-400 block uppercase">Points (xPts)</span>
                            <div class="text-sm font-black text-purple-400 mt-0.5">${adv.xpts ? adv.xpts.home + ' vs ' + adv.xpts.away : '-'}</div>
                            <span class="text-[9px] text-slate-500">Points attendus</span>
                        </div>
                        <div class="p-3 bg-slate-950 rounded-xl border border-slate-800">
                            <span class="text-[10px] text-slate-400 block uppercase">Transition</span>
                            <div class="text-sm font-black text-blue-400 mt-0.5">${adv.direct_speed_mps ? adv.direct_speed_mps.home + ' m/s' : '-'}</div>
                            <span class="text-[9px] text-slate-500">Vitesse verticale</span>
                        </div>
                    </div>
                </div>

                <!-- 3. Tableau des Probabilités Réelles & Cotes Équitables Pures (Zero Vig) -->
                <div>
                    <h4 class="text-xs font-mono uppercase text-slate-400 font-bold mb-2.5 flex items-center gap-1.5">
                        <span>🎯</span>
                        <span>Probabilités Réelles & Cotes Équitables Pures (Sans Marge Bookmaker)</span>
                    </h4>
                    <div class="overflow-x-auto bg-slate-950 rounded-xl border border-slate-800 p-2">
                        <table class="w-full text-left text-xs font-mono text-slate-300">
                            <thead class="border-b border-slate-800 text-[10px] text-slate-400 uppercase">
                                <tr>
                                    <th class="py-2 px-3">Marché</th>
                                    <th class="py-2 px-3 text-center">Probabilité Réelle</th>
                                    <th class="py-2 px-3 text-center">Cote Équitable Pure (Fair)</th>
                                    <th class="py-2 px-3 text-right">Rôle Recommandé</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-slate-800/60 font-sans">
                                <tr>
                                    <td class="py-2.5 px-3 font-bold text-white">Victoire Domicile (1)</td>
                                    <td class="py-2.5 px-3 text-center font-mono text-emerald-400 font-bold">${probs.home_win_pct}%</td>
                                    <td class="py-2.5 px-3 text-center font-mono font-bold text-white">@ ${fair.home ? fair.home.toFixed(2) : '-'}</td>
                                    <td class="py-2.5 px-3 text-right text-xs text-slate-400">${probs.home_win_pct >= 55 ? 'Favori Mathématique' : 'Incertain'}</td>
                                </tr>
                                <tr>
                                    <td class="py-2.5 px-3 font-bold text-white">Match Nul (X)</td>
                                    <td class="py-2.5 px-3 text-center font-mono text-slate-300">${probs.draw_pct}%</td>
                                    <td class="py-2.5 px-3 text-center font-mono font-bold text-white">@ ${fair.draw ? fair.draw.toFixed(2) : '-'}</td>
                                    <td class="py-2.5 px-3 text-right text-xs text-slate-400">Score Serré</td>
                                </tr>
                                <tr>
                                    <td class="py-2.5 px-3 font-bold text-white">Victoire Extérieur (2)</td>
                                    <td class="py-2.5 px-3 text-center font-mono text-blue-400">${probs.away_win_pct}%</td>
                                    <td class="py-2.5 px-3 text-center font-mono font-bold text-white">@ ${fair.away ? fair.away.toFixed(2) : '-'}</td>
                                    <td class="py-2.5 px-3 text-right text-xs text-slate-400">${probs.away_win_pct >= 55 ? 'Favori Mathématique' : 'Outsider'}</td>
                                </tr>
                                <tr>
                                    <td class="py-2.5 px-3 font-bold text-emerald-300">Double Chance 1X</td>
                                    <td class="py-2.5 px-3 text-center font-mono text-emerald-400 font-black">${probs.dc_1x_pct}%</td>
                                    <td class="py-2.5 px-3 text-center font-mono font-bold text-emerald-300">@ ${fair.dc_1x ? fair.dc_1x.toFixed(2) : '-'}</td>
                                    <td class="py-2.5 px-3 text-right text-xs text-emerald-400 font-bold">${probs.dc_1x_pct >= 75 ? '💎 Couverture Optimale' : 'Risqué'}</td>
                                </tr>
                                <tr>
                                    <td class="py-2.5 px-3 font-bold text-white">Plus de 1.5 Buts (Over 1.5)</td>
                                    <td class="py-2.5 px-3 text-center font-mono text-amber-400 font-bold">${probs.over_15_pct}%</td>
                                    <td class="py-2.5 px-3 text-center font-mono font-bold text-white">@ ${fair.over_15 ? fair.over_15.toFixed(2) : '-'}</td>
                                    <td class="py-2.5 px-3 text-right text-xs text-slate-400">${probs.over_15_pct >= 75 ? 'Blindé Anti-Aléa' : 'Modéré'}</td>
                                </tr>
                                <tr>
                                    <td class="py-2.5 px-3 font-bold text-white">Plus de 2.5 Buts (Over 2.5)</td>
                                    <td class="py-2.5 px-3 text-center font-mono text-white">${probs.over_25_pct}%</td>
                                    <td class="py-2.5 px-3 text-center font-mono font-bold text-white">@ ${fair.over_25 ? fair.over_25.toFixed(2) : '-'}</td>
                                    <td class="py-2.5 px-3 text-right text-xs text-slate-400">Match Ouvert</td>
                                </tr>
                                <tr>
                                    <td class="py-2.5 px-3 font-bold text-white">Les Deux Équipes Marquent (BTTS)</td>
                                    <td class="py-2.5 px-3 text-center font-mono text-cyan-400">${probs.btts_yes_pct}%</td>
                                    <td class="py-2.5 px-3 text-center font-mono font-bold text-white">@ ${fair.btts_yes ? fair.btts_yes.toFixed(2) : '-'}</td>
                                    <td class="py-2.5 px-3 text-right text-xs text-slate-400">${probs.btts_yes_pct >= 55 ? 'Attaques Actives' : 'Fermé'}</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- 4. Matrice des Scores Exacts les Plus Probables -->
                ${Object.keys(topScores).length > 0 ? `
                    <div>
                        <h4 class="text-xs font-mono uppercase text-slate-400 font-bold mb-2 flex items-center gap-1.5">
                            <span>🎲</span>
                            <span>Matrice des Scores les Plus Probables (Poisson Bivarié)</span>
                        </h4>
                        <div class="flex flex-wrap gap-2 text-xs font-mono">
                            ${Object.entries(topScores).map(([score, prob]) => `
                                <div class="px-3 py-1.5 bg-slate-950 rounded-lg border border-slate-800 flex items-center gap-2">
                                    <span class="font-bold text-white">${score}</span>
                                    <span class="text-emerald-400">${prob}%</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}

                <!-- 5. 3 Actionable Picks Breakdown -->
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4 pt-1">
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
                        <div class="flex items-center justify-between">
                            <span class="text-xs font-mono uppercase text-blue-400 font-bold">🎯 Choix Rentable (Value Pick)</span>
                            ${data.value_pick.ev_pct ? `<span class="text-xs font-mono font-bold text-emerald-400">+${data.value_pick.ev_pct}% EV</span>` : ''}
                        </div>
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

                <!-- 6. Capital Sizing & Discipline Footer -->
                <div class="p-3.5 bg-slate-950 rounded-xl border border-slate-800 text-xs text-slate-300 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                    <span class="font-mono text-emerald-400 font-bold">⚖️ ${data.advice_rule}</span>
                    <span class="text-[11px] text-slate-400">
                        ${data.is_unlimited ? 'Analyses : Illimitées (Pro)' : `Analyses restantes : <strong class="text-white">${data.analyses_remaining} / 5</strong>`}
                    </span>
                </div>
            </div>
        `;

    } catch (err) {
        if (output) output.innerHTML = `<div class="p-4 text-center text-xs text-rose-400">Erreur lors de l'analyse du match.</div>`;
        if (btn) btn.disabled = false;
    }
}

// --- TAB SWITCHER & READABLE SCAN ---
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

window.addEventListener('DOMContentLoaded', () => {
    initUserSession();
    loadDailyCote2();
    scanMarketReadability();
});
