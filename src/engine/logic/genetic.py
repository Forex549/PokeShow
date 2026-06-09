# ============================================================
# PROPÓSITO DEL ALGORITMO GENÉTICO
# ============================================================
#
# Este módulo utiliza un Algoritmo Genético (GA) para optimizar
# los pesos de la heurística de nivel 3 utilizada por la IA de
# Pokémon para tomar decisiones durante una batalla.
#
# Cada individuo de la población representa una estrategia
# candidata y está codificado mediante un cromosoma:
#
#     [w1, w2, w3, w4]
#
# donde cada gen es un peso utilizado por la función de
# evaluación de movimientos.
#
# Ejemplo:
#
#     [1.5, -0.3, 0.8, 2.1]
#
# El significado exacto de cada gen depende de la heurística,
# pudiendo representar factores como daño esperado,
# efectividad de tipo, riesgo, velocidad, etc.
#
# ------------------------------------------------------------
# FUNCIÓN OBJETIVO (FITNESS)
# ------------------------------------------------------------
#
# El objetivo del algoritmo NO es maximizar daño,
# HP restante o cualquier métrica aislada.
#
# La meta es maximizar la tasa de victorias obtenida por la IA
# en batallas simuladas.
#
# Para evaluar un cromosoma:
#
# 1. Se construye una IA Nivel 3 utilizando esos pesos.
# 2. La IA juega múltiples batallas contra distintos rivales.
# 3. Se calcula el porcentaje de victorias obtenido.
# 4. Ese porcentaje se utiliza como fitness.
#
# Cuanto mayor sea el fitness, mejor es la estrategia.
#
# ------------------------------------------------------------
# EVOLUCIÓN
# ------------------------------------------------------------
#
# En cada generación:
#
# - Los mejores individuos son seleccionados.
# - Se cruzan sus genes (crossover).
# - Se aplican pequeñas mutaciones.
# - Se generan nuevas estrategias.
#
# Con el paso de las generaciones, la población debería
# converger hacia configuraciones de pesos que permitan a la
# IA ganar más batallas.
#
# ------------------------------------------------------------
# LIMITACIONES DEL MODELO ACTUAL
# ------------------------------------------------------------
#
# Actualmente el GA únicamente optimiza los pesos de la
# heurística de selección de movimientos.
#
# La IA no aprende nuevas reglas ni descubre nuevos criterios.
# Solamente ajusta la importancia relativa de los criterios
# definidos manualmente por el desarrollador.
#
# Posibles mejoras futuras:
#
# - Aprender cuándo cambiar de Pokémon.
# - Incorporar memoria de combate.
# - Entrenamiento mediante self-play.
# - Evolución de funciones heurísticas completas mediante
#   Genetic Programming.
# - Uso de redes neuronales para aprender políticas de juego.
#
# ============================================================

# Algoritmo genético para optimizar los pesos de la heurística de nivel 3
from __future__ import annotations

import json
import random as _stdlib_random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, List, Optional, Tuple


# Rango de inicialización de genes y rango de clampeo
_GENE_INIT_LO: float = -2.0
_GENE_INIT_HI: float = 2.0
_GENE_CLAMP_LO: float = -5.0
_GENE_CLAMP_HI: float = 5.0
_CHROMOSOME_LEN: int = 4

# Si no mejoramos durante N generaciones seguidas, paramos antes de tiempo
_EARLY_STOP_PATIENCE: int = 5
_EARLY_STOP_THRESHOLD: float = 0.95


@dataclass
class GAConfig:
    # Parámetros del algoritmo genético, con valores por defecto razonables
    pop_size: int = 20
    generations: int = 15
    n_battles: int = 10
    tournament_k: int = 3
    crossover_rate: float = 0.8
    mutation_rate: float = 0.2
    sigma: float = 0.5
    elitism: int = 2
    seed: int = 42


def random_chromosome(rng: _stdlib_random.Random = None) -> List[float]:
    if rng is None:
        rng = _stdlib_random
    return [rng.uniform(_GENE_INIT_LO, _GENE_INIT_HI) for _ in range(_CHROMOSOME_LEN)]


def clamp_chromosome(c: List[float]) -> List[float]:
    return [max(_GENE_CLAMP_LO, min(_GENE_CLAMP_HI, g)) for g in c]


def tournament_select(
    population: List[List[float]],
    fitnesses: List[float],
    k: int,
    rng: _stdlib_random.Random = None,
) -> List[float]:
    # Tomamos k individuos al azar (sin repetición) y nos quedamos con el mejor
    if rng is None:
        rng = _stdlib_random
    actual_k = min(k, len(population))
    indices = rng.sample(range(len(population)), actual_k)
    best_idx = max(indices, key=lambda i: fitnesses[i])
    return population[best_idx]


def uniform_crossover(
    p1: List[float],
    p2: List[float],
    rng: _stdlib_random.Random = None,
) -> List[float]:
    # Cada gen del hijo viene de uno de los dos padres al azar, 50/50
    if rng is None:
        rng = _stdlib_random
    return [p1[i] if rng.random() < 0.5 else p2[i] for i in range(_CHROMOSOME_LEN)]


def gaussian_mutate(
    c: List[float],
    sigma: float,
    rate: float,
    rng: _stdlib_random.Random = None,
) -> List[float]:
    # Perturbamos algunos genes con ruido gaussiano y recortamos al rango válido
    if rng is None:
        rng = _stdlib_random
    mutated = []
    for gene in c:
        if rng.random() < rate:
            gene = gene + rng.gauss(0.0, sigma)
        mutated.append(gene)
    return clamp_chromosome(mutated)


def random_chromosome_n4(rng: _stdlib_random.Random = None) -> List[float]:
    if rng is None:
        rng = _stdlib_random
    return [rng.uniform(_GENE_INIT_LO, _GENE_INIT_HI) for _ in range(5)]


def _make_nivel4_strategy(pesos: List[float]) -> Callable:
    from src.engine.logic.heuristic import elegir_accion_nivel4, elegir_mejor_sustituto_n4

    def strategy(entrenador, rival):
        poke = entrenador.get_current_pokemon()
        if poke.hp <= 0:
            idx = elegir_mejor_sustituto_n4(entrenador, rival, pesos)
            if idx is not None:
                entrenador.switch_pokemon(idx)
            return None
        accion = elegir_accion_nivel4(entrenador, rival, pesos)
        if isinstance(accion, int):
            entrenador.switch_pokemon(accion)
            return None
        return accion

    return strategy


def _make_nivel3_strategy(pesos: List[float]) -> Callable:
    # Importamos aquí para evitar dependencia circular entre genetic y heuristic
    from src.engine.logic.heuristic import elegir_movimiento_nivel3, elegir_mejor_sustituto_n3

    def strategy(entrenador, rival):
        poke = entrenador.get_current_pokemon()
        if poke.hp <= 0:
            idx = elegir_mejor_sustituto_n3(entrenador, rival, pesos)
            if idx is not None:
                entrenador.switch_pokemon(idx)
            return None
        return elegir_movimiento_nivel3(entrenador, rival, pesos)

    return strategy


def _make_random_strategy() -> Callable:
    from src.engine.logic.heuristic import chose_random_move

    def strategy(entrenador, rival):
        poke = entrenador.get_current_pokemon()
        if poke.hp <= 0:
            for idx, p in enumerate(entrenador.pokemones):
                if p.hp > 0:
                    entrenador.switch_pokemon(idx)
                    break
            return None
        return chose_random_move(poke)

    return strategy


def _make_best_option_strategy() -> Callable:
    from src.engine.logic.heuristic import choose_best_move

    def strategy(entrenador, rival):
        poke = entrenador.get_current_pokemon()
        if poke.hp <= 0:
            for idx, p in enumerate(entrenador.pokemones):
                if p.hp > 0:
                    entrenador.switch_pokemon(idx)
                    break
            return None
        return choose_best_move(poke, rival.get_current_pokemon())

    return strategy


def _make_nivel2_strategy() -> Callable:
    from src.engine.logic.heuristic import elegir_movimiento_nivel2

    def strategy(entrenador, rival):
        poke = entrenador.get_current_pokemon()
        if poke.hp <= 0:
            for idx, p in enumerate(entrenador.pokemones):
                if p.hp > 0:
                    entrenador.switch_pokemon(idx)
                    break
            return None
        return elegir_movimiento_nivel2(entrenador, rival)

    return strategy


def calcular_fitness_completo(
    cromosoma: List[float],
    equipo_factory: Callable[[], Tuple],
    config: GAConfig,
) -> float:
    # Entrena contra los 3 rivales: aleatorio, mejor opción y minimax nivel 2
    # Cada rival tiene un peso distinto: ganarle al más difícil vale más
    from src.engine.logic.battle_runner import run_silent_battle

    strat_n3 = _make_nivel3_strategy(cromosoma)
    rivales = [
        (1, _make_random_strategy()),       # fácil
        (2, _make_best_option_strategy()),  # medio
        (3, _make_nivel2_strategy()),       # difícil
    ]

    total_peso = 0
    victorias_ponderadas = 0.0

    for peso, strat_rival in rivales:
        half = config.n_battles // 2
        remainder = config.n_battles - half
        wins = 0

        for i in range(half):
            t1, t2 = equipo_factory()
            seed = config.seed * 1000 + peso * 100 + i
            winner = run_silent_battle(t1, t2, strat_n3, strat_rival, seed=seed)
            if winner == t1.name:
                wins += 1

        for i in range(remainder):
            t1, t2 = equipo_factory()
            seed = config.seed * 1000 + peso * 100 + half + i
            winner = run_silent_battle(t1, t2, strat_rival, strat_n3, seed=seed)
            if winner == t2.name:
                wins += 1

        win_rate = wins / config.n_battles
        victorias_ponderadas += peso * win_rate
        total_peso += peso

    return victorias_ponderadas / total_peso


def calcular_fitness(
    cromosoma: List[float],
    equipo_factory: Callable[[], Tuple],
    config: GAConfig,
) -> float:
    # Medimos qué tan bueno es un cromosoma enfrentándolo contra un oponente aleatorio
    # La mitad de las batallas jugamos como t1, la otra mitad como t2
    from src.engine.logic.battle_runner import run_silent_battle

    strat_n3 = _make_nivel3_strategy(cromosoma)
    strat_random = _make_random_strategy()

    wins = 0
    half = config.n_battles // 2
    remainder = config.n_battles - half

    for i in range(half):
        t1, t2 = equipo_factory()
        seed = config.seed * 1000 + i
        winner = run_silent_battle(t1, t2, strat_n3, strat_random, seed=seed)
        if winner == t1.name:
            wins += 1

    for i in range(remainder):
        t1, t2 = equipo_factory()
        seed = config.seed * 1000 + half + i
        winner = run_silent_battle(t1, t2, strat_random, strat_n3, seed=seed)
        if winner == t2.name:
            wins += 1

    return wins / config.n_battles


def calcular_fitness_n4(
    cromosoma: List[float],
    equipo_factory: Callable[[], Tuple],
    config: GAConfig,
) -> float:
    from src.engine.logic.battle_runner import run_silent_battle

    strat_n4 = _make_nivel4_strategy(cromosoma)
    rivales = [
        (1, _make_random_strategy()),
        (2, _make_best_option_strategy()),
        (3, _make_nivel2_strategy()),
        (4, _make_nivel3_strategy([1.0, 1.0, 0.5, 1.0])),
    ]

    total_peso = 0
    victorias_ponderadas = 0.0

    for peso, strat_rival in rivales:
        half = config.n_battles // 2
        remainder = config.n_battles - half
        wins = 0

        for i in range(half):
            t1, t2 = equipo_factory()
            seed = config.seed * 1000 + peso * 100 + i
            winner = run_silent_battle(t1, t2, strat_n4, strat_rival, seed=seed)
            if winner == t1.name:
                wins += 1

        for i in range(remainder):
            t1, t2 = equipo_factory()
            seed = config.seed * 1000 + peso * 100 + half + i
            winner = run_silent_battle(t1, t2, strat_rival, strat_n4, seed=seed)
            if winner == t2.name:
                wins += 1

        win_rate = wins / config.n_battles
        victorias_ponderadas += peso * win_rate
        total_peso += peso

    return victorias_ponderadas / total_peso


def save_best_weights_n4(
    best_cromosoma: List[float],
    best_fitness: float,
    generations_run: int,
    output_dir: Optional[Path] = None,
) -> None:
    if output_dir is None:
        output_dir = Path(__file__).parent.parent.parent.parent / "data"
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "pesos": best_cromosoma,
        "fitness": float(best_fitness),
        "generaciones": int(generations_run),
    }
    out_path = output_dir / "best_weights_n4.json"
    out_path.write_text(json.dumps(payload, indent=2))


def optimizar_pesos_n4_ga(
    equipo_factory: Callable[[], Tuple],
    config: Optional[GAConfig] = None,
    fitness_fn: Optional[Callable[[List[float]], float]] = None,
    output_dir: Optional[Path] = None,
) -> List[float]:
    if config is None:
        config = GAConfig()

    rng = _stdlib_random.Random(config.seed)

    if fitness_fn is not None:
        def evaluate(c: List[float]) -> float:
            return fitness_fn(c)
    else:
        def evaluate(c: List[float]) -> float:
            return calcular_fitness_n4(c, equipo_factory, config)

    population = [random_chromosome_n4(rng=rng) for _ in range(config.pop_size)]

    best_cromosoma: List[float] = population[0]
    best_fitness: float = -1.0
    no_improvement_streak: int = 0
    actual_generations: int = 0

    for gen in range(config.generations):
        actual_generations = gen + 1
        fitnesses = [evaluate(c) for c in population]

        gen_best_idx = max(range(len(fitnesses)), key=lambda i: fitnesses[i])
        gen_best_fitness = fitnesses[gen_best_idx]
        gen_best_cromosoma = population[gen_best_idx]

        if gen_best_fitness > best_fitness:
            best_fitness = gen_best_fitness
            best_cromosoma = gen_best_cromosoma[:]
            no_improvement_streak = 0
        else:
            no_improvement_streak += 1

        print(f"  Gen {gen + 1:>2}/{config.generations} — mejor fitness: {best_fitness:.3f} (esta gen: {gen_best_fitness:.3f})")

        if best_fitness >= _EARLY_STOP_THRESHOLD or no_improvement_streak >= _EARLY_STOP_PATIENCE:
            print(f"  Parada temprana en generación {gen + 1}.")
            break

        sorted_pairs = sorted(zip(fitnesses, population), key=lambda x: x[0], reverse=True)
        sorted_pop = [c for _, c in sorted_pairs]

        next_pop: List[List[float]] = []
        for i in range(min(config.elitism, len(sorted_pop))):
            next_pop.append(sorted_pop[i][:])

        while len(next_pop) < config.pop_size:
            sorted_fitnesses = sorted(fitnesses, reverse=True)
            parent1 = tournament_select(sorted_pop, sorted_fitnesses, config.tournament_k, rng=rng)
            parent2 = tournament_select(sorted_pop, sorted_fitnesses, config.tournament_k, rng=rng)
            if rng.random() < config.crossover_rate:
                # Cruce uniforme sobre 5 genes
                child = [parent1[i] if rng.random() < 0.5 else parent2[i] for i in range(5)]
            else:
                child = parent1[:]
            child = gaussian_mutate(child, config.sigma, config.mutation_rate, rng=rng)
            next_pop.append(child)

        population = next_pop[:config.pop_size]

    if best_fitness < 0.0:
        best_fitness = evaluate(population[0])
        best_cromosoma = population[0]

    save_best_weights_n4(best_cromosoma, best_fitness, actual_generations, output_dir=output_dir)
    return best_cromosoma


def save_best_weights(
    best_cromosoma: List[float],
    best_fitness: float,
    generations_run: int,
    output_dir: Optional[Path] = None,
) -> None:
    # Guardamos el mejor cromosoma en data/best_weights.json
    if output_dir is None:
        # genetic.py está en src/engine/logic/, subimos 4 niveles para llegar a la raíz
        output_dir = Path(__file__).parent.parent.parent.parent / "data"

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    payload = {
        "pesos": best_cromosoma,
        "fitness": float(best_fitness),
        "generaciones": int(generations_run),
    }
    out_path = output_dir / "best_weights.json"
    out_path.write_text(json.dumps(payload, indent=2))


def optimizar_pesos_ga(
    equipo_factory: Callable[[], Tuple],
    config: Optional[GAConfig] = None,
    fitness_fn: Optional[Callable[[List[float]], float]] = None,
    output_dir: Optional[Path] = None,
) -> List[float]:
    # Ejecuta el GA y devuelve el mejor vector de pesos encontrado
    # fitness_fn es un hook para tests: permite inyectar una función de fitness falsa
    if config is None:
        config = GAConfig()

    rng = _stdlib_random.Random(config.seed)

    if fitness_fn is not None:
        def evaluate(c: List[float]) -> float:
            return fitness_fn(c)
    else:
        def evaluate(c: List[float]) -> float:
            return calcular_fitness(c, equipo_factory, config)

    population = [random_chromosome(rng=rng) for _ in range(config.pop_size)]

    best_cromosoma: List[float] = population[0]
    best_fitness: float = -1.0
    no_improvement_streak: int = 0
    actual_generations: int = 0

    for gen in range(config.generations):
        actual_generations = gen + 1

        fitnesses = [evaluate(c) for c in population]

        gen_best_idx = max(range(len(fitnesses)), key=lambda i: fitnesses[i])
        gen_best_fitness = fitnesses[gen_best_idx]
        gen_best_cromosoma = population[gen_best_idx]

        if gen_best_fitness > best_fitness:
            best_fitness = gen_best_fitness
            best_cromosoma = gen_best_cromosoma[:]
            no_improvement_streak = 0
        else:
            no_improvement_streak += 1

        print(f"  Gen {gen + 1:>2}/{config.generations} — mejor fitness: {best_fitness:.3f} (esta gen: {gen_best_fitness:.3f})")

        if best_fitness >= _EARLY_STOP_THRESHOLD or no_improvement_streak >= _EARLY_STOP_PATIENCE:
            print(f"  Parada temprana en generación {gen + 1}.")
            break

        sorted_pairs = sorted(
            zip(fitnesses, population), key=lambda x: x[0], reverse=True
        )
        sorted_pop = [c for _, c in sorted_pairs]

        next_pop: List[List[float]] = []

        # Elitismo: los mejores pasan directamente a la siguiente generación
        for i in range(min(config.elitism, len(sorted_pop))):
            next_pop.append(sorted_pop[i][:])

        while len(next_pop) < config.pop_size:
            sorted_fitnesses = sorted(fitnesses, reverse=True)

            parent1 = tournament_select(sorted_pop, sorted_fitnesses, config.tournament_k, rng=rng)
            parent2 = tournament_select(sorted_pop, sorted_fitnesses, config.tournament_k, rng=rng)

            if rng.random() < config.crossover_rate:
                child = uniform_crossover(parent1, parent2, rng=rng)
            else:
                child = parent1[:]

            child = gaussian_mutate(child, config.sigma, config.mutation_rate, rng=rng)
            next_pop.append(child)

        population = next_pop[:config.pop_size]

    if best_fitness < 0.0:
        best_fitness = evaluate(population[0])
        best_cromosoma = population[0]

    save_best_weights(best_cromosoma, best_fitness, actual_generations, output_dir=output_dir)

    return best_cromosoma
