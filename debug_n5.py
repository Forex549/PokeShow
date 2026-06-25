import sys, json
from pathlib import Path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from src.engine.models.pokemon import Pokemon
from src.engine.models.entrenador import Entrenador
from src.engine.logic.heuristic import elegir_accion_nivel4

with open("data/moves-data.json") as f:
    moves_db = json.load(f)
with open("data/pokedex_con_moves.json") as f:
    pokedex = json.load(f)
with open("data/best_weights_n4.json") as f:
    PESOS_N5 = json.load(f)["pesos"]

ia = Entrenador("God", [
    Pokemon("zeraora",    pokedex["zeraora"],    moves_db),
    Pokemon("baxcalibur", pokedex["baxcalibur"], moves_db),
    Pokemon("snorlax",    pokedex["snorlax"],    moves_db),
    Pokemon("metagross",  pokedex["metagross"],  moves_db),
])
rival = Entrenador("MejorOpcion", [
    Pokemon("garchomp",  pokedex["garchomp"],  moves_db),
    Pokemon("lucario",   pokedex["lucario"],   moves_db),
    Pokemon("gengar",    pokedex["gengar"],    moves_db),
    Pokemon("swampert",  pokedex["swampert"],  moves_db),
])

import time
inicio = time.perf_counter()
accion = elegir_accion_nivel4(ia, rival, PESOS_N5)
elapsed = time.perf_counter() - inicio

print(f"Acción elegida: {accion}")
print(f"Tipo de acción: {'CAMBIO (int)' if isinstance(accion, int) else 'MOVIMIENTO'}")
print(f"Tiempo de decisión: {elapsed:.4f}s")