"""
Tests for genetic.py — GAConfig, chromosome operators, and evolve loop.

All tests use injected fake fitness functions so no real battles are run.
RNG is seeded for determinism. Tests were written BEFORE implementation (STRICT TDD).
"""
import json
import random
import pytest
from pathlib import Path


# ── Import under test (RED: will fail until implementation exists) ─────────────

from src.engine.logic.genetic import (
    GAConfig,
    random_chromosome,
    clamp_chromosome,
    tournament_select,
    uniform_crossover,
    gaussian_mutate,
    optimizar_pesos_ga,
)


# ── GAConfig tests ─────────────────────────────────────────────────────────────


class TestGAConfig:
    """Spec C: GAConfig dataclass with correct defaults."""

    def test_default_pop_size(self):
        cfg = GAConfig()
        assert cfg.pop_size == 20

    def test_default_generations(self):
        cfg = GAConfig()
        assert cfg.generations == 15

    def test_default_n_battles(self):
        cfg = GAConfig()
        assert cfg.n_battles == 10

    def test_default_tournament_k(self):
        cfg = GAConfig()
        assert cfg.tournament_k == 3

    def test_default_crossover_rate(self):
        cfg = GAConfig()
        assert cfg.crossover_rate == pytest.approx(0.8)

    def test_default_mutation_rate(self):
        cfg = GAConfig()
        assert cfg.mutation_rate == pytest.approx(0.2)

    def test_default_sigma(self):
        cfg = GAConfig()
        assert cfg.sigma == pytest.approx(0.5)

    def test_default_elitism(self):
        cfg = GAConfig()
        assert cfg.elitism == 2

    def test_default_seed(self):
        cfg = GAConfig()
        assert cfg.seed == 42

    def test_custom_values_override_defaults(self):
        cfg = GAConfig(pop_size=5, generations=3, seed=99)
        assert cfg.pop_size == 5
        assert cfg.generations == 3
        assert cfg.seed == 99


# ── random_chromosome tests ────────────────────────────────────────────────────


class TestRandomChromosome:
    """Spec C: random_chromosome returns list of 4 floats in (-2, 2)."""

    def test_length_is_4(self):
        rng = random.Random(0)
        c = random_chromosome(rng=rng)
        assert len(c) == 4

    def test_all_elements_are_float(self):
        rng = random.Random(1)
        c = random_chromosome(rng=rng)
        for gene in c:
            assert isinstance(gene, float), f"Gene {gene!r} is not a float"

    def test_genes_within_init_bounds(self):
        """Init bound is uniform(-2, 2); all genes must be in [-2, 2]."""
        rng = random.Random(42)
        for _ in range(100):
            c = random_chromosome(rng=rng)
            for gene in c:
                assert -2.0 <= gene <= 2.0, f"Gene {gene} outside [-2, 2]"

    def test_seeded_rng_is_deterministic(self):
        rng1 = random.Random(7)
        rng2 = random.Random(7)
        assert random_chromosome(rng=rng1) == random_chromosome(rng=rng2)


# ── clamp_chromosome tests ─────────────────────────────────────────────────────


class TestClampChromosome:
    """Spec C: clamp_chromosome clips each gene to [-5, 5]."""

    def test_genes_above_max_clamped(self):
        c = [10.0, 6.0, 5.0, 4.0]
        result = clamp_chromosome(c)
        assert result[0] == pytest.approx(5.0)
        assert result[1] == pytest.approx(5.0)

    def test_genes_below_min_clamped(self):
        c = [-10.0, -6.0, -5.0, -4.0]
        result = clamp_chromosome(c)
        assert result[0] == pytest.approx(-5.0)
        assert result[1] == pytest.approx(-5.0)

    def test_genes_in_bounds_unchanged(self):
        c = [1.0, -1.0, 3.5, -4.9]
        result = clamp_chromosome(c)
        for orig, new in zip(c, result):
            assert orig == pytest.approx(new)

    def test_returns_list_of_4(self):
        c = [100.0, -100.0, 0.0, 0.0]
        result = clamp_chromosome(c)
        assert len(result) == 4

    def test_boundary_values_preserved(self):
        c = [5.0, -5.0, 5.0, -5.0]
        result = clamp_chromosome(c)
        assert result == pytest.approx([5.0, -5.0, 5.0, -5.0])


# ── tournament_select tests ────────────────────────────────────────────────────


class TestTournamentSelect:
    """Spec C: tournament_select returns the chromosome with the highest fitness in the sample."""

    def _population(self):
        return [
            [1.0, 0.0, 0.0, 0.0],   # idx 0, fitness 0.1
            [2.0, 0.0, 0.0, 0.0],   # idx 1, fitness 0.5
            [3.0, 0.0, 0.0, 0.0],   # idx 2, fitness 0.9
            [4.0, 0.0, 0.0, 0.0],   # idx 3, fitness 0.2
        ]

    def test_returns_max_fitness_chromosome(self):
        pop = self._population()
        fitnesses = [0.1, 0.5, 0.9, 0.2]
        # Force tournament over entire population (k=4) → must pick idx 2
        rng = random.Random(0)
        winner = tournament_select(pop, fitnesses, k=4, rng=rng)
        assert winner == [3.0, 0.0, 0.0, 0.0], (
            f"Expected chromosome with highest fitness, got {winner}"
        )

    def test_tournament_returns_chromosome_from_population(self):
        pop = self._population()
        fitnesses = [0.1, 0.5, 0.9, 0.2]
        rng = random.Random(1)
        winner = tournament_select(pop, fitnesses, k=2, rng=rng)
        assert winner in pop, "Winner must be a chromosome from the population"

    def test_tournament_k1_returns_any_chromosome(self):
        pop = self._population()
        fitnesses = [0.1, 0.5, 0.9, 0.2]
        rng = random.Random(5)
        winner = tournament_select(pop, fitnesses, k=1, rng=rng)
        assert winner in pop

    def test_tournament_is_deterministic_with_seed(self):
        pop = self._population()
        fitnesses = [0.1, 0.5, 0.9, 0.2]
        rng1 = random.Random(42)
        rng2 = random.Random(42)
        w1 = tournament_select(pop, fitnesses, k=3, rng=rng1)
        w2 = tournament_select(pop, fitnesses, k=3, rng=rng2)
        assert w1 == w2


# ── uniform_crossover tests ────────────────────────────────────────────────────


class TestUniformCrossover:
    """Spec C: each gene in child comes from p1 or p2 (50/50 per gene)."""

    def test_child_genes_from_parents(self):
        p1 = [1.0, 1.0, 1.0, 1.0]
        p2 = [2.0, 2.0, 2.0, 2.0]
        rng = random.Random(0)
        child = uniform_crossover(p1, p2, rng=rng)
        for gene in child:
            assert gene in (1.0, 2.0), f"Gene {gene} not from either parent"

    def test_child_length_is_4(self):
        p1 = [1.0, 2.0, 3.0, 4.0]
        p2 = [5.0, 6.0, 7.0, 8.0]
        rng = random.Random(0)
        child = uniform_crossover(p1, p2, rng=rng)
        assert len(child) == 4

    def test_crossover_deterministic_with_seed(self):
        p1 = [1.0, 2.0, 3.0, 4.0]
        p2 = [5.0, 6.0, 7.0, 8.0]
        rng1 = random.Random(3)
        rng2 = random.Random(3)
        c1 = uniform_crossover(p1, p2, rng=rng1)
        c2 = uniform_crossover(p1, p2, rng=rng2)
        assert c1 == c2

    def test_crossover_takes_genes_from_both_parents_over_many_runs(self):
        """Over many crossovers, both parents contribute genes."""
        p1 = [0.0, 0.0, 0.0, 0.0]
        p2 = [1.0, 1.0, 1.0, 1.0]
        rng = random.Random(0)
        saw_from_p1 = False
        saw_from_p2 = False
        for _ in range(20):
            child = uniform_crossover(p1, p2, rng=rng)
            if any(g == 0.0 for g in child):
                saw_from_p1 = True
            if any(g == 1.0 for g in child):
                saw_from_p2 = True
        assert saw_from_p1 and saw_from_p2, "Should see genes from both parents across many crossovers"


# ── gaussian_mutate tests ──────────────────────────────────────────────────────


class TestGaussianMutate:
    """Spec C: gaussian_mutate adds N(0,sigma) noise per-gene and clamps to [-5, 5]."""

    def test_mutated_genes_within_clamp_bounds(self):
        c = [4.9, -4.9, 0.0, 2.5]
        rng = random.Random(0)
        result = gaussian_mutate(c, sigma=2.0, rate=1.0, rng=rng)  # rate=1.0 ensures all mutated
        for gene in result:
            assert -5.0 <= gene <= 5.0, f"Gene {gene} outside clamp bounds [-5, 5]"

    def test_zero_rate_leaves_chromosome_unchanged(self):
        c = [1.0, 2.0, 3.0, 4.0]
        rng = random.Random(0)
        result = gaussian_mutate(c, sigma=1.0, rate=0.0, rng=rng)  # rate=0 → no mutation
        assert result == pytest.approx(c)

    def test_result_length_is_4(self):
        c = [0.0, 0.0, 0.0, 0.0]
        rng = random.Random(0)
        result = gaussian_mutate(c, sigma=0.5, rate=0.5, rng=rng)
        assert len(result) == 4

    def test_mutation_is_deterministic_with_seed(self):
        c = [1.0, 2.0, 3.0, 4.0]
        rng1 = random.Random(9)
        rng2 = random.Random(9)
        r1 = gaussian_mutate(c, sigma=0.5, rate=1.0, rng=rng1)
        r2 = gaussian_mutate(c, sigma=0.5, rate=1.0, rng=rng2)
        assert r1 == pytest.approx(r2)

    def test_extreme_values_clamped(self):
        """Start at the boundary; large sigma should clamp, not blow past [-5,5]."""
        c = [5.0, 5.0, -5.0, -5.0]
        rng = random.Random(0)
        result = gaussian_mutate(c, sigma=10.0, rate=1.0, rng=rng)
        for gene in result:
            assert -5.0 <= gene <= 5.0


# ── evolve (optimizar_pesos_ga) tests ─────────────────────────────────────────


class TestOptimizarPesosGa:
    """
    Spec C: optimizar_pesos_ga runs the GA loop and persists best_weights.json.

    IMPORTANT: These tests inject a FAKE fitness function (lambda cromosoma: 0.7)
    so NO real battles are run — the GA just evaluates, selects, breeds, and saves.
    The equipo_factory is also a trivial lambda that returns None — unused when
    we inject fake_fitness.

    The design contract: optimizar_pesos_ga(equipo_factory, config=None, fitness_fn=None)
    When fitness_fn is provided, it replaces the real calcular_fitness.
    This hook is required for testability.
    """

    @pytest.fixture
    def small_config(self):
        return GAConfig(
            pop_size=4,
            generations=2,
            n_battles=2,
            tournament_k=2,
            crossover_rate=0.8,
            mutation_rate=0.5,
            sigma=0.3,
            elitism=1,
            seed=42,
        )

    @pytest.fixture
    def fake_equipo_factory(self):
        """Returns a factory that yields None tuples — unused with injected fitness."""
        return lambda: (None, None)

    @pytest.fixture
    def fake_fitness(self):
        """Fake fitness: always returns 0.7 — fast, deterministic."""
        return lambda cromosoma: 0.7

    def test_returns_list_of_4_floats(self, small_config, fake_equipo_factory, fake_fitness, tmp_path, monkeypatch):
        """optimizar_pesos_ga must return a list of 4 floats."""
        # Redirect best_weights.json to tmp_path to avoid polluting data/
        monkeypatch.chdir(tmp_path)
        result = optimizar_pesos_ga(
            equipo_factory=fake_equipo_factory,
            config=small_config,
            fitness_fn=fake_fitness,
            output_dir=tmp_path,
        )
        assert isinstance(result, list), "Result must be a list"
        assert len(result) == 4, "Chromosome must have 4 genes"
        for gene in result:
            assert isinstance(gene, (int, float)), f"Gene {gene!r} must be numeric"

    def test_genes_within_clamp_bounds(self, small_config, fake_equipo_factory, fake_fitness, tmp_path, monkeypatch):
        """All returned genes must be within [-5, 5]."""
        monkeypatch.chdir(tmp_path)
        result = optimizar_pesos_ga(
            equipo_factory=fake_equipo_factory,
            config=small_config,
            fitness_fn=fake_fitness,
            output_dir=tmp_path,
        )
        for gene in result:
            assert -5.0 <= gene <= 5.0, f"Gene {gene} outside [-5, 5]"

    def test_writes_best_weights_json(self, small_config, fake_equipo_factory, fake_fitness, tmp_path, monkeypatch):
        """Spec: data/best_weights.json must exist after evolve completes."""
        monkeypatch.chdir(tmp_path)
        optimizar_pesos_ga(
            equipo_factory=fake_equipo_factory,
            config=small_config,
            fitness_fn=fake_fitness,
            output_dir=tmp_path,
        )
        output_file = tmp_path / "best_weights.json"
        assert output_file.exists(), "best_weights.json must be written"

    def test_best_weights_json_schema(self, small_config, fake_equipo_factory, fake_fitness, tmp_path, monkeypatch):
        """Schema: {pesos: [...], fitness: float, generaciones: int}."""
        monkeypatch.chdir(tmp_path)
        optimizar_pesos_ga(
            equipo_factory=fake_equipo_factory,
            config=small_config,
            fitness_fn=fake_fitness,
            output_dir=tmp_path,
        )
        output_file = tmp_path / "best_weights.json"
        data = json.loads(output_file.read_text())
        assert "pesos" in data, "JSON must have 'pesos' key"
        assert "fitness" in data, "JSON must have 'fitness' key"
        assert "generaciones" in data, "JSON must have 'generaciones' key"
        assert isinstance(data["pesos"], list), "'pesos' must be a list"
        assert len(data["pesos"]) == 4, "'pesos' must have 4 elements"
        assert isinstance(data["fitness"], float), "'fitness' must be float"
        assert isinstance(data["generaciones"], int), "'generaciones' must be int"

    def test_best_weights_fitness_in_range(self, small_config, fake_equipo_factory, fake_fitness, tmp_path, monkeypatch):
        """Fitness value must be in [0.0, 1.0]."""
        monkeypatch.chdir(tmp_path)
        optimizar_pesos_ga(
            equipo_factory=fake_equipo_factory,
            config=small_config,
            fitness_fn=fake_fitness,
            output_dir=tmp_path,
        )
        output_file = tmp_path / "best_weights.json"
        data = json.loads(output_file.read_text())
        assert 0.0 <= data["fitness"] <= 1.0, f"Fitness {data['fitness']} out of [0, 1]"

    def test_generaciones_matches_config(self, small_config, fake_equipo_factory, fake_fitness, tmp_path, monkeypatch):
        """generaciones field must reflect the actual generations run (<= config.generations)."""
        monkeypatch.chdir(tmp_path)
        optimizar_pesos_ga(
            equipo_factory=fake_equipo_factory,
            config=small_config,
            fitness_fn=fake_fitness,
            output_dir=tmp_path,
        )
        output_file = tmp_path / "best_weights.json"
        data = json.loads(output_file.read_text())
        assert data["generaciones"] <= small_config.generations, (
            "generaciones must not exceed config.generations"
        )
        assert data["generaciones"] >= 1, "generaciones must be >= 1"

    def test_deterministic_with_seed(self, small_config, fake_equipo_factory, fake_fitness, tmp_path, monkeypatch):
        """Same seed → same result across two runs."""
        monkeypatch.chdir(tmp_path)
        r1 = optimizar_pesos_ga(
            equipo_factory=fake_equipo_factory,
            config=small_config,
            fitness_fn=fake_fitness,
            output_dir=tmp_path,
        )
        r2 = optimizar_pesos_ga(
            equipo_factory=fake_equipo_factory,
            config=small_config,
            fitness_fn=fake_fitness,
            output_dir=tmp_path,
        )
        assert r1 == pytest.approx(r2), "Same seed must produce same chromosome"
