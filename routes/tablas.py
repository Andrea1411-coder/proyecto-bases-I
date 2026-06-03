# Vista de tabla con los CRUD de las 22 tablas

from flask import (Blueprint, render_template, request, redirect, url_for, flash, jsonify)
from sqlalchemy import text, inspect
from models import db, TABLA_MODELOS
from config import Config

tablas_bp = Blueprint("tablas", __name__)