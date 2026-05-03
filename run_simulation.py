import json
import os
from src.engine.models.pokemon import Pokemon
from src.engine.models.entrenador import Entrenador
from src.engine.models.battle import Battle
from src.engine.logic.heuristic import choose_best_move

# Carga de datos de Pokemon y movimientos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE_DIR, "data", "moves-data.json")) as f:
    moves_db = json.load(f)
with open(os.path.join(BASE_DIR, "data", "pokedex_con_moves.json")) as f:
    pokedex = json.load(f)

# Definimos la estrategia del Jugador (Humano)
def estrategia_humano(entrenador: Entrenador, rival: Entrenador):
    poke = entrenador.get_current_pokemon()
    print(f"\nTurno de {entrenador.name}. Pokémon: {poke.name}")
    
    # Mostrar movimientos disponibles
    for i, move in enumerate(poke.moves):
        print(f"{i+1}. {move.name}")
    print("5. Cambiar Pokémon")  
    print("6. Rendirse")  
    # Capturar elección
    try:
        choice = int(input("Selecciona un ataque (1-6): ")) - 1
        return poke.moves[choice]
    except (ValueError, IndexError):
        print("Selección no válida. Usando el primer movimiento.")
        return poke.moves[0]

# Definimos la estrategia de la IA
def estrategia_ia(entrenador: Entrenador, rival: Entrenador):
    # Usamos funcion heurística para elegir el mejor movimiento
    # Le pasamos el pokemon actual de la IA y el del jugador
    return choose_best_move(entrenador.get_current_pokemon(), rival.get_current_pokemon())

def main():
    poke_p1 = Pokemon("hoopa", pokedex["hoopa"], moves_db)
    poke_p2 = Pokemon("mewtwo", pokedex["mewtwo"], moves_db)

    jugador = Entrenador("Giancarlo", [poke_p1])
    rival_ia = Entrenador("IA_Master", [poke_p2])

    batalla = Battle(jugador, rival_ia)

    # Ejecución de la batalla
    # Pasamos las funciones de estrategia como parámetros
    # Estrategia -> se refiere que es lo que hace cada jugador en su turno para elegir su movimiento
    batalla.start_battle(estrategia_humano, estrategia_ia)

if __name__ == "__main__":
    main()