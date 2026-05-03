from ..models.pokemon import Pokemon
from ..models.movimientos import Movimiento

# Tabla de tipos (asegúrate de que esté completa)
TYPE_CHART = {
    "Normal": {"Rock": 0.5, "Ghost": 0, "Steel": 0.5},

    "Fire": {
        "Fire": 0.5, "Water": 0.5, "Grass": 2, "Ice": 2,
        "Bug": 2, "Rock": 0.5, "Dragon": 0.5, "Steel": 2
    },

    "Water": {
        "Fire": 2, "Water": 0.5, "Grass": 0.5,
        "Ground": 2, "Rock": 2, "Dragon": 0.5
    },

    "Electric": {
        "Water": 2, "Electric": 0.5, "Grass": 0.5,
        "Ground": 0, "Flying": 2, "Dragon": 0.5
    },

    "Grass": {
        "Fire": 0.5, "Water": 2, "Grass": 0.5,
        "Poison": 0.5, "Ground": 2, "Flying": 0.5,
        "Bug": 0.5, "Rock": 2, "Dragon": 0.5, "Steel": 0.5
    },

    "Ice": {
        "Fire": 0.5, "Water": 0.5, "Grass": 2,
        "Ground": 2, "Flying": 2, "Dragon": 2, "Steel": 0.5
    },

    "Fighting": {
        "Normal": 2, "Ice": 2, "Rock": 2, "Dark": 2, "Steel": 2,
        "Poison": 0.5, "Flying": 0.5, "Psychic": 0.5,
        "Bug": 0.5, "Fairy": 0.5, "Ghost": 0
    },

    "Poison": {
        "Grass": 2, "Fairy": 2,
        "Poison": 0.5, "Ground": 0.5, "Rock": 0.5, "Ghost": 0.5,
        "Steel": 0
    },

    "Ground": {
        "Fire": 2, "Electric": 2, "Grass": 0.5,
        "Poison": 2, "Flying": 0,
        "Bug": 0.5, "Rock": 2, "Steel": 2
    },

    "Flying": {
        "Electric": 0.5, "Grass": 2, "Fighting": 2,
        "Bug": 2, "Rock": 0.5, "Steel": 0.5
    },

    "Psychic": {
        "Fighting": 2, "Poison": 2,
        "Psychic": 0.5, "Steel": 0.5, "Dark": 0
    },

    "Bug": {
        "Fire": 0.5, "Grass": 2, "Fighting": 0.5,
        "Poison": 0.5, "Flying": 0.5,
        "Psychic": 2, "Ghost": 0.5,
        "Dark": 2, "Steel": 0.5, "Fairy": 0.5
    },

    "Rock": {
        "Fire": 2, "Ice": 2, "Flying": 2, "Bug": 2,
        "Fighting": 0.5, "Ground": 0.5, "Steel": 0.5
    },

    "Ghost": {
        "Normal": 0, "Psychic": 2, "Ghost": 2, "Dark": 0.5
    },

    "Dragon": {
        "Dragon": 2, "Steel": 0.5, "Fairy": 0
    },

    "Dark": {
        "Fighting": 0.5, "Psychic": 2,
        "Ghost": 2, "Dark": 0.5, "Fairy": 0.5
    },

    "Steel": {
        "Fire": 0.5, "Water": 0.5, "Electric": 0.5,
        "Ice": 2, "Rock": 2, "Fairy": 2, "Steel": 0.5
    },

    "Fairy": {
        "Fire": 0.5, "Fighting": 2, "Dragon": 2,
        "Dark": 2, "Poison": 0.5, "Steel": 0.5
    }
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