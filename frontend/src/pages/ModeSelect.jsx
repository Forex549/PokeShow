import { useNavigate } from "react-router-dom";

function ModeSelect() {
    const navigate = useNavigate();

    const selectMode = (mode) => {
        navigate("/select", {
            state: { mode },
        });
    };

    return (
        <div className="min-h-screen bg-slate-100 flex items-center justify-center px-6">

            <div className="bg-white shadow-2xl rounded-[40px] p-14 w-full max-w-2xl">

                {/* Título */}
                <div className="text-center mb-12">
                    <h1 className="text-5xl font-black text-slate-800 mb-4">
                        Seleccionar Modo
                    </h1>

                    <p className="text-slate-500 text-lg">
                        Elige el tipo de inteligencia artificial
                    </p>
                </div>

                {/* Opciones */}
                <div className="flex flex-col gap-6">

                    {/* RANDOM */}
                    <button
                        onClick={() => selectMode("random")}
                        className="
                            group
                            bg-slate-50
                            hover:bg-sky-50
                            border
                            border-slate-200
                            hover:border-sky-300
                            transition-all
                            duration-300
                            rounded-3xl
                            p-6
                            text-left
                            shadow-sm
                            hover:shadow-lg
                        "
                    >
                        <h2 className="text-2xl font-bold text-slate-800 mb-2">
                            IA Random
                        </h2>

                        <p className="text-slate-500">
                            Selecciona movimientos aleatorios.
                        </p>
                    </button>

                    {/* HEURISTIC */}
                    <button
                        onClick={() => selectMode("heuristic")}
                        className="
                            group
                            bg-slate-50
                            hover:bg-purple-50
                            border
                            border-slate-200
                            hover:border-purple-300
                            transition-all
                            duration-300
                            rounded-3xl
                            p-6
                            text-left
                            shadow-sm
                            hover:shadow-lg
                        "
                    >
                        <h2 className="text-2xl font-bold text-slate-800 mb-2">
                            IA Heurística
                        </h2>

                        <p className="text-slate-500">
                            Evalúa daño, tipos y ventaja táctica.
                        </p>
                    </button>

                    {/* AI VS AI */}
                    <button
                        onClick={() => selectMode("ai-vs-ai")}
                        className="
                            group
                            bg-slate-50
                            hover:bg-rose-50
                            border
                            border-slate-200
                            hover:border-rose-300
                            transition-all
                            duration-300
                            rounded-3xl
                            p-6
                            text-left
                            shadow-sm
                            hover:shadow-lg
                        "
                    >
                        <h2 className="text-2xl font-bold text-slate-800 mb-2">
                            IA vs IA
                        </h2>

                        <p className="text-slate-500">
                            Observa dos inteligencias enfrentarse automáticamente.
                        </p>
                    </button>

                </div>
            </div>
        </div>
    );
}

export default ModeSelect;