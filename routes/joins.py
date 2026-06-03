# JOINS - Funciones de grupo

from flask import Blueprint, render_template, request, jsonify
from sqlalchemy import text
from models import db

joins_bp = Blueprint("joins", __name__)