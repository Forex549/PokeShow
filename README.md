## Despliegue
### Requisitos del Sistema
- **Python 3.7+** (para el backend)
- **Node.js + npm/pnpm** (para el frontend)
- Conexión a internet para instalaciones iniciales (opcional)
### Paso 1: Clonar el Proyecto
```bash
git clone <tu-repositorio>
cd PokeShow
Paso 2: Configurar el Backend
# Instalar dependencias
pip install -r requirements.txt
# Variables de entorno (crear archivo .env si es necesario)
# Ejemplo:
# POKE_API_KEY=your_api_key
# Iniciar servidor
uvicorn src.api.api_v1.endpoints.battle:api --host 0.0.0.0 --port 8000
Paso 3: Configurar el Frontend
# Entrar a la carpeta frontend
cd frontend
# Instalar dependencias
npm install  # o pnpm install si usas pnpm
# Compilar y ejecutar
npm run dev
# El frontend estará disponible en http://localhost:5173
Paso 4: Iniciar el Sistema Completo
1. Terminal 1: Iniciar backend en http://localhost:8000
2. Terminal 2: Iniciar frontend en http://localhost:5173
3. Abrir navegador y visitar http://localhost:5173
Configuración Avanzada
Variables de Entorno (.env)
# Backend
UVICORN_WORKERS=1                    # Número de workers
UVICORN_TIMEOUT_KEEP_ALIVE=5          # Timeout de keep alive
FLASK_ENV=production                 # Entorno (development/production)
# Frontend
VITE_API_BASE_URL=http://localhost:8000  # URL base de la API
Modo Producción con PM2
# Backend (usar pm2 para producción)
pm2 start uvicorn --name pokeshow-backend \
  -- -m uvicorn.src.api.api_v1.endpoints.battle:api --host 0.0.0.0 --port 8000
# Frontend (usar pm2 para producción)
cd frontend
pm2 start npm --name pokeshow-frontend -- run build
pm2 start npm --name pokeshow-frontend -- run start
Estructura de Directorios
PokeShow/
├── src/                      # Códico del backend
│   ├── api/
│   ├── engine/
│   └── models/
├── frontend/                 # Códico del frontend
│   ├── src/
│   ├── public/
│   └── README.md
├── requirements.txt
├── package.json
└── .env                      # Variables de entorno
Enlaces Útiles
- Archivos clave del backend: src/api/api_v1/endpoints/battle.py:8, src/engine/logic/heuristic.py:1
- Archivos clave del frontend: frontend/src/pages/Battle.jsx, frontend/src/pages/PokemonSelect.jsx
- Modelo de IA entrenado: models/minimax_4factors.keras
Solución de Problemas
- Error 127: Asegurar que Node/Numpy estén instalados
- Puerto en uso: Cambiar puerto en uvicorn (--port 8001)
- CORS Issues: Configurar correctamente ALLOWED_ORIGINS en backend
Área de Pruebas y Simulaciones
# Pruebas unitarias
pytest
# Ejecutar simulaciones de batalla
python run_simulation.py
# Entrenar modelo de IA
python run_training.py
Notas Finales
- El backend maneja toda la lógica de batalla Pokemon
- El frontend es una aplicación React + Vite con TailwindCSS
- El sistema incluye múltiples estrategias de IA (random, heuristic, minimax2/3)
- Para produción, se recomienda usar gunicorn + nginx en lugar de uvicorn directamente
