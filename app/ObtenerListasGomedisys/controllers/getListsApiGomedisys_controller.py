# -*- coding: utf-8 -*-
"""
Created on Mon Apr 22 2024
@author: Sebastian Suarez
"""

# Imports
import json
from fastapi import HTTPException
from decouple import config
from colorama import Fore
import httpx
from tqdm import tqdm
import app.Services.getTokenGomedisys_service as getTokenGomedisys_service

# Controller
async def obtener_listas_gomedisys_API():

    # Obtener variables de entorno
    URL_BASE_GOMEDISYS = config("URL_BASE_GOMEDISYS")
    KEY_GOMEDISYS_TEST = config("KEY_GOMEDISYS_TEST")
    RUTA_LISTADOS_PRINCIPALES_GOMEDISYS_API = config(
        "RUTA_LISTADOS_PRINCIPALES_GOMEDISYS_API"
    )

    # Listado generales para creación de pacientes
    LISTAS_GENERALES_API_GOMEDISYS = [
        {
            "Identifier": "Offices",
            "Description": "Exámenes con sedes"
        },
        {
            "Identifier": "Exams",
            "Description": "Exámenes con tipos de examen"
        },
        {
            "Identifier": "Professionals",
            "Description": "Profesionales por examen por sede",
        },
        {
            "Identifier": "Insurances",
            "Description": "Lineas de pago",
        },
        {
            "Identifier": "CausalLists",
            "Description": "Causales para cancelación"
        },
        {"Identifier": "StateApp",
        "Description": "Estados de citas"
        },
    ]

    # Obtener token Gomedisys
    tokenGomedisys = await getTokenGomedisys_service.get_token_gomedisys()

    if not tokenGomedisys:
        raise HTTPException(
            status_code=500, detail="No se pudo obtener el token de Gomedisys."
        )

    archivos_creados = 0
    for identifier_info in tqdm(
        LISTAS_GENERALES_API_GOMEDISYS,
        desc=Fore.GREEN + "Procesando Listados principales Gomedisys API",
        colour="#39FF14",
        smoothing=0.05,
        bar_format="{l_bar}{bar}{r_bar}",
        dynamic_ncols=True,
        ascii=False,
    ):
        identifier = identifier_info["Identifier"]

        # Obtener las listas de Gomedisys
        URL_LISTA = f"{URL_BASE_GOMEDISYS}/Appointment/GetListsForAppointments/{identifier}/{KEY_GOMEDISYS_TEST}"
        headers = {"Authorization": f"Bearer {tokenGomedisys}"}

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(URL_LISTA, headers=headers)
            json_data = response.json()
            if response.status_code == 200:
                with open(
                    f"{RUTA_LISTADOS_PRINCIPALES_GOMEDISYS_API}/{identifier}.json",
                    "w",
                ) as file:
                    json.dump(json_data, file)
                    archivos_creados += 1
            else:
                raise HTTPException(
                    status_code=response.status_code, detail=json_data.get("message", "Error desconocido")
                )

    return {
        "message": "Se han creado correctamente los archivos JSON para los Listados principales Gomedisys API.",
        "archivos_creados": archivos_creados,
        "total_listas": len(LISTAS_GENERALES_API_GOMEDISYS),
    }
