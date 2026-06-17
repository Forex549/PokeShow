import movesData from "../data/moves-data.json";
import { useState } from "react";

/**
 * MoveButtons — renders the player's move grid with PP badges.
 *
 * Props:
 *   moves    — array of MovePP objects: { name, pp, max_pp, available }
 *   onMove   — (moveName: string) => void
 *   disabled — bool (global disable during animation / battle finished)
 */
function MoveButtons({ moves, onMove, disabled }) {
  const [hoveredMove, setHoveredMove] = useState(null);

  const getMoveType = (moveName) => {
    const key = moveName.toLowerCase().replace(/\s+/g, "");
    return movesData[key]?.type || "Unknown";
  };

  const getTypeColor = (type) => {
    const typeColors = {
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
    return typeColors[type] || "#808080";
  };

  return (
    <div className="grid grid-cols-2 gap-2">
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
          <div key={move.name} className="relative">
            <button
              disabled={isDisabled}
              onClick={() => onMove(move.name)}
              className="w-full flex flex-col items-start p-3 transition-all duration-80 text-left"
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
                setHoveredMove(null);
              }}
              onMouseEnter={() => setHoveredMove(move.name)}
              >
              {/* Move name */}
              <span
                className="text-xs sm:text-sm font-bold capitalize leading-tight mb-1 break-words whitespace-normal"
                style={{ fontFamily: "var(--font-pixel)" }}
              >
                {move.name}
              </span>

              {/* PP badge */}
              <span
                className="text-[0.45rem] font-bold px-1.5 py-0.5"
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

            {/* Type tooltip hover */}
            {hoveredMove === move.name && !isDisabled && (
              <div
                style={{
                  position: "absolute",
                  bottom: "100%",
                  left: "50%",
                  transform: "translateX(-50%) translateY(-8px)",
                  background: getTypeColor(getMoveType(move.name)),
                  color: "#fff",
                  padding: "4px 8px",
                  borderRadius: "4px",
                  fontSize: "0.4rem",
                  fontFamily: "var(--font-pixel)",
                  fontWeight: "bold",
                  whiteSpace: "nowrap",
                  zIndex: 50,
                  border: "2px solid rgba(0,0,0,0.3)",
                  boxShadow: "0 2px 4px rgba(0,0,0,0.3)",
                }}
              >
                {getMoveType(move.name)}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

export default MoveButtons;
