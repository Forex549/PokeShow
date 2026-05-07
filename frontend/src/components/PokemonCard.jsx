import { getPokemonSprite } from "../utils/sprites";

function PokemonCard({
    pokemon,
    back = false,
    attacking = false,
    damaged = false,
}) {
    const hpPercent =
        (pokemon.hp / pokemon.max_hp) * 100;

    return (
        <div
            className={`
                bg-white
                rounded-3xl
                shadow-lg
                p-6
                w-80
                transition-all
                duration-300
                ${attacking ? "scale-110" : ""}
                ${attacking && back ? "translate-x-10" : ""}
                ${attacking && !back ? "-translate-x-10" : ""}
                ${damaged ? "brightness-75" : ""}
            `}
        >
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
                <div className="w-full bg-gray-200 rounded-full h-4 mt-2">
                    <div
                        className="bg-green-500 h-4 rounded-full transition-all duration-500"
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