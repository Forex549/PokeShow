from .models.pokemon import Pokemon
from .models.movimientos import Movimiento
from .logic.damage_calc import calculate_damage
from .logic.heuristic import choose_best_move

def execute_turn(p1: Pokemon, m1: Movimiento, p2: Pokemon, m2: Movimiento):
    # Determinar orden por velocidad
    if p1.speed >= p2.speed:
        first, f_move, second, s_move = p1, m1, p2, m2
    else:
        first, f_move, second, s_move = p2, m2, p1, m1

    # Ataque 1
    dmg1 = calculate_damage(first, second, f_move)
    second.hp -= dmg1
    print(f"{first.name} usa {f_move.name} y hace {dmg1} de daño.")

    if second.hp <= 0:
        print(f"{second.name} se ha debilitado!")
        return

    # Ataque 2
    dmg2 = calculate_damage(second, first, s_move)
    first.hp -= dmg2
    print(f"{second.name} usa {s_move.name} y hace {dmg2} de daño.")
    
    if first.hp <= 0:
        print(f"{first.name} se ha debilitado!")

def start_battle(player: Pokemon, enemy: Pokemon):
    while player.hp > 0 and enemy.hp > 0:
        print(f"\n{player.name}: {player.hp} HP | {enemy.name}: {enemy.hp} HP")
        
        # Selección jugador
        for i, m in enumerate(player.moves):
            print(f"{i+1}. {m.name}")
        idx = int(input("Elige ataque: ")) - 1
        p_move = player.moves[idx]

        # IA elige (usando tu lógica de evaluación)
        e_move = choose_best_move(enemy, player)
        
        execute_turn(player, p_move, enemy, e_move)