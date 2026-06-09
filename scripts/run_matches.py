#!/usr/bin/env python3
"""Run many matches between two AI strategies and save results.
"""
import os
import sys
import time
import json
import random
import copy

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

from src.engine.models.pokemon import Pokemon
from src.engine.models.entrenador import Entrenador
from src.engine.models.battle import Battle

# Import strategies and data from run_simulation (module safe to import)
import run_simulation as rs


def make_team(spec_names, trainer_name):
    pokes = [Pokemon(name, rs.pokedex[name], rs.moves_db) for name in spec_names]
    return Entrenador(trainer_name, pokes)

def serialize_team(entrenador):
    team = []
    for p in entrenador.pokemones:
        pm = {
            "name": getattr(p, 'name', None),
            "hp": getattr(p, 'hp', None),
            "max_hp": getattr(p, 'max_hp', None),
            "types": getattr(p, 'types', None),
            "moves": [],
        }
        moves = getattr(p, 'moves', [])
        for m in moves:
            pm['moves'].append({
                'name': getattr(m, 'name', None),
                'type': getattr(m, 'type', None),
                'power': getattr(m, 'power', None),
                'priority': getattr(m, 'priority', None),
                'accuracy': getattr(m, 'accuracy', None),
                'available': getattr(m, 'available', None),
            })
        team.append(pm)
    return team


def run_one_match(seed: int, team_a_spec, team_b_spec, strat_a, strat_b, player_a_label="IA_A", player_b_label="IA_B", max_turns=1000):
    random.seed(seed)
    a = make_team(team_a_spec, player_a_label)
    b = make_team(team_b_spec, player_b_label)
    battle = Battle(a, b)

    turns = 0
    t0 = time.perf_counter()
    try:
        while not battle.is_battle_over() and turns < max_turns:
            move_a = strat_a(a, b)
            move_b = strat_b(b, a)
            battle.ejecutar_turno(move_a, move_b)
            turns += 1
        winner = battle.get_winner() or ""
    except Exception as e:
        winner = f"ERROR: {e}"
    t1 = time.perf_counter()

    return {
        "seed": seed,
        "winner": winner,
        "turns": turns,
        "time_ms": (t1 - t0) * 1000.0,
        "player_a": player_a_label,
        "player_b": player_b_label,
    }


def run_one_match_clone(seed: int, team_a_proto, team_b_proto, strat_a, strat_b, player_a_label="IA_A", player_b_label="IA_B", max_turns=1000):
    random.seed(seed)
    a = copy.deepcopy(team_a_proto)
    b = copy.deepcopy(team_b_proto)
    a.name = player_a_label
    b.name = player_b_label
    battle = Battle(a, b)

    turns = 0
    t0 = time.perf_counter()
    try:
        while not battle.is_battle_over() and turns < max_turns:
            move_a = strat_a(a, b)
            move_b = strat_b(b, a)
            battle.ejecutar_turno(move_a, move_b)
            turns += 1
        winner = battle.get_winner() or ""
    except Exception as e:
        winner = f"ERROR: {e}"
    t1 = time.perf_counter()

    return {
        "seed": seed,
        "winner": winner,
        "turns": turns,
        "time_ms": (t1 - t0) * 1000.0,
        "player_a": player_a_label,
        "player_b": player_b_label,
    }


def run_many(n=100, out_path="results/ai_best_vs_minimax2_n100.json"):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    results = []
    base_seed = 12345

    team_best = ["garchomp", "lucario", "gengar", "swampert"]
    team_minimax = ["zeraora", "baxcalibur", "snorlax", "metagross"]

    # Build prototypes and serialize initial teams once
    random.seed(base_seed)
    proto_a = make_team(team_best, "IA_A")
    proto_b = make_team(team_minimax, "IA_B")
    initial_teams = {
        "player_a": {"label": "IA_A", "strategy": "best", "team": serialize_team(proto_a)},
        "player_b": {"label": "IA_B", "strategy": "minimax2", "team": serialize_team(proto_b)},
    }

    for i in range(n):
        seed = base_seed + i
        res = run_one_match_clone(seed, proto_a, proto_b, rs.estrategia_ia_best_option, rs.estrategia_ia_minimax_nivel2)
        print(f"[{i+1}/{n}] seed={seed} winner={res['winner']} turns={res['turns']} time_ms={res['time_ms']:.1f}")
        results.append(res)

    # summary
    wins = {}
    total_turns = 0
    total_time = 0.0
    for r in results:
        wins[r['winner']] = wins.get(r['winner'], 0) + 1
        total_turns += r['turns']
        total_time += r['time_ms']

    summary = {
        "n": n,
        "wins": wins,
        "avg_turns": total_turns / max(1, n),
        "avg_time_ms": total_time / max(1, n),
    }

    out = {"results": results, "summary": summary, "initial_teams": initial_teams}
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    print("SUMMARY:", summary)
    return out


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run matches between AI strategies.")
    parser.add_argument("-n", "--num", type=int, default=100, help="Number of matches to run")
    parser.add_argument("--a", type=str, default="best", choices=["best", "random", "minimax2", "minimax3"], help="Strategy for player A")
    parser.add_argument("--b", type=str, default="minimax2", choices=["best", "random", "minimax2", "minimax3"], help="Strategy for player B")
    parser.add_argument("--out", type=str, default="results/ai_matches.json", help="Output JSON file")
    args = parser.parse_args()

    strat_map = {
        "best": rs.estrategia_ia_best_option,
        "random": rs.estrategia_ia_random,
        "minimax2": rs.estrategia_ia_minimax_nivel2,
        "minimax3": rs.estrategia_ia_minimax_nivel3,
    }

    strat_a = strat_map[args.a]
    strat_b = strat_map[args.b]

    # adapt run_many to accept strategies
    def run_many_with_strats(n, out_path, strat_a, strat_b):
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        results = []
        base_seed = 12345

        team_best = ["garchomp", "lucario", "gengar", "swampert"]
        team_minimax = ["zeraora", "baxcalibur", "snorlax", "metagross"]

        # Build prototype teams once (deterministic by seeding base_seed)
        random.seed(base_seed)
        proto_a = make_team(team_best, "IA_A")
        proto_b = make_team(team_minimax, "IA_B")

        # Serialize initial teams once and print header mapping
        initial_teams = {
            "player_a": {
                "label": "IA_A",
                "strategy": args.a,
                "team": serialize_team(proto_a),
            },
            "player_b": {
                "label": "IA_B",
                "strategy": args.b,
                "team": serialize_team(proto_b),
            },
        }

        print(f"Running {n} matches")
        print(f"Player A label: IA_A -> strategy={args.a} | Player B label: IA_B -> strategy={args.b}")
        print(f"Team A (IA_A): {[p.name for p in proto_a.pokemones]}")
        print(f"Team B (IA_B): {[p.name for p in proto_b.pokemones]}\n")

        for i in range(n):
            seed = base_seed + i
            # run using clones of the prototypes
            res = run_one_match_clone(seed, proto_a, proto_b, strat_a, strat_b, player_a_label="IA_A", player_b_label="IA_B")
            print(f"[{i+1}/{n}] IA_A({args.a}) vs IA_B({args.b}) seed={seed} winner={res['winner']} turns={res['turns']} time_ms={res['time_ms']:.1f}")
            results.append(res)

        wins = {}
        total_turns = 0
        total_time = 0.0
        for r in results:
            wins[r['winner']] = wins.get(r['winner'], 0) + 1
            total_turns += r['turns']
            total_time += r['time_ms']

        summary = {
            "n": n,
            "wins": wins,
            "avg_turns": total_turns / max(1, n),
            "avg_time_ms": total_time / max(1, n),
        }

        out = {"results": results, "summary": summary, "initial_teams": initial_teams}
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2)

        print("SUMMARY:", summary)
        return out

    run_many_with_strats(args.num, args.out, strat_a, strat_b)
