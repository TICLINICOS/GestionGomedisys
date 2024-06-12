# -*- coding: utf-8 -*-
"""
Created on Mon Apr 18 2024
@author: Sebastian Suarez
"""

# Imports
import json
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from decouple import config
from colorama import Fore, Style
import httpx
from tqdm import tqdm
import app.Services.getTokenGomedisys_service as getTokenGomedisys_service


# Controller
async def obtener_listas_gomedisys():

    # Obtener variables de entorno
    URL_BASE_GOMEDISYS = config("URL_BASE_GOMEDISYS")
    KEY_GOMEDISYS_TEST = config("KEY_GOMEDISYS_TEST")
    RUTA_LISTADOS_GENERALES_CREACION_PACIENTES = config(
        "RUTA_LISTADOS_GENERALES_CREACION_PACIENTES"
    )

#Listado generales para creación de pacientes
    LISTAS_CREACION_PACIENTE = [
        {"Identifier": "ptTypeDocument", "Description": "Tipos de documento"},
        {"Identifier": "ptAdministrativeSex", "Description": "Sexo al nacer"},
        {"Identifier": "ptGenderIdentity", "Description": "Identidad de género"},
        {"Identifier": "ptMaritalStatus", "Description": "Estado civil"},
        {"Identifier": "ptScholarship", "Description": "Nivel de educación"},
        {"Identifier": "ptOccupation", "Description": "Ocupación"},
        {"Identifier": "PtReligion", "Description": "Religión"},
        {"Identifier": "ptZoneResidence", "Description": "Zona de residencia"},
        {"Identifier": "ptCareProvider", "Description": "Asegurador"},
        {"Identifier": "ptPoliticalDivision", "Description": "División política"},
    ]

    # Obtener token Gomedisys
    tokenGomedisys = await getTokenGomedisys_service.get_token_gomedisys()

    if not tokenGomedisys:
        raise HTTPException(
            status_code=500, detail="No se pudo obtener el token de Gomedisys."
        )

    archivos_creados = 0
    for identifier_info in tqdm(LISTAS_CREACION_PACIENTE, desc=Fore.GREEN +"Procesando Listas Generales Creacion Pacientes",colour="#39FF14", smoothing=0.05,bar_format="{l_bar}{bar}{r_bar}", dynamic_ncols=True, ascii=False):
        identifier = identifier_info["Identifier"]

        # Obtener las listas de Gomedisys
        URL_LISTA = f"{URL_BASE_GOMEDISYS}/Appointment/GetListsForAppointments/{identifier}/{KEY_GOMEDISYS_TEST}"
        #print("Procesando la lista de Gomedisys...", URL_LISTA)
        headers = {"Authorization": f"Bearer {tokenGomedisys}"}

        async with httpx.AsyncClient() as client:
            response = await client.get(URL_LISTA, headers=headers)
            json_data = response.json()
            if response.status_code == 200:

                with open(
                    f"{RUTA_LISTADOS_GENERALES_CREACION_PACIENTES}/{identifier}.json",
                    "w",
                ) as file:
                    json.dump(json_data, file)
                    archivos_creados += 1
            else:
                raise HTTPException(
                    status_code=response.status_code, detail=json_data["message"]
                )

    return {
        "message": "Se han creado correctamente los archivos JSON para los Listados generales Creacion Pacientes.",
        "archivos_creados": archivos_creados,
        "total_listas": len(LISTAS_CREACION_PACIENTE)
    }

