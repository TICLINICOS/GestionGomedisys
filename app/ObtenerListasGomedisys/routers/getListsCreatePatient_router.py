# -*- coding: utf-8 -*-
"""
Created on Mon Apr 18 2024
@author: Sebastian Suarez
"""
# Imports
from fastapi import FastAPI, APIRouter
from app.ObtenerListasGomedisys.controllers.getListsCreatePatient_controller import (
    obtener_listas_gomedisys,
)


router = APIRouter(prefix="/ObtenerLISTAS")


@router.get("/ObtenerListasGomedisys")
async def obtener_listas_gomedisys_route():
    json_data = await obtener_listas_gomedisys()

    if json_data:
        return {"data": json_data}
    else:
        return {"error": "No se pudieron obtener los datos del archivo Excel."}
