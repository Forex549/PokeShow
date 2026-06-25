import copy
import math
from random import choice
from typing import Optional, Union

from ..models.pokemon import Pokemon
from ..models.movimientos import Movimiento
from ..models.entrenador import Entrenador
from ..models.battle import Battle
from .damage_calc import calculate_damage, get_effectiveness

def choose_best_move(my_poke: Pokemon, enemy_poke: Pokemon) -> Movimiento:
    best_move: Movimiento = my_poke.moves[0]
    best_score: float = float("-inf")

    for move in my_poke.available_moves:
        dmg, _ = calculate_damage(my_poke, enemy_poke, move)
        if dmg > best_score:
            best_score = dmg
            best_move = move

    return best_move

def chose_random_move(my_poke: Pokemon) -> Optional[Movimiento]:
    if not my_poke.available_moves:
        return None
    return choice(my_poke.available_moves)

def evaluar_heuristica_hp_nivel2(entrenador_aliado: Entrenador, entrenador_rival: Entrenador) -> float:
    """
    Calcula la puntuación del estado actual basándose ÚNICAMENTE en la diferencia de HP
    de ambos equipos
    Puntuación positiva = Ventaja para el aliado.
    Puntuación negativa = Desventaja (Ventaja para el rival).
    """
    # Calculamos el porcentaje de vida total de cada equipo.
    pct_vida_aliado = 0.0
    for p in entrenador_aliado.pokemones:
        pct_vida_aliado += (p.hp / p.max_hp)

    pct_vida_rival = 0.0
    for p in entrenador_rival.pokemones:
        pct_vida_rival += (p.hp / p.max_hp)

    # Retorna la diferencia
    return pct_vida_aliado - pct_vida_rival


def _score_matchup(atacante: Pokemon, rival: Pokemon) -> float:
    # Proxy de daño esperado: potencia × efectividad de tipo × STAB
    # No llama a calculate_damage para evitar aleatoriedad de crits y prints de debug
    if not atacante.available_moves:
        return 0.0
    return max(
        m.power * get_effectiveness(m.type, rival.types) * (1.5 if m.type in atacante.types else 1.0)
        for m in atacante.available_moves
    )


def elegir_mejor_sustituto(entrenador: Entrenador, rival: Entrenador) -> Optional[int]:
    # Nivel greedy: elige al sustituto que más daño puede hacer al rival activo
    rival_activo = rival.get_current_pokemon()
    mejor_idx = None
    mejor_score = float('-inf')
    for i, p in enumerate(entrenador.pokemones):
        if p.hp <= 0 or i == entrenador.current_pokemon_index:
            continue
        score = _score_matchup(p, rival_activo)
        if score > mejor_score:
            mejor_score = score
            mejor_idx = i
    return mejor_idx


def elegir_mejor_sustituto_n2(entrenador: Entrenador, rival: Entrenador) -> Optional[int]:
    # Nivel minimax: considera tanto el daño que podemos hacer como el que nos pueden hacer
    # score = amenaza nuestra - amenaza rival → ventaja neta del matchup
    rival_activo = rival.get_current_pokemon()
    mejor_idx = None
    mejor_score = float('-inf')
    for i, p in enumerate(entrenador.pokemones):
        if p.hp <= 0 or i == entrenador.current_pokemon_index:
            continue
        score = _score_matchup(p, rival_activo) - _score_matchup(rival_activo, p)
        if score > mejor_score:
            mejor_score = score
            mejor_idx = i
    return mejor_idx


def elegir_mejor_sustituto_n3(entrenador: Entrenador, rival: Entrenador, pesos: list) -> Optional[int]:
    # Nivel 3: evalúa cada candidato con la heurística completa de 4 factores
    # Requiere deepcopy para que f3 (velocidad) y f4 (tipo) reflejen al candidato como activo
    mejor_idx = None
    mejor_score = float('-inf')
    for i, p in enumerate(entrenador.pokemones):
        if p.hp <= 0 or i == entrenador.current_pokemon_index:
            continue
        ia_clon = copy.deepcopy(entrenador)
        ia_clon.switch_pokemon(i)
        score = evaluar_heuristica_nivel3(ia_clon, rival, pesos)
        if score > mejor_score:
            mejor_score = score
            mejor_idx = i
    return mejor_idx


def minimax_alfa_beta(
    battle_clone: Battle, 
    profundidad: int, 
    alfa: float, 
    beta: float, 
    es_maximizando: bool, # Para diferenciar si es el turno de la IA (maximizar) o del rival (minimizar)
    entrenador_ia: Entrenador,
    entrenador_rival: Entrenador
) -> float:
    """
    Algoritmo Minimax con Poda Alfa-Beta para simular el mejor escenario de HP.
    """
    # Caso base: Llegamos al límite de predicción o la batalla terminó en la simulación
    if profundidad == 0 or battle_clone.is_battle_over():
        return evaluar_heuristica_hp_nivel2(entrenador_ia, entrenador_rival)

    poke_ia = entrenador_ia.get_current_pokemon()
    poke_rival = entrenador_rival.get_current_pokemon()

    if es_maximizando:
        max_eval = float("-inf")
        for move_ia in poke_ia.available_moves:
            dmg_a_rival, _ = calculate_damage(poke_ia, poke_rival, move_ia)
            hp_original = poke_rival.hp
            poke_rival.hp -= dmg_a_rival

            evaluacion = minimax_alfa_beta(battle_clone, profundidad - 1, alfa, beta, False, entrenador_ia, entrenador_rival)
            poke_rival.hp = hp_original  # restauramos para que la siguiente rama parta del estado correcto

            max_eval = max(max_eval, evaluacion)
            alfa = max(alfa, evaluacion)
            if beta <= alfa:
                break
        return max_eval

    else:
        min_eval = float("inf")
        for move_rival in poke_rival.available_moves:
            dmg_a_ia, _ = calculate_damage(poke_rival, poke_ia, move_rival)
            hp_original = poke_ia.hp
            poke_ia.hp -= dmg_a_ia

            evaluacion = minimax_alfa_beta(battle_clone, profundidad - 1, alfa, beta, True, entrenador_ia, entrenador_rival)
            poke_ia.hp = hp_original  # restauramos para que la siguiente rama parta del estado correcto

            min_eval = min(min_eval, evaluacion)
            beta = min(beta, evaluacion)
            if beta <= alfa:
                break
        return min_eval


def elegir_movimiento_nivel2(entrenador: Entrenador, rival: Entrenador) -> Optional[Movimiento]:
    # Versión limpia del minimax nivel 2 sin prints, para que el GA pueda usarla
    poke_real = entrenador.get_current_pokemon()

    if not poke_real.available_moves:
        return None

    ia_clon = copy.deepcopy(entrenador)
    rival_clon = copy.deepcopy(rival)

    batalla_simulada = Battle(ia_clon, rival_clon)

    poke_ia_clon = ia_clon.get_current_pokemon()
    poke_rival_clon = rival_clon.get_current_pokemon()

    best_move_name: Optional[str] = None
    best_value = float("-inf")

    for move_clon in poke_ia_clon.available_moves:
        dmg, _ = calculate_damage(poke_ia_clon, poke_rival_clon, move_clon)

        hp_original_rival = poke_rival_clon.hp
        poke_rival_clon.hp -= dmg

        valor_futuro = minimax_alfa_beta(
            battle_clone=batalla_simulada,
            profundidad=3,
            alfa=float("-inf"),
            beta=float("inf"),
            es_maximizando=False,
            entrenador_ia=ia_clon,
            entrenador_rival=rival_clon,
        )

        poke_rival_clon.hp = hp_original_rival

        if valor_futuro > best_value:
            best_value = valor_futuro
            best_move_name = move_clon.name

    if best_move_name is not None:
        for move_real in poke_real.available_moves:
            if move_real.name == best_move_name:
                return move_real

    return poke_real.available_moves[0] if poke_real.available_moves else None


# ── Nivel 3: weight-parameterised heuristic ──────────────────────────────────


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def _factor_hp(aliado: Entrenador, rival: Entrenador) -> float:
    # Comparamos el porcentaje de HP total de cada equipo
    # Resultado positivo = vamos ganando en vida, negativo = vamos perdiendo
    hp_a = sum(p.hp / p.max_hp for p in aliado.pokemones)
    hp_r = sum(p.hp / p.max_hp for p in rival.pokemones)
    return (hp_a - hp_r) / max(hp_a + hp_r, 1e-9)


def _factor_alive(aliado: Entrenador, rival: Entrenador) -> float:
    # Cuántos pokémon siguen en pie de cada lado
    viv_a = sum(1 for p in aliado.pokemones if p.hp > 0)
    viv_r = sum(1 for p in rival.pokemones if p.hp > 0)
    return (viv_a - viv_r) / max(viv_a + viv_r, 1)


def _factor_speed(aliado: Entrenador, rival: Entrenador) -> float:
    # Velocidad del pokémon activo de cada lado (ya incluye penalización por parálisis)
    spe_a = aliado.get_current_pokemon().spe
    spe_r = rival.get_current_pokemon().spe
    return (spe_a - spe_r) / max(spe_a + spe_r, 1)


def _eff_to_adv(eff: float) -> float:
    # Pasamos la efectividad cruda a ventaja en [-1, 1] usando log2
    # efectividad 0 o 0.25 → -1, 0.5 → -0.5, 1 → 0, 2 → 0.5, 4 → 1
    return _clamp(math.log2(max(eff, 0.125)) / 2, -1.0, 1.0)


def _factor_type(aliado: Entrenador, rival: Entrenador) -> float:
    # Ventaja de tipo: buscamos el movimiento con mejor efectividad para cada lado
    # Usamos solo efectividad (sin calcular daño) para que sea rápido y puro
    aliado_active = aliado.get_current_pokemon()
    rival_active = rival.get_current_pokemon()

    if aliado_active.available_moves:
        eff_a = max(
            get_effectiveness(m.type, rival_active.types)
            for m in aliado_active.available_moves
        )
    else:
        eff_a = 1.0

    if rival_active.available_moves:
        eff_r = max(
            get_effectiveness(m.type, aliado_active.types)
            for m in rival_active.available_moves
        )
    else:
        eff_r = 1.0

    adv_a = _eff_to_adv(eff_a)
    adv_r = _eff_to_adv(eff_r)
    return _clamp(adv_a - adv_r, -1.0, 1.0)


def evaluar_heuristica_nivel3(
    aliado: Entrenador,
    rival: Entrenador,
    pesos: list,
) -> float:
    # Evaluador del nivel 3: combina los 4 factores con pesos ajustables
    # No modifica nada, solo lee el estado y devuelve un número
    w1, w2, w3, w4 = pesos[0], pesos[1], pesos[2], pesos[3]
    f1 = _factor_hp(aliado, rival)
    f2 = _factor_alive(aliado, rival)
    f3 = _factor_speed(aliado, rival)
    f4 = _factor_type(aliado, rival)
    return w1 * f1 + w2 * f2 + w3 * f3 + w4 * f4


def minimax_alfa_beta_n3(
    battle_clone: Battle,
    profundidad: int,
    alfa: float,
    beta: float,
    es_maximizando: bool,
    entrenador_ia: Entrenador,
    entrenador_rival: Entrenador,
    pesos: list,
) -> float:
    if profundidad == 0 or battle_clone.is_battle_over():
        return evaluar_heuristica_nivel3(entrenador_ia, entrenador_rival, pesos)

    poke_ia = entrenador_ia.get_current_pokemon()
    poke_rival = entrenador_rival.get_current_pokemon()

    if es_maximizando:
        max_eval = float("-inf")
        for move_ia in poke_ia.available_moves:
            dmg_a_rival, _ = calculate_damage(poke_ia, poke_rival, move_ia)
            hp_original = poke_rival.hp
            poke_rival.hp -= dmg_a_rival
            evaluacion = minimax_alfa_beta_n3(
                battle_clone, profundidad - 1, alfa, beta, False,
                entrenador_ia, entrenador_rival, pesos,
            )
            poke_rival.hp = hp_original
            max_eval = max(max_eval, evaluacion)
            alfa = max(alfa, evaluacion)
            if beta <= alfa:
                break
        return max_eval
    else:
        min_eval = float("inf")
        for move_rival in poke_rival.available_moves:
            dmg_a_ia, _ = calculate_damage(poke_rival, poke_ia, move_rival)
            hp_original = poke_ia.hp
            poke_ia.hp -= dmg_a_ia
            evaluacion = minimax_alfa_beta_n3(
                battle_clone, profundidad - 1, alfa, beta, True,
                entrenador_ia, entrenador_rival, pesos,
            )
            poke_ia.hp = hp_original
            min_eval = min(min_eval, evaluacion)
            beta = min(beta, evaluacion)
            if beta <= alfa:
                break
        return min_eval


def elegir_movimiento_nivel3(
    entrenador: Entrenador,
    rival: Entrenador,
    pesos: list,
) -> Optional[Movimiento]:
    # Elige el mejor movimiento usando el minimax con la heurística de 4 factores
    # Trabajamos sobre clones para no tocar el estado real de la batalla
    poke_real = entrenador.get_current_pokemon()

    if not poke_real.available_moves:
        return None

    ia_clon = copy.deepcopy(entrenador)
    rival_clon = copy.deepcopy(rival)

    batalla_simulada = Battle(ia_clon, rival_clon)

    poke_ia_clon = ia_clon.get_current_pokemon()
    poke_rival_clon = rival_clon.get_current_pokemon()

    best_move_name: Optional[str] = None
    best_value = float("-inf")

    for move_clon in poke_ia_clon.available_moves:
        dmg, _ = calculate_damage(poke_ia_clon, poke_rival_clon, move_clon)

        hp_original_rival = poke_rival_clon.hp
        poke_rival_clon.hp -= dmg

        valor_futuro = minimax_alfa_beta_n3(
            battle_clone=batalla_simulada,
            profundidad=4,
            alfa=float("-inf"),
            beta=float("inf"),
            es_maximizando=False,
            entrenador_ia=ia_clon,
            entrenador_rival=rival_clon,
            pesos=pesos,
        )

        poke_rival_clon.hp = hp_original_rival

        if valor_futuro > best_value:
            best_value = valor_futuro
            best_move_name = move_clon.name

    # Buscamos el movimiento real que corresponde al nombre elegido por el clon
    if best_move_name is not None:
        for move_real in poke_real.available_moves:
            if move_real.name == best_move_name:
                return move_real

    return poke_real.available_moves[0] if poke_real.available_moves else None


# ── Nivel 4: heurística de 5 factores + cambio voluntario ────────────────────

_STATUS_PENALTY: dict = {
    "slp": -1.0,   # sueño: no puede atacar varios turnos
    "frz": -0.9,   # congelado: no puede atacar, 20% thaw por turno
    "par": -0.5,   # parálisis: velocidad a la mitad + 25% skip
    "brn": -0.4,   # quemadura: atk físico a la mitad + daño residual 1/16
    "psn": -0.3,   # veneno: daño residual 1/8
    "No State": 0.0,
}

_VOLATILE_PENALTY: dict = {
    "confusion": -0.3,  # confusión: 33% de golpearse a sí mismo
    "No State": 0.0,
}


def _factor_status(aliado: Entrenador, rival: Entrenador) -> float:
    aa = aliado.get_current_pokemon()
    ra = rival.get_current_pokemon()
    score_a = _STATUS_PENALTY.get(aa.status, 0.0) + _VOLATILE_PENALTY.get(aa.volatile_status, 0.0)
    score_r = _STATUS_PENALTY.get(ra.status, 0.0) + _VOLATILE_PENALTY.get(ra.volatile_status, 0.0)
    score_a = max(-1.0, score_a)
    score_r = max(-1.0, score_r)
    # score_a - score_r: positivo = rival sufre más estados = bueno para nosotros
    return _clamp(score_a - score_r, -1.0, 1.0)


def evaluar_heuristica_nivel4(
    aliado: Entrenador,
    rival: Entrenador,
    pesos: list,
) -> float:
    w1, w2, w3, w4, w5 = pesos[0], pesos[1], pesos[2], pesos[3], pesos[4]
    f1 = _factor_hp(aliado, rival)
    f2 = _factor_alive(aliado, rival)
    f3 = _factor_speed(aliado, rival)
    f4 = _factor_type(aliado, rival)
    f5 = _factor_status(aliado, rival)
    valor = (
        w1 * f1 +
        w2 * f2 +
        w3 * f3 +
        w4 * f4 +
        w5 * f5
    )

    return valor


def minimax_alfa_beta_n4(
    battle_clone: Battle,
    profundidad: int,
    alfa: float,
    beta: float,
    es_maximizando: bool,
    entrenador_ia: Entrenador,
    entrenador_rival: Entrenador,
    pesos: list,
) -> float:
    if profundidad == 0 or battle_clone.is_battle_over():
        return evaluar_heuristica_nivel4(entrenador_ia, entrenador_rival, pesos)

    poke_ia = entrenador_ia.get_current_pokemon()
    poke_rival = entrenador_rival.get_current_pokemon()

    if es_maximizando:
        max_eval = float("-inf")

        for move_ia in poke_ia.available_moves:
            dmg_a_rival, _ = calculate_damage(poke_ia, poke_rival, move_ia)
            hp_original = poke_rival.hp
            poke_rival.hp -= dmg_a_rival
            evaluacion = minimax_alfa_beta_n4(
                battle_clone, profundidad - 1, alfa, beta, False,
                entrenador_ia, entrenador_rival, pesos,
            )
            poke_rival.hp = hp_original
            max_eval = max(max_eval, evaluacion)
            alfa = max(alfa, evaluacion)
            if beta <= alfa:
                break

        idx_ia = entrenador_ia.current_pokemon_index
        for i, p in enumerate(entrenador_ia.pokemones):
            if p.hp <= 0 or i == idx_ia:
                continue
            entrenador_ia.current_pokemon_index = i
            evaluacion = minimax_alfa_beta_n4(
                battle_clone, profundidad - 1, alfa, beta, False,
                entrenador_ia, entrenador_rival, pesos,
            )
            entrenador_ia.current_pokemon_index = idx_ia
            max_eval = max(max_eval, evaluacion)
            alfa = max(alfa, evaluacion)
            if beta <= alfa:
                break
        
        return max_eval

    else:
        min_eval = float("inf")

        for move_rival in poke_rival.available_moves:
            dmg_a_ia, _ = calculate_damage(poke_rival, poke_ia, move_rival)
            hp_original = poke_ia.hp
            poke_ia.hp -= dmg_a_ia
            evaluacion = minimax_alfa_beta_n4(
                battle_clone, profundidad - 1, alfa, beta, True,
                entrenador_ia, entrenador_rival, pesos,
            )
            poke_ia.hp = hp_original
            min_eval = min(min_eval, evaluacion)
            beta = min(beta, evaluacion)
            if beta <= alfa:
                break

        idx_rival = entrenador_rival.current_pokemon_index
        for i, p in enumerate(entrenador_rival.pokemones):
            if p.hp <= 0 or i == idx_rival:
                continue
            entrenador_rival.current_pokemon_index = i
            evaluacion = minimax_alfa_beta_n4(
                battle_clone, profundidad - 1, alfa, beta, True,
                entrenador_ia, entrenador_rival, pesos,
            )
            entrenador_rival.current_pokemon_index = idx_rival
            min_eval = min(min_eval, evaluacion)
            beta = min(beta, evaluacion)
            if beta <= alfa:
                break
        
        return min_eval


def elegir_mejor_sustituto_n4(entrenador: Entrenador, rival: Entrenador, pesos: list) -> Optional[int]:
    mejor_idx = None
    mejor_score = float('-inf')
    for i, p in enumerate(entrenador.pokemones):
        if p.hp <= 0 or i == entrenador.current_pokemon_index:
            continue
        ia_clon = copy.deepcopy(entrenador)
        ia_clon.switch_pokemon(i)
        score = evaluar_heuristica_nivel4(ia_clon, rival, pesos)
        if score > mejor_score:
            mejor_score = score
            mejor_idx = i
    return mejor_idx

def elegir_accion_nivel4(
    entrenador: Entrenador,
    rival: Entrenador,
    pesos: list,
) -> Union[Movimiento, int, None]:

    poke_real = entrenador.get_current_pokemon()

    ia_clon = copy.deepcopy(entrenador)
    rival_clon = copy.deepcopy(rival)
    batalla_simulada = Battle(ia_clon, rival_clon)

    poke_ia_clon = ia_clon.get_current_pokemon()
    poke_rival_clon = rival_clon.get_current_pokemon()

    best_action = None
    best_value = float("-inf")

    print("\n===== EVALUANDO ACCIONES =====")

    # Evaluar movimientos
    for move_clon in poke_ia_clon.available_moves:
        dmg, _ = calculate_damage(
            poke_ia_clon,
            poke_rival_clon,
            move_clon
        )

        hp_original = poke_rival_clon.hp
        poke_rival_clon.hp -= dmg

        valor = minimax_alfa_beta_n4(
            batalla_simulada,
            3,
            float("-inf"),
            float("inf"),
            False,
            ia_clon,
            rival_clon,
            pesos,
        )

        poke_rival_clon.hp = hp_original

        print(
            f"Movimiento {move_clon.name:<20}"
            f" daño={dmg:<4} valor={valor:.4f}"
        )

        if valor > best_value:
            best_value = valor
            best_action = move_clon.name

    # Evaluar cambios
    idx_original = ia_clon.current_pokemon_index

    for i, p in enumerate(ia_clon.pokemones):

        if p.hp <= 0 or i == idx_original:
            continue

        ia_clon.current_pokemon_index = i

        valor = minimax_alfa_beta_n4(
            batalla_simulada,
            3,
            float("-inf"),
            float("inf"),
            False,
            ia_clon,
            rival_clon,
            pesos,
        )

        ia_clon.current_pokemon_index = idx_original

        print(
            f"Cambio a {p.name:<20}"
            f" valor={valor:.4f}"
        )

        if valor > best_value:
            best_value = valor
            best_action = i

    print(f"\nMejor acción encontrada: {best_action}")
    print(f"Mejor valor: {best_value:.4f}")
    print("===============================\n")

    if best_action is None:
        return None

    if isinstance(best_action, int):
        return best_action

    for move_real in poke_real.available_moves:
        if move_real.name == best_action:
            return move_real

    return poke_real.available_moves[0] if poke_real.available_moves else None