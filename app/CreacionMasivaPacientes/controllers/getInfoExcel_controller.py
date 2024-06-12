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

    ruta_archivo_creacion = config("RUTA_ARCHIVO_CREACION_PACIENTES")

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
