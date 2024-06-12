# -*- coding: utf-8 -*-
"""
Created on Thursday May 16 2024
@author: Sebastian Suarez
"""

from fastapi import FastAPI, APIRouter
from app.CreacionMasivaPacientes.controllers.validatePatients_controller import (
    validate_patients
)


router = APIRouter(prefix="/CreacionPacientes")


@router.post("/validarPaciente")
async def get_patient_info_route():
    tipo_documento = "CC"
    numero_documento = "1234"
    json_data = await validate_patients(tipo_documento=tipo_documento, numero_documento=numero_documento)

    return json_data
    """if json_data:
        return json_data
    else:
        return {"error": "No se pudo obtener la informacion del Paciente en Gomedisys."}"""
