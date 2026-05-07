import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import { api } from "../services/api";

import PokemonCard from "../components/PokemonCard";
import MoveButtons from "../components/MoveButtons";
import BattleLog from "../components/BattleLog";

function Battle() {
    const navigate = useNavigate();
    const location = useLocation();

    const mode = location.state?.mode;

    const playerPokemon =
        location.state?.playerPokemon;

    const enemyPokemon =
        location.state?.enemyPokemon;

    const [battle, setBattle] = useState(null);

    // NUEVOS STATES
    const [visibleLogs, setVisibleLogs] =
        useState([]);

    const [isAnimating, setIsAnimating] =
        useState(false);

    useEffect(() => {
        startBattle();
    }, []);

    const startBattle = async () => {
        // Crear usuario
        const userResponse = await api.post(
            "/users",
            {
                username: "Esther",
            }
        );

        const userId = userResponse.data.id;

        // Crear batalla
        const battleResponse = await api.post(
            "/battle/start",
            {
                user_id: userId,
                player_pokemon: playerPokemon,
                enemy_pokemon: enemyPokemon,
                mode,
            }
        );

        setBattle(battleResponse.data);

        // Mostrar logs iniciales
        setVisibleLogs(
            battleResponse.data.logs || []
        );
    };

    const playTurn = async (move) => {
        if (isAnimating) return;

        setIsAnimating(true);

        const previousLogs =
            battle.logs || [];

        const response = await api.post(
            "/battle/turn",
            {
                battle_id: battle.battle_id,
                player_move: move,
            }
        );

        setBattle(response.data);

        // Solo logs nuevos
        const newLogs =
            response.data.logs.slice(
                previousLogs.length
            );

        // Mostrar logs uno por uno
        for (let i = 0; i < newLogs.length; i++) {
            await new Promise((resolve) =>
                setTimeout(resolve, 1200)
            );

            setVisibleLogs((prev) => [
                ...prev,
                newLogs[i],
            ]);
        }

        setIsAnimating(false);

        // Esperar antes del resultado
        if (response.data.winner) {
            setTimeout(() => {
                navigate("/result", {
                    state: {
                        winner:
                            response.data.winner,
                        turns:
                            response.data.logs,
                        mode,
                    },
                });
            }, 4000);
        }
    };

    if (!battle) {
        return (
            <div className="min-h-screen flex justify-center items-center text-3xl">
                Cargando batalla...
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-green-300 p-10">
            <h1 className="text-5xl font-bold text-center mb-10">
                Pokémon Battle
            </h1>

            {/* ARENA */}
            <div className="flex justify-between mb-10">
                <PokemonCard
                    pokemon={battle.player}
                    back={true}
                />

                <PokemonCard
                    pokemon={battle.enemy}
                />
            </div>

            {/* LOGS */}
            <div className="mb-10">
                <BattleLog
                    logs={visibleLogs}
                />
            </div>

            {/* MOVES */}
            <MoveButtons
                moves={battle.player.moves}
                onMove={playTurn}
                disabled={isAnimating}
            />
        </div>
    );
}

export default Battle;