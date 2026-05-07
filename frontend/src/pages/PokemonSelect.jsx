import { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";

import pokemonList from "../data/pokemonList";
import { getPokemonSprite } from "../utils/sprites";

function PokemonSelect() {
    const navigate = useNavigate();
    const location = useLocation();

    const mode = location.state?.mode;

    const [playerPokemon, setPlayerPokemon] =
        useState("charizard");

    const [enemyPokemon, setEnemyPokemon] =
        useState("mewtwo");

    const startBattle = () => {
        navigate("/battle", {
            state: {
                mode,
                playerPokemon,
                enemyPokemon,
            },
        });
    };

    return (
        <div className="min-h-screen bg-slate-100 px-6 py-10">

            {/* Header */}
            <div className="text-center mb-12">
                <h1 className="text-6xl font-black text-slate-800 mb-4">
                    Seleccionar Pokémon
                </h1>

                <p className="text-slate-500 text-xl">
                    Elige los combatientes para la batalla
                </p>
            </div>

            {/* Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-10 max-w-6xl mx-auto">

                {/* PLAYER */}
                <div className="
                    bg-white
                    rounded-[32px]
                    p-8
                    shadow-xl
                    border border-slate-200
                ">

                    <div className="flex items-center justify-between mb-6">
                        <h2 className="text-3xl font-black text-slate-800">
                            Jugador
                        </h2>

                        <span className="
                            bg-sky-100
                            text-sky-700
                            px-4 py-2
                            rounded-full
                            text-sm
                            font-bold
                        ">
                            USUARIO
                        </span>
                    </div>

                    {/* SELECT */}
                    <select
                        className="
                            w-full
                            p-4
                            rounded-2xl
                            border border-slate-300
                            bg-slate-50
                            text-lg
                            mb-8
                            outline-none
                            focus:ring-4
                            focus:ring-sky-200
                        "
                        value={playerPokemon}
                        onChange={(e) =>
                            setPlayerPokemon(e.target.value)
                        }
                    >
                        {pokemonList.map((pokemon) => (
                            <option key={pokemon} value={pokemon}>
                                {pokemon}
                            </option>
                        ))}
                    </select>

                    {/* SPRITE */}
                    <div className="
                        bg-slate-50
                        rounded-3xl
                        p-6
                        flex
                        justify-center
                        items-center
                        h-[320px]
                    ">
                        <img
                            src={getPokemonSprite(
                                playerPokemon,
                                true
                            )}
                            alt={playerPokemon}
                            className="
                                w-64
                                hover:scale-110
                                transition-all
                                duration-300
                            "
                        />
                    </div>
                </div>

                {/* ENEMY */}
                <div className="
                    bg-white
                    rounded-[32px]
                    p-8
                    shadow-xl
                    border border-slate-200
                ">

                    <div className="flex items-center justify-between mb-6">
                        <h2 className="text-3xl font-black text-slate-800">
                            Enemigo
                        </h2>

                        <span className="
                            bg-rose-100
                            text-rose-700
                            px-4 py-2
                            rounded-full
                            text-sm
                            font-bold
                        ">
                            IA
                        </span>
                    </div>

                    {/* SELECT */}
                    <select
                        className="
                            w-full
                            p-4
                            rounded-2xl
                            border border-slate-300
                            bg-slate-50
                            text-lg
                            mb-8
                            outline-none
                            focus:ring-4
                            focus:ring-rose-200
                        "
                        value={enemyPokemon}
                        onChange={(e) =>
                            setEnemyPokemon(e.target.value)
                        }
                    >
                        {pokemonList.map((pokemon) => (
                            <option key={pokemon} value={pokemon}>
                                {pokemon}
                            </option>
                        ))}
                    </select>

                    {/* SPRITE */}
                    <div className="
                        bg-slate-50
                        rounded-3xl
                        p-6
                        flex
                        justify-center
                        items-center
                        h-[320px]
                    ">
                        <img
                            src={getPokemonSprite(enemyPokemon)}
                            alt={enemyPokemon}
                            className="
                                w-64
                                hover:scale-110
                                transition-all
                                duration-300
                            "
                        />
                    </div>
                </div>
            </div>

            {/* BUTTON */}
            <div className="flex justify-center mt-14">
                <button
                    onClick={startBattle}
                    className="
                        bg-sky-500
                        hover:bg-sky-600
                        text-white
                        text-2xl
                        font-bold
                        px-12
                        py-5
                        rounded-2xl
                        shadow-xl
                        transition-all
                        duration-300
                        hover:scale-105
                    "
                >
                    Iniciar Batalla
                </button>
            </div>
        </div>
    );
}

export default PokemonSelect;