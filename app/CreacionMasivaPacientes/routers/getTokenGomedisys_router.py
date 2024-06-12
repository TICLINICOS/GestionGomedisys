# -*- coding: utf-8 -*-
"""
Created on Mon Apr 22 2024
@author: Sebastian Suarez
"""

from fastapi import FastAPI, APIRouter
from app.Services.getTokenGomedisys_service import get_token_gomedisys


router = APIRouter(prefix="/Auth")


@router.post("/TokenGomedisys")
async def get_token_gomedisys_route():
    json_data = await get_token_gomedisys()

    if json_data:
        return {"token": json_data}
    else:
        return {"error": "No se pudo obtener el token"}
