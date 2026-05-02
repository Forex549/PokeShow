import json
import random

class Pokemon:
    def __init__(self, name, data):
        self.name = name
        self.types = data["types"]  # tipo del pokemon
        self.stats = data["baseStats"]
        self.hp = data["baseStats"]["hp"]
        self.max_hp = data["baseStats"]["hp"]
        self.moves = random.sample(data["moves"], 4)

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
type_chart = {
    "Fire": {"Grass": 2, "Water": 0.5},
    "Water": {"Fire": 2, "Grass": 0.5},
    "Electric": {"Water": 2, "Ground": 0},
    "Ground": {"Electric": 2, "Flying": 0},
}

with open("abilities-data.json") as f:
    abilities = json.load(f)

with open("moves-data.json") as f:
    moves = json.load(f)

with open("pokedex_con_moves.json") as f:
    pokedex = json.load(f)


def get_effectiveness(move_type, defender_types):
    multiplier = 1
    for t in defender_types:
        if move_type in type_chart and t in type_chart[move_type]:
            multiplier *= type_chart[move_type][t]
    return multiplier

def calculate_damage(attacker:Pokemon, defender:Pokemon, move):
    if move["category"] not in ["Physical", "Special"]:
        return 0

    atk = attacker.atk if move["category"] == "Physical" else attacker.spa
    defense = defender.defense if move["category"] == "Physical" else defender.spd

    base = move["basePower"]

    damage = ((2 * 50 / 5 + 2) * base * (atk / defense)) / 50 + 2

    # STAB
    if move["type"] in attacker.types:
        damage *= 1.5

    # Effectiveness
    damage *= get_effectiveness(move["type"], defender.types)

    return int(damage)

def estimate_enemy_damage(enemy, me):
    worst = 0

    for move_name in enemy.moves:
        move = moves.get(move_name.lower().replace(" ", ""))
        if not move:
            continue

        dmg = calculate_damage(enemy, me, move)
        if dmg > worst:
            worst = dmg

    return worst

def evaluate(my_poke, enemy_poke):
    score = 0

    # HP
    score += (my_poke.hp / my_poke.max_hp) * 100
    score -= (enemy_poke.hp / enemy_poke.max_hp) * 100

    # Mejor daño propio
    best_damage = 0
    best_eff = 1

    for move_name in my_poke.moves:
        move = moves.get(move_name.lower().replace(" ", ""))
        if not move:
            continue

        dmg = calculate_damage(my_poke, enemy_poke, move)
        eff = get_effectiveness(move["type"], enemy_poke.types)

        if dmg > best_damage:
            best_damage = dmg
            best_eff = eff

    score += best_damage * 0.6
    score += best_eff * 25

    # Riesgo enemigo
    enemy_damage = estimate_enemy_damage(enemy_poke, my_poke)
    score -= enemy_damage * 0.6

    # Velocidad
    if my_poke.spe > enemy_poke.spe:
        score += 15
    else:
        score -= 15

    return score

def choose_best_move(my_poke, enemy_poke):
    best_move = None
    best_score = float("-inf")

    for move_name in my_poke.moves:
        move = moves.get(move_name.lower().replace(" ", ""))
        if not move:
            continue

        if move["category"] not in ["Physical", "Special"]:
            continue

        # copiar enemigo
        enemy_copy = Pokemon(enemy_poke.name, {
            "types": enemy_poke.types,
            "baseStats": enemy_poke.stats,
            "moves": enemy_poke.moves
        })
        enemy_copy.hp = enemy_poke.hp

        # velocidad: simular si enemigo pega primero
        if enemy_poke.spe > my_poke.spe:
            dmg_enemy = estimate_enemy_damage(enemy_poke, my_poke)
            if dmg_enemy >= my_poke.hp:
                continue  # morirías antes

        # aplicar daño
        dmg = calculate_damage(my_poke, enemy_copy, move)
        enemy_copy.hp -= dmg

        score = evaluate(my_poke, enemy_copy)

        if score > best_score:
            best_score = score
            best_move = move_name

    return best_move

def get_move_data(move_name):
    return moves.get(move_name.lower().replace(" ", ""))

def execute_turn(player, enemy, player_move_name, enemy_move_name):
    player_move = get_move_data(player_move_name)
    enemy_move = get_move_data(enemy_move_name)

    print(f"\n{player.name} uses {player_move_name}")
    print(f"{enemy.name} uses {enemy_move_name}")

    # determinar orden
    if player.spe >= enemy.spe:
        first, first_move, second, second_move = player, player_move, enemy, enemy_move
    else:
        first, first_move, second, second_move = enemy, enemy_move, player, player_move

    # primer ataque
    dmg = calculate_damage(first, second, first_move)
    second.hp -= dmg
    print(f"{first.name} deals {dmg} damage to {second.name}")

    if second.hp <= 0:
        print(f"{second.name} fainted!")
        return

    # segundo ataque
    dmg = calculate_damage(second, first, second_move)
    first.hp -= dmg
    print(f"{second.name} deals {dmg} damage to {first.name}")

    if first.hp <= 0:
        print(f"{first.name} fainted!")
def battle(player, enemy):
    turn = 1

    while player.hp > 0 and enemy.hp > 0:
        print("\n" + "="*30)
        print(f"Turn {turn}")
        print(f"{player.name}: {player.hp} HP")
        print(f"{enemy.name}: {enemy.hp} HP")

        # mostrar moves del jugador
        print("\nYour moves:")
        for i, move in enumerate(player.moves):
            print(f"{i+1}. {move}")

        # input jugador
        choice = int(input("Choose move: ")) - 1
        player_move = player.moves[choice]

        # IA elige
        enemy_move = choose_best_move(enemy, player)

        # ejecutar turno
        execute_turn(player, enemy, player_move, enemy_move)

        turn += 1

    print("\n" + "="*30)
    if player.hp > 0:
        print("YOU WIN")
    else:
        print("YOU LOSE")





player = Pokemon("salamence", pokedex["salamence"])
enemy = Pokemon("mewtwo", pokedex["mewtwo"])
print("player",player.moves)
print("enemigo",enemy.moves)
print("------------------------------------")
battle(player, enemy)

