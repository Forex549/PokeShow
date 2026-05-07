export const getPokemonSprite = (name, back = false) => {
  const formatted = name
    .toLowerCase()
    .replaceAll(" ", "")
    .replaceAll(".", "");

  const folder = back ? "ani-back" : "ani";

  return `https://play.pokemonshowdown.com/sprites/${folder}/${formatted}.gif`;
};