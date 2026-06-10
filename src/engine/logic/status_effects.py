import random

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

# Inmunidades por tipo (como en los juegos: el fuego no se quema, etc.)
STATUS_TYPE_IMMUNITY = {
    "brn": {"Fire"},
    "par": {"Electric"},
    "psn": {"Poison", "Steel"},
    "frz": {"Ice"},
    "slp": set(),
}

STATUS_APPLY_MESSAGES = {
    "brn": "¡{name} sufrió quemaduras!",
    "par": "¡{name} fue paralizado! Quizás no pueda moverse.",
    "psn": "¡{name} fue envenenado!",
    "slp": "¡{name} se durmió!",
    "frz": "¡{name} fue congelado!",
}


def _roll(chance_pct: float) -> bool:
    """True si un d100 cae por debajo de `chance_pct`."""
    return random.random() * 100 < chance_pct


def pre_move_check(pokemon) -> tuple[bool, list[str]]:
    """
    Chequeos previos al ataque: sueño, congelación, parálisis y confusión.
    Devuelve (puede_actuar, logs). Puede modificar al pokémon (descuento de
    turnos, descongelado, autogolpe por confusión).
    """
    logs: list[str] = []

    if pokemon.status == "slp":
        pokemon.decreasestatus_turn()
        if pokemon.status == "slp":
            logs.append(f"{pokemon.name} está profundamente dormido.")
            return False, logs
        logs.append(f"¡{pokemon.name} se despertó!")
    elif pokemon.status == "frz":
        if _roll(STATUS_RULES["frz"]["thaw_chance"]):
            pokemon.status = "No State"
            logs.append(f"¡{pokemon.name} se descongeló!")
        else:
            logs.append(f"{pokemon.name} está congelado. No puede moverse.")
            return False, logs
    elif pokemon.status == "par":
        if _roll(STATUS_RULES["par"]["skip_turn_chance"]):
            logs.append(f"{pokemon.name} está paralizado. ¡No puede moverse!")
            return False, logs

    if pokemon.volatile_status == "confusion":
        pokemon.decrease_volatile_turn()
        if pokemon.volatile_status == "confusion":
            logs.append(f"{pokemon.name} está confuso.")
            rule = VOLATILE_STATUS_RULES["confusion"]
            if _roll(rule["self_hit_chance"]):
                # Autogolpe: físico sin tipo, mismo amortiguador 0.35 del motor
                power = rule["self_hit_power"]
                raw = (((2 * pokemon.level / 5 + 2) * power
                        * (pokemon.atk / pokemon.defense)) / 50 + 2) * 0.35
                pokemon.hp = max(0, pokemon.hp - max(1, int(raw)))
                logs.append(f"¡{pokemon.name} se hirió a sí mismo en su confusión!")
                return False, logs
        else:
            logs.append(f"¡{pokemon.name} se libró de la confusión!")

    return True, logs


def _set_status(pokemon, code: str, logs: list[str]) -> bool:
    """Aplica un estado principal respetando inmunidades de tipo."""
    if any(t in STATUS_TYPE_IMMUNITY.get(code, set()) for t in pokemon.types):
        return False
    pokemon.status = code
    if code == "slp":
        rule = STATUS_RULES["slp"]
        pokemon.status_turns = random.randint(rule["min_turns"], rule["max_turns"])
    logs.append(STATUS_APPLY_MESSAGES[code].format(name=pokemon.name))
    return True


def try_apply_move_status(defender, move) -> list[str]:
    """
    Efectos de estado de un movimiento que conectó:
    - direct_status: movimientos de estado puro (Thunder Wave, Will-O-Wisp…)
    - secondary_status / secondary_volatile: efectos con probabilidad
    """
    logs: list[str] = []
    if defender.hp <= 0:
        return logs

    if move.direct_status and move.direct_status in STATUS_RULES:
        if defender.status != "No State" or not _set_status(defender, move.direct_status, logs):
            logs.append("¡Pero falló!")

    if move.secondary_status and move.secondary_status in STATUS_RULES:
        if defender.status == "No State" and _roll(move.secondary_chance):
            _set_status(defender, move.secondary_status, logs)

    if move.secondary_volatile == "confusion" and defender.volatile_status == "No State":
        if _roll(move.secondary_chance):
            rule = VOLATILE_STATUS_RULES["confusion"]
            defender.volatile_status = "confusion"
            defender.volatile_turns = random.randint(rule["min_turns"], rule["max_turns"])
            logs.append(f"¡{defender.name} se confundió!")

    return logs


def end_of_turn_residuals(pokemon) -> list[str]:
    """Daño residual de quemadura/veneno al final del turno."""
    logs: list[str] = []
    if pokemon.hp <= 0:
        return logs
    rule = STATUS_RULES.get(pokemon.status)
    if rule and rule.get("residual_damage_pct"):
        dmg = max(1, int(pokemon.max_hp * rule["residual_damage_pct"]))
        pokemon.hp = max(0, pokemon.hp - dmg)
        label = "su quemadura" if pokemon.status == "brn" else "el veneno"
        logs.append(f"{pokemon.name} sufre por {label}. (-{dmg} PS)")
    return logs