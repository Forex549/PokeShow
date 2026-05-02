from ..models.pokemon import Pokemon
from ..models.movimientos import Movimiento
from .damage_calc import calculate_damage

def choose_best_move(my_poke: Pokemon, enemy_poke: Pokemon, moves_dict: dict) -> str:
    best_move_name: str = my_poke.moves[0]
    best_score: float = float("-inf")

    for m_name in my_poke.moves:
        # Normalización del ID para el diccionario
        m_id = m_name.lower().replace(" ", "").replace("-", "")
        
        if m_id in moves_dict:
            move_obj = Movimiento(m_id, moves_dict[m_id])
            dmg = calculate_damage(my_poke, enemy_poke, move_obj)
            
            if dmg > best_score:
                best_score = dmg
                best_move_name = m_name
            
    return best_move_name