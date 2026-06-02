import copy
import contextlib
import io
import random
from typing import Callable, Optional

from src.engine.models.battle import Battle
from src.engine.models.entrenador import Entrenador
from src.engine.models.movimientos import Movimiento


def run_silent_battle(
    t1: Entrenador,
    t2: Entrenador,
    strat1: Callable,
    strat2: Callable,
    seed: Optional[int] = None,
) -> str:
    # Corre una batalla completa sin imprimir nada en consola
    # Usamos deepcopy para que los entrenadores originales queden intactos después
    if seed is not None:
        random.seed(seed)

    t1_copy = copy.deepcopy(t1)
    t2_copy = copy.deepcopy(t2)

    battle = Battle(t1_copy, t2_copy)

    sink = io.StringIO()
    with contextlib.redirect_stdout(sink):
        battle.start_battle(strat1, strat2)

    winner = battle.get_winner()
    return winner if winner is not None else ""
