import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { api } from "../services/api";
import PokemonCard from "../components/PokemonCard";
import MoveButtons from "../components/MoveButtons";
import BattleLog from "../components/BattleLog";

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

// Mini componente: muestra el equipo completo con HP
function TeamBar({ team, activeIndex, isPlayer }) {
    const accent = isPlayer ? "bg-sky-500" : "bg-rose-500";
    const faintedColor = "bg-slate-300";

    return (
        <div className="flex gap-2 items-center">
            {team.map((p, i) => {
                const pct = Math.max(0, Math.round((p.hp / p.max_hp) * 100));
                const isActive = i === activeIndex;
                const isFainted = p.hp <= 0;

                return (
                    <div
                        key={i}
                        className={`flex flex-col items-center gap-1
                            ${isActive ? "opacity-100" : "opacity-50"}`}
                    >
                        <span className="text-xs text-slate-500 capitalize truncate w-14 text-center">
                            {p.name}
                        </span>
                        <div className="w-14 h-2 bg-slate-200 rounded-full overflow-hidden">
                            <div
                                className={`h-full rounded-full transition-all duration-500
                                    ${isFainted ? faintedColor : accent}`}
                                style={{ width: `${pct}%` }}
                            />
                        </div>
                        <span className="text-xs text-slate-400">
                            {isFainted ? "✗" : `${pct}%`}
                        </span>
                    </div>
                );
            })}
        </div>
    );
}

// Panel de cambio obligatorio cuando el pokémon cae
function SwitchPanel({ team, activeIndex, onSwitch }) {
    return (
        <div className="bg-white rounded-3xl p-6 shadow-xl border border-rose-200">
            <h3 className="text-lg font-black text-rose-600 mb-4 text-center">
                ¡Tu Pokémon se debilitó! Elige el siguiente
            </h3>
            <div className="grid grid-cols-2 gap-3">
                {team.map((p, i) => {
                    const canSwitch = p.hp > 0 && i !== activeIndex;
                    return (
                        <button
                            key={i}
                            disabled={!canSwitch}
                            onClick={() => onSwitch(i)}
                            className={`p-3 rounded-2xl border text-left transition-all duration-200
                                ${canSwitch
                                    ? "bg-sky-50 border-sky-300 hover:bg-sky-100 hover:scale-105"
                                    : "bg-slate-50 border-slate-200 opacity-40 cursor-not-allowed"}`}
                        >
                            <p className="font-bold text-slate-800 capitalize text-sm">{p.name}</p>
                            <p className="text-xs text-slate-500">
                                {p.hp <= 0 ? "Debilitado" : `${p.hp}/${p.max_hp} HP`}
                            </p>
                        </button>
                    );
                })}
            </div>
        </div>
    );
}

function Battle() {
    const navigate = useNavigate();
    const location = useLocation();

    const mode = location.state?.mode;
    const playerTeam = location.state?.playerTeam;  // array de 4 nombres
    const enemyTeam = location.state?.enemyTeam;

    const [battle, setBattle] = useState(null);
    const [visibleLogs, setVisibleLogs] = useState([]);
    const [isAnimating, setIsAnimating] = useState(false);
    const [attacking, setAttacking] = useState(null);
    const [damaged, setDamaged] = useState(null);
    const [battleMessage, setBattleMessage] = useState("Elige un movimiento");
    const [showVoluntarySwitch, setShowVoluntarySwitch] = useState(false);

    useEffect(() => {
        startBattle();
    }, []);

    const startBattle = async () => {
        const userResponse = await api.post("/users", { username: "Jugador" });
        const userId = userResponse.data.id;

        const battleResponse = await api.post("/battle/start", {
            user_id: userId,
            player_team: playerTeam,   // ["garchomp", "sylveon", "greninja", "ceruledge"]
            mode: mode,
        });

        setBattle(battleResponse.data);
        setVisibleLogs(battleResponse.data.logs || []);
    };

    const playTurn = async (move) => {
        if (isAnimating || !battle || battle.needs_switch) return;

        setIsAnimating(true);
        const previousLogs = battle.logs || [];

        const response = await api.post("/battle/turn", {
            battle_id: battle.battle_id,
            player_move: move,
        });

        await animateTurn(response.data, previousLogs);
        setIsAnimating(false);

        if (response.data.winner) {
            setTimeout(() => {
                navigate("/result", {
                    state: { winner: response.data.winner, turns: response.data.logs, mode },
                });
            }, 2000);
        }
    };

    const switchPokemon = async (index, voluntary = false) => {
        if (isAnimating || !battle) return;

        setIsAnimating(true);
        setShowVoluntarySwitch(false);

        const response = await api.post("/battle/switch", {
            battle_id: battle.battle_id,
            pokemon_index: index,
            voluntary,
        });

        await animateTurn(response.data, battle.logs);
        setIsAnimating(false);

        if (response.data.winner) {
            setTimeout(() => navigate("/result", {
                state: { winner: response.data.winner, turns: response.data.logs, mode }
            }), 2000);
        }
    };

    const animateTurn = async (updatedBattle, previousLogs) => {
        const firstTurn = updatedBattle.first_turn;
        const newLogs = updatedBattle.logs.slice(previousLogs.length);

        for (let i = 0; i < newLogs.length; i++) {
            const log = newLogs[i];
            setVisibleLogs((prev) => [...prev, log]);
            setBattleMessage(log);
            await sleep(700);

            const isPlayerAttack =
                (firstTurn === "player" && i === 1) ||
                (firstTurn === "enemy" && i === 2);
            const isEnemyAttack =
                (firstTurn === "enemy" && i === 1) ||
                (firstTurn === "player" && i === 2);

            if (isPlayerAttack && log.includes("usó")) {
                setAttacking("player"); await sleep(400);
                setAttacking(null);
                setDamaged("enemy"); await sleep(300);
                setDamaged(null);
            }
            if (isEnemyAttack && log.includes("usó")) {
                setAttacking("enemy"); await sleep(400);
                setAttacking(null);
                setDamaged("player"); await sleep(300);
                setDamaged(null);
            }
            if (log.includes("debilitó")) {
                await sleep(1000);
            }
        }

        setBattle(updatedBattle);
        if (!updatedBattle.needs_switch) {
            setBattleMessage("Elige un movimiento");
        } else {
            setBattleMessage("¡Elige tu siguiente Pokémon!");
        }
    };

    // ── Loading ──────────────────────────────────────────────────────────────
    if (!battle) {
        return (
            <div className="min-h-screen flex justify-center items-center text-2xl text-slate-600">
                Cargando batalla...
            </div>
        );
    }

    // ── Render ───────────────────────────────────────────────────────────────
    return (
        <div className="min-h-screen bg-slate-100 p-8">

            <div className="flex justify-center">
                <h1 className="text-4xl font-extrabold text-slate-800 mb-8">
                    Pokémon Battle
                </h1>
            </div>

            {/* BARRAS DE EQUIPO */}
            <div className="flex justify-between items-center bg-white rounded-2xl px-6 py-4 shadow mb-6">
                <div>
                    <p className="text-xs text-slate-400 mb-2 font-bold uppercase tracking-wider">
                        Tu equipo
                    </p>
                    <TeamBar
                        team={battle.player_team}
                        activeIndex={battle.player_index}
                        isPlayer={true}
                    />
                </div>
                <div className="text-slate-300 text-3xl font-black">VS</div>
                <div className="text-right">
                    <p className="text-xs text-slate-400 mb-2 font-bold uppercase tracking-wider">
                        Equipo IA
                    </p>
                    <TeamBar
                        team={battle.enemy_team}
                        activeIndex={battle.enemy_index}
                        isPlayer={false}
                    />
                </div>
            </div>

            {/* MENSAJE */}
            <div className="flex justify-center mb-4">
                <div className="bg-white px-8 py-3 rounded-2xl shadow text-lg font-semibold
                    text-slate-700 min-w-[320px] text-center transition-all duration-300">
                    {battleMessage}
                </div>
            </div>

            {/* ARENA */}
            <div className="flex justify-between items-end mb-6 bg-white rounded-[40px] p-8 shadow-xl">
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
            <div className="mb-6">
                <BattleLog logs={visibleLogs} />
            </div>

            {/* CAMBIO OBLIGATORIO o MOVIMIENTOS */}
            {battle.needs_switch ? (
                <SwitchPanel
                    team={battle.player_team}
                    activeIndex={battle.player_index}
                    onSwitch={(i) => switchPokemon(i, false)}
                />
            ) : (
                <div className="flex flex-col gap-4">
                    <MoveButtons
                        moves={battle.player.moves}
                        onMove={playTurn}
                        disabled={isAnimating || battle.finished}
                    />

                    {/* Botón cambio voluntario */}
                    {!battle.finished && (
                        <div className="flex justify-center">
                            <button
                                onClick={() => setShowVoluntarySwitch(!showVoluntarySwitch)}
                                disabled={isAnimating}
                                className="bg-amber-100 hover:bg-amber-200 text-amber-800
                        font-bold px-6 py-3 rounded-2xl border border-amber-300
                        transition-all duration-200 disabled:opacity-40"
                            >
                                {showVoluntarySwitch ? "Cancelar" : "⇄ Cambiar Pokémon"}
                            </button>
                        </div>
                    )}

                    {/* Panel de cambio voluntario */}
                    {showVoluntarySwitch && (
                        <div className="bg-white rounded-3xl p-6 shadow-xl border border-amber-200">
                            <h3 className="text-lg font-black text-amber-700 mb-2 text-center">
                                Cambiar Pokémon
                            </h3>
                            <p className="text-slate-400 text-sm text-center mb-4">
                                La IA atacará este turno igualmente
                            </p>
                            <div className="grid grid-cols-2 gap-3">
                                {battle.player_team.map((p, i) => {
                                    const canSwitch = p.hp > 0 && i !== battle.player_index;
                                    return (
                                        <button
                                            key={i}
                                            disabled={!canSwitch}
                                            onClick={() => switchPokemon(i, true)}  // voluntario
                                            className={`p-3 rounded-2xl border text-left transition-all duration-200
                                    ${canSwitch
                                                    ? "bg-amber-50 border-amber-300 hover:bg-amber-100 hover:scale-105"
                                                    : "bg-slate-50 border-slate-200 opacity-40 cursor-not-allowed"}`}
                                        >
                                            <p className="font-bold text-slate-800 capitalize text-sm">{p.name}</p>
                                            <p className="text-xs text-slate-500">
                                                {p.hp <= 0 ? "Debilitado" : `${p.hp}/${p.max_hp} HP`}
                                            </p>
                                        </button>
                                    );
                                })}
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

export default Battle;