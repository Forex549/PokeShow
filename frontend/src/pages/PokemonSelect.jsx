import { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import pokemonList from "../data/pokemonList";
import { getPokemonSprite } from "../utils/sprites";
import RetroPanel from "../components/RetroPanel";
import RetroButton from "../components/RetroButton";

const TEAM_SIZE = 4;
const EMPTY = "";

/** Fisher-Yates sample — picks k unique items from an array. */
function sampleWithoutReplacement(arr, k) {
  const copy = [...arr];
  for (let i = copy.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy.slice(0, k);
}

function SlotCard({ slot, index, team, onChange }) {
  const others = team.filter((_, i) => i !== index);

  return (
    <div
      className="flex flex-col gap-2 p-3"
      style={{
        border: `3px solid ${slot ? "var(--color-poke-blue)" : "var(--color-poke-panel-edge)"}`,
        borderRadius: "var(--radius-retro)",
        background: "var(--color-poke-panel-dark)",
        boxShadow: "2px 2px 0 var(--color-poke-panel-edge)",
        borderStyle: slot ? "solid" : "dashed",
      }}
    >
      <div className="flex justify-between items-center">
        <span
          className="text-[0.45rem] font-bold uppercase tracking-widest"
          style={{ fontFamily: "var(--font-pixel)", color: "var(--color-poke-text-muted)" }}
        >
          Slot {index + 1}
        </span>
        {slot && (
          <span
            className="text-[0.4rem] px-2 py-1 font-bold capitalize"
            style={{
              fontFamily: "var(--font-pixel)",
              background: "var(--color-poke-blue)",
              color: "#fff",
              borderRadius: "var(--radius-retro-sm)",
            }}
          >
            {slot}
          </span>
        )}
      </div>

      <select
        className="w-full p-2 text-sm outline-none"
        style={{
          border: "2px solid var(--color-poke-panel-edge)",
          borderRadius: "var(--radius-retro-sm)",
          background: "var(--color-poke-panel)",
          color: "var(--color-poke-text)",
          fontFamily: "var(--font-body)",
        }}
        value={slot}
        onChange={(e) => onChange(index, e.target.value)}
      >
        <option value="">— Elegir —</option>
        {pokemonList.map((p) => (
          <option key={p} value={p} disabled={others.includes(p)}>
            {p}
          </option>
        ))}
      </select>

      <div
        className="flex justify-center items-center h-24"
        style={{
          background: "var(--color-poke-arena)",
          borderRadius: "var(--radius-retro-sm)",
        }}
      >
        {slot ? (
          <img
            src={getPokemonSprite(slot, false)}
            alt={slot}
            className="h-20 hover:scale-110 transition-all duration-300"
          />
        ) : (
          <span className="text-3xl" style={{ color: "var(--color-poke-panel-edge)" }}>?</span>
        )}
      </div>
    </div>
  );
}

function PokemonSelect() {
  const navigate = useNavigate();
  const location = useLocation();
  const battleConfig = location.state?.battleConfig;

  const [playerTeam, setPlayerTeam] = useState(Array(TEAM_SIZE).fill(EMPTY));

  const teamComplete = playerTeam.every((p) => p !== EMPTY);

  const handleChange = (i, v) => {
    setPlayerTeam((prev) => {
      const next = [...prev];
      next[i] = v;
      return next;
    });
  };

  const randomTeam = () => {
    setPlayerTeam(sampleWithoutReplacement(pokemonList, TEAM_SIZE));
  };

  const startBattle = () => {
    if (!teamComplete) return;
    navigate("/battle", { state: { battleConfig, playerTeam } });
  };

  return (
    <div
      className="min-h-screen px-6 py-10"
      style={{ background: "var(--color-poke-arena)" }}
    >
      {/* Header */}
      <div className="text-center mb-8">
        <h1
          className="retro-title text-xl mb-2"
          style={{ color: "var(--color-poke-red)" }}
        >
          PokeShow
        </h1>
        <p
          className="text-[0.45rem] uppercase tracking-widest"
          style={{ fontFamily: "var(--font-pixel)", color: "var(--color-poke-text-muted)" }}
        >
          Seleccionar equipo
        </p>
      </div>

      <div className="max-w-2xl mx-auto flex flex-col gap-6">

        {/* Team panel */}
        <RetroPanel className="p-6">
          <div className="flex items-center justify-between mb-4">
            <p
              className="text-[0.5rem] font-bold uppercase tracking-widest"
              style={{ fontFamily: "var(--font-pixel)", color: "var(--color-poke-text-muted)" }}
            >
              Tu equipo
            </p>
            <div className="flex items-center gap-3">
              <span
                className="text-[0.45rem]"
                style={{ fontFamily: "var(--font-pixel)", color: "var(--color-poke-text-muted)" }}
              >
                {playerTeam.filter((p) => p !== EMPTY).length}/{TEAM_SIZE}
              </span>
              {/* Random team button */}
              <RetroButton
                variant="danger"
                size="sm"
                onClick={randomTeam}
              >
                ★ Equipo aleatorio
              </RetroButton>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            {playerTeam.map((slot, i) => (
              <SlotCard
                key={i}
                slot={slot}
                index={i}
                team={playerTeam}
                onChange={handleChange}
              />
            ))}
          </div>
        </RetroPanel>

        {/* Actions */}
        <div className="flex flex-col items-center gap-3">
          {!teamComplete && (
            <p
              className="text-[0.45rem]"
              style={{ fontFamily: "var(--font-pixel)", color: "var(--color-poke-text-muted)" }}
            >
              Completa los {TEAM_SIZE} slots para continuar
            </p>
          )}

          <RetroButton
            size="lg"
            disabled={!teamComplete}
            onClick={startBattle}
            className="w-full max-w-xs justify-center"
          >
            ► ¡Iniciar Batalla!
          </RetroButton>

          <RetroButton
            variant="neutral"
            size="sm"
            onClick={() => navigate("/mode")}
            className="w-full max-w-xs justify-center"
          >
            ◄ Volver
          </RetroButton>
        </div>

      </div>
    </div>
  );
}

export default PokemonSelect;
