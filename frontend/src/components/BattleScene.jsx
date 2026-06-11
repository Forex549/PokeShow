import { getPokemonSprite } from "../utils/sprites";

/**
 * BattleScene — HGSS-style battle field (ref: Pokémon HeartGold/SoulSilver, Showdown).
 *
 * Layout:
 *   - background image fills the scene (pixelated)
 *   - enemy: front sprite top-right on an oval platform, HP box top-left
 *   - player: back sprite bottom-left on an oval platform, HP box mid-right
 *   - dialog bar pinned to the bottom (dark slate outer, teal inner, red border)
 *
 * Props:
 *   background — url of the battlefield image
 *   player / enemy — battle pokemon: { name, hp, max_hp }
 *   attacking — "player" | "enemy" | null
 *   damaged   — "player" | "enemy" | null
 *   message   — current battle dialog text
 */

function hpColor(percent) {
  if (percent >= 50) return "var(--color-poke-green)";
  if (percent >= 25) return "var(--color-poke-amber)";
  return "var(--color-poke-red)";
}

// Status condition badges (engine codes → in-game Spanish labels)
const STATUS_BADGES = {
  brn:       { label: "QUE", color: "#e07030" },
  par:       { label: "PAR", color: "#c8a020" },
  psn:       { label: "ENV", color: "#9050b0" },
  slp:       { label: "DOR", color: "#8890a0" },
  frz:       { label: "CON", color: "#50a8d8" },
  confusion: { label: "CNF", color: "#d05878" },
};

function StatusBadge({ code }) {
  const badge = STATUS_BADGES[code];
  if (!badge) return null;
  return (
    <span
      style={{
        fontSize: "0.4rem",
        color: "#fff",
        background: badge.color,
        border: "1px solid var(--color-hgss-edge)",
        borderRadius: "3px",
        padding: "2px 4px",
        lineHeight: 1,
      }}
    >
      {badge.label}
    </span>
  );
}

// ── HP box (cream panel, olive edge, HGSS style) ─────────────
function HpBox({ pokemon, side }) {
  const isPlayer = side === "player";
  const percent = pokemon.max_hp > 0
    ? Math.max(0, (pokemon.hp / pokemon.max_hp) * 100)
    : 0;

  return (
    <div
      className="w-64 sm:w-72"
      style={{
        background: "var(--color-hgss-cream)",
        border: "3px solid var(--color-hgss-edge)",
        borderRadius: "8px",
        boxShadow: "4px 5px 0 var(--color-hgss-shadow)",
        padding: "8px 12px 7px",
        fontFamily: "var(--font-pixel)",
      }}
    >
      {/* Name + status + level */}
      <div className="flex items-center gap-2">
        <span
          className="uppercase truncate"
          style={{ fontSize: "0.55rem", color: "var(--color-hgss-edge)" }}
        >
          {pokemon.name}
        </span>
        <StatusBadge code={pokemon.status} />
        <StatusBadge code={pokemon.volatile_status} />
        <span
          className="ml-auto"
          style={{ fontSize: "0.5rem", color: "var(--color-hgss-edge)" }}
        >
          Lv100
        </span>
      </div>

      {/* HP label + bar */}
      <div className="flex items-center gap-1 mt-2">
        <span
          style={{
            fontSize: "0.4rem",
            color: "var(--color-hgss-hp-label)",
            background: "var(--color-hgss-bar-track)",
            border: "1px solid var(--color-hgss-edge)",
            borderRadius: "3px 0 0 3px",
            padding: "2px 4px",
          }}
        >
          HP
        </span>
        <div
          className="flex-1 h-2.5 overflow-hidden"
          style={{
            background: "var(--color-hgss-bar-track)",
            border: "1px solid var(--color-hgss-edge)",
            borderRadius: "0 3px 3px 0",
          }}
        >
          <div
            className="h-full transition-all duration-500"
            style={{
              width: `${percent}%`,
              background: hpColor(percent),
              borderRadius: "2px",
            }}
          />
        </div>
      </div>

      {/* Player only: HP numbers + EXP bar */}
      {isPlayer && (
        <>
          <p
            className="text-right mt-1.5"
            style={{ fontSize: "0.5rem", color: "var(--color-hgss-edge)" }}
          >
            {Math.max(0, pokemon.hp)}/{pokemon.max_hp}
          </p>
          <div className="flex items-center gap-1 mt-1">
            <span
              style={{
                fontSize: "0.35rem",
                color: "var(--color-hgss-hp-label)",
              }}
            >
              EXP
            </span>
            <div
              className="flex-1 h-1"
              style={{
                background: "var(--color-hgss-bar-track)",
                border: "1px solid var(--color-hgss-edge)",
                borderRadius: "2px",
              }}
            />
          </div>
        </>
      )}
    </div>
  );
}

// ── Oval ground platform under each sprite ───────────────────
function Platform({ className, style }) {
  return (
    <div
      className={`absolute ${className}`}
      style={{
        borderRadius: "50%",
        background:
          "radial-gradient(ellipse at center, rgba(40,48,40,0.30) 0%, rgba(40,48,40,0.18) 55%, rgba(40,48,40,0) 75%)",
        ...style,
      }}
    />
  );
}

// ── Battle sprite with attack / damage / faint states ────────
// Height comes from the positioned container so sprites scale with the scene
function BattleSprite({ pokemon, back, attacking, damaged }) {
  const fainted = pokemon.hp <= 0;
  const attackShift = back
    ? "translate(28px, -14px)"
    : "translate(-28px, 14px)";

  return (
    <img
      key={pokemon.name}
      src={getPokemonSprite(pokemon.name, back)}
      alt={pokemon.name}
      className={`pixelated relative h-full w-auto transition-all duration-300 ${damaged ? "animate-shake" : ""}`}
      style={{
        transform: fainted
          ? "translateY(30px)"
          : attacking
            ? attackShift
            : "none",
        opacity: fainted ? 0 : 1,
        filter: damaged ? "brightness(0.55)" : "none",
        imageRendering: "pixelated",
      }}
    />
  );
}

// ── Scene ─────────────────────────────────────────────────────
function BattleScene({ background, player, enemy, attacking, damaged, message }) {
  return (
    <div
      className="relative w-full overflow-hidden select-none"
      style={{
        aspectRatio: "16 / 10",
        border: "3px solid var(--color-poke-panel-edge)",
        borderRadius: "var(--radius-retro-lg)",
        boxShadow: "4px 4px 0 var(--color-poke-panel-edge)",
        background: "var(--color-poke-arena)",
      }}
    >
      {/* Battlefield */}
      <img
        src={background}
        alt=""
        className="absolute inset-0 w-full h-full object-cover pixelated"
        style={{ imageRendering: "pixelated" }}
      />

      {/* Enemy side — closer to center, sprite scales with the scene */}
      <div className="absolute top-[6%] left-[3%] z-10">
        <HpBox pokemon={enemy} side="enemy" />
      </div>
      <div className="absolute top-[40%] right-[26%] w-[26%] flex justify-center items-end" style={{ height: "22%" }}>
        <Platform className="bottom-[-3%] left-1/2 -translate-x-1/2 w-[115%] h-[24%]" />
        <BattleSprite
          pokemon={enemy}
          back={false}
          attacking={attacking === "enemy"}
          damaged={damaged === "enemy"}
        />
      </div>

      {/* Player side — closer to center, larger back sprite */}
      <div className="absolute bottom-[23%] left-[15%] w-[28%] flex justify-center items-end" style={{ height: "22%" }}>
        <Platform className="bottom-[-3%] left-1/2 -translate-x-1/2 w-[115%] h-[22%]" />
        <BattleSprite
          pokemon={player}
          back={true}
          attacking={attacking === "player"}
          damaged={damaged === "player"}
        />
      </div>
      <div className="absolute bottom-[26%] right-[3%] z-10">
        <HpBox pokemon={player} side="player" />
      </div>

      {/* Dialog bar */}
      <div
        className="absolute bottom-0 left-0 right-0 z-20"
        style={{
          height: "22%",
          background: "var(--color-hgss-dialog-outer)",
          padding: "8px 10px",
        }}
      >
        <div
          className="w-full h-full"
          style={{
            background: "var(--color-hgss-dialog-inner)",
            border: "4px solid var(--color-hgss-dialog-border)",
            borderRadius: "10px",
            padding: "10px 16px",
          }}
        >
          <p
            style={{
              fontFamily: "var(--font-pixel)",
              fontSize: "0.6rem",
              lineHeight: 1.9,
              color: "#f8f8f8",
              textShadow: "2px 2px 0 rgba(0,0,0,0.35)",
            }}
          >
            {message}
          </p>
        </div>
      </div>
    </div>
  );
}

export default BattleScene;
