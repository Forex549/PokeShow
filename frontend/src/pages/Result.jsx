import { useLocation, useNavigate } from "react-router-dom";

function Result() {
    const navigate = useNavigate();
    const location = useLocation();

    const winner = location.state?.winner;
    const turns = location.state?.turns;
    const mode = location.state?.mode;

    return (
        <div className="min-h-screen bg-slate-100 flex justify-center items-center p-8">
            <div className="
                w-full
                max-w-2xl
                bg-white
                rounded-[40px]
                shadow-2xl
                border
                border-slate-200
                overflow-hidden
            ">
                {/* HEADER */}
                <div className="
                    bg-gradient-to-r
                    from-sky-500
                    to-indigo-500
                    p-8
                    text-center
                ">
                    <h1 className="text-5xl font-black text-white mb-3">
                        Battle Result
                    </h1>

                    <p className="text-sky-100 text-lg">
                        La batalla ha terminado
                    </p>
                </div>

                {/* CONTENT */}
                <div className="p-10">
                    {/* WINNER */}
                    <div className="text-center mb-10">
                        <p className="text-slate-500 text-xl mb-3">
                            Ganador
                        </p>

                        <h2 className="
                            text-6xl
                            font-black
                            text-slate-800
                            capitalize
                            tracking-wide
                        ">
                            {winner}
                        </h2>
                    </div>

                    {/* MODE */}
                    <div className="
                        bg-slate-100
                        rounded-3xl
                        p-5
                        mb-8
                        flex
                        justify-between
                        items-center
                    ">
                        <span className="text-slate-500 text-lg">
                            Modo de batalla
                        </span>

                        <span className="
                            bg-sky-500
                            text-white
                            px-4
                            py-2
                            rounded-xl
                            font-bold
                            capitalize
                        ">
                            {mode}
                        </span>
                    </div>

                    {/* LOGS */}
                    <div className="mb-10">
                        <h3 className="
                            text-2xl
                            font-bold
                            text-slate-700
                            mb-4
                        ">
                            Historial de batalla
                        </h3>

                        <div className="
                            bg-slate-900
                            rounded-3xl
                            p-5
                            h-64
                            overflow-y-auto
                            space-y-3
                            shadow-inner
                        ">
                            {turns?.map((turn, index) => (
                                <div
                                    key={index}
                                    className="
                                        text-slate-200
                                        bg-slate-800
                                        px-4
                                        py-3
                                        rounded-2xl
                                        text-left
                                    "
                                >
                                    {turn}
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* BUTTON */}
                    <div className="flex justify-center">
                        <button
                            onClick={() => navigate("/")}
                            className="
                                bg-sky-500
                                hover:bg-sky-600
                                transition-all
                                duration-300
                                text-white
                                px-10
                                py-4
                                rounded-2xl
                                text-2xl
                                font-bold
                                shadow-lg
                                hover:scale-105
                            "
                        >
                            Volver al Inicio
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Result;