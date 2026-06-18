import { useNavigate } from "react-router-dom";
import RetroPanel from "../components/RetroPanel";
import RetroButton from "../components/RetroButton";

function Home() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex flex-col justify-center items-center px-6 py-12">
      <RetroPanel className="p-12 flex flex-col items-center w-full max-w-xl gap-8">

        {/* Brand */}
        <div className="text-center">
          <h1
            className="retro-title text-3xl mb-3"
            style={{ color: "var(--color-poke-red)" }}
          >
            PokeShow
          </h1>
          <div
            className="text-[0.55rem] font-bold uppercase tracking-widest mt-1"
            style={{
              fontFamily: "var(--font-pixel)",
              color: "var(--color-poke-text-muted)",
            }}
          >
            Battle Simulator
          </div>
        </div>

        {/* Pixel divider */}
        <div
          className="w-full h-[3px]"
          style={{ background: "var(--color-poke-panel-edge)" }}
        />

        {/* Tagline */}
        <p
          className="text-center text-sm leading-relaxed"
          style={{ color: "var(--color-poke-text-muted)" }}
        >
          Simulador de combates Pokémon con Inteligencia Artificial
        </p>

        {/* CTA */}
        <RetroButton
          size="lg"
          onClick={() => navigate("/mode")}
          className="w-full justify-center mt-2"
        >
          ► Iniciar Batalla
        </RetroButton>

      </RetroPanel>

      {/* Footer label */}
      <p
        className="mt-6 text-[0.4rem]"
        style={{
          fontFamily: "var(--font-pixel)",
          color: "var(--color-poke-text-muted)",
        }}
      >
        © 2004 PokeShow — Powered by AI
      </p>
    </div>
  );
}

export default Home;
