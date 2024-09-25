# -*- coding: utf-8 -*-
"""
Created on Mon Apr 18 2024
@author: Sebastian Suarez
"""

# Imports
import pandas as pd
from decouple import config


# Controller
async def obtener_datos_excel():

    ruta_archivo_creacion = config("RUTA_ARCHIVO_PACIENTES")

    try:
        df = pd.read_excel(ruta_archivo_creacion)
    except Exception as e:
        print(f"No se pudo leer el archivo Excel: {e}")
        return None

    # Convertir las fechas a strings
    df["FECHANACIMIENTO"] = df["FECHANACIMIENTO"].dt.strftime("%Y-%m-%d")
    df = df.fillna("")
    data_dict = df.to_dict(orient="records")

    datosPacientes = [
        {"id": i + 1, "InfoPaciente": item} for i, item in enumerate(data_dict)
    ]

    return datosPacientes




"""
import httpx
import pandas as pd
from io import BytesIO
from decouple import config
from fastapi import HTTPException
import time

# Configura tus credenciales de Azure AD
CLIENT_ID = config("CLIENT_ID")
CLIENT_SECRET = config("CLIENT_SECRET")
TENANT_ID = config("TENANT_ID")

# ID del archivo en OneDrive o SharePoint (extraído de la URL)
FILE_ID = "Ed6NpH-Z3FlLtQvUHfXRsB8BwTLGuJTY0hTBEnkEWVxkwQ"  # Cambia esto por el ID real

# Inicializa las variables para el token
access_token = None
token_expires_at = 0

async def get_access_token():
    global access_token, token_expires_at
    if access_token and time.time() < token_expires_at:
        return access_token

    try:
        data = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "client_credentials",
            "scope": "https://graph.microsoft.com/.default",
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token", data=data)
            response.raise_for_status()
            token_info = response.json()
            access_token = token_info["access_token"]
            token_expires_at = time.time() + token_info["expires_in"]

    except httpx.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error en la solicitud HTTP: {e}")

    return access_token

async def obtener_datos_excel():
    token = await get_access_token()

    if token:
        try:
            # URL para descargar el archivo usando el ID
            url = f"https://graph.microsoft.com/v1.0/me/drive/items/{FILE_ID}/content"

            headers = {
                'Authorization': f'Bearer {token}'
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)

                if response.status_code != 200:
                    raise Exception(f"Error en la solicitud HTTP. Código de estado: {response.status_code}")

                # Verifica el contenido del archivo
                if 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' not in response.headers['Content-Type']:
                    raise Exception(f"El archivo descargado no es un archivo Excel. Tipo de contenido: {response.headers['Content-Type']}")

                # Leer el archivo Excel desde los bytes descargados
                df = pd.read_excel(BytesIO(response.content), engine='openpyxl')

                # Convertir las fechas a strings y limpiar los datos
                df["FECHANACIMIENTO"] = df["FECHANACIMIENTO"].dt.strftime("%Y-%m-%d")
                df = df.fillna("")
                data_dict = df.to_dict(orient="records")

                datosPacientes = [
                    {"id": i + 1, "InfoPaciente": item} for i, item in enumerate(data_dict)
                ]

                return datosPacientes

        except Exception as e:
            print(f"No se pudo leer el archivo Excel: {e}")
            return {"error": f"No se pudieron obtener los datos del archivo Excel. Detalles: {e}"}
    else:
        print("Error en la autenticación.")
        return {"error": "Error en la autenticación con Microsoft Graph."}
"""