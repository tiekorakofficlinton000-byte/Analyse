#!/usr/bin/env python3
"""
DuoSecur Pro - 100% PURE PYTHON INTERACTIVE TERMINAL
Pure mathematical decision engine.
"""

import sys
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(base_dir, "lib"))
sys.path.insert(0, os.path.join(base_dir, "backend"))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt

from app.modules.quant_engine.cote2_builder import generate_daily_cote_2
from app.modules.quant_engine.match_analyzer import analyze_match_on_demand
from app.modules.quant_engine.readable_picks_engine import evaluate_market_readability
from app.modules.quant_engine.bankroll_mentor import simulate_compound_growth
from app.modules.billing.payment_gateway import initiate_subscription_payment, confirm_subscription_payment

console = Console()


def show_header():
    console.clear()
    title = Text("DUOSECUR PRO — TERMINAL QUANTITATIF 100% PYTHON", style="bold white on blue")
    subtitle = Text("« On ne cherche pas à gagner gros, on cherche à ne pas perdre. »", style="italic green")
    console.print(Panel.fit(f"{title}\n{subtitle}", border_style="cyan"))


def menu_cote2():
    show_header()
    console.print("\n[bold cyan]🎯 CHARGEMENT DU TICKET COTE 2.00 SÉCURISÉE DU JOUR...[/bold cyan]\n")
    ticket = generate_daily_cote_2()

    table = Table(title=f"Ticket Cote {ticket['combined_odds']:.2f} — Fiabilité Conjointe : {ticket['joint_probability_pct']}%", border_style="green")
    table.add_column("#", style="bold yellow", width=3)
    table.add_column("Match & Compétition", style="white", width=30)
    table.add_column("Sélection Recommandée", style="bold green", width=32)
    table.add_column("Cote", style="bold cyan", justify="right", width=8)
    table.add_column("Pourquoi ce choix", style="dim white", width=35)
    table.add_column("Piège Évité", style="bold red", width=30)

    for i, leg in enumerate(ticket["legs"], 1):
        table.add_row(
            str(i),
            f"{leg['match']}\n[dim]{leg['competition']} ({leg['time']})[/dim]",
            leg["selection"],
            f"{leg['odds']:.2f}",
            leg["why_this_pick"],
            f"🚫 {leg['trap_avoided']}"
        )

    console.print(table)
    console.print(Panel(
        f"[bold yellow]⚖️ RÈGLE DE GESTION :[/bold yellow] Misez exactement [bold green]2.5%[/bold green] de votre bankroll.\n"
        f"Exemple sur 50 000 FCFA : misez [bold green]1 250 FCFA[/bold green] pour chercher [bold green]2 550 FCFA[/bold green].\n"
        f"Option Solo Alternative : [cyan]{ticket['alternative_single']['match']} — {ticket['alternative_single']['selection']} @ {ticket['alternative_single']['odds']}[/cyan]",
        border_style="yellow"
    ))
    Prompt.ask("\n[dim]Appuyez sur Entrée pour revenir au menu...[/dim]")


def menu_analyze_match():
    show_header()
    console.print("\n[bold cyan]🔍 ANALYSEUR LIBRE DE MATCH & VERDICT MATHÉMATIQUE[/bold cyan]\n")
    home = Prompt.ask("Entrez l'équipe à domicile (ex: Real Madrid, ASEC, Man City)", default="Real Madrid")
    away = Prompt.ask("Entrez l'équipe à l'extérieur (ex: Villarreal, Africa Sports, Chelsea)", default="Villarreal")

    console.print(f"\n[dim]Calcul des probabilités Dixon-Coles pour {home} vs {away}...[/dim]\n")
    res = analyze_match_on_demand(home, away)

    badge_color = "green" if res["verdict_status"] == "SAFE_GREEN" else ("yellow" if res["verdict_status"] == "BALANCED_YELLOW" else "red")
    
    console.print(Panel(
        f"[bold {badge_color}]{res['verdict_badge']} — Indice de Lisibilité : {res['readability_score']}/100[/bold {badge_color}]\n"
        f"[bold white]{res['home_team']} vs {res['away_team']}[/bold white]\n"
        f"[dim]{res['verdict_desc']}[/dim]\n"
        f"Score le plus probable : [bold cyan]{round(res['projected_xg']['home'])} - {round(res['projected_xg']['away'])}[/bold cyan] (xG : {res['projected_xg']['home']} vs {res['projected_xg']['away']})",
        border_style=badge_color,
        title="VERDICT GLOBAL DU MODÈLE"
    ))

    table = Table(title="OPTIONS RECOMMANDÉES PAR LE MODÈLE", border_style="cyan")
    table.add_column("Type de Choix", style="bold yellow", width=25)
    table.add_column("Sélection", style="bold white", width=35)
    table.add_column("Cote Estimée", style="bold green", justify="center", width=14)
    table.add_column("Fiabilité", style="bold cyan", justify="center", width=12)
    table.add_column("Analyse Mathématique", style="dim white", width=35)

    table.add_row(
        "🛡️ Choix Blindé (Le Plus Sûr)",
        res["safe_pick"]["title"],
        f"@{res['safe_pick']['estimated_odds']}",
        f"{res['safe_pick']['win_probability_pct']}%",
        res["safe_pick"]["reason"]
    )
    table.add_row(
        "🎯 Choix Équilibré (~2.00)",
        res["value_pick"]["title"],
        f"@{res['value_pick']['estimated_odds']}",
        f"{res['value_pick']['win_probability_pct']}%",
        res["value_pick"]["reason"]
    )

    console.print(table)

    console.print(Panel(
        f"[bold red]⚠️ LE PIÈGE DU BOOKMAKER À ÉVITER :[/bold red] [bold white]{res['trap_warning']['trap_market']}[/bold white]\n"
        f"[dim]{res['trap_warning']['why_its_a_trap']}[/dim]\n"
        f"[bold yellow]👉 Conseil :[/bold yellow] {res['trap_warning']['recommendation']}",
        border_style="red"
    ))

    Prompt.ask("\n[dim]Appuyez sur Entrée pour revenir au menu...[/dim]")


def menu_market_ranking():
    show_header()
    console.print("\n[bold cyan]💎 CLASSEMENT DES MARCHÉS PAR INDICE DE LISIBILITÉ[/bold cyan]\n")
    home = Prompt.ask("Équipe Domicile", default="Real Madrid")
    away = Prompt.ask("Équipe Extérieur", default="Villarreal")

    data = evaluate_market_readability(home, away)

    table = Table(title=f"Hiérarchie des Marchés pour {home} vs {away}", border_style="cyan")
    table.add_column("Pari", style="bold white", width=35)
    table.add_column("Cote", style="bold green", justify="center", width=8)
    table.add_column("Probabilité", style="bold cyan", justify="center", width=12)
    table.add_column("Lisibilité", style="bold yellow", justify="center", width=12)
    table.add_column("Statut / Rôle", style="white", width=35)

    for m in data["all_ranked_markets"]:
        color = "green" if m["badge_class"] == "diamond" else ("blue" if m["badge_class"] == "gold" else ("yellow" if m["badge_class"] == "silver" else "red"))
        table.add_row(
            m["name"],
            f"{m['odds']:.2f}",
            f"{m['win_prob_pct']}%",
            f"{m['readability_score']}/100",
            f"[{color}]{m['tier_badge']}[/{color}]\n[dim]{m['recommended_role']}[/dim]"
        )

    console.print(table)
    console.print(Panel(
        f"[bold green]💡 RÈGLE D'OR :[/bold green] {data['rule_of_thumb']}",
        border_style="green"
    ))
    Prompt.ask("\n[dim]Appuyez sur Entrée pour revenir au menu...[/dim]")


def menu_mentor_compound():
    show_header()
    console.print("\n[bold cyan]🛡️ MENTOR DE CAPITAL : « MÊME AVEC PEU, ON PEUT RÉUSSIR »[/bold cyan]\n")
    cap_str = Prompt.ask("Capital de départ en FCFA (ex: 10000, 25000, 50000)", default="25000")
    days_str = Prompt.ask("Durée en jours (30, 60, 90)", default="60")

    cap = float(cap_str)
    days = int(days_str)

    res = simulate_compound_growth(initial_capital=cap, currency="FCFA", days=days, stake_pct=2.5, win_rate_pct=66.0)

    table = Table(title=f"Tableau de Marche sur {days} Jours (Mise 2.5% sur Cote 2.00)", border_style="green")
    table.add_column("Étape", style="bold yellow", width=12)
    table.add_column("Capital Discipliné", style="bold green", justify="right", width=22)
    table.add_column("Mise du Jour (2.5%)", style="bold cyan", justify="right", width=20)
    table.add_column("Gain Net Total", style="white", justify="right", width=18)
    table.add_column("Parieur Combinés (Perte)", style="bold red", justify="right", width=25)

    for p in res["trajectory"]:
        table.add_row(
            f"Jour {p['day']}",
            f"{p['quant_capital']:,.0f} FCFA",
            f"{p['daily_stake']:,.0f} FCFA",
            f"+{p['growth_pct']}%",
            f"{p['casual_capital']:,.0f} FCFA"
        )

    console.print(table)
    console.print(Panel(
        f"[bold green]RÉSULTAT FINAL :[/bold green] Capital initial de [white]{cap:,.0f} FCFA[/white] ➡️ [bold green]{res['final_capital']:,.0f} FCFA[/bold green] (+{res['roi_pct']}% net).\n"
        f"[bold red]PARIEUR SANS MÉTHODE :[/bold red] A dépensé son argent sur des combinés impossibles et se retrouve à [bold red]0 FCFA[/bold red].",
        border_style="green"
    ))
    Prompt.ask("\n[dim]Appuyez sur Entrée pour revenir au menu...[/dim]")


def menu_mobile_money():
    show_header()
    console.print("\n[bold cyan]💳 SIMULATEUR D'ENCAISSEMENT ABONNEMENTS (MOBILE MONEY & STRIPE)[/bold cyan]\n")
    phone = Prompt.ask("Numéro de téléphone de l'abonné", default="+225 07 00 00 00 00")
    provider = Prompt.ask("Opérateur", choices=["wave", "orange_money", "mtn_momo", "stripe"], default="wave")

    console.print(f"\n[dim]Création de l'intention de paiement de 15 000 FCFA via {provider}...[/dim]")
    intent = initiate_subscription_payment(phone, provider, plan_tier="PRO", currency="FCFA")
    
    console.print(f"[bold yellow]ID Transaction :[/bold yellow] {intent['transaction_id']}")
    console.print(f"[bold yellow]Instructions :[/bold yellow] {intent['instructions']}")

    Prompt.ask("\n[dim]Appuyez sur Entrée pour simuler la validation du paiement par l'opérateur...[/dim]")
    confirmed = confirm_subscription_payment(intent["transaction_id"])

    console.print(Panel(
        f"[bold green]✅ PAIEMENT DE 15 000 FCFA VALIDÉ ![/bold green]\n"
        f"Statut : {confirmed['status']}\n"
        f"Abonnement activé : [bold cyan]{confirmed['activated_tier']} (30 jours)[/bold cyan]\n"
        f"L'abonné a été ajouté automatiquement à la liste des 1 000 membres payants.",
        border_style="green"
    ))
    Prompt.ask("\n[dim]Appuyez sur Entrée pour revenir au menu...[/dim]")


def main():
    while True:
        show_header()
        console.print("[bold yellow]MENU PRINCIPAL — DUOSECUR PRO (100% PYTHON)[/bold yellow]\n")
        console.print("  [bold green]1.[/bold green] 🎯 Afficher le Ticket Cote 2.00 Sécurisée du Jour")
        console.print("  [bold green]2.[/bold green] 🔍 Analyser N'importe Quel Match à la Demande (Verdict & Pièges)")
        console.print("  [bold green]3.[/bold green] 💎 Classer les Marchés par Lisibilité (Choix Diamant vs Loterie)")
        console.print("  [bold green]4.[/bold green] 🛡️ Mentor de Capital (Simulation Intérêts Composés sur 60 jours)")
        console.print("  [bold green]5.[/bold green] 💳 Simuler un Encaissement Mobile Money (Wave / Orange Money)")
        console.print("  [bold red]0.[/bold red] 🚪 Quitter le Terminal\n")

        choice = Prompt.ask("Votre choix", choices=["1", "2", "3", "4", "5", "0"], default="1")

        if choice == "1":
            menu_cote2()
        elif choice == "2":
            menu_analyze_match()
        elif choice == "3":
            menu_market_ranking()
        elif choice == "4":
            menu_mentor_compound()
        elif choice == "5":
            menu_mobile_money()
        elif choice == "0":
            console.print("\n[bold cyan]Au revoir ! Continuez à protéger votre capital.[/bold cyan]\n")
            sys.exit(0)


if __name__ == "__main__":
    main()
