import { useNavigate } from "react-router-dom";
import RetroPanel from "../components/RetroPanel";
import RetroButton from "../components/RetroButton";
import Logo from "../components/Logo";

function Home() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex flex-col justify-center items-center px-6 py-12">
      <RetroPanel className="p-12 flex flex-col items-center w-full max-w-xl gap-8">

        {/* Brand */}
        <div className="text-center">
          <Logo width={220} />
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
      <div className="mt-6 flex flex-col items-center gap-2">
        <Logo width={140} />
        <p
          className="text-[0.4rem]"
          style={{
            fontFamily: "var(--font-pixel)",
            color: "var(--color-poke-text-muted)",
          }}
        >
          © 2004 — Powered by AI
        </p>
      </div>
    </div>
  );
}

export default Home;
