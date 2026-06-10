import { useState } from "react";
import { useNavigate } from "react-router-dom";
import RetroPanel from "../components/RetroPanel";
import RetroButton from "../components/RetroButton";

// Canonical 5 AI levels (matches backend BattleMode enum)
const AI_LEVELS = [
  { value: "random",    label: "Nv.1 Aleatorio",   desc: "Movimientos al azar" },
  { value: "heuristic", label: "Nv.2 Heurística",  desc: "Daño + ventaja táctica" },
  { value: "minimax2",  label: "Nv.3 Minimax 2",   desc: "Árbol de decisión prof. 2" },
  { value: "minimax3",  label: "Nv.4 Minimax 3",   desc: "Minimax con pesos GA" },
  { value: "minimax4",  label: "Nv.5 Minimax 4",   desc: "Puede cambiar Pokémon" },
];

function LevelPicker({ label, selected, onChange }) {
  return (
    <div className="flex flex-col gap-2">
      <p
        className="text-[0.5rem] font-bold uppercase tracking-widest mb-1"
        style={{ fontFamily: "var(--font-pixel)", color: "var(--color-poke-text-muted)" }}
      >
        {label}
      </p>
      <div className="flex flex-col gap-2">
        {AI_LEVELS.map((lvl) => {
          const active = selected === lvl.value;
          return (
            <button
              key={lvl.value}
              onClick={() => onChange(lvl.value)}
              className="text-left p-3 transition-all duration-100"
              style={{
                border: `3px solid ${active ? "var(--color-poke-red)" : "var(--color-poke-panel-edge)"}`,
                borderRadius: "var(--radius-retro)",
                background: active ? "var(--color-poke-red)" : "var(--color-poke-panel-dark)",
                boxShadow: active
                  ? "3px 3px 0 var(--color-poke-red-dark)"
                  : "2px 2px 0 var(--color-poke-panel-edge)",
                color: active ? "#fff" : "var(--color-poke-text)",
              }}
            >
              <p
                className="text-[0.5rem] font-bold"
                style={{ fontFamily: "var(--font-pixel)" }}
              >
                {lvl.label}
              </p>
              <p className="text-xs mt-1" style={{ color: active ? "rgba(255,255,255,0.8)" : "var(--color-poke-text-muted)" }}>
                {lvl.desc}
              </p>
            </button>
          );
        })}
      </div>
    </div>
  );
}

function ModeSelect() {
  const navigate = useNavigate();
  // "pvp" = Jugador vs IA | "ava" = IA vs IA | null = not chosen yet
  const [battleType, setBattleType] = useState(null);
  const [enemyMode, setEnemyMode]   = useState("random");
  const [playerMode, setPlayerMode] = useState("random");

  const confirm = () => {
    if (!battleType) return;
    const config =
      battleType === "pvp"
        ? { player_mode: "human", enemy_mode: enemyMode }
        : { player_mode: playerMode, enemy_mode: enemyMode };
    navigate("/select", { state: { battleConfig: config } });
  };

  const canConfirm = battleType !== null;

  return (
    <div
      className="min-h-screen flex items-center justify-center px-6 py-12"
      style={{ background: "var(--color-poke-arena)" }}
    >
      <RetroPanel className="p-8 w-full max-w-lg flex flex-col gap-6">

        {/* Title */}
        <div className="text-center">
          <h1
            className="retro-title text-lg mb-1"
            style={{ color: "var(--color-poke-red)" }}
          >
            PokeShow
          </h1>
          <p
            className="text-[0.45rem] uppercase tracking-widest"
            style={{ fontFamily: "var(--font-pixel)", color: "var(--color-poke-text-muted)" }}
          >
            Seleccionar modo de batalla
          </p>
        </div>

        {/* Pixel divider */}
        <div className="w-full h-[3px]" style={{ background: "var(--color-poke-panel-edge)" }} />

        {/* Type selector */}
        <div className="grid grid-cols-2 gap-4">

          {/* Jugador vs IA */}
          <button
            onClick={() => setBattleType("pvp")}
            className="flex flex-col items-center gap-2 p-5 transition-all duration-100"
            style={{
              border: `3px solid ${battleType === "pvp" ? "var(--color-poke-blue)" : "var(--color-poke-panel-edge)"}`,
              borderRadius: "var(--radius-retro)",
              background: battleType === "pvp" ? "var(--color-poke-blue)" : "var(--color-poke-panel-dark)",
              boxShadow: battleType === "pvp"
                ? "3px 3px 0 var(--color-poke-blue-dark)"
                : "2px 2px 0 var(--color-poke-panel-edge)",
              color: battleType === "pvp" ? "#fff" : "var(--color-poke-text)",
            }}
          >
            <span className="text-2xl">🕹️</span>
            <p
              className="text-[0.5rem] font-bold text-center leading-tight"
              style={{ fontFamily: "var(--font-pixel)" }}
            >
              Jugador vs IA
            </p>
            <p className="text-xs text-center" style={{ color: battleType === "pvp" ? "rgba(255,255,255,0.8)" : "var(--color-poke-text-muted)" }}>
              Tú eliges los movimientos
            </p>
          </button>

          {/* IA vs IA */}
          <button
            onClick={() => setBattleType("ava")}
            className="flex flex-col items-center gap-2 p-5 transition-all duration-100"
            style={{
              border: `3px solid ${battleType === "ava" ? "var(--color-poke-red)" : "var(--color-poke-panel-edge)"}`,
              borderRadius: "var(--radius-retro)",
              background: battleType === "ava" ? "var(--color-poke-red)" : "var(--color-poke-panel-dark)",
              boxShadow: battleType === "ava"
                ? "3px 3px 0 var(--color-poke-red-dark)"
                : "2px 2px 0 var(--color-poke-panel-edge)",
              color: battleType === "ava" ? "#fff" : "var(--color-poke-text)",
            }}
          >
            <span className="text-2xl">🤖</span>
            <p
              className="text-[0.5rem] font-bold text-center leading-tight"
              style={{ fontFamily: "var(--font-pixel)" }}
            >
              IA vs IA
            </p>
            <p className="text-xs text-center" style={{ color: battleType === "ava" ? "rgba(255,255,255,0.8)" : "var(--color-poke-text-muted)" }}>
              Observa la batalla automática
            </p>
          </button>
        </div>

        {/* Level pickers — shown once type is selected */}
        {battleType === "pvp" && (
          <div>
            <div className="w-full h-[2px] mb-4" style={{ background: "var(--color-poke-panel-edge)" }} />
            <LevelPicker
              label="Nivel de la IA rival"
              selected={enemyMode}
              onChange={setEnemyMode}
            />
          </div>
        )}

        {battleType === "ava" && (
          <div>
            <div className="w-full h-[2px] mb-4" style={{ background: "var(--color-poke-panel-edge)" }} />
            <div className="grid grid-cols-2 gap-6">
              <LevelPicker
                label="IA Jugador (izq)"
                selected={playerMode}
                onChange={setPlayerMode}
              />
              <LevelPicker
                label="IA Rival (der)"
                selected={enemyMode}
                onChange={setEnemyMode}
              />
            </div>
          </div>
        )}

        {/* Confirm */}
        <RetroButton
          size="lg"
          disabled={!canConfirm}
          onClick={confirm}
          className="w-full justify-center"
        >
          ► Continuar
        </RetroButton>

        {/* Back */}
        <RetroButton
          variant="neutral"
          size="sm"
          onClick={() => navigate("/")}
          className="w-full justify-center"
        >
          ◄ Volver
        </RetroButton>

      </RetroPanel>
    </div>
  );
}

export default ModeSelect;
