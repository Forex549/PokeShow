import { useNavigate } from "react-router-dom";

function Home() {
    const navigate = useNavigate();

    return (
        <div className="min-h-screen bg-slate-100 flex flex-col justify-center items-center px-6">

            {/* Card principal */}
            <div className="bg-white shadow-2xl rounded-[40px] p-16 flex flex-col items-center w-full max-w-2xl">

                {/* Logo / título */}
                <h1 className="text-7xl font-black text-slate-800 tracking-tight mb-4">
                    PokeGen.ai
                </h1>

                <p className="text-slate-500 text-xl mb-12 text-center">
                    Simulador de Combates Pokémon con Inteligencia Artificial
                </p>

                {/* Botón */}
                <button
                    onClick={() => navigate("/mode")}
                    className="
                        bg-sky-500
                        hover:bg-sky-600
                        transition-all
                        duration-300
                        text-white
                        px-12
                        py-5
                        rounded-2xl
                        text-2xl
                        font-bold
                        shadow-lg
                        hover:scale-105
                    "
                >
                    Iniciar Batalla
                </button>

            </div>
        </div>
    );
}

export default Home;