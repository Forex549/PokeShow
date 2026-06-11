"""Script para comprobar si Minimax nivel 4 decide cambiar de Pokémon en situaciones adversas.

Crea dos equipos de 4 pokémon y llama a elegir_accion_nivel4 para la IA.
Imprime la acción sugerida: Movimiento escogido (nombre) o índice de cambio.

Uso:
    py -3 scripts/simulate_minimax4_switch.py
"""
import sys
import os
import copy
import random

# Asegurar path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import run_simulation as rs
from src.engine.models.entrenador import Entrenador
from src.engine.models.pokemon import Pokemon
from src.engine.models.movimientos import Movimiento
from src.engine.logic.heuristic import elegir_accion_nivel4, minimax_alfa_beta_n4
from src.engine.logic.damage_calc import calculate_expected_damage
from src.engine.models.battle import Battle
import run_simulation as rs
from run_simulation import cargar_pesos_nivel3


def build_pokemon_from_name(name, moves_keys, hp=None, spe=None):
    pokedex = rs.pokedex
    moves_db = rs.moves_db
    p = Pokemon(name, pokedex[name], moves_db)
    p.moves = [Movimiento(moves_db[k]) for k in moves_keys]
    if hp is not None:
        p.hp = hp
    if spe is not None:
        p._stats['spe'] = spe
    return p


def make_team_a():
    # Equipo en desventaja: pokes con poca vida o mal matchup
    team = [
        build_pokemon_from_name('garchomp', ['earthquake','dragonclaw','stoneedge','outrage'], hp=1, spe=120),
        build_pokemon_from_name('lucario', ['closecombat','bulletpunch','ironhead','aura_sphere'.replace('_','')], hp=10, spe=90),
        build_pokemon_from_name('gengar', ['shadowball','sludgebomb','focusblast','thunderbolt'], hp=20, spe=110),
        build_pokemon_from_name('swampert', ['earthquake','waterfall','icepunch','scald'], hp=15, spe=60),
    ]
    return Entrenador('IA_A', team)


def make_team_b():
    # Equipo rival: buenas resistencias y prioridad
    team = [
        build_pokemon_from_name('zeraora', ['plasmafists','closecombat','voltswitch','accelerock'], hp=40, spe=100),
        build_pokemon_from_name('scizor', ['bulletpunch','ironhead','uturn','xscissor'], hp=45, spe=65),
        build_pokemon_from_name('mamoswine', ['iceshard','earthquake','stoneedge','knockoff'], hp=50, spe=80),
        build_pokemon_from_name('metagross', ['meteormash','zenheadbutt','earthquake','bulletpunch'], hp=60, spe=70),
    ]
    return Entrenador('IA_B', team)


def main():
    random.seed(0)
    ta = make_team_a()
    tb = make_team_b()

    # Forzamos que el activo sea el primero
    ta.current_pokemon_index = 0
    tb.current_pokemon_index = 0

    pesos = cargar_pesos_nivel3()
    # La heurística nivel4 espera 5 pesos; si solo hay 4 (GA nivel3), extendemos con 1.0
    if not isinstance(pesos, list):
        pesos = [1.0, 1.0, 1.0, 1.0, 1.0]
    if len(pesos) < 5:
        pesos = pesos + [1.0] * (5 - len(pesos))

    # Mostrar estado de la batalla
    def print_battle_state(ta, tb):
        print("\n=== ESTADO DE LA BATALLA ===")
        def show_trainer(t):
            print(f"Entrenador: {t.name}")
            for i, p in enumerate(t.pokemones):
                active = '<- ACTIVO' if i == t.current_pokemon_index else ''
                print(f"  [{i}] {p.name} HP={p.hp}/{p.max_hp} SPE={p.spe} {active}")
                print("    Movs:")
                for m in p.moves:
                    print(f"      - {m.name} | power={m.power} priority={m.priority} accuracy={getattr(m, 'accuracy', 'N/A')}")
        show_trainer(ta)
        show_trainer(tb)
        print("=== FIN DEL ESTADO ===\n")

    print_battle_state(ta, tb)

    # Helper: evaluate every move and possible switch for a trainer vs rival
    def evaluate_actions(entrenador, rival, pesos):
        ia_clon = copy.deepcopy(entrenador)
        rival_clon = copy.deepcopy(rival)
        batalla_simulada = Battle(ia_clon, rival_clon)

        poke_ia_clon = ia_clon.get_current_pokemon()
        poke_rival_clon = rival_clon.get_current_pokemon()

        move_results = []  # (move_name, value)
        for move_clon in poke_ia_clon.available_moves:
            dmg = calculate_expected_damage(poke_ia_clon, poke_rival_clon, move_clon)
            hp_original = poke_rival_clon.hp
            poke_rival_clon.hp -= dmg
            valor = minimax_alfa_beta_n4(
                batalla_simulada, 3, float("-inf"), float("inf"),
                False, ia_clon, rival_clon, pesos,
            )
            poke_rival_clon.hp = hp_original
            move_results.append((move_clon.name, valor, dmg))

        switch_results = []  # (idx, pokemon_name, value)
        idx_original = ia_clon.current_pokemon_index
        for i, p in enumerate(ia_clon.pokemones):
            if p.hp <= 0 or i == idx_original:
                continue
            ia_clon.current_pokemon_index = i
            # incoming threat: best expected damage the rival can do to the switched-in
            new_active = ia_clon.get_current_pokemon()
            try:
                incoming = max(
                    calculate_expected_damage(poke_rival_clon, new_active, m)
                    for m in poke_rival_clon.available_moves
                ) if poke_rival_clon.available_moves else 0.0
            except Exception:
                incoming = 0.0
            valor = minimax_alfa_beta_n4(
                batalla_simulada, 3, float("-inf"), float("inf"),
                False, ia_clon, rival_clon, pesos,
            )

            
            ia_clon.current_pokemon_index = idx_original
            switch_results.append((i, p.name, valor, incoming))

        # Sort by descending value (better for the IA)
        move_results.sort(key=lambda x: x[1], reverse=True)
        switch_results.sort(key=lambda x: x[2], reverse=True)
        return move_results, switch_results

    # Evaluate and print for both trainers so it's reciprocal
    for trainer, opponent in [(ta, tb), (tb, ta)]:
        print(f"\n--- Evaluando acciones para: {trainer.name} vs {opponent.name} ---")
        moves, switches = evaluate_actions(trainer, opponent, pesos)
        if moves:
            print("Movimientos (ordenados por valor):")
            for name, val, dmg in moves:
                print(f"  - {name}: value={val:.4f} expected_dmg={dmg:.1f}")
        else:
            print("No hay movimientos disponibles.")

        if switches:
            print("Cambios posibles (ordenados por valor):")
            for idx, pname, val, incoming in switches:
                print(f"  - switch to [{idx}] {pname}: value={val:.4f} incoming_expected_dmg={incoming:.1f}")
        else:
            print("No hay cambios viables (bench vacío o todos K.O.).")

        chosen = elegir_accion_nivel4(trainer, opponent, pesos)
        if chosen is None:
            print(f'{trainer.name} Minimax4: No action suggested (None)')
        elif isinstance(chosen, int):
            print(f'{trainer.name} Minimax4: choose switch to index {chosen} (pokemon: {trainer.pokemones[chosen].name})')
        else:
            print(f'{trainer.name} Minimax4: choose move {chosen.name}')

    print()


if __name__ == '__main__':
    main()
