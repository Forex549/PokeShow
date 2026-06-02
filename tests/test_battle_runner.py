"""
Tests for run_silent_battle in battle_runner.py.

Strategy:
- Use the same duck-typed stubs (FakeMove, FakePokemon, FakeEntrenador) from
  test_heuristic_nivel3.py to avoid loading JSON / real Pokemon.
- Build two stub trainers: one whose Pokemon has a guaranteed-kill move power,
  the other with a very weak Pokemon. Seed random so the battle is deterministic.
- Use capsys to assert outer stdout is EMPTY (redirect_stdout absorbed all I/O).
- Assert the returned winner name matches one of the trainer names.
- Assert original trainers' state is unmodified after the call.

All tests comply with STRICT TDD — they were written BEFORE the implementation.
"""
import copy
import random
import pytest

from types import SimpleNamespace


# ── Duck-typed stubs (mirrors test_heuristic_nivel3.py stubs) ─────────────────


class FakeMove:
    """Minimal move stub matching the Movimiento interface used by Battle."""

    def __init__(
        self,
        name: str = "tackle",
        type: str = "Normal",
        power: int = 40,
        priority: int = 0,
        accuracy: int = 100,
        category: str = "Physical",
        available: bool = True,
    ):
        self.name = name
        self.type = type
        self.power = power
        self.priority = priority
        self.accuracy = accuracy
        self.category = category
        self.available = available
        # Battle.ejecutar_turno checks these for status application
        self.direct_status = None
        self.secondary_status = None
        self.secondary_volatile = None
        self.secondary_chance = 0


class FakePokemon:
    """Minimal Pokemon stub with deterministic stats (no JSON / random sampling)."""

    def __init__(
        self,
        name: str = "Fake",
        types: list = None,
        hp: int = 100,
        max_hp: int = 100,
        spe: int = 100,
        atk: int = 100,
        defense: int = 50,
        spa: int = 80,
        spd: int = 50,
        moves: list = None,
        level: int = 50,
    ):
        self.name = name
        self.types = types if types is not None else ["Normal"]
        self._hp = hp
        self.max_hp = max_hp
        self.spe = spe
        self.atk = atk
        self.defense = defense
        self.spa = spa
        self.spd = spd
        self.level = level
        self.moves = moves if moves is not None else [FakeMove()]
        # Status fields expected by Battle
        self.status = "No State"
        self.status_turns = 0
        self.volatile_status = "No State"
        self.volatile_turns = 0

    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, value):
        self._hp = max(0, min(value, self.max_hp))

    @property
    def available_moves(self):
        return [m for m in self.moves if m.available]

    def decreasestatus_turn(self):
        self.status_turns = max(0, self.status_turns - 1)

    def decrease_volatile_turn(self):
        self.volatile_turns = max(0, self.volatile_turns - 1)

    def clear_volatiles(self):
        self.volatile_status = "No State"
        self.volatile_turns = 0


class FakeEntrenador:
    """Minimal trainer stub."""

    def __init__(self, name: str, pokemones: list, current_index: int = 0):
        self.name = name
        self.pokemones = pokemones
        self.current_pokemon_index = current_index

    def get_current_pokemon(self):
        return self.pokemones[self.current_pokemon_index]

    def has_usable_pokemon(self):
        return any(p.hp > 0 for p in self.pokemones)

    def switch_pokemon(self, idx: int):
        if 0 <= idx < len(self.pokemones) and self.pokemones[idx].hp > 0:
            self.current_pokemon_index = idx


# ── Strategies ─────────────────────────────────────────────────────────────────


def _always_first_move(entrenador, rival):
    """Strategy that always picks the first available move, or None on forced switch."""
    poke = entrenador.get_current_pokemon()
    if poke.hp <= 0:
        # Forced switch: find first alive pokemon
        for idx, p in enumerate(entrenador.pokemones):
            if p.hp > 0:
                entrenador.switch_pokemon(idx)
                break
        return None
    moves = poke.available_moves
    return moves[0] if moves else None


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def one_vs_one_trainers():
    """
    Two trainers, each with 1 Pokémon.
    t1's Pokemon has 300 ATK (OHKOs t2).
    t2's Pokemon has 1 ATK (tickle damage).
    With seed=0, t1 should almost always win on turn 1.
    """
    strong_move = FakeMove(name="Hyper Beam", power=150, accuracy=100)
    strong_poke = FakePokemon(
        name="Blastoise", hp=100, max_hp=100, atk=300, defense=50, level=50,
        moves=[strong_move],
    )
    t1 = FakeEntrenador("Ash", [strong_poke])

    weak_move = FakeMove(name="Splash", power=1, accuracy=100)
    weak_poke = FakePokemon(
        name="Magikarp", hp=1, max_hp=1, atk=5, defense=50, level=50,
        moves=[weak_move],
    )
    t2 = FakeEntrenador("Gary", [weak_poke])
    return t1, t2


# ── Import under test (RED: will fail until implementation exists) ─────────────


from src.engine.logic.battle_runner import run_silent_battle


# ── Tests ─────────────────────────────────────────────────────────────────────


class TestRunSilentBattleReturnsWinner:
    """Spec B: run_silent_battle returns non-empty str equal to one trainer's name."""

    def test_returns_string(self, one_vs_one_trainers, capsys):
        t1, t2 = one_vs_one_trainers
        random.seed(0)
        result = run_silent_battle(t1, t2, _always_first_move, _always_first_move, seed=0)
        assert isinstance(result, str), "Result must be a str"

    def test_winner_is_one_of_the_trainers(self, one_vs_one_trainers, capsys):
        t1, t2 = one_vs_one_trainers
        result = run_silent_battle(t1, t2, _always_first_move, _always_first_move, seed=0)
        assert result in (t1.name, t2.name), (
            f"Winner '{result}' must be one of: {t1.name!r} or {t2.name!r}"
        )

    def test_winner_is_nonempty(self, one_vs_one_trainers, capsys):
        t1, t2 = one_vs_one_trainers
        result = run_silent_battle(t1, t2, _always_first_move, _always_first_move, seed=0)
        assert result != "", "Winner must not be empty string"

    def test_strong_team_wins(self, one_vs_one_trainers, capsys):
        """t1 (Blastoise, 300 ATK) vs t2 (Magikarp, 1 HP) — t1 wins deterministically."""
        t1, t2 = one_vs_one_trainers
        result = run_silent_battle(t1, t2, _always_first_move, _always_first_move, seed=42)
        assert result == t1.name, f"Expected {t1.name!r} to win, got {result!r}"


class TestRunSilentBattleNoStdout:
    """Spec B: outer stdout must be empty — redirect_stdout absorbed all battle I/O."""

    def test_capsys_outer_stdout_empty(self, one_vs_one_trainers, capsys):
        t1, t2 = one_vs_one_trainers
        run_silent_battle(t1, t2, _always_first_move, _always_first_move, seed=0)
        captured = capsys.readouterr()
        assert captured.out == "", (
            f"Expected no stdout output, got:\n{captured.out!r}"
        )

    def test_capsys_outer_stderr_empty(self, one_vs_one_trainers, capsys):
        t1, t2 = one_vs_one_trainers
        run_silent_battle(t1, t2, _always_first_move, _always_first_move, seed=0)
        captured = capsys.readouterr()
        assert captured.err == "", (
            f"Expected no stderr output, got:\n{captured.err!r}"
        )


class TestRunSilentBattleCallerStatePreserved:
    """Spec B: original trainer objects must be unmodified after the call."""

    def test_t1_hp_unchanged(self, one_vs_one_trainers):
        t1, t2 = one_vs_one_trainers
        original_hp_t1 = [p.hp for p in t1.pokemones]
        run_silent_battle(t1, t2, _always_first_move, _always_first_move, seed=0)
        assert [p.hp for p in t1.pokemones] == original_hp_t1, (
            "t1 pokemon HP values must not change after run_silent_battle"
        )

    def test_t2_hp_unchanged(self, one_vs_one_trainers):
        t1, t2 = one_vs_one_trainers
        original_hp_t2 = [p.hp for p in t2.pokemones]
        run_silent_battle(t1, t2, _always_first_move, _always_first_move, seed=0)
        assert [p.hp for p in t2.pokemones] == original_hp_t2, (
            "t2 pokemon HP values must not change after run_silent_battle"
        )

    def test_result_is_reproducible_with_same_seed(self, one_vs_one_trainers):
        """Same seed → same winner every time."""
        t1, t2 = one_vs_one_trainers
        results = [
            run_silent_battle(t1, t2, _always_first_move, _always_first_move, seed=7)
            for _ in range(3)
        ]
        assert len(set(results)) == 1, (
            f"Same seed should produce same winner, got: {results}"
        )
