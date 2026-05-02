class Pokemon:
    def __init__(self, name, data):
        self.name = name
        self.types = data["types"]
        self.stats = data["baseStats"]
        self.hp = data["baseStats"]["hp"]
        self.max_hp = data["baseStats"]["hp"]
        self.moves = data["moves"]

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