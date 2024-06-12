# -*- coding: utf-8 -*-
"""
Created on Sun Apr 22 2024
@author: Sebastian Suarez
"""
# Imports
from fastapi import FastAPI, APIRouter
from app.ObtenerListasGomedisys.controllers.getListsApiGomedisys_controller import (
    obtener_listas_gomedisys_API,
)


router = APIRouter(prefix="/ObtenerLISTAS")


@router.get("/ObtenerListasGeneralesGomedisysAPI")
async def obtener_listas_generales_gomedisys_route():
    json_data = await obtener_listas_gomedisys_API()

    if json_data:
        return {"data": json_data}
    else:
        return {"error": "No se pudieron obtener los datos de Listados principales Gomedisys API."}
