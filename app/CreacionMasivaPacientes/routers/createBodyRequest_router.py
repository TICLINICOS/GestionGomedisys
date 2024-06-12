# -*- coding: utf-8 -*-
"""
Created on Mon Apr 18 2024
@author: Sebastian Suarez
"""

from colorama import Fore
from fastapi import FastAPI, APIRouter
from tqdm import tqdm
from app.CreacionMasivaPacientes.controllers.createBodyRequest_controller import (
    create_body_request
)
from app.CreacionMasivaPacientes.controllers.getInfoExcel_controller import obtener_datos_excel


router = APIRouter(prefix="/CreacionPacientes")


@router.post("/CrearBodyRequest")
async def create_body_request_route():
    infoExcel = await obtener_datos_excel()
    for item in tqdm(infoExcel,
            desc=Fore.BLUE + "Procesando pacientes",
            colour="#39FF14",
            smoothing=0.05,
            bar_format="{l_bar}{bar}{r_bar}",
            dynamic_ncols=True,
            ascii=False,
        ):
            paciente_data = item["InfoPaciente"]
    json_data = await create_body_request(paciente_data)

    if json_data:
        return json_data
    else:
        return {"error": "No se pudo crear el BodyRequest."}
