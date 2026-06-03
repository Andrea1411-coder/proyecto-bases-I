# Tablas principales - sin FK

from flask import Blueprint, render_template, redirect, url_for
from models import TABLA_MODELOS

principales_bp = Blueprint("principales", __name__)