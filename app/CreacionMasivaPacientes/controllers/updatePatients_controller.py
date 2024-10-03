# -*- coding: utf-8 -*-
"""
Creado el 2 de Octubre de 2024
Autor: Sebastian Suarez
"""

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

# Controller
async def update_patient_gomedisys():
    URL_BASE_GOMEDISYS = config("URL_BASE_GOMEDISYS")

    # Función para obtener un nuevo token
    async def obtener_nuevo_token():
        return await getTokenGomedisys_service.get_token_gomedisys()

    # Inicializamos el token
    tokenGomedisys = await obtener_nuevo_token()

    if not tokenGomedisys:
        raise HTTPException(status_code=500, detail="No se pudo obtener el token de Gomedisys.")

    patientsUpdate = []
    patientsNotUpdate = []
    infoExcel = await obtener_datos_excel()

    for item in tqdm(
        infoExcel,
        desc=Fore.BLUE + "Actualizando pacientes",
        colour="#39FF14",
        smoothing=0.05,
        bar_format="{l_bar}{bar}{r_bar}",
        dynamic_ncols=True,
        ascii=False,
    ):
        paciente_data = item["InfoPaciente"]
        validar_Paciente = await validate_patients(paciente_data["TIPODOCUMENTO"], str(paciente_data["DOCUMENTO"]))
        print("validacionPaciente:", validar_Paciente, "informacionPaciente:", paciente_data )
        # Si el paciente se encuentra en la base de datos, procedemos a actualizarlo
        #if validar_Paciente != "{\"CodError\":400,\"DescError\":\"Paciente no encontrado\"}":
        update_body = await create_body_request(paciente_data)  # Aquí usas la misma función para el body de actualización
        print("bodyPaciente:",update_body )

        try:
            URL = f"{URL_BASE_GOMEDISYS}/Appointment/CreatePatient"  # Endpoint para actualizar pacientes
            print(URL)
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {tokenGomedisys}"}
                response = await client.post(URL, json=update_body, headers=headers)
                print(response )

                # Si el token está vencido (401 Unauthorized), lo renovamos y volvemos a intentar
                if response.status_code == 401:
                    tokenGomedisys = await obtener_nuevo_token()  # Obtener nuevo token
                    headers = {"Authorization": f"Bearer {tokenGomedisys}"}
                    response = await client.post(URL, json=update_body, headers=headers)  # Reintentar la solicitud

                patientsUpdate.append(
                    {"Estado": "Éxito", "Paciente": paciente_data, "Respuesta": response.json()}
                )

            # Guardar las respuestas en archivo JSON
            Actualizados_json = "Actualizados_pacientes.json"
            with open(Actualizados_json, "w", encoding="utf-8") as archivo:
                json.dump(patientsUpdate, archivo, ensure_ascii=False, indent=4)

        except httpx.RequestError as e:
            patientsUpdate.append(
                {"Estado": "Error en la solicitud HTTP", "Paciente": paciente_data, "Error": str(e)}
            )

        except httpx.HTTPError as e:
            patientsUpdate.append(
                {"Estado": "Error en la respuesta HTTP", "Paciente": paciente_data, "Error": str(e)}
            )

        except ValueError as e:
            patientsUpdate.append(
                {"Estado": "Error al analizar JSON", "Paciente": paciente_data, "Error": str(e)}
            )
    #else:
        patientsNotUpdate.append(paciente_data)

        # Guardar los pacientes no encontrados en archivo JSON
        NoEncontrados_json = "NoEncontrados_pacientes.json"
        with open(NoEncontrados_json, "w", encoding="utf-8") as archivo:
            json.dump(patientsNotUpdate, archivo, ensure_ascii=False, indent=4)
        continue

    # Guardar los resultados en un archivo JSON
    resultado = {
        "Pacientes actualizados": patientsUpdate,
        "Pacientes no encontrados para actualizar": patientsNotUpdate
    }

    # Definir la ruta del archivo
    archivo_json = "resultados_actualizacion_pacientes.json"

    # Guardar en archivo JSON
    with open(archivo_json, "w", encoding="utf-8") as archivo:
        json.dump(resultado, archivo, ensure_ascii=False, indent=4)

    return "Pacientes Actualizados", len(patientsUpdate), "Pacientes no encontrados", len(patientsNotUpdate)
