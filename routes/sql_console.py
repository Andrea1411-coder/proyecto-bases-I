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
            {"nombre": "SELECT todos los profesionales",
             "sql": "SELECT * FROM PROFESIONALES"},
            {"nombre": "INSERT profesional",
             "sql": """INSERT INTO PROFESIONALES (
            id_profesional, nombre_profesional, num_documento_profesional,
            num_tarjeta_profesional, telefono_profesional
            ) VALUES (
                999, 'Dra. Laura García', '98765432', 'TP-001', '3109876543'
            )"""},
        ]
    },
    {
        "grupo": "CRUD — Citas",
        "items": [
            {"nombre": "SELECT todas las citas",
             "sql": "SELECT * FROM CITAS"},
            {"nombre": "SELECT citas de hoy",
             "sql": "SELECT * FROM CITAS WHERE fecha_cita = TRUNC(SYSDATE)"},
        ]
    },
    {
        "grupo": "INNER JOIN",
        "items": [
            {"nombre": "Citas con paciente y profesional",
             "sql": """SELECT P.nombre_paciente, PR.nombre_profesional,
            C.fecha_cita, C.motivo_cita
            FROM CITAS C
            INNER JOIN PACIENTES P    ON C.id_paciente   = P.id_paciente
            INNER JOIN PROFESIONALES PR ON C.id_profesional = PR.id_profesional"""},
                        {"nombre": "Paciente + tipo de documento",
                        "sql": """SELECT P.nombre_paciente, P.num_documento_paciente,
                TD.nombre_tipo_documento
            FROM PACIENTES P
            INNER JOIN TIPOS_DOCUMENTOS TD ON P.id_tipo_documento = TD.id_tipo_documento"""},
                        {"nombre": "Historias clínicas con paciente",
                        "sql": """SELECT HC.id_historia_clinica, P.nombre_paciente,
                HC.fecha_registro, HC.observaciones
            FROM HISTORIAS_CLINICAS HC
            INNER JOIN PACIENTES P ON HC.id_paciente = P.id_paciente"""},
                        {"nombre": "Fórmulas con profesional e historia",
                        "sql": """SELECT FM.id_formula_medica, PR.nombre_profesional,
                FM.fecha_formula, FM.indicacion_formula
            FROM FORMULAS_MEDICAS FM
            INNER JOIN PROFESIONALES PR ON FM.id_profesional = PR.id_profesional
            INNER JOIN HISTORIAS_CLINICAS HC ON FM.id_historia_clinica = HC.id_historia_clinica"""},
                        {"nombre": "Tratamiento + terapia + medicamento",
                        "sql": """SELECT T.nombre_tratamiento, T.tipo_tratamiento,
                TT.nombre_tipo_terapia, PM.nombre_presentacion_medicamento
            FROM TRATAMIENTOS T
            INNER JOIN TIPOS_TERAPIAS TT ON T.id_tipo_terapia = TT.id_tipo_terapia
            INNER JOIN PRESENTACIONES_MEDICAMENTOS PM
                ON T.id_presentacion_medicamento = PM.id_presentacion_medicamento"""},
        ]
    },
    {
        "grupo": "LEFT JOIN",
        "items": [
            {"nombre": "Pacientes con o sin citas",
             "sql": """SELECT P.nombre_paciente, C.fecha_cita, C.motivo_cita
                FROM PACIENTES P
                LEFT JOIN CITAS C ON P.id_paciente = C.id_paciente"""},
                            {"nombre": "Pacientes SIN citas registradas",
                            "sql": """SELECT P.nombre_paciente, P.num_documento_paciente
                FROM PACIENTES P
                LEFT JOIN CITAS C ON P.id_paciente = C.id_paciente
                WHERE C.id_paciente IS NULL"""},
                            {"nombre": "Profesionales con o sin especialidad",
                            "sql": """SELECT PR.nombre_profesional, E.nombre_especialidad
                FROM PROFESIONALES PR
                LEFT JOIN ESPECIALIDADES_PROFESIONALES EP ON PR.id_profesional = EP.id_profesional
                LEFT JOIN ESPECIALIDADES E ON EP.id_especialidad = E.id_especialidad"""},
            ]
    },
    {
        "grupo": "GROUP BY / Funciones de Grupo",
        "items": [
                {"nombre": "Citas por profesional (ORDER BY total DESC)",
                "sql": """SELECT PR.nombre_profesional,
                COUNT(*) AS total_citas
                FROM CITAS C
                INNER JOIN PROFESIONALES PR ON C.id_profesional = PR.id_profesional
                GROUP BY PR.nombre_profesional
                ORDER BY total_citas DESC"""},
                            {"nombre": "Citas por estado",
                            "sql": """SELECT EC.descripcion_estado_cita,
                    COUNT(*) AS total
                FROM CITAS C
                INNER JOIN ESTADOS_CITAS EC ON C.id_estado_cita = EC.id_estado_cita
                GROUP BY EC.descripcion_estado_cita
                ORDER BY total DESC"""},
                            {"nombre": "Pacientes por tipo de documento",
                            "sql": """SELECT TD.nombre_tipo_documento,
                    COUNT(*) AS total_pacientes
                FROM PACIENTES P
                INNER JOIN TIPOS_DOCUMENTOS TD ON P.id_tipo_documento = TD.id_tipo_documento
                GROUP BY TD.nombre_tipo_documento
                ORDER BY total_pacientes DESC"""},
                            {"nombre": "MIN / MAX fecha de citas",
                            "sql": """SELECT PR.nombre_profesional,
                    MIN(C.fecha_cita) AS primera_cita,
                    MAX(C.fecha_cita) AS ultima_cita,
                    COUNT(*)          AS total_citas
                FROM CITAS C
                INNER JOIN PROFESIONALES PR ON C.id_profesional = PR.id_profesional
                GROUP BY PR.nombre_profesional"""},
                            {"nombre": "Diagnósticos más frecuentes",
                            "sql": """SELECT D.nombre_diagnostico,
                    COUNT(*) AS frecuencia
                FROM DIAGNOSTICOS_HISTORIAS DH
                INNER JOIN DIAGNOSTICOS D ON DH.id_diagnostico = D.id_diagnostico
                GROUP BY D.nombre_diagnostico
                ORDER BY frecuencia DESC"""},
            ]   
    },
    {
        "grupo": "Verificación de esquema",
        "items": [
            {"nombre": "Ver todas las tablas del usuario",
             "sql": "SELECT * FROM TAB"},
            {"nombre": "Ver PRIMARY KEYs",
             "sql": "SELECT CONSTRAINT_NAME, TABLE_NAME FROM USER_CONSTRAINTS WHERE CONSTRAINT_TYPE = 'P' ORDER BY TABLE_NAME"},
            {"nombre": "Ver FOREIGN KEYs",
             "sql": "SELECT CONSTRAINT_NAME, TABLE_NAME FROM USER_CONSTRAINTS WHERE CONSTRAINT_TYPE = 'R' ORDER BY TABLE_NAME"},
            {"nombre": "Ver CHECK constraints",
             "sql": "SELECT CONSTRAINT_NAME, TABLE_NAME, SEARCH_CONDITION FROM USER_CONSTRAINTS WHERE CONSTRAINT_TYPE = 'C' ORDER BY TABLE_NAME"},
            {"nombre": "Columnas de una tabla",
             "sql": "SELECT COLUMN_NAME, DATA_TYPE, DATA_LENGTH, NULLABLE FROM USER_TAB_COLUMNS WHERE TABLE_NAME = 'PACIENTES' ORDER BY COLUMN_ID"},
        ]
    },

]

@sql_bp.route("/", methods=["GET"])
def consola():
    return render_template("sql/consola.html",
                           consultas=CONSULTAS_PREDEFINIDAS)


@sql_bp.route("/ejecutar", methods=["POST"])
def ejecutar():
    sql_raw = (request.json or {}).get("sql", "").strip()
    if not sql_raw:
        return jsonify({"error": "La consulta está vacía."}), 400

    # Detectar tipo de sentencia
    primera_palabra = sql_raw.upper().split()[0] if sql_raw.split() else ""
    es_select = primera_palabra in ("SELECT", "WITH", "SHOW")

    try:
        with db.engine.connect() as conn:
            resultado = conn.execute(text(sql_raw))

            if es_select:
                columnas = list(resultado.keys())
                filas = [
                    [str(v) if v is not None else "" for v in row]
                    for row in resultado.fetchall()
                ]
                return jsonify({
                    "tipo": "select",
                    "columnas": columnas,
                    "filas": filas,
                    "total": len(filas),
                })
            else:
                conn.commit()
                return jsonify({
                    "tipo": "dml",
                    "mensaje": f"Sentencia ejecutada correctamente. "
                               f"Filas afectadas: {resultado.rowcount}",
                    "filas_afectadas": resultado.rowcount,
                })
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400