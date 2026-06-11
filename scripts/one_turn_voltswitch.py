"""Simula un único turno para probar Volt Switch (daño + cambio).

Imprime logs detallados (estadísticas, datos del movimiento, daño esperado, resultado del turno,
y si el cambio por Volt Switch se aplica).

Uso:
    py -3 scripts\one_turn_voltswitch.py [--seed N] [--attacker zeraora] [--defender garchomp]

Ejemplo:
    py -3 scripts\one_turn_voltswitch.py --seed 0 --attacker zeraora --defender garchomp
"""
import sys
import os
import copy
import argparse
import random

# Ensure project root is importable
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import run_simulation as rs
from src.engine.models.pokemon import Pokemon
from src.engine.models.movimientos import Movimiento
from src.engine.models.entrenador import Entrenador
from src.engine.models.battle import Battle
from src.engine.logic.damage_calc import calculate_damage, calculate_expected_damage


def build_team_with_active(active_name, bench_names=None):
    # bench_names is a list of species for bench; ensure at least one switch candidate
    if bench_names is None:
        bench_names = ["lucario", "gengar", "swampert"]
    pokes = []
    # active
    pokes.append(Pokemon(active_name, rs.pokedex[active_name], rs.moves_db))
    for n in bench_names:
        pokes.append(Pokemon(n, rs.pokedex[n], rs.moves_db))
    return pokes


def find_move_by_key(poke: Pokemon, key: str) -> Movimiento:
    # moves_db keys are lower-case keys like 'voltswitch'
    for m in poke.moves:
        if m.name.replace(" ", "").lower() == rs.moves_db[key]['name'].replace(" ", "").lower() or m.name.replace(' ', '').lower() == key:
            return m
    # fallback: try by key in global db
    return Movimento(rs.moves_db[key])


def print_poke(p: Pokemon):
    print(f"{p.name} HP={p.hp}/{p.max_hp} Atk={p.atk} Def={p.defense} SpA={p.spa} SpD={p.spd} SPE={p.spe} Types={p.types}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--attacker", type=str, default="zeraora")
    parser.add_argument("--defender", type=str, default="garchomp")
    parser.add_argument("--attacker_hp", type=int, default=None)
    parser.add_argument("--defender_hp", type=int, default=None)
    parser.add_argument("--defender_move", type=str, default=None)
    args = parser.parse_args()

    random.seed(args.seed)

    # Build teams
    team_a = build_team_with_active(args.attacker)
    team_b = build_team_with_active(args.defender)

    trainer_a = Entrenador("A", team_a)
    trainer_b = Entrenador("B", team_b)

    # Optionally override current HP
    if args.attacker_hp is not None:
        trainer_a.get_current_pokemon().hp = args.attacker_hp
    if args.defender_hp is not None:
        trainer_b.get_current_pokemon().hp = args.defender_hp

    # Select moves
    attacker_poke = trainer_a.get_current_pokemon()
    defender_poke = trainer_b.get_current_pokemon()

    # Attacker move: volt switch
    if 'voltswitch' not in rs.moves_db:
        print('voltswitch not found in moves_db')
        return
    move_attacker = Movimiento(rs.moves_db['voltswitch'])

    # Defender move: user-specified or default first move
    if args.defender_move:
        if args.defender_move not in rs.moves_db:
            print(f"Defender move key {args.defender_move} not found in moves_db")
            return
        move_defender = Movimiento(rs.moves_db[args.defender_move])
    else:
        # use first available move of defender species
        move_defender = defender_poke.moves[0]

    print("\n=== Pre-turn info ===")
    print("Attacker:")
    print_poke(attacker_poke)
    print("Moves:")
    for m in attacker_poke.moves:
        print(f" - {m.name} (power={m.power} priority={m.priority} accuracy={getattr(m, 'accuracy', 'N/A')})")
    print("\nDefender:")
    print_poke(defender_poke)
    print("Moves:")
    for m in defender_poke.moves:
        print(f" - {m.name} (power={m.power} priority={m.priority} accuracy={getattr(m, 'accuracy', 'N/A')})")

    # Show expected damage
    exp_dmg = calculate_expected_damage(attacker_poke, defender_poke, move_attacker)
    print(f"\nExpected damage of {move_attacker.name} from {attacker_poke.name} to {defender_poke.name}: {exp_dmg}")
    exp_dmg_def = calculate_expected_damage(defender_poke, attacker_poke, move_defender) if move_defender else 0
    print(f"Expected damage of {move_defender.name} from {defender_poke.name} to {attacker_poke.name}: {exp_dmg_def}")

    print("\n--- Executing single turn (manual resolution) ---")

    # Determine action order by priority then speed
    a_priority = move_attacker.priority if hasattr(move_attacker, 'priority') else 0
    d_priority = move_defender.priority if hasattr(move_defender, 'priority') else 0

    a_speed = attacker_poke.spe
    d_speed = defender_poke.spe

    # Prepare state snapshots
    before_defender_hp = defender_poke.hp
    before_attacker_hp = attacker_poke.hp

    # Determine order: higher priority acts first; tie -> higher speed acts first
    first, second = None, None
    if a_priority > d_priority:
        first = ('A', attacker_poke, move_attacker, defender_poke)
        second = ('B', defender_poke, move_defender, attacker_poke)
    elif d_priority > a_priority:
        first = ('B', defender_poke, move_defender, attacker_poke)
        second = ('A', attacker_poke, move_attacker, defender_poke)
    else:
        if a_speed >= d_speed:
            first = ('A', attacker_poke, move_attacker, defender_poke)
            second = ('B', defender_poke, move_defender, attacker_poke)
        else:
            first = ('B', defender_poke, move_defender, attacker_poke)
            second = ('A', attacker_poke, move_attacker, defender_poke)

    def resolve_action(actor_label, actor_poke, move, target_poke):
        if actor_poke.hp <= 0:
            print(f"{actor_label} {actor_poke.name} está debilitado y no puede actuar.")
            return {'acted': False, 'hit': False, 'damage': 0, 'fainted': False}

        # Accuracy roll
        acc = getattr(move, 'accuracy', 100)
        roll = random.randint(1, 100)
        hit = roll <= acc
        print(f"\n{actor_label} {actor_poke.name} intenta usar {move.name} contra {target_poke.name} (accuracy={acc}) -> roll={roll} -> {'HIT' if hit else 'MISS'})")

        if not hit:
            return {'acted': True, 'hit': False, 'damage': 0, 'fainted': False}

        # If move is damaging
        if move.category in ["Physical", "Special"]:
            dmg, is_crit = calculate_damage(actor_poke, target_poke, move)
            print(f"  Damage computed: {dmg} (crit={is_crit})")
            target_poke.hp -= dmg
            if target_poke.hp <= 0:
                target_poke.hp = 0
                print(f"  --> {target_poke.name} se ha debilitado!")
                return {'acted': True, 'hit': True, 'damage': dmg, 'fainted': True}
            return {'acted': True, 'hit': True, 'damage': dmg, 'fainted': False}
        else:
            # Status move handling minimal
            print(f"  {move.name} es de categoría Status; no se calcula daño en esta simulación.")
            return {'acted': True, 'hit': True, 'damage': 0, 'fainted': False}

    # Resolve first action
    res_first = resolve_action(*first)

    # If first action fainted the target, second action may not occur depending on which was targeted
    # If second actor was fainted by first, they can't act
    # If first actor killed the other's active, and the other's action would have targeted them, second may be skipped
    if second[1].hp <= 0:
        print(f"\nSegundo actor {second[1].name} está debilitado y no puede actuar.")
        res_second = {'acted': False, 'hit': False, 'damage': 0, 'fainted': False}
    else:
        res_second = resolve_action(*second)

    # Volt Switch specifics: if attacker used Volt Switch and it hit, they switch out
    volt_used = move_attacker.name.replace(' ', '').lower() == 'voltswitch'
    volt_hit = (res_first if first[0] == 'A' else res_second).get('hit', False)

    print("\n--- Turn summary ---")
    print(f"Attacker {attacker_poke.name}: HP before={before_attacker_hp} after={attacker_poke.hp}")
    print(f"Defender {defender_poke.name}: HP before={before_defender_hp} after={defender_poke.hp}")

    if volt_used and volt_hit and attacker_poke.hp > 0:
        # NOTE: el motor actual NO aplica el cambio automático tras Volt Switch.
        # Aquí solo informamos qué sucedería (candidato a sustituir), sin ejecutar el switch.
        cur_idx = trainer_a.current_pokemon_index
        candidate = None
        for i, p in enumerate(trainer_a.pokemones):
            if i != cur_idx and p.hp > 0:
                candidate = (i, p.name)
                break
        if candidate:
            print(f"\nVolt Switch: hit — si el motor aplicara el pivot cambiaría {trainer_a.get_current_pokemon().name} -> {candidate[1]} (index {candidate[0]})")
        else:
            print("\nVolt Switch: hit, pero no hay sustituto viable en el bench (todos K.O.).")
    else:
        if volt_used:
            print("Volt Switch used but did not hit — no switch will occur.")

    print("\n=== Final state after turn ===")
    print("Attacker now:")
    print_poke(trainer_a.get_current_pokemon())
    print("Defender now:")
    print_poke(trainer_b.get_current_pokemon())


if __name__ == '__main__':
    main()
