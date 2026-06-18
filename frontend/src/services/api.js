import axios from "axios";

export const api = axios.create({
  baseURL: "http://localhost:8000/api/v1",
});

/**
 * Start a new battle.
 * @param {object} params
 * @param {string}   params.userId
 * @param {string[]} params.playerTeam  — exactly 4 names
 * @param {string}   params.playerMode  — "human" | BattleMode value
 * @param {string}   params.enemyMode   — BattleMode value (random|heuristic|minimax2|minimax3|minimax4)
 * @param {string[]} params.enemyTeam   — optional, exactly 4 names (for AI vs AI or pre-selected enemy team)
 * @returns {Promise<PublicBattleStateResponse>}
 */
export async function startBattle({ userId, playerTeam, playerMode = "human", enemyMode = "random", enemyTeam = null }) {
  const body = {
    user_id: userId,
    player_team: playerTeam,
    player_mode: playerMode,
    enemy_mode: enemyMode,
  };
  if (enemyTeam) {
    body.enemy_team = enemyTeam;
  }
  const response = await api.post("/battle/start", body);
  return response.data;
}

/**
 * Play one turn.
 * @param {object} params
 * @param {string}         params.battleId
 * @param {string|null}    params.playerMove — null when player_mode != "human" (IA-vs-IA)
 * @returns {Promise<PublicBattleStateResponse>}
 */
export async function playTurn({ battleId, playerMove = null }) {
  const body = { battle_id: battleId };
  if (playerMove !== null) body.player_move = playerMove;
  const response = await api.post("/battle/turn", body);
  return response.data;
}

/**
 * Switch active Pokémon.
 * @param {object} params
 * @param {string}  params.battleId
 * @param {number}  params.pokemonIndex
 * @param {boolean} params.voluntary  — true = voluntary switch; false = forced faint switch
 * @returns {Promise<PublicBattleStateResponse>}
 */
export async function switchPokemon({ battleId, pokemonIndex, voluntary = false }) {
  const response = await api.post("/battle/switch", {
    battle_id: battleId,
    pokemon_index: pokemonIndex,
    voluntary,
  });
  return response.data;
}

/**
 * Create or retrieve a user by username.
 * @param {string} username
 * @returns {Promise<{id: string}>}
 */
export async function getOrCreateUser(username = "Jugador") {
  const response = await api.post("/users", { username });
  return response.data;
}
