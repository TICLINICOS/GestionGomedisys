# -*- coding: utf-8 -*-
"""
Creado el 18 de abril de 2024
Autor: Sebastian Suarez
"""

# Importaciones
import http.client
import json
from fastapi import HTTPException
from decouple import config
import httpx
import app.Services.getTokenGomedisys_service as getTokenGomedisys_service

# Configuraciones
KEY_GOMEDISYS_TEST = config("KEY_GOMEDISYS_TEST")
URL_BASE_GOMEDISYS = config("URL_BASE_GOMEDISYS")


async def validate_patients(tipo_documento: str, numero_documento: str):
    

    try:
        tokenGomedisys = await getTokenGomedisys_service.get_token_gomedisys()

        if not tokenGomedisys:
            raise HTTPException(
                status_code=500, detail="No se pudo obtener el token de Gomedisys."
            )

        data_patient = {
            "keyWS": KEY_GOMEDISYS_TEST,
            "typeDocument": tipo_documento,
            "documentNumber": numero_documento,
        }

        conn = http.client.HTTPSConnection("servicesrest.gomedisys.com")
        payload = json.dumps({
            "keyWS": KEY_GOMEDISYS_TEST,
            "typeDocument": tipo_documento,
            "documentNumber": numero_documento
        })
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {tokenGomedisys}',
        }
        conn.request("GET", "/api/Appointment/GetPatientInfo", payload, headers)
        res = conn.getresponse()
        data = res.read()
        #print(data.decode("utf-8"))

    except httpx.HTTPError as http_err:
        raise HTTPException(status_code=500, detail="Error en la solicitud HTTP.")

    except Exception as e:
        raise HTTPException(status_code=500, detail="Error interno del servidor.")

    return data.decode("utf-8")
