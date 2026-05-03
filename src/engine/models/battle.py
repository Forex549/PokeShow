import random
from collections.abc import Callable
from typing import Optional

from ..logic.damage_calc import calculate_damage
from ..models.entrenador import Entrenador
from ..models.pokemon import Pokemon
from ..models.movimientos import Movimiento

class Battle:
    def __init__(self, entrenador1: Entrenador, entrenador2: Entrenador):
        self.entrenador1 = entrenador1
        self.entrenador2 = entrenador2
        self.turno = 0  # 0 para entrenador1, 1 para entrenador2

    def ejecutar_turno(self, move1: Optional[Movimiento], move2: Optional[Movimiento]):
        poke1 = self.entrenador1.get_current_pokemon()
        poke2 = self.entrenador2.get_current_pokemon()

        # None indica cambio de Pokémon: ese entrenador no ataca este turno
        ataques = []
        if move1 is not None:
            ataques.append((poke1, move1, poke2))
        if move2 is not None:
            ataques.append((poke2, move2, poke1))

        # Priority primero, luego velocidad (ambos descendentes)
        ataques.sort(key=lambda x: (x[1].priority, x[0].spe), reverse=True)

        for atacante, movimiento, defensor in ataques:
            if atacante.hp <= 0:
                continue

            # Accuracy: si el movimiento falla, saltar
            if random.randint(1, 100) > movimiento.accuracy:
                print(f"» {atacante.name} usó {movimiento.name}... ¡pero falló!")
                continue

            dmg, is_crit = calculate_damage(atacante, defensor, movimiento)
            if is_crit:
                print("¡Golpe crítico!")
            defensor.hp -= dmg
            print(f"» {atacante.name} usó {movimiento.name}! Hizo {dmg} de daño.")

            if defensor.hp <= 0:
                print(f"¡{defensor.name} se ha debilitado!")
                break
    
    def is_battle_over(self):
        return not self.entrenador1.has_usable_pokemon() or not self.entrenador2.has_usable_pokemon()
    
    def get_winner(self):
        if not self.entrenador1.has_usable_pokemon():
            return self.entrenador2.name
        elif not self.entrenador2.has_usable_pokemon():
            return self.entrenador1.name
        return None

    def display_status(self):
        poke1 = self.entrenador1.get_current_pokemon()
        poke2 = self.entrenador2.get_current_pokemon()
        print(f"{self.entrenador1.name} - {poke1.name}: {poke1.hp}/{poke1.max_hp} HP")
        print(f"{self.entrenador2.name} - {poke2.name}: {poke2.hp}/{poke2.max_hp} HP")
        
    def start_battle(
        self,
        strategy_p1: Callable[[Entrenador, Entrenador], Optional[Movimiento]],
        strategy_p2: Callable[[Entrenador, Entrenador], Optional[Movimiento]],
    ) -> None:
        """
        Ejecuta el bucle principal de la batalla.
        
        :param strategy_p1: Función que recibe (aliado, rival) y retorna un Movimiento.
        :param strategy_p2: Función que recibe (aliado, rival) y retorna un Movimiento.
        """
        print(f"\n" + "="*30)
        print(f"¡COMIENZA LA BATALLA!")
        print(f"{self.entrenador1.name} vs {self.entrenador2.name}")
        print("="*30 + "\n")

        while not self.is_battle_over():
            self.display_status()
            
            try:
                # Invocamos las estrategias tipadas
                move1: Optional[Movimiento] = strategy_p1(self.entrenador1, self.entrenador2)
                move2: Optional[Movimiento] = strategy_p2(self.entrenador2, self.entrenador1)
                
                self.ejecutar_turno(move1, move2)
                
            except Exception as e:
                print(f"Error crítico en el flujo de batalla: {e}")
                break
        
        winner: Optional[str] = self.get_winner()
        print("\n" + "="*30)
        print(f"¡LA BATALLA HA TERMINADO!")
        print(f"EL GANADOR ES: {winner}")
        print("="*30)