import sys
import os
import json
import time
import io
import contextlib
from pathlib import Path

project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.engine.models.pokemon import Pokemon
from src.engine.models.entrenador import Entrenador
from src.engine.models.battle import Battle
from src.engine.logic.heuristic import (
    choose_best_move,
    elegir_mejor_sustituto,
    elegir_accion_nivel4,
    elegir_mejor_sustituto_n4,
)

BASE_DIR = project_root
with open(BASE_DIR / "data" / "moves-data.json") as f:
    moves_db = json.load(f)
with open(BASE_DIR / "data" / "pokedex_con_moves.json") as f:
    pokedex = json.load(f)
with open(BASE_DIR / "data" / "best_weights_n4.json") as f:
    data = json.load(f)
    PESOS_N5 = data["pesos"]

print(f"Pesos N5 cargados: {[round(p,4) for p in PESOS_N5]}")


def estrategia_n2(entrenador: Entrenador, rival: Entrenador):
    poke = entrenador.get_current_pokemon()
    if poke.hp <= 0:
        idx = elegir_mejor_sustituto(entrenador, rival)
        if idx is not None:
            entrenador.switch_pokemon(idx)
        return None
    return choose_best_move(poke, rival.get_current_pokemon())


def estrategia_n5(entrenador: Entrenador, rival: Entrenador):
    poke = entrenador.get_current_pokemon()
    if poke.hp <= 0:
        idx = elegir_mejor_sustituto_n4(entrenador, rival, PESOS_N5)
        if idx is not None:
            entrenador.switch_pokemon(idx)
        return None
    accion = elegir_accion_nivel4(entrenador, rival, PESOS_N5)
    if isinstance(accion, int):
        entrenador.switch_pokemon(accion)
        return None
    return accion


# ── Loop de 100 batallas ──────────────────────────────────────────────────────

N = 100
wins_n2 = 0
wins_n5 = 0
total_turnos = 0
total_tiempo = 0.0

for i in range(N):
    ia1 = Entrenador("MejorOpcion", [
        Pokemon("garchomp",  pokedex["garchomp"],  moves_db),
        Pokemon("lucario",   pokedex["lucario"],   moves_db),
        Pokemon("gengar",    pokedex["gengar"],    moves_db),
        Pokemon("swampert",  pokedex["swampert"],  moves_db),
    ])
    ia2 = Entrenador("God", [
        Pokemon("zeraora",    pokedex["zeraora"],    moves_db),
        Pokemon("baxcalibur", pokedex["baxcalibur"], moves_db),
        Pokemon("snorlax",    pokedex["snorlax"],    moves_db),
        Pokemon("metagross",  pokedex["metagross"],  moves_db),
    ])

    battle = Battle(ia1, ia2)
    inicio = time.perf_counter()
    buf = io.StringIO()

    with contextlib.redirect_stdout(buf):
        battle.start_battle(estrategia_n2, estrategia_n5)

    elapsed = time.perf_counter() - inicio
    total_tiempo += elapsed

    # Contar turnos: cada turno imprime display_status con " HP"
    # display_status imprime 2 líneas por turno, dividimos entre 2
    lineas_hp = [l for l in buf.getvalue().splitlines() if " HP" in l]
    turnos = len(lineas_hp) // 2

    ganador = battle.get_winner()
    if ganador == "MejorOpcion":
        wins_n2 += 1
    else:
        wins_n5 += 1

    total_turnos += turnos
    print(f"Batalla {i+1}/{N}: {ganador} | {turnos} turnos | {elapsed:.2f}s")

# ── Guardar resultados ────────────────────────────────────────────────────────

resultado = {
    "wins_nivel2":         wins_n2,
    "wins_nivel5":         wins_n5,
    "total":               N,
    "pct_nivel2":          round(wins_n2 / N * 100, 1),
    "pct_nivel5":          round(wins_n5 / N * 100, 1),
    "turnos_promedio":     round(total_turnos / N, 2),
    "tiempo_promedio_seg": round(total_tiempo / N, 2),
}

os.makedirs("results", exist_ok=True)
with open("results/ai_best_vs_god_n100.json", "w") as f:
    json.dump(resultado, f, indent=2)

print("\n=== RESULTADO FINAL ===")
print(json.dumps(resultado, indent=2))