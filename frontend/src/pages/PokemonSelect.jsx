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
        <div className="min-h-screen bg-green-200 p-10">
            <h1 className="text-5xl font-bold text-center mb-10">
                Seleccionar Pokémon
            </h1>

            <div className="grid grid-cols-2 gap-10">
                {/* PLAYER */}
                <div className="bg-white rounded-2xl p-6 shadow-xl">
                    <h2 className="text-3xl font-bold mb-4">
                        Jugador
                    </h2>

                    <select
                        className="w-full p-3 border rounded-xl mb-5"
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

                    <div className="flex justify-center">
                        <img
                            src={getPokemonSprite(
                                playerPokemon,
                                true
                            )}
                            alt={playerPokemon}
                            className="w-52"
                        />
                    </div>
                </div>

                {/* ENEMY */}
                <div className="bg-white rounded-2xl p-6 shadow-xl">
                    <h2 className="text-3xl font-bold mb-4">
                        Enemigo
                    </h2>

                    <select
                        className="w-full p-3 border rounded-xl mb-5"
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

                    <div className="flex justify-center">
                        <img
                            src={getPokemonSprite(enemyPokemon)}
                            alt={enemyPokemon}
                            className="w-52"
                        />
                    </div>
                </div>
            </div>

            <div className="flex justify-center mt-10">
                <button
                    onClick={startBattle}
                    className="bg-blue-500 hover:bg-blue-600 text-white text-2xl px-10 py-4 rounded-2xl shadow-xl"
                >
                    Iniciar Batalla
                </button>
            </div>
        </div>
    );
}

export default PokemonSelect;