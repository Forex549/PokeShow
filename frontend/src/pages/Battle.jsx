import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { startBattle, playTurn, switchPokemon, getOrCreateUser } from "../services/api";
import BattleScene from "../components/BattleScene";
import MoveButtons from "../components/MoveButtons";
import PlayerTeamBar from "../components/PlayerTeamBar";
import EnemyTeamBar from "../components/EnemyTeamBar";
import RetroPanel from "../components/RetroPanel";
import RetroButton from "../components/RetroButton";

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

// Battlefield backgrounds — one is picked at random per battle
const BACKGROUNDS = [
  "/backgrounds/fisi.png",
  "/backgrounds/comedor.png",
  "/backgrounds/fray.png",
];

// ──────────────────────────────────────────────────────────────
// Mandatory faint-switch panel
// ──────────────────────────────────────────────────────────────
function SwitchPanel({ team, activeIndex, onSwitch }) {
  return (
    <RetroPanel className="p-6">
      <h3
        className="text-[0.55rem] font-bold text-center mb-4"
        style={{
          fontFamily: "var(--font-pixel)",
          color: "var(--color-poke-red)",
        }}
      >
        ¡Tu Pokémon se debilitó!
        <br />
        <span style={{ color: "var(--color-poke-text-muted)" }}>Elige el siguiente</span>
      </h3>

      <div className="grid grid-cols-2 gap-3">
        {team.map((p, i) => {
          const canSwitch = p.hp > 0 && !p.is_fainted && i !== activeIndex;
          return (
            <button
              key={i}
              disabled={!canSwitch}
              onClick={() => onSwitch(i)}
              className="p-3 text-left transition-all duration-100"
              style={{
                border: `3px solid ${canSwitch ? "var(--color-poke-blue)" : "var(--color-poke-panel-edge)"}`,
                borderRadius: "var(--radius-retro)",
                background: canSwitch ? "var(--color-poke-blue)" : "var(--color-poke-panel-dark)",
                boxShadow: canSwitch
                  ? "3px 3px 0 var(--color-poke-blue-dark)"
                  : "2px 2px 0 var(--color-poke-panel-edge)",
                color: canSwitch ? "#fff" : "var(--color-poke-text-muted)",
                opacity: canSwitch ? 1 : 0.45,
                cursor: canSwitch ? "pointer" : "not-allowed",
              }}
            >
              <p
                className="text-[0.5rem] font-bold capitalize"
                style={{ fontFamily: "var(--font-pixel)" }}
              >
                {p.name}
              </p>
              <p className="text-xs mt-1" style={{ color: canSwitch ? "rgba(255,255,255,0.8)" : "var(--color-poke-text-muted)" }}>
                {p.hp <= 0 || p.is_fainted ? "Debilitado" : `${p.hp}/${p.max_hp} HP`}
              </p>
            </button>
          );
        })}
      </div>
    </RetroPanel>
  );
}

// ──────────────────────────────────────────────────────────────
// Main Battle component
// ──────────────────────────────────────────────────────────────
function Battle() {
  const navigate  = useNavigate();
  const location  = useLocation();

  const battleConfig = location.state?.battleConfig ?? { player_mode: "human", enemy_mode: "random" };
  const playerTeam   = location.state?.playerTeam;

  const isAIvsAI = battleConfig.player_mode !== "human";

  const [battle, setBattle]               = useState(null);
  const [isAnimating, setIsAnimating]     = useState(false);
  const [attacking, setAttacking]         = useState(null);   // "player" | "enemy" | null
  const [damaged, setDamaged]             = useState(null);   // "player" | "enemy" | null
  const [battleMessage, setBattleMessage] = useState("Elige un movimiento");
  const [background] = useState(
    () => BACKGROUNDS[Math.floor(Math.random() * BACKGROUNDS.length)]
  );
  const [showVoluntarySwitch, setShowVoluntarySwitch] = useState(false);
  const [error, setError]                 = useState(null);

  // ── Init battle ──────────────────────────────────────────
  useEffect(() => {
    initBattle();
  }, []);

  const initBattle = async () => {
    try {
      setError(null);
      const user = await getOrCreateUser("Jugador");
      const data = await startBattle({
        userId:     user.id,
        playerTeam,
        playerMode: battleConfig.player_mode,
        enemyMode:  battleConfig.enemy_mode,
      });
      setBattle(data);
      if (data.player_mode !== "human") {
        setBattleMessage("Observando batalla IA vs IA...");
      }
    } catch (e) {
      setError(`Error al iniciar batalla: ${e.message}`);
    }
  };

  // ── IA-vs-IA auto-advance ────────────────────────────────
  // Re-arms after every resolved turn: `battle` changes and `isAnimating`
  // drops to false, so the next turn is scheduled until the battle ends.
  useEffect(() => {
    if (!battle || !isAIvsAI || battle.finished || battle.needs_switch || isAnimating) return;
    const timer = setTimeout(() => handlePlayTurn(null), 1200);
    return () => clearTimeout(timer);
  }, [battle, isAIvsAI, isAnimating]);

  // ── Human turn ───────────────────────────────────────────
  const handlePlayTurn = async (moveName) => {
    if (isAnimating || !battle || battle.needs_switch) return;

    setIsAnimating(true);
    setShowVoluntarySwitch(false);
    setError(null);

    const prevLogs = battle.logs || [];

    try {
      const data = await playTurn({
        battleId:  battle.battle_id,
        playerMove: moveName,   // null for IA-vs-IA
      });
      await animateTurn(data, prevLogs);

      if (data.winner) {
        setTimeout(() => navigate("/result", {
          state: {
            winner: data.winner,
            turns:  data.logs,
            battleConfig,
          },
        }), 2000);
      }
    } catch (e) {
      setError(e.response?.data?.detail ?? e.message);
    } finally {
      setIsAnimating(false);
    }
  };

  // ── Switch ───────────────────────────────────────────────
  const handleSwitch = async (index, voluntary = false) => {
    if (isAnimating || !battle) return;

    setIsAnimating(true);
    setShowVoluntarySwitch(false);
    setError(null);

    const prevLogs = battle.logs || [];

    try {
      const data = await switchPokemon({
        battleId:     battle.battle_id,
        pokemonIndex: index,
        voluntary,
      });
      await animateTurn(data, prevLogs);

      if (data.winner) {
        setTimeout(() => navigate("/result", {
          state: {
            winner: data.winner,
            turns:  data.logs,
            battleConfig,
          },
        }), 2000);
      }
    } catch (e) {
      setError(e.response?.data?.detail ?? e.message);
    } finally {
      setIsAnimating(false);
    }
  };

  // ── Animation ────────────────────────────────────────────
  const animateTurn = async (updatedBattle, previousLogs) => {
    const newLogs = updatedBattle.logs.slice(previousLogs.length);
    // Attack logs are attributed by attacker name — status messages shift
    // log positions, so index-based detection is no longer reliable
    const playerNames = new Set(updatedBattle.player_team.map((p) => p.name));

    for (const log of newLogs) {
      setBattleMessage(log);
      await sleep(700);

      if (log.includes(" usó ")) {
        const attacker = log.split(" usó ")[0];
        const side = playerNames.has(attacker) ? "player" : "enemy";
        setAttacking(side); await sleep(400);
        setAttacking(null);
        if (log.includes("de daño")) {
          setDamaged(side === "player" ? "enemy" : "player");
          await sleep(300);
          setDamaged(null);
        }
      }
      if (log.includes("debilitó")) {
        await sleep(1000);
      }
    }

    setBattle(updatedBattle);

    if (!updatedBattle.needs_switch) {
      setBattleMessage(
        updatedBattle.player_mode !== "human"
          ? "Observando batalla IA vs IA..."
          : "Elige un movimiento"
      );
    } else {
      setBattleMessage("¡Elige tu siguiente Pokémon!");
    }
  };

  // ── Loading / error ───────────────────────────────────────
  if (error && !battle) {
    return (
      <div
        className="min-h-screen flex flex-col justify-center items-center gap-6 px-6"
        style={{ background: "var(--color-poke-arena)" }}
      >
        <RetroPanel className="p-8 max-w-md w-full text-center">
          <p
            className="text-[0.55rem] mb-4"
            style={{ fontFamily: "var(--font-pixel)", color: "var(--color-poke-red)" }}
          >
            Error al iniciar
          </p>
          <p className="text-sm mb-6" style={{ color: "var(--color-poke-text-muted)" }}>{error}</p>
          <RetroButton onClick={() => navigate("/mode")} className="w-full justify-center">
            ◄ Volver al menú
          </RetroButton>
        </RetroPanel>
      </div>
    );
  }

  if (!battle) {
    return (
      <div
        className="min-h-screen flex justify-center items-center"
        style={{ background: "var(--color-poke-arena)" }}
      >
        <p
          className="text-[0.6rem]"
          style={{ fontFamily: "var(--font-pixel)", color: "var(--color-poke-text-muted)" }}
        >
          Cargando batalla...
        </p>
      </div>
    );
  }

  // ── Render ────────────────────────────────────────────────
  return (
    <div
      className="min-h-screen p-3 flex flex-col items-center"
      style={{ background: "var(--color-poke-arena)" }}
    >
      {/* Scene-driven width: 16/10 aspect → the battle fills ~80% of the
          viewport's constraining dimension (126vh wide ⇒ ~79vh tall) */}
      <div
        className="flex flex-col gap-2"
        style={{ width: "min(96vw, 126vh)" }}
      >
      {/* Team bars */}
      <RetroPanel className="px-4 py-2">
        <div className="flex justify-between items-center gap-4">
          <div className="flex flex-col gap-1">
            <p
              className="text-[0.4rem] font-bold uppercase tracking-widest mb-1"
              style={{ fontFamily: "var(--font-pixel)", color: "var(--color-poke-text-muted)" }}
            >
              {isAIvsAI ? `IA (${battle.player_mode})` : "Tu equipo"}
            </p>
            <PlayerTeamBar
              team={battle.player_team}
              activeIndex={battle.player_index}
            />
          </div>

          <div
            className="text-lg font-black"
            style={{
              fontFamily: "var(--font-pixel)",
              color: "var(--color-poke-text-muted)",
              fontSize: "0.7rem",
            }}
          >
            VS
          </div>

          <div className="flex flex-col items-end gap-1">
            <p
              className="text-[0.4rem] font-bold uppercase tracking-widest mb-1"
              style={{ fontFamily: "var(--font-pixel)", color: "var(--color-poke-text-muted)" }}
            >
              Rival IA ({battle.enemy_mode})
            </p>
            <EnemyTeamBar
              team={battle.enemy_team}
              activeIndex={battle.enemy_index}
            />
          </div>
        </div>
      </RetroPanel>

      {/* Error inline */}
      {error && (
        <div
          className="px-4 py-2 text-sm text-center"
          style={{
            background: "var(--color-poke-red-light)",
            border: "2px solid var(--color-poke-red)",
            borderRadius: "var(--radius-retro)",
            color: "#fff",
          }}
        >
          {error}
        </div>
      )}

      {/* Arena — HGSS-style battle scene */}
      <BattleScene
        background={background}
        player={battle.player}
        enemy={battle.enemy}
        attacking={attacking}
        damaged={damaged}
        message={battleMessage}
      />

      {/* Controls */}
      {battle.needs_switch ? (
        <SwitchPanel
          team={battle.player_team}
          activeIndex={battle.player_index}
          onSwitch={(i) => handleSwitch(i, false)}
        />
      ) : isAIvsAI ? null : (
        <div className="flex flex-col gap-3">
          {/* Move buttons */}
          <MoveButtons
            moves={battle.player.moves}
            onMove={handlePlayTurn}
            disabled={isAnimating || battle.finished}
          />

          {/* Voluntary switch */}
          {!battle.finished && (
            <div className="flex justify-center">
              <RetroButton
                variant="danger"
                size="sm"
                disabled={isAnimating}
                onClick={() => setShowVoluntarySwitch((v) => !v)}
              >
                {showVoluntarySwitch ? "✕ Cancelar" : "⇄ Cambiar Pokémon"}
              </RetroButton>
            </div>
          )}

          {showVoluntarySwitch && (
            <RetroPanel className="p-5">
              <h3
                className="text-[0.5rem] font-bold text-center mb-1"
                style={{ fontFamily: "var(--font-pixel)", color: "var(--color-poke-yellow-dark)" }}
              >
                Cambiar Pokémon
              </h3>
              <p
                className="text-xs text-center mb-4"
                style={{ color: "var(--color-poke-text-muted)" }}
              >
                La IA atacará este turno igualmente
              </p>

              <div className="grid grid-cols-2 gap-3">
                {battle.player_team.map((p, i) => {
                  const canSwitch = p.hp > 0 && !p.is_fainted && i !== battle.player_index;
                  return (
                    <button
                      key={i}
                      disabled={!canSwitch}
                      onClick={() => handleSwitch(i, true)}
                      className="p-3 text-left transition-all duration-100"
                      style={{
                        border: `3px solid ${canSwitch ? "var(--color-poke-yellow-dark)" : "var(--color-poke-panel-edge)"}`,
                        borderRadius: "var(--radius-retro)",
                        background: canSwitch ? "var(--color-poke-yellow)" : "var(--color-poke-panel-dark)",
                        boxShadow: canSwitch
                          ? "3px 3px 0 var(--color-poke-yellow-dark)"
                          : "2px 2px 0 var(--color-poke-panel-edge)",
                        color: canSwitch ? "var(--color-poke-text)" : "var(--color-poke-text-muted)",
                        opacity: canSwitch ? 1 : 0.45,
                        cursor: canSwitch ? "pointer" : "not-allowed",
                      }}
                    >
                      <p
                        className="text-[0.5rem] font-bold capitalize"
                        style={{ fontFamily: "var(--font-pixel)" }}
                      >
                        {p.name}
                      </p>
                      <p className="text-xs mt-1">
                        {p.hp <= 0 || p.is_fainted ? "Debilitado" : `${p.hp}/${p.max_hp} HP`}
                      </p>
                    </button>
                  );
                })}
              </div>
            </RetroPanel>
          )}
        </div>
      )}
      </div>
    </div>
  );
}

export default Battle;
