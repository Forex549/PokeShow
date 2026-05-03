from random import random
from typing import Optional

from ..models.pokemon import Pokemon
from ..models.movimientos import Movimiento
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
    return 1