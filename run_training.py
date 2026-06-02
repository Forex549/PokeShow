import json
import os

from src.engine.models.pokemon import Pokemon
from src.engine.models.entrenador import Entrenador
from src.engine.logic.genetic import optimizar_pesos_ga, GAConfig, calcular_fitness_completo

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE_DIR, "data", "moves-data.json")) as f:
    moves_db = json.load(f)
with open(os.path.join(BASE_DIR, "data", "pokedex_con_moves.json")) as f:
    pokedex = json.load(f)


def equipo_factory():
    # Equipo A — BST promedio 545, mezcla de tipos y velocidades
    # garchomp (Dragon/Ground, rápido), ceruledge (Fire/Ghost, medio),
    # sylveon (Fairy, lento/tanque), greninja (Water/Dark, muy rápido)
    t1 = Entrenador("EquipoA", [
        Pokemon("garchomp", pokedex["garchomp"], moves_db),
        Pokemon("ceruledge", pokedex["ceruledge"], moves_db),
        Pokemon("sylveon", pokedex["sylveon"], moves_db),
        Pokemon("greninja", pokedex["greninja"], moves_db),
    ])
    # Equipo B — BST promedio 553, balance similar con tipos distintos
    # salamence (Dragon/Flying, rápido), swampert (Water/Ground, lento/tanque),
    # lucario (Fighting/Steel, medio), volcarona (Bug/Fire, rápido especial)
    t2 = Entrenador("EquipoB", [
        Pokemon("salamence", pokedex["salamence"], moves_db),
        Pokemon("swampert", pokedex["swampert"], moves_db),
        Pokemon("lucario", pokedex["lucario"], moves_db),
        Pokemon("volcarona", pokedex["volcarona"], moves_db),
    ])
    return t1, t2


if __name__ == "__main__":
    config = GAConfig(
        pop_size=40,
        generations=20,
        n_battles=10,
        seed=42,
    )

    batallas_por_gen = config.pop_size * 3 * config.n_battles
    print("Entrenamiento completo — nivel 3 vs aleatorio, mejor opción y minimax nivel 2")
    print("Equipos balanceados: EquipoA (BST 545) vs EquipoB (BST 553)")
    print("Población: {} | Generaciones: {} | Batallas por individuo: {}".format(
        config.pop_size, config.generations, config.n_battles * 3))
    print("Total batallas estimadas: {:,}".format(batallas_por_gen * config.generations))
    print("Esto puede tardar varios minutos...\n")

    def fitness_fn(cromosoma):
        return calcular_fitness_completo(cromosoma, equipo_factory, config)

    mejores_pesos = optimizar_pesos_ga(equipo_factory, config=config, fitness_fn=fitness_fn)

    print("\nMejores pesos encontrados: {}".format([round(p, 4) for p in mejores_pesos]))
    print("Guardados en data/best_weights.json")
