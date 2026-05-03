from random import random


class Movimiento:
    def __init__(self, data: dict):
        """
        Instancia un movimiento a partir de su ID (ej. 'accelerock') 
        y los datos del JSON de moves-data.json.
        """
        # Usamos el nombre legible que viene dentro del objeto data
        self.name: str = data.get("name", "Unknown Move")
        
        # El tipo elemental (Rock, Fire, etc.)
        self.type: str = data.get("type", "Normal")
        
        # Categoría: 'Physical' o 'Special'
        self.category: str = data.get("category", "Physical")
        
        # Poder base: mapeamos 'basePower' a 'power' para el motor
        self.power: int = data.get("basePower", 0)
        
        # Precisión
        self.accuracy: int = data.get("accuracy", 100)
        
        # Prioridad (esencial para movimientos como Accelerock que tiene 1)
        self.priority: int = data.get("priority", 0)

        self.pp: int = data.get("pp", 0)

        self.available: bool = True

    def __repr__(self) -> str:
        return f"<Move {self.name} ({self.type}) Power: {self.power} Priority: {self.priority}>"
    
    def decrease_pp(self) -> None:
        if self.pp > 0:
            self.pp -= 1
        else:
            self.setDisabled()
        
    def setDisabled(self) -> None:
        self.available = False

    