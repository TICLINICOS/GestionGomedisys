# Import Libraries
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from decouple import config

# Import Routers
#Obtener Token
#-------------------------------------------------------------------------
from app.CreacionMasivaPacientes.routers import getTokenGomedisys_router
#-------------------------------------------------------------------------
#CrearPacientes
#-------------------------------------------------------------------------
from app.CreacionMasivaPacientes.routers import getInfoExcel_router
from app.CreacionMasivaPacientes.routers import createBodyRequest_router
from app.CreacionMasivaPacientes.routers import createPatients_router
from app.CreacionMasivaPacientes.routers import getTokenGomedisys_router
#-------------------------------------------------------------------------
#Listas Api Gomedisys
#-------------------------------------------------------------------------
from app.ObtenerListasGomedisys.routers import getListsCreatePatient_router
#-------------------------------------------------------------------------
from app.ObtenerListasGomedisys.routers import getListsApiGomedisys_router
#-------------------------------------------------------------------------
#Validar Pacientes
#-------------------------------------------------------------------------
from app.CreacionMasivaPacientes.routers import validatePatients_router
# SERVER
app = FastAPI()

# CORS
origins = ["*"
    #config("CLIENT_URL")
]

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # Lista de orígenes permitidos
    allow_credentials=True,           # Permitir cookies / autorización con credenciales
    allow_methods=["*"],              # Permitir todos los métodos (GET, POST, PUT, etc.)
    allow_headers=["*"],              # Permitir todos los encabezados
)

# Routers
#Obtener Token
#-------------------------------------------------------------------------
app.include_router(getTokenGomedisys_router.router)
#-------------------------------------------------------------------------
#CrearPacientes
#-------------------------------------------------------------------------
app.include_router(getInfoExcel_router.router)
app.include_router(createBodyRequest_router.router)
app.include_router(createPatients_router.router)
#-------------------------------------------------------------------------
#Obtener Listas
#-------------------------------------------------------------------------
app.include_router(getListsCreatePatient_router.router)
app.include_router(getListsApiGomedisys_router.router)
#-------------------------------------------------------------------------
#Validar Info Paciente
#-------------------------------------------------------------------------
app.include_router(validatePatients_router.router)










# Additional configuration
if __name__ == "__main__":
    import uvicorn

    # Get the configuration from environment variables or .env file
    host = config("HOST", default="127.0.0.1")
    port = config("PORT", default=5000, cast=int)

    # Run the application using uvicorn
    uvicorn.run("main:app", host=host, port=port, reload=True)
