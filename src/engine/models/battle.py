import random
from collections.abc import Callable
from typing import Optional

from ..logic.damage_calc import calculate_damage
from ..models.entrenador import Entrenador
from ..models.pokemon import Pokemon
from ..models.movimientos import Movimiento

from src.engine.logic.status_effects import STATUS_RULES, VOLATILE_STATUS_RULES

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
            
            # Estado sueño: si el Pokémon está dormido, no puede atacar
            if atacante.status == "slp":
                if atacante.status_turns > 0:
                    print(f"{atacante.name} está profundamente dormido.")
                    atacante.decreasestatus_turn()
                    continue  
                else:
                    print(f"{atacante.name} se ha despertado!")

            # Estado congelación: si el Pokémon está congelado, tiene una chance de descongelarse antes de atacar
            if atacante.status == "frz":
                chance_descongelar = STATUS_RULES["frz"]["thaw_chance"]
                if random.randint(1, 100) <= chance_descongelar:
                    print(f"{atacante.name} se ha descongelado!")
                    atacante.status = "No State"
                else:
                    print(f"❄️ {atacante.name} está congelado y no se puede mover.")
                    continue  

            # Estado parálisis: si el Pokémon está paralizado, tiene una chance de quedar totalmente paralizado y no atacar
            if atacante.status == "par":
                chance_paralizarse = STATUS_RULES["par"]["skip_turn_chance"]
                if random.randint(1, 100) <= chance_paralizarse:
                    print(f"{atacante.name} está paralizado y no puede moverse.")
                    continue  

            # Estado confusión: si el Pokémon está confundido, tiene una chance de golpearse a sí mismo en lugar de atacar
            if atacante.volatile_status == "confusion":
                if atacante.volatile_turns > 0:
                    print(f"{atacante.name} se encuentra confundido...")
                    atacante.decrease_volatile_turn()
                    
                    chance_autogolpe = VOLATILE_STATUS_RULES["confusion"]["self_hit_chance"]
                    if random.randint(1, 100) <= chance_autogolpe:
                        print(f"{atacante.name} se hirió a sí mismo en su confusión!")
                        potencia_confusion = VOLATILE_STATUS_RULES["confusion"]["self_hit_power"]
                        
                        # Daño por confusión usando sus propios stats
                        dmg_conf = max(1, int((atacante.atk / atacante.defense) * potencia_confusion * 0.15))
                        atacante.hp -= dmg_conf
                        print(f"¡{atacante.name} se hizo {dmg_conf} de daño!")
                        
                        if atacante.hp <= 0:
                            print(f"¡{atacante.name} se ha debilitado!")
                        continue  
                else:
                    atacante.volatile_status = "No State"
            

            # Accuracy: si el movimiento falla, saltar
            if random.randint(1, 100) > movimiento.accuracy:
                print(f"» {atacante.name} usó {movimiento.name}... ¡pero falló!")
                continue

            if movimiento.category != "Status" or movimiento.category != "status":
                dmg, is_crit = calculate_damage(atacante, defensor, movimiento)
                if is_crit:
                    print("¡Golpe crítico!")
                defensor.hp -= dmg
                print(f"» {atacante.name} usó {movimiento.name}! Hizo {dmg} de daño.")
            else:
                print(f"» {atacante.name} usó {movimiento.name}!")
            

            if defensor.hp > 0:
                # Aplicar Estado Principal (Si el defensor está sano)
                if defensor.status == "No State":
                    estado_a_aplicar = None
                    if movimiento.direct_status:
                        estado_a_aplicar = movimiento.direct_status
                    elif movimiento.secondary_status and random.randint(1, 100) <= movimiento.secondary_chance:
                        estado_a_aplicar = movimiento.secondary_status

                    if estado_a_aplicar:
                        defensor.status = estado_a_aplicar
                        print(f"{defensor.name} ahora está bajo el estado: {estado_a_aplicar.upper()}!")
                        if estado_a_aplicar == "slp":
                            defensor.status_turns = random.randint(STATUS_RULES["slp"]["min_turns"], STATUS_RULES["slp"]["max_turns"])

                # Aplicar Estado Volátil 
                if defensor.volatile_status == "No State" and movimiento.secondary_volatile:
                    if random.randint(1, 100) <= movimiento.secondary_chance:
                        estado_volatil = movimiento.secondary_volatile
                        defensor.volatile_status = estado_volatil
                        
                        if estado_volatil in VOLATILE_STATUS_RULES:
                            reglas = VOLATILE_STATUS_RULES[estado_volatil]
                            defensor.volatile_turns = random.randint(reglas["min_turns"], reglas["max_turns"])
                            nombre_bonito = reglas["name"]
                        else:
                            defensor.volatile_turns = 1
                            nombre_bonito = estado_volatil
                        
                        print(f"{defensor.name} ha quedado bajo el estado de: {nombre_bonito}!")
            if defensor.hp <= 0:
                print(f"¡{defensor.name} se ha debilitado!")
                break
        self.resolver_efectos_fin_turno() 
    
    def resolver_efectos_fin_turno(self):
        """Aplica los daños residuales de veneno y quemadura usando el diccionario."""
        for entrenador in [self.entrenador1, self.entrenador2]:
            poke = entrenador.get_current_pokemon()
            if poke.hp > 0 and poke.status in STATUS_RULES:
                reglas_estado = STATUS_RULES[poke.status]
                
                if "residual_damage_pct" in reglas_estado:
                    porcentaje_daño = reglas_estado["residual_damage_pct"]
                    dmg = max(1, int(poke.max_hp * porcentaje_daño))
                    poke.hp -= dmg

                    print(f"{poke.name} sufre {dmg} de daño debido a su estado ({reglas_estado['name']}).")
                
                if poke.hp <= 0:
                    print(f"¡{poke.name} se ha debilitado por el daño de fin de turno!")
                    
                    
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
                # 🔥 FORZAR CAMBIOS ANTES DEL TURNO
                if self.entrenador1.get_current_pokemon().hp <= 0:
                    strategy_p1(self.entrenador1, self.entrenador2)
                    continue

                if self.entrenador2.get_current_pokemon().hp <= 0:
                    strategy_p2(self.entrenador2, self.entrenador1)
                    continue
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