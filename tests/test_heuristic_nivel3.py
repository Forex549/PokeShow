"""
Tests for evaluar_heuristica_nivel3, _factor_* helpers, and elegir_movimiento_nivel3.

Uses duck-typed stubs — NO real Pokemon/JSON loading.
All stubs are deterministic and fast.
"""
import math
import pytest
from types import SimpleNamespace

# ── Duck-typed stubs ─────────────────────────────────────────────────────────


class FakeMove:
    """Minimal move stub matching the Movimiento interface used by the heuristic."""

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


class FakePokemon:
    """Minimal pokemon stub with explicit stat values (no random sampling)."""

    def __init__(
        self,
        name: str = "Fake",
        types: list = None,
        hp: int = 100,
        max_hp: int = 100,
        spe: int = 100,
        atk: int = 100,
        defense: int = 100,
        spa: int = 100,
        spd: int = 100,
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
        self.level = level  # needed by calculate_damage crit formula
        self.moves = moves if moves is not None else [FakeMove()]

    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, value: int):
        self._hp = max(0, min(value, self.max_hp))

    @property
    def available_moves(self):
        return [m for m in self.moves if m.available]


class FakeEntrenador:
    """Minimal trainer stub with a fixed team and active index."""

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


# ── Helpers ───────────────────────────────────────────────────────────────────


def _make_symmetric_trainers(hp: int = 100, max_hp: int = 100, spe: int = 100):
    """Return two trainers with identical 4-pokemon teams (normal type, neutral matchup)."""
    def make_team(name):
        pokemons = [
            FakePokemon(name=f"{name}_{i}", types=["Normal"], hp=hp, max_hp=max_hp, spe=spe,
                        moves=[FakeMove(type="Normal")])
            for i in range(4)
        ]
        return FakeEntrenador(name, pokemons)
    return make_team("Aliado"), make_team("Rival")


# ── Imports under test (will fail until implementation exists) ────────────────

from src.engine.logic.heuristic import (
    evaluar_heuristica_nivel3,
    elegir_movimiento_nivel3,
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TASK 1.1 — Factor unit tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class TestSymmetricStateScoresZero:
    """Spec: symmetric identical teams → evaluar returns 0.0."""

    def test_symmetric_all_weights_equal(self):
        aliado, rival = _make_symmetric_trainers()
        result = evaluar_heuristica_nivel3(aliado, rival, [1.0, 1.0, 1.0, 1.0])
        assert result == pytest.approx(0.0, abs=1e-9)

    def test_symmetric_zero_weights(self):
        aliado, rival = _make_symmetric_trainers()
        result = evaluar_heuristica_nivel3(aliado, rival, [0.0, 0.0, 0.0, 0.0])
        assert result == pytest.approx(0.0, abs=1e-9)

    def test_symmetric_mixed_weights(self):
        aliado, rival = _make_symmetric_trainers()
        result = evaluar_heuristica_nivel3(aliado, rival, [2.0, 0.5, 1.0, 0.3])
        assert result == pytest.approx(0.0, abs=1e-9)


class TestFactorHP:
    """f1: HP ratio is in [-1, 1]; ally full HP vs rival half HP → f1 > 0."""

    def test_ally_hp_advantage_positive(self):
        """Spec: ally full HP, rival at half HP, pesos=[1,0,0,0] → result > 0."""
        aliado = FakeEntrenador("A", [
            FakePokemon(hp=100, max_hp=100, spe=50, moves=[FakeMove(type="Normal")]) for _ in range(4)
        ])
        rival = FakeEntrenador("R", [
            FakePokemon(hp=50, max_hp=100, spe=50, moves=[FakeMove(type="Normal")]) for _ in range(4)
        ])
        result = evaluar_heuristica_nivel3(aliado, rival, [1.0, 0.0, 0.0, 0.0])
        assert result > 0.0
        assert result <= 1.0

    def test_rival_hp_advantage_negative(self):
        aliado = FakeEntrenador("A", [
            FakePokemon(hp=50, max_hp=100, spe=50, moves=[FakeMove(type="Normal")]) for _ in range(4)
        ])
        rival = FakeEntrenador("R", [
            FakePokemon(hp=100, max_hp=100, spe=50, moves=[FakeMove(type="Normal")]) for _ in range(4)
        ])
        result = evaluar_heuristica_nivel3(aliado, rival, [1.0, 0.0, 0.0, 0.0])
        assert result < 0.0
        assert result >= -1.0

    def test_hp_factor_bounds_never_exceed_one(self):
        """Even in extreme all-dead vs all-alive, f1 stays in [-1, 1]."""
        aliado = FakeEntrenador("A", [
            FakePokemon(hp=100, max_hp=100, spe=50, moves=[FakeMove(type="Normal")]) for _ in range(4)
        ])
        rival = FakeEntrenador("R", [
            FakePokemon(hp=0, max_hp=100, spe=50, moves=[FakeMove(type="Normal")]) for _ in range(4)
        ])
        result = evaluar_heuristica_nivel3(aliado, rival, [1.0, 0.0, 0.0, 0.0])
        assert -1.0 <= result <= 1.0

    def test_hp_does_not_mutate_inputs(self):
        """Spec: inputs (hp values) are unchanged after the call."""
        aliado = FakeEntrenador("A", [
            FakePokemon(hp=100, max_hp=100, spe=50, moves=[FakeMove(type="Normal")]) for _ in range(4)
        ])
        rival = FakeEntrenador("R", [
            FakePokemon(hp=50, max_hp=100, spe=50, moves=[FakeMove(type="Normal")]) for _ in range(4)
        ])
        before_a = [p.hp for p in aliado.pokemones]
        before_r = [p.hp for p in rival.pokemones]
        evaluar_heuristica_nivel3(aliado, rival, [1.0, 0.0, 0.0, 0.0])
        assert [p.hp for p in aliado.pokemones] == before_a
        assert [p.hp for p in rival.pokemones] == before_r


class TestFactorAlive:
    """f2: alive-count ratio in [-1, 1]; symmetric → 0; ally advantage → > 0."""

    def test_symmetric_alive_zero(self):
        aliado, rival = _make_symmetric_trainers()
        result = evaluar_heuristica_nivel3(aliado, rival, [0.0, 1.0, 0.0, 0.0])
        assert result == pytest.approx(0.0, abs=1e-9)

    def test_ally_more_alive_positive(self):
        aliado = FakeEntrenador("A", [
            FakePokemon(hp=100, max_hp=100, spe=50, moves=[FakeMove(type="Normal")]) for _ in range(4)
        ])
        rival = FakeEntrenador("R", [
            FakePokemon(hp=0, max_hp=100, spe=50, moves=[FakeMove(type="Normal")]),
            FakePokemon(hp=0, max_hp=100, spe=50, moves=[FakeMove(type="Normal")]),
            FakePokemon(hp=100, max_hp=100, spe=50, moves=[FakeMove(type="Normal")]),
            FakePokemon(hp=100, max_hp=100, spe=50, moves=[FakeMove(type="Normal")]),
        ])
        result = evaluar_heuristica_nivel3(aliado, rival, [0.0, 1.0, 0.0, 0.0])
        assert result > 0.0
        assert result <= 1.0

    def test_alive_factor_bounds(self):
        aliado = FakeEntrenador("A", [
            FakePokemon(hp=100, max_hp=100, spe=50, moves=[FakeMove(type="Normal")]) for _ in range(4)
        ])
        rival = FakeEntrenador("R", [
            FakePokemon(hp=0, max_hp=100, spe=50, moves=[FakeMove(type="Normal")]) for _ in range(4)
        ])
        result = evaluar_heuristica_nivel3(aliado, rival, [0.0, 1.0, 0.0, 0.0])
        assert -1.0 <= result <= 1.0


class TestFactorSpeed:
    """f3: speed ratio of active Pokémon; in [-1, 1]; symmetric → 0."""

    def test_symmetric_speed_zero(self):
        aliado, rival = _make_symmetric_trainers(spe=100)
        result = evaluar_heuristica_nivel3(aliado, rival, [0.0, 0.0, 1.0, 0.0])
        assert result == pytest.approx(0.0, abs=1e-9)

    def test_ally_faster_positive(self):
        aliado = FakeEntrenador("A", [FakePokemon(spe=200, moves=[FakeMove(type="Normal")])])
        rival = FakeEntrenador("R", [FakePokemon(spe=50, moves=[FakeMove(type="Normal")])])
        result = evaluar_heuristica_nivel3(aliado, rival, [0.0, 0.0, 1.0, 0.0])
        assert result > 0.0
        assert result <= 1.0

    def test_rival_faster_negative(self):
        aliado = FakeEntrenador("A", [FakePokemon(spe=50, moves=[FakeMove(type="Normal")])])
        rival = FakeEntrenador("R", [FakePokemon(spe=200, moves=[FakeMove(type="Normal")])])
        result = evaluar_heuristica_nivel3(aliado, rival, [0.0, 0.0, 1.0, 0.0])
        assert result < 0.0
        assert result >= -1.0

    def test_speed_zero_both_returns_zero(self):
        """Edge case: both active Pokémon have spe=0 → f3=0 (no div-by-zero)."""
        aliado = FakeEntrenador("A", [FakePokemon(spe=0, moves=[FakeMove(type="Normal")])])
        rival = FakeEntrenador("R", [FakePokemon(spe=0, moves=[FakeMove(type="Normal")])])
        result = evaluar_heuristica_nivel3(aliado, rival, [0.0, 0.0, 1.0, 0.0])
        assert math.isfinite(result)
        assert result == pytest.approx(0.0, abs=1e-9)


class TestFactorType:
    """f4: type-advantage factor; in [-1, 1].

    Design formulas:
      adv(e) = clamp(log2(max(e, 0.125)) / 2, -1, 1)
      e=1   → adv=0  (neutral)
      e=2   → adv=0.5
      e=4   → adv=1.0
      e=0.5 → adv=-0.5
      e=0.25 → adv=-1.0
      e=0   → adv=-1.0 (treated as 0.125)
    """

    def test_neutral_effectiveness_zero_advantage(self):
        """Normal vs Normal → eff=1 → adv=0 → f4=0."""
        aliado = FakeEntrenador("A", [
            FakePokemon(types=["Normal"], moves=[FakeMove(type="Normal")], spe=50)
        ])
        rival = FakeEntrenador("R", [
            FakePokemon(types=["Normal"], moves=[FakeMove(type="Normal")], spe=50)
        ])
        result = evaluar_heuristica_nivel3(aliado, rival, [0.0, 0.0, 0.0, 1.0])
        assert result == pytest.approx(0.0, abs=1e-9)

    def test_supereffective_advantage_positive(self):
        """Ally has super-effective move (e=2), rival neutral → f4 > 0."""
        aliado = FakeEntrenador("A", [
            FakePokemon(types=["Fire"], moves=[FakeMove(type="Fire")], spe=50)
        ])
        rival = FakeEntrenador("R", [
            FakePokemon(types=["Grass"], moves=[FakeMove(type="Normal")], spe=50)
        ])
        result = evaluar_heuristica_nivel3(aliado, rival, [0.0, 0.0, 0.0, 1.0])
        assert result > 0.0
        assert result <= 1.0

    def test_effectiveness_4x_advantage_maps_to_one(self):
        """Fire vs Grass+Ice (both 2x) = 4x eff → adv=1; rival neutral → f4=1.0."""
        aliado = FakeEntrenador("A", [
            FakePokemon(types=["Fire"], moves=[FakeMove(type="Fire")], spe=50)
        ])
        rival = FakeEntrenador("R", [
            FakePokemon(types=["Grass", "Ice"], moves=[FakeMove(type="Normal")], spe=50)
        ])
        result = evaluar_heuristica_nivel3(aliado, rival, [0.0, 0.0, 0.0, 1.0])
        assert result == pytest.approx(1.0, abs=1e-9)

    def test_effectiveness_zero_maps_to_minus_one(self):
        """Normal vs Ghost (immune, eff=0, clamped to 0.125 → adv=-1); rival neutral → f4=-1."""
        aliado = FakeEntrenador("A", [
            FakePokemon(types=["Normal"], moves=[FakeMove(type="Normal")], spe=50)
        ])
        rival = FakeEntrenador("R", [
            # Ghost is immune to Normal moves
            FakePokemon(types=["Ghost"], moves=[FakeMove(type="Normal")], spe=50)
        ])
        result = evaluar_heuristica_nivel3(aliado, rival, [0.0, 0.0, 0.0, 1.0])
        assert result == pytest.approx(-1.0, abs=1e-9)

    def test_type_factor_bounds(self):
        """f4 never exceeds [-1, 1]."""
        aliado = FakeEntrenador("A", [
            FakePokemon(types=["Fire"], moves=[FakeMove(type="Fire")], spe=50)
        ])
        rival = FakeEntrenador("R", [
            FakePokemon(types=["Grass", "Ice"], moves=[FakeMove(type="Water")], spe=50)
        ])
        result = evaluar_heuristica_nivel3(aliado, rival, [0.0, 0.0, 0.0, 1.0])
        assert -1.0 <= result <= 1.0

    def test_no_available_moves_zero_advantage(self):
        """If aliado active has no available moves → eff_a defaults to 1.0 → adv_a=0."""
        exhausted_move = FakeMove(available=False)
        aliado = FakeEntrenador("A", [
            FakePokemon(types=["Fire"], moves=[exhausted_move], spe=50)
        ])
        rival = FakeEntrenador("R", [
            FakePokemon(types=["Grass"], moves=[FakeMove(type="Normal")], spe=50)
        ])
        result = evaluar_heuristica_nivel3(aliado, rival, [0.0, 0.0, 0.0, 1.0])
        # adv_a = adv(1.0) = 0; adv_r = adv(eff of Normal vs Fire) = adv(0.5) = -0.5
        # f4 = clamp(0 - (-0.5), -1, 1) = 0.5 → result = 0.5
        assert math.isfinite(result)
        assert -1.0 <= result <= 1.0


class TestCombinedWeightedSum:
    """Combined: w1*f1 + w2*f2 + w3*f3 + w4*f4 with no extra normalization."""

    def test_only_hp_weight(self):
        aliado = FakeEntrenador("A", [
            FakePokemon(hp=100, max_hp=100, spe=50, moves=[FakeMove(type="Normal")]) for _ in range(4)
        ])
        rival = FakeEntrenador("R", [
            FakePokemon(hp=50, max_hp=100, spe=50, moves=[FakeMove(type="Normal")]) for _ in range(4)
        ])
        # Only f1 is non-zero. Manual: hp_a=4.0, hp_r=2.0 → f1=(4-2)/max(6,1e-9)=1/3
        result = evaluar_heuristica_nivel3(aliado, rival, [3.0, 0.0, 0.0, 0.0])
        expected_f1 = (4.0 - 2.0) / max(4.0 + 2.0, 1e-9)  # = 1/3
        assert result == pytest.approx(3.0 * expected_f1, rel=1e-6)

    def test_result_is_finite(self):
        aliado, rival = _make_symmetric_trainers()
        result = evaluar_heuristica_nivel3(aliado, rival, [1.0, 1.0, 1.0, 1.0])
        assert math.isfinite(result)

    def test_weights_scale_result(self):
        """Doubling all weights doubles the result (linearity)."""
        aliado = FakeEntrenador("A", [
            FakePokemon(hp=100, max_hp=100, spe=200, moves=[FakeMove(type="Normal")]) for _ in range(4)
        ])
        rival = FakeEntrenador("R", [
            FakePokemon(hp=50, max_hp=100, spe=50, moves=[FakeMove(type="Normal")]) for _ in range(4)
        ])
        result1 = evaluar_heuristica_nivel3(aliado, rival, [1.0, 1.0, 1.0, 1.0])
        result2 = evaluar_heuristica_nivel3(aliado, rival, [2.0, 2.0, 2.0, 2.0])
        assert result2 == pytest.approx(2.0 * result1, rel=1e-6)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TASK 1.2 — elegir_movimiento_nivel3 returns a Movimiento or None
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class FakeBattleForChooser:
    """Minimal Battle-compatible stub so the minimax clone doesn't blow up."""

    def __init__(self, t1, t2):
        self.entrenador1 = t1
        self.entrenador2 = t2

    def is_battle_over(self):
        return not self.entrenador1.has_usable_pokemon() or not self.entrenador2.has_usable_pokemon()


class TestElegirMovimientoNivel3:
    """Spec: chooser returns a Movimiento from real available_moves, or None when exhausted."""

    def _make_simple_pair(self):
        """Two trainers with 1 Pokémon each and 2 deterministic moves."""
        move_a = FakeMove(name="flamethrower", type="Fire", power=90, category="Special")
        move_b = FakeMove(name="tackle", type="Normal", power=40, category="Physical")
        poke_ia = FakePokemon(
            name="Aliado",
            types=["Fire"],
            hp=100, max_hp=100, spe=100,
            atk=100, defense=60, spa=120, spd=60,
            moves=[move_a, move_b],
        )
        poke_rival = FakePokemon(
            name="Rival",
            types=["Grass"],
            hp=100, max_hp=100, spe=80,
            atk=80, defense=80, spa=80, spd=80,
            moves=[FakeMove(name="vinewhip", type="Grass", power=45, category="Physical")],
        )
        ia = FakeEntrenador("IA", [poke_ia])
        rival = FakeEntrenador("Rival", [poke_rival])
        return ia, rival

    def test_returns_movimiento_in_available_moves(self):
        """Spec: GIVEN active pokemon with available_moves, WHEN chooser runs,
        THEN it returns a Movimiento present in real available_moves."""
        ia, rival = self._make_simple_pair()
        pesos = [1.0, 1.0, 0.5, 1.0]
        result = elegir_movimiento_nivel3(ia, rival, pesos)
        real_names = [m.name for m in ia.get_current_pokemon().available_moves]
        assert result is not None
        assert result.name in real_names

    def test_returns_none_when_no_available_moves(self):
        """When all moves are exhausted, chooser returns None."""
        exhausted = FakeMove(available=False)
        poke_ia = FakePokemon(
            name="Aliado",
            types=["Normal"],
            hp=100, max_hp=100, spe=100,
            moves=[exhausted],
        )
        poke_rival = FakePokemon(
            name="Rival",
            types=["Normal"],
            hp=100, max_hp=100, spe=80,
            moves=[FakeMove()],
        )
        ia = FakeEntrenador("IA", [poke_ia])
        rival = FakeEntrenador("Rival", [poke_rival])
        result = elegir_movimiento_nivel3(ia, rival, [1.0, 1.0, 1.0, 1.0])
        assert result is None

    def test_does_not_mutate_real_hp(self):
        """Chooser must NOT mutate the real trainer Pokémon HP."""
        ia, rival = self._make_simple_pair()
        original_ia_hp = ia.get_current_pokemon().hp
        original_rival_hp = rival.get_current_pokemon().hp
        elegir_movimiento_nivel3(ia, rival, [1.0, 1.0, 0.5, 1.0])
        assert ia.get_current_pokemon().hp == original_ia_hp
        assert rival.get_current_pokemon().hp == original_rival_hp

    def test_different_weights_return_valid_move(self):
        """Chooser works correctly with arbitrary weight vectors."""
        ia, rival = self._make_simple_pair()
        for pesos in [[0.0, 0.0, 0.0, 0.0], [0.5, 0.5, 0.5, 0.5], [2.0, 0.0, 1.0, 3.0]]:
            result = elegir_movimiento_nivel3(ia, rival, pesos)
            if result is not None:
                real_names = [m.name for m in ia.get_current_pokemon().available_moves]
                assert result.name in real_names
