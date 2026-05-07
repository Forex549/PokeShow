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
                            : "bg-blue-500 hover:bg-blue-600"
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