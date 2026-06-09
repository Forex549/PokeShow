#!/usr/bin/env python3
"""Diagnose why 'best' may beat 'minimax3' by comparing first-turn moves.
"""
import sys
import os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

import random
import run_simulation as rs


def make_team(spec_names, trainer_name):
    from src.engine.models.pokemon import Pokemon
    from src.engine.models.entrenador import Entrenador
    pokes = [Pokemon(name, rs.pokedex[name], rs.moves_db) for name in spec_names]
    return Entrenador(trainer_name, pokes)


def diagnose(seeds=range(12345, 12355)):
    team_a = ["garchomp", "lucario", "gengar", "swampert"]
    team_b = ["zeraora", "baxcalibur", "snorlax", "metagross"]

    print("Seed | Best move (A) | Minimax3 move (A) | Enemy first move (B)")
    for s in seeds:
        random.seed(s)
        a = make_team(team_a, "IA_A")
        b = make_team(team_b, "IA_B")

        # snapshot current active pokemon
        poke_a = a.get_current_pokemon()
        poke_b = b.get_current_pokemon()

        m_best = rs.estrategia_ia_best_option(a, b)
        # For minimax3, call strategy but ensure it doesn't mutate real HP (it shouldn't)
        m_minimax3 = rs.estrategia_ia_minimax_nivel3(a, b)

        # Also ask what the enemy would pick on first turn (best option)
        m_enemy = rs.estrategia_ia_best_option(b, a)

        name_best = m_best.name if m_best is not None else 'None'
        name_minimax3 = m_minimax3.name if m_minimax3 is not None else 'None'
        name_enemy = m_enemy.name if m_enemy is not None else 'None'

        print(f"{s} | {name_best} | {name_minimax3} | {name_enemy}")


if __name__ == "__main__":
    diagnose()
