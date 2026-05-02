import random

class Pokemon:
    def __init__(self, name : str, data : dict):
        self.name = name
        self.types = data["types"]  # tipo del pokemon
        self.stats = data["baseStats"]
        self.hp = data["baseStats"]["hp"]
        self.max_hp = data["baseStats"]["hp"]
        self.moves = random.sample(data["moves"], 4)

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