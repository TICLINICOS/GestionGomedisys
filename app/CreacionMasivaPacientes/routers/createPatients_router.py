# -*- coding: utf-8 -*-
"""
Created on Mon Apr 18 2024
@author: Sebastian Suarez
"""

from fastapi import FastAPI, APIRouter
from app.CreacionMasivaPacientes.controllers.createPatients_controller import (
    create_patient_gomedisys
)


router = APIRouter(prefix="/CreacionPacientes")


@router.post("/CrearPacientes")
async def create_patient_gomedisys_route():
    json_data = await create_patient_gomedisys()

    if json_data:
        return json_data
    else:
        return {"error": "No se pudieron crear los Pacientes en Gomedisys."}
