# Importaciones necesarias
from fastapi import APIRouter, HTTPException
from app.CreacionMasivaPacientes.controllers.updatePatients_controller import update_patient_gomedisys

# Crear el router
router = APIRouter(prefix="/CreacionPacientes")

# Ruta para actualizar la información de los pacientes en Gomedisys
@router.post("/update-patient", response_description="Actualización masiva de pacientes en Gomedisys")
async def actualizar_pacientes():
    try:
        # Llamar al controller para actualizar pacientes
        resultado_actualizacion = await update_patient_gomedisys()

        # Retornar el resultado de la operación
        return {
            "Mensaje": "Proceso de actualización completado",
            "Pacientes actualizados": resultado_actualizacion[1],
            "Pacientes no actualizados": resultado_actualizacion[3]
        }

    except Exception as e:
        # Manejar excepciones y retornar un error
        raise HTTPException(status_code=500, detail=f"Error durante la actualización: {str(e)}")
