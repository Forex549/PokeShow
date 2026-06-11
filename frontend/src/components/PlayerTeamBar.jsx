/**
 * PlayerTeamBar — full info (name + HP bar + %) for the player's bench.
 * Props:
 *   team        — array of BattlePokemonState (full: hp, max_hp, is_fainted)
 *   activeIndex — currently active slot index
 */
function PlayerTeamBar({ team, activeIndex }) {
  return (
    <div className="flex gap-3 items-center flex-wrap">
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
            className="flex flex-col items-center gap-1"
            style={{ opacity: isActive ? 1 : 0.55 }}
          >
            <span
              className="text-[0.4rem] capitalize truncate w-14 text-center"
              style={{
                fontFamily: "var(--font-pixel)",
                color: "var(--color-poke-text)",
                fontWeight: isActive ? "bold" : "normal",
              }}
            >
              {p.name}
            </span>

            <div
              className="w-14 h-2 overflow-hidden"
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
