# -*- coding: utf-8 -*-
"""
Created on Thursday May 16 2024
@author: Sebastian Suarez
"""
"""DESCOMENTAR PARA HACER LA PRUEBA UNITARIA
from fastapi import FastAPI, APIRouter
from app.CreacionMasivaPacientes.controllers.validatePatients_controller import (
    validate_patients
)


router = APIRouter(prefix="/CreacionPacientes")


@router.post("/validarPaciente")
async def get_patient_info_route():
    tipo_documento = "CC"
    numero_documento = "3226469"
    json_data = await validate_patients(tipo_documento=tipo_documento, numero_documento=numero_documento)

    if json_data:
        return json_data
    else:
        return {"error": "No se pudo obtener la informacion del Paciente en Gomedisys."}"""


from fastapi import APIRouter
from tqdm import tqdm
from colorama import Fore
from app.CreacionMasivaPacientes.controllers.validatePatients_controller import (
    validate_patients
)
from app.CreacionMasivaPacientes.controllers.getInfoExcel_controller import obtener_datos_excel


router = APIRouter(prefix="/CreacionPacientes")

@router.post("/validarPaciente")
async def get_patient_info_route():
    respuestasServicio = []  # Lista para almacenar respuestas de cada paciente
    patientsFound = []  # Lista para almacenar pacientes encontrados
    patientsNotFound = []  # Lista para almacenar pacientes no encontrados

    # Obtener datos del Excel
    infoExcel = await obtener_datos_excel()

    # Procesar cada paciente en el archivo Excel
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

        # Validar el paciente usando la función validate_patients
        validar_Paciente = await validate_patients(
            tipo_documento=paciente_data["TIPODOCUMENTO"],
            numero_documento=str(paciente_data["DOCUMENTO"])
        )

        # Verificar si el paciente no fue encontrado (comparar con el mensaje de error esperado)
        if validar_Paciente == "{\"CodError\":400,\"DescError\":\"Paciente no encontrado\"}":
            patientsNotFound.append({
                "tipo_documento": paciente_data["TIPODOCUMENTO"],
                "numero_documento": paciente_data["DOCUMENTO"],
                "error": validar_Paciente
            })
        else:
            # Si la validación fue exitosa, añadir a la lista de pacientes encontrados
            patientsFound.append(validar_Paciente)

        # Agregar todas las respuestas a la lista general (opcional)
        respuestasServicio.append(validar_Paciente)

    # Devolver la información de los pacientes encontrados y no encontrados
    return {
        "patients_found": patientsFound if patientsFound else "No se encontraron pacientes.",
        "patients_not_found": patientsNotFound if patientsNotFound else "Todos los pacientes fueron encontrados."
    }
