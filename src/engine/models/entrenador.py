from typing import List
from .pokemon import Pokemon

class Entrenador:
    def __init__(self, name: str, pokemones: List[Pokemon]):
        self.name = name
        self.pokemones = pokemones
        self.current_pokemon_index = 0
    
    def switch_pokemon(self, index: int):
        if 0 <= index < len(self.pokemones):
            if self.pokemones[index].hp > 0:
                self.current_pokemon_index = index
            else:
                print(f"{self.pokemones[index].name} está debilitado y no puede ser seleccionado.")
    
    def get_current_pokemon(self):
        return self.pokemones[self.current_pokemon_index]
    
    def has_usable_pokemon(self):
        return any(pokemon.hp > 0 for pokemon in self.pokemones)
    

    
    