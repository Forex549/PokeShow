from ..models.pokemon import Pokemon
from ..models.movimientos import Movimiento

# Tabla de tipos (asegúrate de que esté completa)
TYPE_CHART = {
    "Fire": {"Grass": 2, "Water": 0.5},
    "Water": {"Fire": 2, "Grass": 0.5},
    "Electric": {"Water": 2, "Ground": 0},
    "Ground": {"Electric": 2, "Flying": 0},
}

def get_effectiveness(move_type: str, defender_types: list[str]) -> float:
    multiplier = 1.0
    for t in defender_types:
        if move_type in TYPE_CHART and t in TYPE_CHART.get(move_type, {}):
            multiplier *= TYPE_CHART[move_type][t]
    return multiplier

def calculate_damage(attacker: Pokemon, defender: Pokemon, move: Movimiento) -> int:
    if move.category not in ["Physical", "Special"]:
        return 0

    # USANDO TUS PROPIEDADES: atk, spa, defense, spd
    if move.category == "Physical":
        atk_val = attacker.atk
        def_val = defender.defense
    else:
        atk_val = attacker.spa
        def_val = defender.spd

    # Tu fórmula original de la demo
    base_dmg = ((2 * 50 / 5 + 2) * move.power * (atk_val / def_val)) / 50 + 2

    # STAB (Same Type Attack Bonus)
    stab = 1.5 if move.type in attacker.types else 1.0
    
    # Efectividad elemental
    eff = get_effectiveness(move.type, defender.types)

    final_damage = base_dmg * stab * eff

    if eff == 0: 
        return 0
    return max(1, int(final_damage))