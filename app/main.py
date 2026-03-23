from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth

app = FastAPI(
    title="Vue Auth Demo API",
    description="Backend para autenticación con Vue.js",
    version="1.0.0"
)

# Configurar CORS para el frontend Vue
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(auth.router)

@app.get("/")
async def root():
    return {"message": "FastAPI backend funcionando 🚀"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
