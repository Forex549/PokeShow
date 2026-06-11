"""Quick non-interactive runner to produce a sample results file.

This runs N matches of Aleatorio vs Minimax4 with the Default team and writes results to results/ia_pairings.json
"""
import os
import json
from collections import defaultdict
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
import run_simulation as rs
from src.engine.models.entrenador import Entrenador
from src.engine.models.pokemon import Pokemon
from src.engine.models.battle import Battle
import random

RESULTS_PATH = os.path.join(BASE_DIR, "results", "ia_pairings.json")

TEAM = ["garchomp", "lucario", "gengar", "swampert"]

def build_team(species):
    return [Pokemon(name, rs.pokedex[name], rs.moves_db) for name in species]


def run_match(ia1, ia2, team_a_species, team_b_species, seed=None):
    if seed is None:
        seed = random.randint(0, 2**30)
    random.seed(seed)
    p1 = Entrenador("IA1", build_team(team_a_species))
    p2 = Entrenador("IA2", build_team(team_b_species))
    b = Battle(p1, p2)
    b.start_battle(ia1, ia2)
    return b.get_winner()


def main():
    ia1 = rs.estrategia_ia_random
    ia2 = rs.estrategia_ia_minimax_nivel4
    key = "Aleatorio_vs_Minimax4__Default_Default"
    results = defaultdict(lambda: {"winsA": 0, "winsB": 0, "draws": 0, "matches": 0})
    N = 3
    for i in range(N):
        winner = run_match(ia1, ia2, TEAM, TEAM)
        results[key]["matches"] += 1
        if winner is None:
            results[key]["draws"] += 1
        elif winner == "IA1":
            results[key]["winsA"] += 1
        elif winner == "IA2":
            results[key]["winsB"] += 1
    # write results
    os.makedirs(os.path.dirname(RESULTS_PATH), exist_ok=True)
    with open(RESULTS_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Wrote sample results to {RESULTS_PATH}")

if __name__ == '__main__':
    main()
