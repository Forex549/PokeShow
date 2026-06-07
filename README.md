## Arquitectura del sistema de batalla

### Flujo general
PokemonSelect → /battle/start → turnos → /battle/turn → resultado

### Equipos
Cada entrenador tiene exactamente 4 Pokémon. El jugador los elige en
PokemonSelect; la IA recibe el equipo enemigo también desde el frontend.

### Estrategias de IA disponibles
| Modo        | Descripción                                              |
|-------------|----------------------------------------------------------|
| `random`    | Elige movimiento aleatorio cada turno                    |
| `heuristic` | Elige el movimiento de mayor daño calculado              |
| `minimax2`  | Minimax con poda alfa-beta, heurística de HP, prof. 3    |
| `minimax3`  | Minimax con heurística de 4 factores (HP, vivos,         |
|             | velocidad, ventaja de tipo) con pesos entrenados por GA  |

### Endpoints de la API
| Método | Ruta              | Descripción                              |
|--------|-------------------|------------------------------------------|
| POST   | /battle/start     | Inicia batalla, recibe dos equipos de 4  |
| POST   | /battle/turn      | Ejecuta un turno con el movimiento dado  |
| POST   | /battle/switch    | Cambia el Pokémon activo del jugador     |
| GET    | /battle/{id}      | Recupera el estado actual de la batalla  |

### Cambio forzado de Pokémon
Cuando el Pokémon del jugador cae, el backend devuelve `needs_switch: true`.
El frontend bloquea los botones de movimiento y muestra el panel de selección
hasta que el jugador elija un Pokémon vivo. La IA cambia automáticamente.

### Archivos clave
- `src/api/schemas/battle.py` — modelos Pydantic de request/response
- `src/api/services/battle_service.py` — lógica central de batalla
- `src/api/api_v1/endpoints/battle.py` — rutas FastAPI
- `src/engine/logic/heuristic.py` — algoritmos de IA (Minimax niveles 1-3)
- `src/engine/models/battle.py` — motor de batalla (turnos, estados, efectos)
- `frontend/src/pages/Battle.jsx` — pantalla de batalla
- `frontend/src/pages/PokemonSelect.jsx` — selección de equipos