# -*- coding: utf-8 -*-
"""
Creado el 18 de abril de 2024
Autor: Sebastian Suarez
"""

# Importaciones
import http.client
import json
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from colorama import Fore
from tqdm import tqdm
from decouple import config
import httpx
import app.Services.getTokenGomedisys_service as getTokenGomedisys_service
from app.CreacionMasivaPacientes.controllers.createBodyRequest_controller import (
    create_body_request,
)
from app.CreacionMasivaPacientes.controllers.getInfoExcel_controller import (
    obtener_datos_excel,
)
from app.CreacionMasivaPacientes.controllers.validatePatients_controller import (
    validate_patients,
)


async def create_patient_gomedisys():
    URL_BASE_GOMEDISYS = config("URL_BASE_GOMEDISYS")
    
    # Función para obtener un nuevo token
    async def obtener_nuevo_token():
        return await getTokenGomedisys_service.get_token_gomedisys()

    # Inicializamos el token
    tokenGomedisys = await obtener_nuevo_token()

    if not tokenGomedisys:
        raise HTTPException(status_code=500, detail="No se pudo obtener el token de Gomedisys.")

    respuestasServicio = []
    patientsFound = []
    infoExcel = await obtener_datos_excel()

    for item in tqdm(
        infoExcel,
        desc=Fore.BLUE + "Procesando pacientes",
        colour="#39FF14",
        smoothing=0.05,
        bar_format="{l_bar}{bar}{r_bar}",
        dynamic_ncols=True,
        ascii=False,
    ):
        paciente_data = item["InfoPaciente"]
        validar_Paciente = await validate_patients(paciente_data["TIPODOCUMENTO"], str(paciente_data["DOCUMENTO"]))

        if validar_Paciente == "{\"CodError\":400,\"DescError\":\"Paciente no encontrado\"}" or validar_Paciente == "{\"CodError\":400,\"DescError\":\"No se encontraron registros para el criterio de búsqueda\"}":
            create_body = await create_body_request(paciente_data)

            try:
                URL = f"{URL_BASE_GOMEDISYS}/Appointment/CreatePatient"

                async with httpx.AsyncClient() as client:
                    headers = {"Authorization": f"Bearer {tokenGomedisys}"}
                    response = await client.post(URL, json=create_body, headers=headers)

                    # Si el token está vencido (401 Unauthorized), lo renovamos y volvemos a intentar
                    if response.status_code == 401:
                        tokenGomedisys = await obtener_nuevo_token()  # Obtener nuevo token
                        headers = {"Authorization": f"Bearer {tokenGomedisys}"}
                        response = await client.post(URL, json=create_body, headers=headers)  # Reintentar la solicitud
                        #response.raise_for_status()

                    print(response.raise_for_status())

                    respuestasServicio.append(
                        {"Estado": "Éxito", "Paciente": paciente_data, "Respuesta": response.json()}
                    )

                # Definir la ruta del archivo
                Creados_json = "Creados_pacientes.json"

                # Guardar en archivo JSON
                with open(Creados_json, "w", encoding="utf-8") as archivo:
                    json.dump(respuestasServicio, archivo, ensure_ascii=False, indent=4)

            except httpx.RequestError as e:
                respuestasServicio.append(
                    {"Estado": "Error en la solicitud HTTP", "Paciente": paciente_data, "Error": str(e)}
                )

            except httpx.HTTPError as e:
                respuestasServicio.append(
                    {"Estado": "Error en la respuesta HTTP", "Paciente": paciente_data, "Error": str(e)}
                )

            except ValueError as e:
                respuestasServicio.append(
                    {"Estado": "Error al analizar JSON", "Paciente": paciente_data, "Error": str(e)}
                )
        else:
            patientsFound.append(paciente_data)

            # Definir la ruta del archivo
            Encontrados_json = "Encontrados_pacientes.json"

            # Guardar en archivo JSON
            with open(Encontrados_json, "w", encoding="utf-8") as archivo:
                json.dump(patientsFound, archivo, ensure_ascii=False, indent=4)
            continue

    # Guardar los resultados en un archivo JSON
    resultado = {
        "Respuestas Carga Masiva": respuestasServicio,
        "Pacientes no creados porque se encontraron en la base de datos": patientsFound
    }

    # Definir la ruta del archivo
    archivo_json = "resultados_pacientes.json"

    # Guardar en archivo JSON
    with open(archivo_json, "w", encoding="utf-8") as archivo:
        json.dump(resultado, archivo, ensure_ascii=False, indent=4)

    return "Pacientes Creados", len(respuestasServicio), "Pacientes encontrados", len(patientsFound)



"""
# Controller
async def create_patient_gomedisys():
    URL_BASE_GOMEDISYS = config("URL_BASE_GOMEDISYS")

    tokenGomedisys = await getTokenGomedisys_service.get_token_gomedisys()

    if not tokenGomedisys:
        raise HTTPException(
            status_code=500, detail="No se pudo obtener el token de Gomedisys."
        )

    respuestasServicio = []
    patientsFound = []
    infoExcel = await obtener_datos_excel()
    for item in tqdm(
        infoExcel,
        desc=Fore.BLUE + "Procesando pacientes",
        colour="#39FF14",
        smoothing=0.05,
        bar_format="{l_bar}{bar}{r_bar}",
        dynamic_ncols=True,
        ascii=False,
    ):
        paciente_data = item["InfoPaciente"]
        #print(paciente_data)
        validar_Paciente = await validate_patients(paciente_data["TIPODOCUMENTO"], str(paciente_data["DOCUMENTO"]))
        #print(validar_Paciente)
        #print(str(paciente_data["DOCUMENTO"]), paciente_data["TIPODOCUMENTO"])


        if validar_Paciente == str("{\"CodError\":400,\"DescError\":\"Paciente no encontrado\"}"):
            create_body = await create_body_request(paciente_data)
            #print("Crear usuario")
            try:
                URL = f"{URL_BASE_GOMEDISYS}/Appointment/CreatePatient"

                async with httpx.AsyncClient() as client:
                    headers = {"Authorization": f"Bearer {tokenGomedisys}"}
                    response = await client.post(URL, json=create_body, headers=headers)
                    #print("response.json(): ", response.json())
                    response.raise_for_status()
                    respuestasServicio.append(
                        {"Estado": "Éxito", "Paciente": paciente_data, "Respuesta": response.json()}
                    )

            except httpx.RequestError as e:
                respuestasServicio.append(
                    {"Estado": "Error en la solicitud HTTP", "Paciente": paciente_data, "Error": str(e)}
                )

            except httpx.HTTPError as e:
                respuestasServicio.append(
                    {"Estado": "Error en la respuesta HTTP", "Paciente": paciente_data, "Error": str(e)}
                )

            except ValueError as e:
                respuestasServicio.append(
                    {"Estado": "Error al analizar JSON", "Paciente": paciente_data, "Error": str(e)}
                )
        else:
            patientsFound.append(paciente_data)
            #print("Saltar a otro usuario")
            continue

    return JSONResponse(content={"Respuestas Carga Masiva": respuestasServicio, "Pacientes no creados porque se encontraron en la base de datos": patientsFound})
    """
