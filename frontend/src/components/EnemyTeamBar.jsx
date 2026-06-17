/**
 * EnemyTeamBar — MASKED enemy bench.
 * Renders only name + alive/fainted dot. No HP bars (hp/max_hp are absent
 * from the masked PublicEnemyPokemonState contract).
 *
 * Props:
 *   team        — array of PublicEnemyPokemonState: { name, is_fainted }
 *   activeIndex — currently active slot index
 */
function EnemyTeamBar({ team, activeIndex }) {
  return (
    <div className="flex gap-3 items-center w-full justify-between">
      {team.map((p, i) => {
        const isActive  = i === activeIndex;
        const isFainted = p.is_fainted;

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

            {/* Status dot — no HP bar (data intentionally absent) */}
            <div
              className="w-4 h-4 rounded-full border-2"
              style={{
                background: isFainted
                  ? "var(--color-poke-text-muted)"
                  : "var(--color-poke-green)",
                borderColor: "var(--color-poke-panel-edge)",
              }}
              title={isFainted ? "Debilitado" : "En pie"}
            />

            <span
              className="text-[0.35rem]"
              style={{
                fontFamily: "var(--font-pixel)",
                color: isFainted ? "var(--color-poke-red)" : "var(--color-poke-text-muted)",
              }}
            >
              {isFainted ? "✗" : "●"}
            </span>
          </div>
        );
      })}
    </div>
  );
}

export default EnemyTeamBar;
