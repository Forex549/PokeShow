from typing import List
from .pokemon import Pokemon

class Entrenador:
    def __init__(self, name: str, pokemones: List[Pokemon]):
        self.name = name
        self.pokemones = pokemones
    def cambiar_pokemon(self, index: int):
        if 0 <= index < len(self.pokemones):
            if self.pokemones[index].hp > 0:
                self.activo = self.pokemones[index]