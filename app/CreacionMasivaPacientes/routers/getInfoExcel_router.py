# -*- coding: utf-8 -*-
"""
Created on Mon Apr 18 2024
@author: Sebastian Suarez
"""

from fastapi import FastAPI, APIRouter
from app.CreacionMasivaPacientes.controllers.getInfoExcel_controller import (
    obtener_datos_excel,
)


router = APIRouter(prefix="/CreacionPacientes")


@router.get("/ObtenerDatosExcel")
async def obtener_datos_excel_route():
    json_data = await obtener_datos_excel()

    if json_data:
        return {"data": json_data}
    else:
        return {"error": "No se pudieron obtener los datos del archivo Excel."}
