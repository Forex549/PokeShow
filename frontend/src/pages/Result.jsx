import { useLocation, useNavigate } from "react-router-dom";

function Result() {
    const navigate = useNavigate();
    const location = useLocation();

    const winner = location.state?.winner;
    const turns = location.state?.turns;
    const mode = location.state?.mode;

    return (
        <div className="min-h-screen bg-green-200 flex flex-col justify-center items-center p-10">
            <div className="bg-white rounded-2xl shadow-2xl p-10 w-[500px] text-center">
                <h1 className="text-5xl font-bold mb-8">
                    Resultado
                </h1>

                <h2 className="text-3xl mb-5">
                    Ganador:
                </h2>

                <p className="text-4xl font-bold text-blue-600 mb-8">
                    {winner}
                </p>

                <div className="text-xl mb-3">
                    <strong>Turnos:</strong> {turns}
                </div>

                <div className="text-xl mb-8">
                    <strong>Modo:</strong> {mode}
                </div>

                <button
                    onClick={() => navigate("/")}
                    className="bg-blue-500 hover:bg-blue-600 text-white px-8 py-4 rounded-2xl text-2xl"
                >
                    Volver al Inicio
                </button>
            </div>
        </div>
    );
}

export default Result;