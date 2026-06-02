import json
import os
import tempfile
import itertools
from pathlib import Path

from src.engine.models.pokemon import Pokemon
from src.engine.models.entrenador import Entrenador
from src.engine.logic.genetic import optimizar_pesos_ga, GAConfig, calcular_fitness_completo

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE_DIR, "data", "moves-data.json")) as f:
    moves_db = json.load(f)
with open(os.path.join(BASE_DIR, "data", "pokedex_con_moves.json")) as f:
    pokedex = json.load(f)

# Archivo donde guardamos los resultados parciales y finales
RESULTS_FILE = os.path.join(BASE_DIR, "data", "hyperparameter_results.json")

# Espacio de búsqueda — modifica estos valores si quieres explorar más o menos
SEARCH_SPACE = {
    "pop_size":    [10, 20, 40],
    "generations": [10, 20, 30],
    "n_battles":   [4, 8, 12],
}


def equipo_factory():
    t1 = Entrenador("EquipoA", [
        Pokemon("garchomp",  pokedex["garchomp"],  moves_db),
        Pokemon("ceruledge", pokedex["ceruledge"], moves_db),
        Pokemon("sylveon",   pokedex["sylveon"],   moves_db),
        Pokemon("greninja",  pokedex["greninja"],  moves_db),
    ])
    t2 = Entrenador("EquipoB", [
        Pokemon("salamence", pokedex["salamence"], moves_db),
        Pokemon("swampert",  pokedex["swampert"],  moves_db),
        Pokemon("lucario",   pokedex["lucario"],   moves_db),
        Pokemon("volcarona", pokedex["volcarona"],  moves_db),
    ])
    return t1, t2


def cargar_resultados_parciales():
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE) as f:
            return json.load(f)
    return []


def guardar_resultados(resultados):
    os.makedirs(os.path.dirname(RESULTS_FILE), exist_ok=True)
    with open(RESULTS_FILE, "w") as f:
        json.dump(resultados, f, indent=2)


def clave_combinacion(params):
    return "pop{pop_size}_gen{generations}_bat{n_battles}".format(**params)


def imprimir_tabla(resultados):
    ordenados = sorted(resultados, key=lambda r: r["fitness"], reverse=True)
    print("\n{:<30} {:>8} {:>12} {:>10}".format("Combinación", "Fitness", "Generaciones", "Pesos"))
    print("-" * 70)
    for r in ordenados:
        pesos_str = "[{}]".format(", ".join("{:.3f}".format(p) for p in r["pesos"]))
        print("{:<30} {:>8.4f} {:>12} {}".format(
            r["clave"], r["fitness"], r["generaciones_reales"], pesos_str))


if __name__ == "__main__":
    combinaciones = [
        dict(zip(SEARCH_SPACE.keys(), vals))
        for vals in itertools.product(*SEARCH_SPACE.values())
    ]
    total = len(combinaciones)

    # Estimación de tiempo (muy aproximada)
    batallas_totales = sum(
        c["pop_size"] * 3 * c["n_battles"] * c["generations"]
        for c in combinaciones
    )
    print("Búsqueda de hiperparámetros — {} combinaciones".format(total))
    print("Batallas totales estimadas: {:,}".format(batallas_totales))
    print("El progreso se guarda en data/hyperparameter_results.json\n")

    # Retomamos desde donde quedamos si ya hay resultados parciales
    resultados = cargar_resultados_parciales()
    claves_hechas = {r["clave"] for r in resultados}

    pendientes = [c for c in combinaciones if clave_combinacion(c) not in claves_hechas]
    if len(pendientes) < total:
        print("Retomando — {} combinaciones ya completadas, {} pendientes.\n".format(
            total - len(pendientes), len(pendientes)))

    for i, params in enumerate(pendientes, start=total - len(pendientes) + 1):
        clave = clave_combinacion(params)
        print("[{}/{}] {}".format(i, total, clave))

        config = GAConfig(
            pop_size=params["pop_size"],
            generations=params["generations"],
            n_battles=params["n_battles"],
            seed=42,
        )

        def fitness_fn(cromosoma, _config=config):
            return calcular_fitness_completo(cromosoma, equipo_factory, _config)

        # Usamos un directorio temporal para no pisar data/best_weights.json durante la búsqueda
        with tempfile.TemporaryDirectory() as tmpdir:
            best_pesos = optimizar_pesos_ga(
                equipo_factory,
                config=config,
                fitness_fn=fitness_fn,
                output_dir=Path(tmpdir),
            )
            data = json.loads((Path(tmpdir) / "best_weights.json").read_text())
            fitness = data["fitness"]
            generaciones_reales = data["generaciones"]

        resultado = {
            "clave": clave,
            "pop_size": params["pop_size"],
            "generations": params["generations"],
            "n_battles": params["n_battles"],
            "fitness": fitness,
            "generaciones_reales": generaciones_reales,
            "pesos": best_pesos,
        }
        resultados.append(resultado)
        guardar_resultados(resultados)
        print("  → fitness: {:.4f}\n".format(fitness))

    print("\n=== BÚSQUEDA COMPLETADA ===")
    imprimir_tabla(resultados)

    # Guardamos los pesos del ganador en best_weights.json
    ganador = max(resultados, key=lambda r: r["fitness"])
    payload = {
        "pesos": ganador["pesos"],
        "fitness": ganador["fitness"],
        "generaciones": ganador["generaciones_reales"],
        "config": {
            "pop_size": ganador["pop_size"],
            "generations": ganador["generations"],
            "n_battles": ganador["n_battles"],
        },
    }
    out_path = os.path.join(BASE_DIR, "data", "best_weights.json")
    with open(out_path, "w") as f:
        json.dump(payload, f, indent=2)

    print("\nGanador: {} — fitness {:.4f}".format(ganador["clave"], ganador["fitness"]))
    print("Pesos guardados en data/best_weights.json")
