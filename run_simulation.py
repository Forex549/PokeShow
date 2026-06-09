import json
import os
import random
from typing import Optional
#from importJson import calculate_damage
from src.engine.models.movimientos import Movimiento
from src.engine.logic.damage_calc import calculate_damage
from src.engine.models.pokemon import Pokemon
from src.engine.models.entrenador import Entrenador
from src.engine.models.battle import Battle
from src.engine.logic.heuristic import choose_best_move, chose_random_move, minimax_alfa_beta, elegir_movimiento_nivel3, elegir_mejor_sustituto, elegir_mejor_sustituto_n2, elegir_mejor_sustituto_n3, elegir_accion_nivel4, elegir_mejor_sustituto_n4
import copy
import traceback

# Carga de datos de Pokemon y movimientos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE_DIR, "data", "moves-data.json")) as f:
    moves_db = json.load(f)
with open(os.path.join(BASE_DIR, "data", "pokedex_con_moves.json")) as f:
    pokedex = json.load(f)


_PESOS_N3_DEFAULT = [1.0, 1.0, 0.5, 1.0]
_pesos_nivel3_cache: Optional[list] = None

_PESOS_N4_DEFAULT = [1.0, 1.0, 0.5, 1.0, 0.8]
_pesos_nivel4_cache: Optional[list] = None


def cargar_pesos_nivel4() -> list:
    global _pesos_nivel4_cache
    if _pesos_nivel4_cache is not None:
        return _pesos_nivel4_cache
    path = os.path.join(BASE_DIR, "data", "best_weights_n4.json")
    try:
        with open(path) as f:
            data = json.load(f)
        pesos = data["pesos"] if isinstance(data, dict) else data
        if not (isinstance(pesos, list) and len(pesos) == 5 and all(isinstance(x, (int, float)) for x in pesos)):
            raise ValueError("formato inválido")
        _pesos_nivel4_cache = [float(x) for x in pesos]
    except (FileNotFoundError, ValueError, json.JSONDecodeError):
        print("[nivel4] best_weights_n4.json no encontrado o corrupto — usando pesos por defecto.")
        _pesos_nivel4_cache = list(_PESOS_N4_DEFAULT)
    return _pesos_nivel4_cache


def cargar_pesos_nivel3() -> list:
    global _pesos_nivel3_cache
    if _pesos_nivel3_cache is not None:
        return _pesos_nivel3_cache
    path = os.path.join(BASE_DIR, "data", "best_weights.json")
    try:
        with open(path) as f:
            data = json.load(f)
        pesos = data["pesos"] if isinstance(data, dict) else data
        if not (isinstance(pesos, list) and len(pesos) == 4 and all(isinstance(x, (int, float)) for x in pesos)):
            raise ValueError("formato inválido")
        _pesos_nivel3_cache = [float(x) for x in pesos]
    except (FileNotFoundError, ValueError, json.JSONDecodeError):
        print("[nivel3] best_weights.json no encontrado o corrupto — usando pesos por defecto.")
        _pesos_nivel3_cache = list(_PESOS_N3_DEFAULT)
    return _pesos_nivel3_cache


def mostrar_equipo(entrenador: Entrenador):
    print(f"\nEquipo de {entrenador.name}:")
    for i, p in enumerate(entrenador.pokemones):
        estado = f"{p.hp}/{p.max_hp} HP" if p.hp > 0 else "DEBILITADO"
        activo = " ← activo" if i == entrenador.current_pokemon_index else ""
        print(f"  {i+1}. {p.name} — {estado}{activo}")


def seleccionar_pokemon(entrenador: Entrenador, forzado: bool = False) -> bool:
    """Muestra el equipo y pide al jugador que elija un Pokémon.
    Retorna True si el cambio se realizó, False si el jugador canceló (solo en cambio voluntario).
    """
    mostrar_equipo(entrenador)
    while True:
        try:
            idx = int(input("Elige un Pokémon (número): ")) - 1
            if not (0 <= idx < len(entrenador.pokemones)):
                print("Número fuera de rango.")
                continue
            if entrenador.pokemones[idx].hp <= 0:
                print(f"{entrenador.pokemones[idx].name} está debilitado.")
                continue
            if idx == entrenador.current_pokemon_index:
                if forzado:
                    print("Ese Pokémon ya está en batalla, elige otro.")
                    continue
                else:
                    print("Ese Pokémon ya está en batalla.")
                    return False
            entrenador.switch_pokemon(idx)
            print(f"¡{entrenador.name} envió a {entrenador.get_current_pokemon().name}!")
            return True
        except ValueError:
            print("Entrada no válida.")


# Definimos la estrategia del Jugador (Humano)
def estrategia_humano(entrenador: Entrenador, rival: Entrenador):
    poke = entrenador.get_current_pokemon()

    # Cambio forzado si el Pokémon actual está debilitado
    if poke.hp <= 0:
        print(f"\n¡{poke.name} se ha debilitado! Elige tu siguiente Pokémon.")
        seleccionar_pokemon(entrenador, forzado=True)
        return None

    print(f"\nTurno de {entrenador.name}. Pokémon: {poke.name} types: {poke.types} HP: {poke.hp}/{poke.max_hp}")
    for i, move in enumerate(poke.moves):
        print(f"{i+1}. {move.name} | power: {move.power} priority: {move.priority} type: {move.type}")
    print("5. Cambiar Pokémon")
    print("6. Rendirse")

    while True:
        try:
            choice = int(input("Selecciona una acción (1-6): ")) - 1
            if choice == 4:  # Cambiar Pokémon
                if seleccionar_pokemon(entrenador):
                    return None  # Pierde el turno de ataque
                # Si no cambió (mismo Pokémon), re-preguntar
            elif 0 <= choice < len(poke.moves):
                return poke.moves[choice]
            else:
                print("Selección no válida.")
        except ValueError:
            print("Selección no válida.")


# Definimos la estrategia de la IA
def estrategia_ia_best_option(entrenador: Entrenador, rival: Entrenador):
    poke = entrenador.get_current_pokemon()

    if poke.hp <= 0:
        idx = elegir_mejor_sustituto(entrenador, rival)
        if idx is not None:
            entrenador.switch_pokemon(idx)
            print(f"¡{entrenador.name} envió a {entrenador.get_current_pokemon().name}!")
        return None

    return choose_best_move(poke, rival.get_current_pokemon())

def estrategia_ia_random(entrenador: Entrenador, rival: Entrenador):
    poke = entrenador.get_current_pokemon()

    if poke.hp <= 0:
        for i, p in enumerate(entrenador.pokemones):
            if p.hp > 0:
                entrenador.switch_pokemon(i)
                print(f"¡{entrenador.name} envió a {p.name}!")
                return None

    return chose_random_move(poke)


def estrategia_ia_minimax_nivel2(entrenador: Entrenador, rival: Entrenador) -> Optional[Movimiento]:
    poke_real = entrenador.get_current_pokemon()

    if poke_real.hp <= 0:
        idx = elegir_mejor_sustituto_n2(entrenador, rival)
        if idx is not None:
            entrenador.switch_pokemon(idx)
            print(f"¡{entrenador.name} envió a {entrenador.get_current_pokemon().name} debido a debilitación!")
        return None

    
    ia_clon = copy.deepcopy(entrenador)
    rival_clon = copy.deepcopy(rival)
    
    # Creamos una batalla espejo temporal  para cumplir con los parámetros del Minimax
    batalla_simulada = Battle(ia_clon, rival_clon)
    
    poke_ia_clon = ia_clon.get_current_pokemon()
    poke_rival_clon = rival_clon.get_current_pokemon()

    best_move = None # Guardamos el nombre del movimiento para buscarlo en el real luego
    best_value = float("-inf")

    # El Minimax corre usando únicamente los objetos del clon fantasma
    for i, move_clon in enumerate(poke_ia_clon.available_moves):
        dmg, _ = calculate_damage(poke_ia_clon, poke_rival_clon, move_clon)
        
        # Simulamos en el clon sin miedo
        hp_original_rival = poke_rival_clon.hp
        poke_rival_clon.hp -= dmg
        
        valor_futuro = minimax_alfa_beta(
            battle_clone=batalla_simulada,
            profundidad=3,
            alfa=float("-inf"),
            beta=float("inf"),
            es_maximizando=False,
            entrenador_ia=ia_clon,        # Mandamos el clon
            entrenador_rival=rival_clon   # Mandamos el clon
        )
        
        poke_rival_clon.hp = hp_original_rival
        
        if valor_futuro > best_value:
            best_value = valor_futuro
            best_move_name = move_clon.name  # Nos guardamos el nombre elegido

    # Buscamos y devolvemos el movimiento real correspondiente al que eligió el clon
    for move_real in poke_real.available_moves:
        if move_real.name == best_move_name:
            return move_real
            
    return poke_real.available_moves[0] if poke_real.available_moves else None

def estrategia_ia_minimax_nivel3(entrenador: Entrenador, rival: Entrenador) -> Optional[Movimiento]:
    poke_real = entrenador.get_current_pokemon()

    if poke_real.hp <= 0:
        pesos = cargar_pesos_nivel3()
        idx = elegir_mejor_sustituto_n3(entrenador, rival, pesos)
        if idx is not None:
            entrenador.switch_pokemon(idx)
            print(f"¡{entrenador.name} envió a {entrenador.get_current_pokemon().name} debido a debilitación!")
        return None

    pesos = cargar_pesos_nivel3()
    return elegir_movimiento_nivel3(entrenador, rival, pesos)


def estrategia_ia_minimax_nivel4(entrenador: Entrenador, rival: Entrenador):
    poke_real = entrenador.get_current_pokemon()
    pesos = cargar_pesos_nivel4()

    if poke_real.hp <= 0:
        idx = elegir_mejor_sustituto_n4(entrenador, rival, pesos)
        if idx is not None:
            entrenador.switch_pokemon(idx)
            print(f"¡{entrenador.name} envió a {entrenador.get_current_pokemon().name} (N4)!")
        return None

    accion = elegir_accion_nivel4(entrenador, rival, pesos)
    if isinstance(accion, int):
        entrenador.switch_pokemon(accion)
        print(f"¡{entrenador.name} cambia voluntariamente a {entrenador.get_current_pokemon().name} (N4)!")
        return None
    return accion


def main():
    # Menu de selección de modo
    print("Selecciona el modo de juego:")
    print("1. Humano vs IA")
    print("2. IA vs IA")
    print("3. Humano vs Humano")
    
    while True:
        try:
            modo = int(input("Elige un modo (1-3): "))
            if modo not in [1, 2, 3]:
                print("Selección no válida.")
                continue
            break
        except ValueError:
            print("Entrada no válida.")
    
    # Funcion auxiliar para seleccionar bot ia
    def seleccionar_bot_ia(nombre_ia: str):
        print(f"\nSelecciona el bot para {nombre_ia}:")
        print("1. Aleatorio")
        print("2. Mejor opción")
        print("3. Minimax Nivel 2")
        print("4. Minimax Nivel 3 (pesos GA, sin cambio voluntario)")
        print("5. Minimax Nivel 4 (pesos GA, con cambio voluntario + estados)")
        while True:
            try:
                bot = int(input("Elige un bot (1-5): "))
                if bot == 1:
                    return estrategia_ia_random
                elif bot == 2:
                    return estrategia_ia_best_option
                elif bot == 3:
                    return estrategia_ia_minimax_nivel2
                elif bot == 4:
                    return estrategia_ia_minimax_nivel3
                elif bot == 5:
                    return estrategia_ia_minimax_nivel4
                else:
                    print("Selección no válida.")
                    continue
            except ValueError:
                print("Entrada no válida.")
    
    # Configurar entrenadores y estrategias según el modo
    if modo == 1:  # Humano vs IA
        estrategia_rival = seleccionar_bot_ia("la IA rival")
        estrategia_jugador = estrategia_humano
        jugador = Entrenador("Topollillo", [
            Pokemon("garchomp",  pokedex["garchomp"],  moves_db),
            Pokemon("lucario", pokedex["lucario"], moves_db),
            Pokemon("gengar",   pokedex["gengar"],   moves_db),
            Pokemon("swampert",  pokedex["swampert"],  moves_db),
        ])
        rival = Entrenador("Sobrevilla", [
            Pokemon("zeraora", pokedex["zeraora"], moves_db),
            Pokemon("baxcalibur",  pokedex["baxcalibur"],  moves_db),
            Pokemon("snorlax",   pokedex["snorlax"],   moves_db),
            Pokemon("metagross", pokedex["metagross"],  moves_db),
        ])
    elif modo == 2:  # IA vs IA
        estrategia_jugador = seleccionar_bot_ia("IA1")
        estrategia_rival = seleccionar_bot_ia("IA2")
        jugador = Entrenador("IA1", [
            Pokemon("garchomp",  pokedex["garchomp"],  moves_db),
            Pokemon("lucario", pokedex["lucario"], moves_db),
            Pokemon("gengar",   pokedex["gengar"],   moves_db),
            Pokemon("swampert",  pokedex["swampert"],  moves_db),
        ])
        rival = Entrenador("IA2", [
            Pokemon("zeraora", pokedex["zeraora"], moves_db),
            Pokemon("baxcalibur",  pokedex["baxcalibur"],  moves_db),
            Pokemon("snorlax",   pokedex["snorlax"],   moves_db),
            Pokemon("metagross", pokedex["metagross"],  moves_db),
        ])
    elif modo == 3:  # Humano vs Humano
        estrategia_jugador = estrategia_humano
        estrategia_rival = estrategia_humano
        jugador = Entrenador("Jugador1", [
            Pokemon("garchomp",  pokedex["garchomp"],  moves_db),
            Pokemon("lucario", pokedex["lucario"], moves_db),
            Pokemon("gengar",   pokedex["gengar"],   moves_db),
            Pokemon("swampert",  pokedex["swampert"],  moves_db),
        ])
        rival = Entrenador("Jugador2", [
            Pokemon("zeraora", pokedex["zeraora"], moves_db),
            Pokemon("baxcalibur",  pokedex["baxcalibur"],  moves_db),
            Pokemon("snorlax",   pokedex["snorlax"],   moves_db),
            Pokemon("metagross", pokedex["metagross"],  moves_db),
        ])
    
    batalla = Battle(jugador, rival)
    batalla.start_battle(estrategia_jugador, estrategia_rival)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        print(traceback.format_exc())
        traceback.print_exc()
