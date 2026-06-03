# Consola SQL interactiva

from flask import Blueprint, render_template, request,jsonify
from sqlalchemy import text
from models import db

sql_bp = Blueprint('sql', __name__)

CONSULTAS_PREDEFINIDAS = [
    {
        "grupo": "CRUD - Pacientes",
        "items": [
            {"nombre": "SELECT todos los pacientes",
             "sql": "SELECT * FROM PACIENTES"},
            {"nombre": "SELECT paciente por ID",
             "sql": "SELECT * FROM PACIENTES WHERE id_paciente = :id"},
            {"nombre": "INSERT nuevo paciente",
             "sql": """INSERT INTO PACIENTES (
             id_paciente, id_tipo_documento, nombre_paciente, num_documento_paciente,
             telefono_principal_paciente) VALUES (999, 1, 'Juan Perez', '123456789', '3001234567')"""},
            {"nombre": "UPDATE nombre paciente",
              "sql": "UPDATE PACIENTES SET nombre_paciente = 'Nuevo Nombre' WHERE id_paciente = 999"},
            {"nombre": "DELETE paciente",
             "sql": "DELETE FROM PACIENTES WHERE id_paciente = 999" },
        ]   
    },
    {
        "grupo": "CRUD - Profesionales",
        "items": [
            

        ]
    }



]