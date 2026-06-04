# Tablas principales - sin FK

from flask import Blueprint, render_template, redirect, url_for
from models import TABLA_MODELOS

principales_bp = Blueprint("principales", __name__)

PRINCIPALES = [
    "TIPOS_DOCUMENTOS",
    "ESPECIALIDADES",
    "ESTADOS_CITAS",
    "TIPOS_CITAS",
    "CONSULTORIOS",
    "ACUDIENTES",
    "DIAGNOSTICOS",
    "PRESENTACIONES_MEDICAMENTOS",
    "TIPOS_TERAPIAS",
    "DIAS_SEMANAS",
]

@principales_bp.route("/")
def index():
    return render_template("principales/index.html",
                           catalogos=PRINCIPALES)

@principales_bp.route("/<nombre>")
def ver(nombre):
    # vista genérica de tablas
    return redirect(url_for("tablas.listar", nombre_tabla=nombre.upper()))