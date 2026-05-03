import random
from .movimientos import Movimiento

class Pokemon:
    def __init__(self, name : str, data : dict, data_moves: dict):
        self.name = name
        self.types = data["types"]  # tipo del pokemon
        self.stats = data["baseStats"]
        self.hp = data["baseStats"]["hp"]
        self.max_hp = data["baseStats"]["hp"]
        self.names_moves = [move.lower().replace(" ", "").replace("-", "") for move in data["moves"]]  # lista de nombres de movimientos
        self.moves = [Movimiento(data=data_moves[move_name]) for move_name in self.names_moves]

        self._status = "No State"    # envenenado, dormido, etc
        self._status_turns = 0   # contador de turnos para efectos de estado 

    @property
    def atk(self): return self.stats["atk"]

    @property
    def spa(self): return self.stats["spa"]

    @property
    def defense(self): return self.stats["def"]

    @property
    def spd(self): return self.stats["spd"]

    @property
    def spe(self): return self.stats["spe"]

    @property
    def available_moves(self):
        return [move for move in self.moves if move.available]

    @property
    def status(self): return self.status

    @status.setter
    def status(self, newstatus: str):
        # Asignamos a la variable privada para evitar el bucle infinito
        self.status = newstatus

    @property
    def status_turns(self):
        return self.status_turns

    @status_turns.setter
    def status_turns(self, turns: int):
        self.status_turns = turns

    def decreasestatus_turn(self):
        if self._status_turns > 0:
            self._status_turns -= 1
        if self._status_turns == 0:
            self._status = "No State"