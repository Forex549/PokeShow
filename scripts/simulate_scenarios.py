"""Herramienta rápida para montar escenarios hipotéticos y ver qué movimiento
elegiría cada estrategia (best, random, minimax nivel2/nivel3).

Ejemplo de uso:
    py -3 scripts/simulate_scenarios.py

El script crea entrenadores con pokémon modificados (hp, velocidad, lista de movimientos)
para forzar situaciones como: mi pokémon tiene 1 HP pero es más rápido; el rival tiene
un movimiento con prioridad. Se imprimen las elecciones de las distintas IAs.
"""
import random
import os
import copy
import sys
import json

# Asegurarnos de que el directorio raíz del proyecto esté en sys.path para poder
# importar el módulo de estrategias `run_simulation.py` situado en la raíz.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import run_simulation as rs
from src.engine.models.pokemon import Pokemon
from src.engine.models.movimientos import Movimiento
from src.engine.models.entrenador import Entrenador


def build_pokemon(pname: str, move_keys: list, hp: int = None, spe: int = None) -> Pokemon:
    """Crea un Pokemon a partir del pokedex y reemplaza sus movimientos por los indicados.
    move_keys deben ser las claves del archivo moves-data.json (ej. 'accelerock').
    Si hp es proporcionado se ajusta el HP actual (no el máximo).
    Si spe es proporcionado se ajusta la estadística de velocidad base.
    """
    # run_simulation ya cargó moves_db y pokedex en import
    moves_db = rs.moves_db
    pokedex = rs.pokedex

    if pname not in pokedex:
        raise ValueError(f"No hay datos para el Pokémon '{pname}' en pokedex")

    p = Pokemon(pname, pokedex[pname], moves_db)

    # Reemplazamos moves por las que pasaron explícitamente
    new_moves = []
    for mk in move_keys:
        if mk not in moves_db:
            raise ValueError(f"Movimiento '{mk}' no encontrado en moves_db")
        new_moves.append(Movimiento(moves_db[mk]))
    p.moves = new_moves

    # Ajustes finos
    if hp is not None:
        # Mantener max_hp igual pero forzar hp actual
        p.hp = hp
    if spe is not None:
        p._stats["spe"] = spe

    return p


def scenario_priority():
    """Mi poke muy bajo de vida pero muy rápido; rival tiene prioridad."""
    # Elegimos dos especies neutrales (las estadísticas las ajustaremos manualmente)
    my = build_pokemon("garchomp", ["earthquake", "dragonclaw", "outrage", "stoneedge"], hp=1, spe=300)
    opp = build_pokemon("lucario", ["accelerock", "bulletpunch", "closecombat", "ironhead"], hp=30, spe=100)

    trainer_a = Entrenador("IA_A", [my])
    trainer_b = Entrenador("IA_B", [opp])

    return trainer_a, trainer_b


def scenario_both_low_hp_priority():
    """Ambos con poca vida, mi poke más rápido, rival tiene movimiento prioritario."""
    my = build_pokemon("garchomp", ["dragonclaw", "outrage", "earthquake", "stoneedge"], hp=4, spe=200)
    opp = build_pokemon("zeraora", ["accelerock", "plasmafists", "closecombat", "voltswitch"], hp=4, spe=120)

    trainer_a = Entrenador("IA_A", [my])
    trainer_b = Entrenador("IA_B", [opp])

    return trainer_a, trainer_b


def print_choices(tr_a: Entrenador, tr_b: Entrenador):
    """Consulta las distintas estrategias y muestra qué movimiento elegirían para IA_A.
    Asumimos que IA_A está en el rol del jugador que queremos testear.
    """
    # Hacemos copias porque algunas estrategias clonan pero otras podrían alterar estado
    a_copy = copy.deepcopy(tr_a)
    b_copy = copy.deepcopy(tr_b)

    strategies = {
        "best": rs.estrategia_ia_best_option,
        "random": rs.estrategia_ia_random,
        "minimax2": rs.estrategia_ia_minimax_nivel2,
        "minimax3": rs.estrategia_ia_minimax_nivel3,
        "minimax4": rs.estrategia_ia_minimax_nivel4,
    }

    print("\n--- Escenario ---")
    print(f"Mi Pokémon: {a_copy.get_current_pokemon().name} HP={a_copy.get_current_pokemon().hp} SPE={a_copy.get_current_pokemon().spe}")
    print(f"Rival: {b_copy.get_current_pokemon().name} HP={b_copy.get_current_pokemon().hp} SPE={b_copy.get_current_pokemon().spe}")
    print("Movimientos mi poke:")
    for m in a_copy.get_current_pokemon().moves:
        print(f"  - {m.name} (power={m.power} priority={m.priority})")
    print("Movimientos rival:")
    for m in b_copy.get_current_pokemon().moves:
        print(f"  - {m.name} (power={m.power} priority={m.priority})")

    for name, strat in strategies.items():
        # Estrategias esperan (entrenador, rival) y retornan Movimiento o None
        # Mostramos la elección aplicada a IA_A (mi poke) y a IA_B (rival) para claridad.
        ta1 = copy.deepcopy(tr_a)
        tb1 = copy.deepcopy(tr_b)
        random.seed(42)
        choice_a = strat(ta1, tb1)
        choice_a_name = choice_a.name if choice_a is not None else "(cambio/None)"

        ta2 = copy.deepcopy(tr_a)
        tb2 = copy.deepcopy(tr_b)
        random.seed(42)
        # Cuando llamamos la estrategia para IA_B intercambiamos los argumentos
        choice_b = strat(tb2, ta2)
        choice_b_name = choice_b.name if choice_b is not None else "(cambio/None)"

        print(f"[{name}] IA_A elegiría: {choice_a_name} | IA_B elegiría: {choice_b_name}")


def main():
    print("Simulador de escenarios - decisiones de IA")

    scenarios = [scenario_priority, scenario_both_low_hp_priority]

    for s in scenarios:
        ta, tb = s()
        print_choices(ta, tb)


if __name__ == "__main__":
    main()
