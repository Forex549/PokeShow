from random import choice
from typing import Optional

from ..models.pokemon import Pokemon
from ..models.movimientos import Movimiento
from ..models.entrenador import Entrenador
from ..models.battle import Battle
from .damage_calc import calculate_damage

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
        # La IA evalúa todos sus movimientos disponibles
        for move_ia in poke_ia.available_moves:
            # Simulamos el daño que haríamos usando tu función de daño actual
            from ..logic.damage_calc import calculate_damage
            dmg_a_rival, _ = calculate_damage(poke_ia, poke_rival, move_ia)
            
            # Aplicamos el daño hipotético en el futuro simulado
            poke_rival.hp -= dmg_a_rival
            
            # Pasamos al siguiente nivel del árbol (turno del rival, que intenta minimizar)
            evaluacion = minimax_alfa_beta(battle_clone, profundidad - 1, alfa, beta, False, entrenador_ia, entrenador_rival)
             
            max_eval = max(max_eval, evaluacion)
            alfa = max(alfa, evaluacion)
            if beta <= alfa:
                break  # Poda Alfa-Beta (Dejamos de buscar en esta rama)
        return max_eval

    else:
        min_eval = float("inf")
        # Simulamos los movimientos del rival buscando hacernos el mayor daño (minimizar nuestra puntuación)
        for move_rival in poke_rival.available_moves:
            dmg_a_ia, _ = calculate_damage(poke_rival, poke_ia, move_rival)
            
            # El rival nos hace daño en la simulación
            poke_ia.hp -= dmg_a_ia
            
            # Pasamos al siguiente nivel (nuestro turno de maximizar)
            evaluacion = minimax_alfa_beta(battle_clone, profundidad - 1, alfa, beta, True, entrenador_ia, entrenador_rival)
            
            min_eval = min(min_eval, evaluacion)
            beta = min(beta, evaluacion)
            if beta <= alfa:
                break  # Poda Alfa-Beta
        return min_eval