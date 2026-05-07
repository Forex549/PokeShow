import { BrowserRouter, Routes, Route } from "react-router-dom";

import Home from "./pages/Home";
import ModeSelect from "./pages/ModeSelect";
import PokemonSelect from "./pages/PokemonSelect";
import Battle from "./pages/Battle";
import Result from "./pages/Result";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />

        <Route
          path="/mode"
          element={<ModeSelect />}
        />

        <Route
          path="/select"
          element={<PokemonSelect />}
        />

        <Route
          path="/battle"
          element={<Battle />}
        />

        <Route
          path="/result"
          element={<Result />}
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;