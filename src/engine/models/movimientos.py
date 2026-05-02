class Movimiento:
    def __init__(self, name_id: str, data: dict):
        """
        Instancia un movimiento a partir de su ID (ej. 'accelerock') 
        y los datos del JSON de moves-data.json.
        """
        # Usamos el nombre legible que viene dentro del objeto data
        self.name: str = data.get("name", name_id)
        
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

    def __repr__(self) -> str:
        return f"<Move {self.name} ({self.type}) Power: {self.power} Priority: {self.priority}>"