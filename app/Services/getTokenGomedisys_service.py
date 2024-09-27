# -*- coding: utf-8 -*-
"""
Created on Mon Apr 18 2024
@author: Sebastian Suarez
"""

""" # Imports
from decouple import config
from fastapi import HTTPException
import httpx


# Service Get Token
async def get_token_gomedisys():

    USERNAME_GOMEDISYS = config("USERNAME_GOMEDISYS")
    PASSWORD_GOMEDISYS = config("PASSWORD_GOMEDISYS")
    URL_BASE_GOMEDISYS = config("URL_BASE_GOMEDISYS")

    try:
        URL = f"{URL_BASE_GOMEDISYS}/token"

        data = {"Username": USERNAME_GOMEDISYS, "Password": PASSWORD_GOMEDISYS}

        async with httpx.AsyncClient() as client:
            response = await client.post(URL, json=data)
            response.raise_for_status()
            tokenGomedisys = response.json()

    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Error en la solicitud HTTP: {e}")

    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=response.status_code, detail=f"Error en la respuesta HTTP: {e}"
        )

    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Error al analizar JSON: {e}")

    return tokenGomedisys
#-------------Version con validacion de expiración-------------#
# -*- coding: utf-8 -*-

Created on Mon Apr 18 2024
@author: Sebastian Suarez


# Imports
from decouple import config
from fastapi import HTTPException
import httpx
import time

# Variables globales para almacenar el token y su tiempo de expiración
token_gomedisys = None
token_gomedisys_expires_at = None


# Service Get Token
async def get_token_gomedisys():
    global token_gomedisys, token_gomedisys_expires_at

    # Verificar si ya tenemos un token válido en caché
    if token_gomedisys and time.time() < token_gomedisys_expires_at:
        return token_gomedisys

    USERNAME_GOMEDISYS = config("USERNAME_GOMEDISYS")
    PASSWORD_GOMEDISYS = config("PASSWORD_GOMEDISYS")
    URL_BASE_GOMEDISYS = config("URL_BASE_GOMEDISYS")

    try:
        URL = f"{URL_BASE_GOMEDISYS}/token"

        data = {"Username": USERNAME_GOMEDISYS, "Password": PASSWORD_GOMEDISYS}

        async with httpx.AsyncClient() as client:
            response = await client.post(URL, json=data)
            response.raise_for_status()
            token_info = response.json()
            token_gomedisys = token_info["token"]
            token_gomedisys_expires_at = time.time() + token_info["expires_in"]

    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Error en la solicitud HTTP: {e}")

    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=response.status_code, detail=f"Error en la respuesta HTTP: {e}"
        )

    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Error al analizar JSON: {e}")

    return token_gomedisys

"""
# Imports
from decouple import config
from fastapi import HTTPException
import httpx
import time

# Variables globales para almacenar el token y su tiempo de expiración
token_gomedisys = None
token_gomedisys_expires_at = None

# Service Get Token
async def get_token_gomedisys():
    global token_gomedisys, token_gomedisys_expires_at

    # Verificar si ya tenemos un token válido en caché
    if token_gomedisys and time.time() < token_gomedisys_expires_at:
        return token_gomedisys

    USERNAME_GOMEDISYS = config("USERNAME_GOMEDISYS")
    PASSWORD_GOMEDISYS = config("PASSWORD_GOMEDISYS")
    URL_BASE_GOMEDISYS = config("URL_BASE_GOMEDISYS")

    try:
        print("Token Nuevo")
        URL = f"{URL_BASE_GOMEDISYS}/token"
        data = {"Username": USERNAME_GOMEDISYS, "Password": PASSWORD_GOMEDISYS}

        async with httpx.AsyncClient() as client:
            response = await client.post(URL, json=data)
            #print(response.json())
            token_gomedisys = response.json()
            #response.raise_for_status() # Directamente obteniendo el token

            # Estimamos el tiempo de expiración del token (por ejemplo, 1 hora)
            token_gomedisys_expires_at = time.time() + 1800  # 3600 segundos = 1 hora

    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Error en la solicitud HTTP: {e}")

    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=response.status_code, detail=f"Error en la respuesta HTTP: {e}"
        )

    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Error al analizar JSON: {e}")

    return token_gomedisys
