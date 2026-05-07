function BattleLog({ logs }) {
    return (
        <div className="bg-black text-green-400 p-4 rounded-xl h-[250px] overflow-y-auto font-mono">
            {logs.map((log, index) => (
                <p key={index}>{log}</p>
            ))}
        </div>
    );
}

export default BattleLog;