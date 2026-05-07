function MoveButtons({
    moves,
    onMove,
    disabled,
}) {
    return (
        <div className="grid grid-cols-2 gap-4 mt-8">
            {moves.map((move) => (
                <button
                    key={move}
                    disabled={disabled}
                    onClick={() => onMove(move)}
                    className={`
                        p-4 rounded-xl text-lg font-bold text-white transition

                        ${disabled
                            ? "bg-gray-400 cursor-not-allowed opacity-60"
                            : "bg-slate-700 hover:bg-slate-800"
                        }
                    `}
                >
                    {move}
                </button>
            ))}
        </div>
    );
}

export default MoveButtons;