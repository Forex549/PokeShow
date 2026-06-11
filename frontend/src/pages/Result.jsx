import { useLocation, useNavigate } from "react-router-dom";
import RetroPanel from "../components/RetroPanel";
import RetroButton from "../components/RetroButton";

function Result() {
  const navigate = useNavigate();
  const location = useLocation();

  const winner      = location.state?.winner;
  const turns       = location.state?.turns;
  const battleConfig = location.state?.battleConfig;

  // Friendly label for the battle mode
  const modeLabel = battleConfig
    ? battleConfig.player_mode === "human"
      ? `Jugador vs IA (${battleConfig.enemy_mode})`
      : `IA (${battleConfig.player_mode}) vs IA (${battleConfig.enemy_mode})`
    : "—";

  return (
    <div
      className="min-h-screen flex justify-center items-center p-8"
      style={{ background: "var(--color-poke-arena)" }}
    >
      <RetroPanel className="w-full max-w-2xl overflow-hidden flex flex-col">

        {/* Header */}
        <div
          className="p-8 text-center"
          style={{ background: "var(--color-poke-red)", borderBottom: "3px solid var(--color-poke-panel-edge)" }}
        >
          <h1
            className="retro-title text-xl mb-2"
            style={{ color: "#fff" }}
          >
            PokeShow
          </h1>
          <p
            className="text-[0.45rem] uppercase tracking-widest"
            style={{ fontFamily: "var(--font-pixel)", color: "rgba(255,255,255,0.75)" }}
          >
            Resultado de batalla
          </p>
        </div>

        {/* Content */}
        <div className="p-8 flex flex-col gap-6">

          {/* Winner */}
          <div className="text-center">
            <p
              className="text-[0.45rem] uppercase mb-2"
              style={{ fontFamily: "var(--font-pixel)", color: "var(--color-poke-text-muted)" }}
            >
              Ganador
            </p>
            <h2
              className="retro-title text-2xl capitalize"
              style={{ color: "var(--color-poke-red)" }}
            >
              {winner}
            </h2>
          </div>

          {/* Pixel divider */}
          <div className="w-full h-[3px]" style={{ background: "var(--color-poke-panel-edge)" }} />

          {/* Mode badge */}
          <div
            className="flex justify-between items-center px-4 py-3"
            style={{
              border: "2px solid var(--color-poke-panel-edge)",
              borderRadius: "var(--radius-retro)",
              background: "var(--color-poke-panel-dark)",
            }}
          >
            <span
              className="text-[0.4rem]"
              style={{ fontFamily: "var(--font-pixel)", color: "var(--color-poke-text-muted)" }}
            >
              Modo de batalla
            </span>
            <span
              className="text-[0.4rem] font-bold px-3 py-1"
              style={{
                fontFamily: "var(--font-pixel)",
                background: "var(--color-poke-blue)",
                color: "#fff",
                borderRadius: "var(--radius-retro-sm)",
                border: "2px solid var(--color-poke-panel-edge)",
              }}
            >
              {modeLabel}
            </span>
          </div>

          {/* Battle log */}
          <div>
            <p
              className="text-[0.45rem] font-bold uppercase mb-3"
              style={{ fontFamily: "var(--font-pixel)", color: "var(--color-poke-text-muted)" }}
            >
              Historial de batalla
            </p>
            <div
              className="p-4 h-56 overflow-y-auto"
              style={{
                background: "var(--color-poke-log-bg)",
                border: "3px solid var(--color-poke-panel-edge)",
                borderRadius: "var(--radius-retro)",
                boxShadow: "inset 2px 2px 0 rgba(0,0,0,0.4)",
                fontFamily: "var(--font-pixel)",
                fontSize: "0.4rem",
                lineHeight: "1.8",
                color: "var(--color-poke-log-text)",
              }}
            >
              {turns?.map((turn, index) => (
                <p key={index} className="mb-1">&gt; {turn}</p>
              ))}
            </div>
          </div>

          {/* Back button */}
          <RetroButton
            size="lg"
            onClick={() => navigate("/")}
            className="w-full justify-center"
          >
            ◄ Volver al Inicio
          </RetroButton>
        </div>
      </RetroPanel>
    </div>
  );
}

export default Result;
