import random
from .movimientos import Movimiento
from src.engine.logic.status_effects import STATUS_RULES

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

        # Estados principales
        self._status = "No State"
        self._status_turns = 0

        # Para estados volátiles
        self._volatile_status = "No State"
        self._volatile_turns = 0

   
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
    def atk(self): 
        base_atk = self._stats["atk"]
        if self._status == "brn":
            return int(base_atk * STATUS_RULES["brn"]["multiplier"])
        return base_atk

    @property
    def spa(self): return self._stats["spa"]

    @property
    def defense(self): return self._stats["def"]

    @property
    def spd(self): return self._stats["spd"]

    @property
    def spe(self): 
        base_spe = self._stats["spe"]
        if self._status == "par":
            return int(base_spe * STATUS_RULES["par"]["multiplier"])
        return base_spe

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
            
    # Atributos y métodos para estados volátiles 
    @property
    def volatile_status(self): return self._volatile_status

    @volatile_status.setter
    def volatile_status(self, new_status: str): self._volatile_status = new_status

    @property
    def volatile_turns(self): return self._volatile_turns

    @volatile_turns.setter
    def volatile_turns(self, turns: int): self._volatile_turns = turns

    def decrease_volatile_turn(self):
        if self._volatile_turns > 0:
            self._volatile_turns -= 1
        if self._volatile_turns == 0:
            self._volatile_status = "No State"
            print(f"{self.name} se ha librado de la confusión!")
            
    def clear_volatiles(self):
        """Limpia los estados volátiles al cambiar de Pokémon."""
        self._volatile_status = "No State"
        self._volatile_turns = 0

    