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

    const [visibleLogs, setVisibleLogs] =
        useState([]);

    const [isAnimating, setIsAnimating] =
        useState(false);

    const [attacking, setAttacking] = useState(null);

    const [damaged, setDamaged] =
        useState(null);

    const [battleMessage, setBattleMessage] =
        useState("Elige un movimiento");

    const sleep = (ms) =>
        new Promise((resolve) =>
            setTimeout(resolve, ms)
        );

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
        if (
            isAnimating ||
            !battle
        )
            return;

        setIsAnimating(true);

        const previousLogs =
            battle.logs || [];

        const response = await api.post(
            "/battle/turn",
            {
                battle_id:
                    battle.battle_id,
                player_move: move,
            }
        );

        const updatedBattle = response.data;

        const firstTurn =
            updatedBattle.first_turn;

        const newLogs =
            updatedBattle.logs.slice(
                previousLogs.length
            );

        for (
            let i = 0;
            i < newLogs.length;
            i++
        ) {
            const log = newLogs[i];

            // Mostrar log
            setVisibleLogs((prev) => [
                ...prev,
                log,
            ]);

            setBattleMessage(log);

            await sleep(700);

            // Detectar ataques
            const isPlayerAttack =
                (
                    firstTurn === "player" &&
                    i === 1
                ) ||
                (
                    firstTurn === "enemy" &&
                    i === 2
                );

            const isEnemyAttack =
                (
                    firstTurn === "enemy" &&
                    i === 1
                ) ||
                (
                    firstTurn === "player" &&
                    i === 2
                );

            // PLAYER ATTACK
            if (
                isPlayerAttack &&
                log.includes("uso")
            ) {
                setAttacking("player");

                await sleep(400);

                setAttacking(null);

                setDamaged("enemy");

                await sleep(300);

                setDamaged(null);
            }

            // ENEMY ATTACK
            if (
                isEnemyAttack &&
                log.includes("uso")
            ) {
                setAttacking("enemy");

                await sleep(400);

                setAttacking(null);

                setDamaged("player");

                await sleep(300);

                setDamaged(null);
            }

            // KO
            if (
                log.includes(
                    "se debilito"
                )
            ) {
                setBattleMessage(
                    "¡Pokémon debilitado!"
                );

                await sleep(2000);
            }
        }

        setBattle(updatedBattle);

        setBattleMessage(
            "Elige un movimiento"
        );

        setIsAnimating(false);
        if (response.data.winner) {
            setTimeout(() => {
                navigate("/result", {
                    state: {
                        winner:
                            response.data
                                .winner,
                        turns:
                            response.data
                                .logs,
                        mode,
                    },
                });
            }, 3000);
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
        <div className="min-h-screen bg-slate-100 p-10">
            <h1 className="text-5xl font-extrabold text-slate-800 mb-10">
                Pokémon Battle
            </h1>

            <div className="flex justify-center mb-6">
                <div
                    className="
                        bg-white
                        px-8
                        py-4
                        rounded-2xl
                        shadow-md
                        text-xl
                        font-semibold
                        text-slate-700
                        min-w-[320px]
                        text-center
                        transition-all
                        duration-300
                    "
                >
                    {battleMessage}
                </div>
            </div>

            {/* ARENA */}
            <div
                className="
                    flex
                    justify-between
                    items-end
                    mb-10
                    bg-white
                    rounded-[40px]
                    p-10
                    shadow-xl
                "
            >
                <PokemonCard
                    pokemon={battle.player}
                    back={true}
                    attacking={attacking === "player"}
                    damaged={damaged === "player"}
                />

                <PokemonCard
                    pokemon={battle.enemy}
                    attacking={attacking === "enemy"}
                    damaged={damaged === "enemy"}
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