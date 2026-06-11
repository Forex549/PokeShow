"""Run pairings of AI strategies from run_simulation.py.

Usage:
    py -3 scripts\run_all_ias.py          # prompts for mode (all-vs-all or one-vs-one)

Saves results to results/ia_pairings.json
"""
import os
import sys
import json
import random
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import run_simulation as rs
from src.engine.models.entrenador import Entrenador
from src.engine.models.pokemon import Pokemon
from src.engine.models.battle import Battle


IA_OPTIONS = [
    ("Aleatorio", rs.estrategia_ia_random),
    ("Mejor", rs.estrategia_ia_best_option),
    ("Minimax2", rs.estrategia_ia_minimax_nivel2),
    ("Minimax3", rs.estrategia_ia_minimax_nivel3),
    ("Minimax4", rs.estrategia_ia_minimax_nivel4),
]

RESULTS_DIR = os.path.join(BASE_DIR, "results")
os.makedirs(RESULTS_DIR, exist_ok=True)


def build_default_team(name_prefix="P1"):
    # small helper to build the default 4-pokemon team used elsewhere
    return [
        Pokemon("garchomp", rs.pokedex["garchomp"], rs.moves_db),
        Pokemon("lucario", rs.pokedex["lucario"], rs.moves_db),
        Pokemon("gengar", rs.pokedex["gengar"], rs.moves_db),
        Pokemon("swampert", rs.pokedex["swampert"], rs.moves_db),
    ]


TEAM_DEFS = {
    "Default": ["garchomp", "lucario", "gengar", "swampert"],
    "Fast Priority": ["zeraora", "garchomp", "mamoswine", "scizor"],
    "Balanced": ["garchomp", "metagross", "lucario", "swampert"],
    "Offensive": ["baxcalibur", "zeraora", "garchomp", "lucario"],
}


def build_team_from_species(species_list):
    return [Pokemon(name, rs.pokedex[name], rs.moves_db) for name in species_list]


def run_match(ia1, ia2, team_a_species, team_b_species, seed=None):
    if seed is None:
        seed = random.randint(0, 2**30)
    random.seed(seed)

    p1 = Entrenador("IA1", build_team_from_species(team_a_species))
    p2 = Entrenador("IA2", build_team_from_species(team_b_species))
    b = Battle(p1, p2)
    b.start_battle(ia1, ia2)
    winner = b.get_winner()
    return winner


def main():
    print("Seleccione modo:")
    print("1. All vs All (todas las combinaciones)")
    print("2. Un par específico")
    mode = input("Modo (1-2): ").strip()
    if mode not in ("1", "2"):
        print("Modo inválido")
        return

    ia_names = [name for name, _ in IA_OPTIONS]

    pairings = []
    if mode == "1":
        for i in range(len(IA_OPTIONS)):
            for j in range(len(IA_OPTIONS)):
                pairings.append((i, j))
    else:
        for idx, (name, _) in enumerate(IA_OPTIONS, start=1):
            print(f"{idx}. {name}")
        a = int(input("Selecciona IA A (número): ")) - 1
        b = int(input("Selecciona IA B (número): ")) - 1
        pairings.append((a, b))

    # Team selection
    print("\nEquipos disponibles:")
    team_keys = list(TEAM_DEFS.keys())
    for idx, k in enumerate(team_keys, start=1):
        print(f"{idx}. {k}: {', '.join(TEAM_DEFS[k])}")
    print(f"{len(team_keys)+1}. ALL TEAMS (ejecutar todas las combinaciones)")
    choice_a = int(input("Selecciona equipo para IA A (número): ")) - 1
    choice_b = int(input("Selecciona equipo para IA B (número): ")) - 1

    all_team_combinations = False
    teams_a = []
    teams_b = []
    if choice_a == len(team_keys):
        teams_a = [TEAM_DEFS[k] for k in team_keys]
        all_team_combinations = True
    else:
        teams_a = [TEAM_DEFS[team_keys[choice_a]]]

    if choice_b == len(team_keys):
        teams_b = [TEAM_DEFS[k] for k in team_keys]
        all_team_combinations = True
    else:
        teams_b = [TEAM_DEFS[team_keys[choice_b]]]

    n = int(input("Cuántas partidas por emparejamiento? (ej: 10): "))

    results = defaultdict(lambda: {"winsA": 0, "winsB": 0, "draws": 0, "matches": 0})

    for ia_idx_a, ia_idx_b in pairings:
        name_a, func_a = IA_OPTIONS[ia_idx_a]
        name_b, func_b = IA_OPTIONS[ia_idx_b]
        key_base = f"{name_a}_vs_{name_b}"
        for team_a in teams_a:
            for team_b in teams_b:
                key = f"{key_base}__{team_a[0]}_{team_b[0]}"
                print(f"Ejecutando {n} partidas: {key}")
                for i in range(n):
                    winner = run_match(func_a, func_b, team_a, team_b)
                    results[key]["matches"] += 1
                    if winner is None:
                        results[key]["draws"] += 1
                    elif winner == "IA1":
                        results[key]["winsA"] += 1
                    elif winner == "IA2":
                        results[key]["winsB"] += 1
                # write partial results to disk after each pairing
                with open(os.path.join(RESULTS_DIR, "ia_pairings.json"), "w") as f:
                    json.dump(results, f, indent=2)

    print("Hecho. Resultados guardados en results/ia_pairings.json")


if __name__ == '__main__':
    main()
