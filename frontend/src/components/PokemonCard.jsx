import { getPokemonSprite } from "../utils/sprites";

function PokemonCard({
    pokemon,
    back = false,
}) {
    const hpPercent =
        (pokemon.hp / pokemon.max_hp) * 100;

    return (
        <div className="bg-white rounded-2xl shadow-xl p-5 w-[300px]">
            <div className="flex justify-center">
                <img
                    src={getPokemonSprite(
                        pokemon.name,
                        back
                    )}
                    alt={pokemon.name}
                    className="w-44"
                />
            </div>

            <h2 className="text-2xl font-bold text-center capitalize">
                {pokemon.name}
            </h2>

            <div className="mt-4">
                <div className="w-full bg-gray-300 rounded-full h-5">
                    <div
                        className="bg-green-500 h-5 rounded-full transition-all"
                        style={{
                            width: `${hpPercent}%`,
                        }}
                    />
                </div>

                <p className="text-center mt-2">
                    HP: {pokemon.hp}/{pokemon.max_hp}
                </p>
            </div>
        </div>
    );
}

export default PokemonCard;