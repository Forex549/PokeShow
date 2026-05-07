import { useNavigate } from "react-router-dom";

function Home() {
    const navigate = useNavigate();

    return (
        <div className="min-h-screen flex flex-col justify-center items-center bg-green-200">
            <h1 className="text-6xl font-bold mb-10">
                PokeGen.ai
            </h1>

            <button
                onClick={() => navigate("/mode")}
                className="bg-blue-500 text-white px-8 py-4 rounded-2xl text-2xl"
            >
                Start
            </button>
        </div>
    );
}

export default Home;