import { useNavigate } from "react-router-dom";

function ModeSelect() {
    const navigate = useNavigate();

    const selectMode = (mode) => {
        navigate("/select", {
            state: {
                mode,
            },
        });
    };

    return (
        <div className="min-h-screen bg-green-200 flex flex-col items-center justify-center p-10">
            <h1 className="text-5xl font-bold mb-10">
                Seleccionar Modo
            </h1>

            <div className="flex flex-col gap-5 w-[350px]">
                <button
                    onClick={() => selectMode("random")}
                    className="bg-blue-500 text-white p-4 rounded-2xl text-xl shadow-xl"
                >
                    IA Random
                </button>

                <button
                    onClick={() => selectMode("heuristic")}
                    className="bg-purple-500 text-white p-4 rounded-2xl text-xl shadow-xl"
                >
                    IA Heurística
                </button>

                <button
                    onClick={() => selectMode("ai-vs-ai")}
                    className="bg-red-500 text-white p-4 rounded-2xl text-xl shadow-xl"
                >
                    IA vs IA
                </button>
            </div>
        </div>
    );
}

export default ModeSelect;