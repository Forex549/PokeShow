/**
 * PlayerTeamBar — full info (name + HP bar + %) for the player's bench.
 * Props:
 *   team        — array of BattlePokemonState (full: hp, max_hp, is_fainted)
 *   activeIndex — currently active slot index
 */

const TYPE_COLORS = {
  Normal: "#A8A878",
  Fire: "#F08030",
  Water: "#6890F0",
  Electric: "#F8D030",
  Grass: "#78C850",
  Ice: "#98D8D8",
  Fighting: "#C03028",
  Poison: "#A040A0",
  Ground: "#E0C068",
  Flying: "#A890F0",
  Psychic: "#F85888",
  Bug: "#A8B820",
  Rock: "#B8A038",
  Ghost: "#705898",
  Dragon: "#7038F8",
  Dark: "#705848",
  Steel: "#B8B8D0",
  Fairy: "#EE99AC",
};

function TypeBadge({ type }) {
  return (
    <span
      className="text-[0.3rem] font-bold uppercase px-1 py-0"
      style={{
        background: TYPE_COLORS[type] || "#808080",
        color: "#fff",
        border: "1px solid rgba(0,0,0,0.2)",
        borderRadius: "2px",
        lineHeight: 1,
        fontFamily: "var(--font-pixel)",
        textShadow: "0.5px 0.5px 0 rgba(0,0,0,0.3)",
        display: "inline-block",
      }}
    >
      {type}
    </span>
  );
}

function PlayerTeamBar({ team, activeIndex }) {
  return (
    <div className="flex gap-3 items-center w-full justify-between">
      {team.map((p, i) => {
        const pct     = p.max_hp > 0 ? Math.max(0, Math.round((p.hp / p.max_hp) * 100)) : 0;
        const isActive  = i === activeIndex;
        const isFainted = p.hp <= 0 || p.is_fainted;

        const barColor = isFainted
          ? "var(--color-poke-text-muted)"
          : pct >= 50
            ? "var(--color-poke-green)"
            : pct >= 25
              ? "var(--color-poke-amber)"
              : "var(--color-poke-red)";

        return (
          <div
            key={i}
            className="flex flex-col items-center gap-1 transition-all duration-200"
            style={{ opacity: isActive ? 1 : 0.55, transform: isActive ? 'scale(1.03)' : 'none' }}
          >
            <span
              className="text-[0.45rem] capitalize text-center w-20"
              style={{
                fontFamily: "var(--font-pixel)",
                color: "var(--color-poke-text)",
                fontWeight: isActive ? "bold" : "normal",
                whiteSpace: 'nowrap',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                letterSpacing: 'normal',
              }}
            >
              {p.name}
            </span>

            {/* Type badges */}
            {p.types && p.types.length > 0 && (
              <div className="flex gap-0.5 justify-center flex-wrap">
                {p.types.map((type) => (
                  <TypeBadge key={type} type={type} />
                ))}
              </div>
            )}

            <div
              className="w-16 h-2 overflow-hidden"
              style={{
                background: "var(--color-poke-panel-dark)",
                border: "2px solid var(--color-poke-panel-edge)",
                borderRadius: "var(--radius-retro-sm)",
              }}
            >
              <div
                className="h-full transition-all duration-500"
                style={{ width: `${pct}%`, background: barColor }}
              />
            </div>

            <span
              className="text-[0.4rem]"
              style={{
                fontFamily: "var(--font-pixel)",
                color: isFainted ? "var(--color-poke-red)" : "var(--color-poke-text-muted)",
              }}
            >
              {isFainted ? "✗" : `${pct}%`}
            </span>
          </div>
        );
      })}
    </div>
  );
}

export default PlayerTeamBar;
