# -*- coding: utf-8 -*-
'''
Created on Thursday Aug 15 2024
@author: Sebastian Suarez
'''

# Import libraries
from pydantic import BaseModel


# Classes
class loginModel(BaseModel):
    tipo_documento : str
    numero_documento = str