import { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";

import pokemonList from "../data/pokemonList";
import { getPokemonSprite } from "../utils/sprites";

const TEAM_SIZE = 4;
const EMPTY = "";

function SlotCard({ slot, index, team, onChange, isPlayer }) {
    const others = team.filter((_, i) => i !== index);
    const accent = isPlayer
        ? { ring: "focus:ring-sky-200", badge: "bg-sky-100 text-sky-800" }
        : { ring: "focus:ring-rose-200", badge: "bg-rose-100 text-rose-800" };

    return (
        <div className={`bg-white rounded-3xl p-4 border shadow-sm transition-all duration-200
            ${slot ? "border-slate-200" : "border-dashed border-slate-300"}`}>

            <div className="flex justify-between items-center mb-3">
                <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">
                    Slot {index + 1}
                </span>
                {slot && (
                    <span className={`${accent.badge} px-2 py-1 rounded-full text-xs font-bold capitalize`}>
                        {slot}
                    </span>
                )}
            </div>

            <select
                className={`w-full p-2 rounded-xl border border-slate-300 bg-slate-50
                    text-sm mb-3 outline-none focus:ring-4 ${accent.ring}`}
                value={slot}
                onChange={(e) => onChange(index, e.target.value)}
            >
                <option value="">— Elegir —</option>
                {pokemonList.map((p) => (
                    <option key={p} value={p} disabled={others.includes(p)}>
                        {p}
                    </option>
                ))}
            </select>

            <div className="bg-slate-50 rounded-2xl flex justify-center items-center h-24">
                {slot ? (
                    <img
                        src={getPokemonSprite(slot, isPlayer)}
                        alt={slot}
                        className="h-20 hover:scale-110 transition-all duration-300"
                    />
                ) : (
                    <span className="text-slate-300 text-3xl">?</span>
                )}
            </div>
        </div>
    );
}

function TeamPanel({ label, team, onChange, isPlayer }) {
    const badgeClass = isPlayer
        ? "bg-sky-100 text-sky-700"
        : "bg-rose-100 text-rose-700";

    const filled = team.filter((p) => p !== EMPTY).length;

    return (
        <div className="bg-white rounded-[32px] p-6 shadow-xl border border-slate-200">
            <div className="flex items-center justify-between mb-4">
                <h2 className="text-2xl font-black text-slate-800">{label}</h2>
                <div className="flex items-center gap-2">
                    <span className="text-slate-400 text-sm">{filled}/{TEAM_SIZE}</span>
                    <span className={`${badgeClass} px-3 py-1 rounded-full text-xs font-bold`}>
                        {isPlayer ? "USUARIO" : "IA"}
                    </span>
                </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
                {team.map((slot, i) => (
                    <SlotCard
                        key={i}
                        slot={slot}
                        index={i}
                        team={team}
                        onChange={onChange}
                        isPlayer={isPlayer}
                    />
                ))}
            </div>
        </div>
    );
}

function PokemonSelect() {
    const navigate = useNavigate();
    const location = useLocation();
    const mode = location.state?.mode;

    const [playerTeam, setPlayerTeam] = useState(Array(TEAM_SIZE).fill(EMPTY));
    const [enemyTeam, setEnemyTeam] = useState(Array(TEAM_SIZE).fill(EMPTY));

    const updateTeam = (setter) => (index, value) => {
        setter((prev) => {
            const next = [...prev];
            next[index] = value;
            return next;
        });
    };

    const teamComplete = (team) => team.every((p) => p !== EMPTY);
    const canStart = teamComplete(playerTeam) && teamComplete(enemyTeam);

    const startBattle = () => {
        if (!canStart) return;
        navigate("/battle", {
            state: { mode, playerTeam, enemyTeam },
        });
    };

    return (
        <div className="min-h-screen bg-slate-100 px-6 py-10">

            <div className="text-center mb-10">
                <h1 className="text-5xl font-black text-slate-800 mb-3">
                    Seleccionar Equipo
                </h1>
                <p className="text-slate-500 text-lg">
                    Elige 4 Pokémon para cada lado
                </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-6xl mx-auto">
                <TeamPanel
                    label="Jugador"
                    team={playerTeam}
                    onChange={updateTeam(setPlayerTeam)}
                    isPlayer={true}
                />
                <TeamPanel
                    label="Enemigo"
                    team={enemyTeam}
                    onChange={updateTeam(setEnemyTeam)}
                    isPlayer={false}
                />
            </div>

            <div className="flex flex-col items-center mt-10 gap-3">
                {!canStart && (
                    <p className="text-slate-400 text-sm">
                        Completa los 4 slots de cada equipo para continuar
                    </p>
                )}
                <button
                    onClick={startBattle}
                    disabled={!canStart}
                    className={`text-white text-xl font-bold px-12 py-4 rounded-2xl shadow-xl
                        transition-all duration-300
                        ${canStart
                            ? "bg-sky-500 hover:bg-sky-600 hover:scale-105"
                            : "bg-slate-300 cursor-not-allowed"}`}
                >
                    ¡Iniciar Batalla!
                </button>
            </div>
        </div>
    );
}

export default PokemonSelect;