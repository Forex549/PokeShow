
# Estados principales (Persisten al cambiar de Pokémon, solo uno a la vez)
STATUS_RULES = {
    "brn": {
        "name": "Quemadura",
        "stat_affected": "atk",
        "multiplier": 0.5,            # Reduce el ataque físico a la mitad
        "residual_damage_pct": 0.0625 # Daño al final del turno (1/16 de HP máx)
    },
    "par": {
        "name": "Parálisis",
        "stat_affected": "spe",
        "multiplier": 0.5,            # Reduce la velocidad a la mitad
        "skip_turn_chance": 25        # 25% de probabilidad de quedar totalmente paralizado
    },
    "psn": {
        "name": "Veneno",
        "stat_affected": None,
        "multiplier": 1.0,
        "residual_damage_pct": 0.125   # Daño al final del turno (1/8 de HP máx)
    },
    "slp": {
        "name": "Sueño",
        "stat_affected": None,
        "multiplier": 1.0,
        "can_attack": False,
        "min_turns": 1,
        "max_turns": 3
    },
    "frz": {
        "name": "Congelación",
        "stat_affected": None,
        "multiplier": 1.0,
        "can_attack": False,
        "thaw_chance": 20              # 20% de probabilidad de descongelarse antes de mover
    }
}

# Estados volatiles (Se eliminan automáticamente al cambiar de Pokémon)
VOLATILE_STATUS_RULES = {
    "confusion": {
        "name": "Confusión",
        "min_turns": 2,
        "max_turns": 5,
        "self_hit_chance": 33,         # 33% de chance de golpearse a sí mismo
        "self_hit_power": 40           # Potencia base del autogolpe
    }
}