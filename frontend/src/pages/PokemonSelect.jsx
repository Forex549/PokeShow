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
      className="flex flex-col gap-3 p-5"
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
          className="text-[0.6rem] font-bold uppercase tracking-widest"
          style={{ fontFamily: "var(--font-pixel)", color: "var(--color-poke-text-muted)" }}
        >
          Slot {index + 1}
        </span>
        {slot && (
          <span
            className="text-[0.55rem] px-3 py-1 font-bold capitalize"
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
        className="w-full p-3 text-base outline-none"
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
        className="flex justify-center items-center h-40"
        style={{
          background: "var(--color-poke-arena)",
          borderRadius: "var(--radius-retro-sm)",
        }}
      >
        {slot ? (
          <img
            src={getPokemonSprite(slot, false)}
            alt={slot}
            className="h-32 hover:scale-110 transition-all duration-300"
          />
        ) : (
          <span className="text-6xl" style={{ color: "var(--color-poke-panel-edge)" }}>?</span>
        )}
      </div>
    </div>
  );
}

function PokemonSelect() {
  const navigate = useNavigate();
  const location = useLocation();
  const battleConfig = location.state?.battleConfig;

  const isPlayerHuman = battleConfig?.player_mode === "human";
  const player1Label = isPlayerHuman ? "Tu equipo (Jugador)" : "Equipo IA 1";
  const player2Label = isPlayerHuman ? "Equipo de la IA" : "Equipo IA 2";

  const [playerTeam, setPlayerTeam] = useState(Array(TEAM_SIZE).fill(EMPTY));
  const [enemyTeam, setEnemyTeam] = useState(Array(TEAM_SIZE).fill(EMPTY));

  const playerComplete = playerTeam.every((p) => p !== EMPTY);
  const enemyComplete = enemyTeam.every((p) => p !== EMPTY);
  const teamsComplete = playerComplete && enemyComplete;

  const handlePlayerChange = (i, v) => {
    setPlayerTeam((prev) => {
      const next = [...prev];
      next[i] = v;
      return next;
    });
  };

  const handleEnemyChange = (i, v) => {
    setEnemyTeam((prev) => {
      const next = [...prev];
      next[i] = v;
      return next;
    });
  };

  const randomPlayerTeam = () => {
    setPlayerTeam(sampleWithoutReplacement(pokemonList, TEAM_SIZE));
  };

  const randomEnemyTeam = () => {
    setEnemyTeam(sampleWithoutReplacement(pokemonList, TEAM_SIZE));
  };

  const randomBothTeams = () => {
    const samePokemon = sampleWithoutReplacement(pokemonList, TEAM_SIZE);
    setPlayerTeam(samePokemon);
    setEnemyTeam([...samePokemon]);
  };

  const startBattle = () => {
    if (!teamsComplete) return;
    navigate("/battle", { state: { battleConfig, playerTeam, enemyTeam } });
  };

  return (
    <div className="min-h-screen px-4 py-8">
      {/* Header */}
      <div className="text-center mb-10">
        <h1
          className="retro-title text-3xl mb-3"
          style={{ color: "var(--color-poke-red)" }}
        >
          PokeShow
        </h1>
        <p
          className="text-[0.55rem] uppercase tracking-widest"
          style={{ fontFamily: "var(--font-pixel)", color: "#fff" }}
        >
          Seleccionar equipos
        </p>
      </div>

      <div className="max-w-7xl mx-auto flex flex-col gap-8">

        {/* Teams container - two columns */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          
          {/* Player/IA1 Team Panel */}
          <RetroPanel className="p-8">
            <div className="flex items-center justify-between mb-6">
              <p
                className="text-[0.65rem] font-bold uppercase tracking-widest"
                style={{ fontFamily: "var(--font-pixel)", color: "var(--color-poke-text-muted)" }}
              >
                {player1Label}
              </p>
              <div className="flex items-center gap-3">
                <span
                  className="text-[0.55rem]"
                  style={{ fontFamily: "var(--font-pixel)", color: "var(--color-poke-text-muted)" }}
                >
                  {playerTeam.filter((p) => p !== EMPTY).length}/{TEAM_SIZE}
                </span>
                <RetroButton
                  variant="danger"
                  size="sm"
                  onClick={randomPlayerTeam}
                >
                  ★ Aleatorio
                </RetroButton>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              {playerTeam.map((slot, i) => (
                <SlotCard
                  key={i}
                  slot={slot}
                  index={i}
                  team={playerTeam}
                  onChange={handlePlayerChange}
                />
              ))}
            </div>
          </RetroPanel>

          {/* Enemy/IA2 Team Panel */}
          <RetroPanel className="p-8">
            <div className="flex items-center justify-between mb-6">
              <p
                className="text-[0.65rem] font-bold uppercase tracking-widest"
                style={{ fontFamily: "var(--font-pixel)", color: "var(--color-poke-text-muted)" }}
              >
                {player2Label}
              </p>
              <div className="flex items-center gap-3">
                <span
                  className="text-[0.55rem]"
                  style={{ fontFamily: "var(--font-pixel)", color: "var(--color-poke-text-muted)" }}
                >
                  {enemyTeam.filter((p) => p !== EMPTY).length}/{TEAM_SIZE}
                </span>
                <RetroButton
                  variant="danger"
                  size="sm"
                  onClick={randomEnemyTeam}
                >
                  ★ Aleatorio
                </RetroButton>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              {enemyTeam.map((slot, i) => (
                <SlotCard
                  key={i}
                  slot={slot}
                  index={i}
                  team={enemyTeam}
                  onChange={handleEnemyChange}
                />
              ))}
            </div>
          </RetroPanel>

        </div>

        {/* Special button for same random teams - show for both modes */}
        <div className="flex justify-center">
          <RetroButton
            variant="neutral"
            size="lg"
            onClick={randomBothTeams}
          >
            ★ Mismos Pokémon aleatorios en ambos equipos
          </RetroButton>
        </div>

        {/* Actions */}
        <div className="flex flex-col items-center gap-4">
          {!teamsComplete && (
            <p
              className="text-[0.55rem]"
              style={{ fontFamily: "var(--font-pixel)", color: "var(--color-poke-text-muted)" }}
            >
              Completa los {TEAM_SIZE} slots en ambos equipos para continuar
            </p>
          )}

          <RetroButton
            size="lg"
            disabled={!teamsComplete}
            onClick={startBattle}
            className="w-full max-w-sm justify-center"
          >
            ► ¡Iniciar Batalla!
          </RetroButton>

          <RetroButton
            variant="neutral"
            size="sm"
            onClick={() => navigate("/mode")}
            className="w-full max-w-sm justify-center"
          >
            ◄ Volver
          </RetroButton>
        </div>

      </div>
    </div>
  );
}

export default PokemonSelect;
