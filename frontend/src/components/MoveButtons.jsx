/**
 * MoveButtons — renders the player's move grid with PP badges.
 *
 * Props:
 *   moves    — array of MovePP objects: { name, pp, max_pp, available }
 *   onMove   — (moveName: string) => void
 *   disabled — bool (global disable during animation / battle finished)
 */
function MoveButtons({ moves, onMove, disabled }) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
      {moves.map((move) => {
        const isExhausted = move.pp <= 0 || !move.available;
        const isDisabled  = disabled || isExhausted;

        // PP color: green >= 50%, amber >= 25%, red < 25%
        const ppRatio = move.max_pp > 0 ? move.pp / move.max_pp : 0;
        const ppColor =
          isExhausted
            ? "var(--color-poke-text-muted)"
            : ppRatio >= 0.5
              ? "var(--color-poke-green)"
              : ppRatio >= 0.25
                ? "var(--color-poke-amber)"
                : "var(--color-poke-red)";

        return (
          <button
            key={move.name}
            disabled={isDisabled}
            onClick={() => onMove(move.name)}
            className="flex flex-col items-start p-3 transition-all duration-80 text-left"
            style={{
              border: `3px solid ${isDisabled ? "var(--color-poke-panel-edge)" : "var(--color-poke-panel-edge)"}`,
              borderRadius: "var(--radius-retro)",
              background: isDisabled
                ? "var(--color-poke-panel-dark)"
                : "var(--color-poke-blue)",
              boxShadow: isDisabled
                ? "2px 2px 0 var(--color-poke-panel-edge)"
                : "3px 3px 0 var(--color-poke-blue-dark)",
              color: isDisabled ? "var(--color-poke-text-muted)" : "#fff",
              opacity: isExhausted ? 0.45 : 1,
              cursor: isDisabled ? "not-allowed" : "pointer",
            }}
            onMouseDown={(e) => {
              if (!isDisabled) {
                e.currentTarget.style.transform = "translate(2px,2px)";
                e.currentTarget.style.boxShadow = "1px 1px 0 var(--color-poke-blue-dark)";
              }
            }}
            onMouseUp={(e) => {
              e.currentTarget.style.transform = "";
              e.currentTarget.style.boxShadow = isDisabled
                ? "2px 2px 0 var(--color-poke-panel-edge)"
                : "3px 3px 0 var(--color-poke-blue-dark)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = "";
            }}
          >
            {/* Move name */}
            <span
              className="text-[0.5rem] font-bold capitalize leading-tight mb-1"
              style={{ fontFamily: "var(--font-pixel)" }}
            >
              {move.name}
            </span>

            {/* PP badge */}
            <span
              className="text-[0.4rem] font-bold px-1.5 py-0.5"
              style={{
                fontFamily: "var(--font-pixel)",
                border: `2px solid ${isDisabled ? "var(--color-poke-panel-edge)" : "rgba(255,255,255,0.4)"}`,
                borderRadius: "var(--radius-retro-sm)",
                background: isDisabled ? "var(--color-poke-panel)" : "rgba(0,0,0,0.2)",
                color: ppColor,
              }}
            >
              PP {move.pp}/{move.max_pp}
            </span>
          </button>
        );
      })}
    </div>
  );
}

export default MoveButtons;
