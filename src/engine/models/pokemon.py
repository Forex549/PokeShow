import random
from .movimientos import Movimiento

def calculate_hp(base, level=50):
    return int(((2 * base) * level) / 100 + level + 10)

class Pokemon:
    def __init__(self, name: str, data: dict, data_moves: dict):
        self.name = name
        self.level = 50
        self.types = data["types"]
        self._stats = data["baseStats"]  
        
        # HP inicial y máximo
        hp_calculado = calculate_hp(self._stats["hp"], self.level)
        self._hp = hp_calculado
        self._max_hp = hp_calculado
        
        # Procesamiento de movimientos
        self.names_moves = [
            move.lower().replace(" ", "").replace("-", "") 
            for move in data["moves"]
        ]
        
        # Selección aleatoria de 4 movimientos
        self.moves = [
            Movimiento(data=data_moves[move_name]) 
            for move_name in random.sample(self.names_moves, 4)
        ]

        # Estados de salud
        self._status = "No State"
        self._status_turns = 0

   
    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, value: int):
        # Asegura que el HP no sea negativo ni exceda el máximo
        self._hp = max(0, min(value, self._max_hp))

    @property
    def max_hp(self):
        return self._max_hp

    @property
    def atk(self): return self._stats["atk"]

    @property
    def spa(self): return self._stats["spa"]

    @property
    def defense(self): return self._stats["def"]

    @property
    def spd(self): return self._stats["spd"]

    @property
    def spe(self): return self._stats["spe"]

    @property
    def available_moves(self):
        return [move for move in self.moves if move.available]

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, new_status: str):
        self._status = new_status

    @property
    def status_turns(self):
        return self._status_turns

    @status_turns.setter
    def status_turns(self, turns: int):
        self._status_turns = turns

    def decreasestatus_turn(self):
        if self._status_turns > 0:
            self._status_turns -= 1
        
        if self._status_turns == 0:
            self._status = "No State"