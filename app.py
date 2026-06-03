# Autoras: Paola Camacho y Andrea Correa
from flask import Flask, render_template, redirect, url_for
from config import Config
from models import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

