# -*- coding: utf-8 -*-
"""
Created on Mon Apr 18 2024
@author: Sebastian Suarez
"""

# Imports
import json
import unicodedata

# Function
def leer_json(ruta_archivo):
    with open(ruta_archivo, 'r') as archivo:
        datos = json.load(archivo)
    return datos

def normalize_string(s):
    if s is None:
        return None
    s = s.upper()
    s = " ".join(s.split())  # Eliminar espacios duplicados
    s = "".join(
        (c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    )
    return s