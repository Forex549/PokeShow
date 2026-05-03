import json
import os
from src.engine.models.pokemon import Pokemon
from src.engine.logic.damage_calc import calculate_damage
from src.engine.logic.heuristic import choose_best_move

# --- CARGA DE DATOS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE_DIR, "data", "moves-data.json")) as f:
    moves_db = json.load(f)
with open(os.path.join(BASE_DIR, "data", "pokedex_con_moves.json")) as f:
    pokedex = json.load(f)

def execute_turn(p1: Pokemon, p2: Pokemon, p1_move, p2_move) -> None:
    m1 = p1_move
    m2 = p2_move

    # Determinar orden por velocidad
    if p1.spe >= p2.spe:
        order = [(p1, m1, p2), (p2, m2, p1)]
    else:
        order = [(p2, m2, p1), (p1, m1, p2)]

    for attacker, move, defender in order:
        if attacker.hp <= 0: 
            continue
        
        dmg: int = calculate_damage(attacker, defender, move)
        defender.hp -= dmg
        print(f"» {attacker.name} usó {move.name}! Hizo {dmg} de daño.")
        
        if defender.hp <= 0:
            print(f"¡{defender.name} se ha debilitado!")
            break

def battle() -> None:
    # Instanciamos con tus clases actuales (Salamence vs Mewtwo)
    player: Pokemon = Pokemon("zeraora", pokedex["zeraora"], moves_db)
    enemy: Pokemon = Pokemon("mewtwo", pokedex["mewtwo"], moves_db)
    
    print(f"--- INICIA: {player.name.upper()} vs {enemy.name.upper()} ---")

    while player.hp > 0 and enemy.hp > 0:
        print(f"\nSTATUS: {player.name}: {player.hp} HP | {enemy.name}: {enemy.hp} HP")
        print("Movimientos del enemigo: ",enemy.moves)
        # Mostrar ataques
        for i, move in enumerate(player.moves):
            print(f"{i+1}. {move.name}")
        
        choice: int = int(input("Selecciona un ataque (1-4): ")) - 1
        p_move = player.moves[choice]
        
        # IA decide
        e_move = choose_best_move(enemy, player)

        execute_turn(player, enemy, p_move, e_move)

    print("\n" + "="*20)
    print("¡GANASTE!" if player.hp > 0 else "PERDISTE...")

if __name__ == "__main__":
    battle()