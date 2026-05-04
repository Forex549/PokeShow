import json
import os
import random
from src.engine.models.pokemon import Pokemon
from src.engine.models.entrenador import Entrenador
from src.engine.models.battle import Battle
from src.engine.logic.heuristic import choose_best_move
from src.engine.logic.heuristic import chose_random_move

# Carga de datos de Pokemon y movimientos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE_DIR, "data", "moves-data.json")) as f:
    moves_db = json.load(f)
with open(os.path.join(BASE_DIR, "data", "pokedex_con_moves.json")) as f:
    pokedex = json.load(f)


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

    print(f"\nTurno de {entrenador.name}. Pokémon: {poke.name}")
    for i, move in enumerate(poke.moves):
        print(f"{i+1}. {move.name}")
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
def estrategia_ia(entrenador: Entrenador, rival: Entrenador):
    poke = entrenador.get_current_pokemon()

    # Auto-cambio si el Pokémon actual está debilitado
    if poke.hp <= 0:
        for i, p in enumerate(entrenador.pokemones):
            if p.hp > 0:
                entrenador.switch_pokemon(i)
                print(f"¡{entrenador.name} envió a {entrenador.get_current_pokemon().name}!")
                return None

    return choose_best_move(entrenador.get_current_pokemon(), rival.get_current_pokemon())

def estrategia_random(entrenador: Entrenador, rival: Entrenador):
    poke = entrenador.get_current_pokemon()

    if poke.hp <= 0:
        for i, p in enumerate(entrenador.pokemones):
            if p.hp > 0:
                entrenador.switch_pokemon(i)
                print(f"{entrenador.name} envió a {p.name}")
                return None
    return random.choice(poke.moves)
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
        while True:
            try:
                bot = int(input("Elige un bot (1-2): "))
                if bot == 1:
                    
                    return estrategia_random
                elif bot == 2:
                    
                    return estrategia_ia
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
            Pokemon("hoopa", pokedex["hoopa"], moves_db),
            Pokemon("gengar", pokedex["gengar"], moves_db),
            Pokemon("charizard", pokedex["charizard"], moves_db),
            Pokemon("snorlax", pokedex["snorlax"], moves_db),
        ])
        rival = Entrenador("Sobrevilla", [
            Pokemon("mewtwo", pokedex["mewtwo"], moves_db),
            Pokemon("tyranitar", pokedex["tyranitar"], moves_db),
            Pokemon("typhlosion", pokedex["typhlosion"], moves_db),
            Pokemon("articuno", pokedex["articuno"], moves_db),
        ])
    elif modo == 2:  # IA vs IA
        estrategia_jugador = seleccionar_bot_ia("IA1")
        estrategia_rival = seleccionar_bot_ia("IA2")
        jugador = Entrenador("IA1", [
            Pokemon("hoopa", pokedex["hoopa"], moves_db),
            Pokemon("gengar", pokedex["gengar"], moves_db),
            Pokemon("charizard", pokedex["charizard"], moves_db),
            Pokemon("snorlax", pokedex["snorlax"], moves_db),
        ])
        rival = Entrenador("IA2", [
            Pokemon("mewtwo", pokedex["mewtwo"], moves_db),
            Pokemon("tyranitar", pokedex["tyranitar"], moves_db),
            Pokemon("typhlosion", pokedex["typhlosion"], moves_db),
            Pokemon("articuno", pokedex["articuno"], moves_db),
        ])
    elif modo == 3:  # Humano vs Humano
        estrategia_jugador = estrategia_humano
        estrategia_rival = estrategia_humano
        jugador = Entrenador("Jugador1", [
            Pokemon("hoopa", pokedex["hoopa"], moves_db),
            Pokemon("gengar", pokedex["gengar"], moves_db),
            Pokemon("charizard", pokedex["charizard"], moves_db),
            Pokemon("snorlax", pokedex["snorlax"], moves_db),
        ])
        rival = Entrenador("Jugador2", [
            Pokemon("mewtwo", pokedex["mewtwo"], moves_db),
            Pokemon("tyranitar", pokedex["tyranitar"], moves_db),
            Pokemon("typhlosion", pokedex["typhlosion"], moves_db),
            Pokemon("articuno", pokedex["articuno"], moves_db),
        ])
    
    batalla = Battle(jugador, rival)
    batalla.start_battle(estrategia_jugador, estrategia_rival)

if __name__ == "__main__":
    main()
