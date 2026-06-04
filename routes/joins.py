# JOINS - Funciones de grupo

from flask import Blueprint, render_template, request, jsonify
from sqlalchemy import text
from models import db

joins_bp = Blueprint("joins", __name__)

# Joins predefinidos

JOINS_CATALOG = [
    # INNER JOIN
    {
        "id":          "citas_completo",
        "tipo":        "INNER JOIN",
        "titulo":      "Citas — Paciente + Profesional + Consultorio",
        "descripcion": "Muestra todas las citas con el nombre del paciente, "
                       "el profesional, el consultorio y el estado.",
        "venn":        "inner",
        "sql": """SELECT
        C.id_cita,
        P.nombre_paciente,
        PR.nombre_profesional,
        CO.nombre_consultorio,
        TC.nombre_tipo_cita,
        EC.descripcion_estado_cita,
        C.fecha_cita,
        C.motivo_cita
        FROM CITAS C
        INNER JOIN PACIENTES P ON C.id_paciente = P.id_paciente
        INNER JOIN PROFESIONALES PR ON C.id_profesional = PR.id_profesional
        INNER JOIN CONSULTORIOS CO ON C.id_consultorio = CO.id_consultorio
        INNER JOIN TIPOS_CITAS TC ON C.id_tipo_cita = TC.id_tipo_cita
        INNER JOIN ESTADOS_CITAS EC ON C.id_estado_cita = EC.id_estado_cita
        ORDER BY C.fecha_cita DESC""",
    },
    {
        "id":          "historias_paciente",
        "tipo":        "INNER JOIN",
        "titulo":      "Historias Clínicas con Diagnósticos",
        "descripcion": "Lista las historias clínicas con los diagnósticos asociados.",
        "venn":        "inner",
        "sql": """SELECT
        HC.id_historia_clinica,
        P.nombre_paciente,
        HC.fecha_registro,
        D.nombre_diagnostico
        FROM HISTORIAS_CLINICAS HC
        INNER JOIN PACIENTES P ON HC.id_paciente = P.id_paciente
        INNER JOIN DIAGNOSTICOS_HISTORIAS DH ON HC.id_historia_clinica = DH.id_historia_clinica
        INNER JOIN DIAGNOSTICOS D ON DH.id_diagnostico = D.id_diagnostico
        ORDER BY HC.fecha_registro DESC""",
    },
    {
        "id":          "formulas_detalles",
        "tipo":        "INNER JOIN",
        "titulo":      "Fórmulas Médicas con Tratamientos",
        "descripcion": "Detalle de fórmulas: profesional, paciente y tratamiento prescrito.",
        "venn":        "inner",
        "sql": """SELECT
        FM.id_formula_medica,
        PR.nombre_profesional,
        P.nombre_paciente,
        T.nombre_tratamiento,
        T.tipo_tratamiento,
        DF.dosis_formula,
        DF.frecuencia_tratamiento_formula,
        DF.duracion_formula,
        FM.fecha_formula
        FROM FORMULAS_MEDICAS FM
        INNER JOIN HISTORIAS_CLINICAS HC ON FM.id_historia_clinica = HC.id_historia_clinica
        INNER JOIN PACIENTES P ON HC.id_paciente  = P.id_paciente
        INNER JOIN PROFESIONALES PR ON FM.id_profesional = PR.id_profesional
        INNER JOIN DETALLES_FORMULAS DF ON FM.id_formula_medica = DF.id_formula_medica
        INNER JOIN TRATAMIENTOS T ON DF.id_tratamiento = T.id_tratamiento
        ORDER BY FM.fecha_formula DESC""",
    },
    {
        "id":          "profesionales_especialidades",
        "tipo":        "INNER JOIN",
        "titulo":      "Profesionales con Especialidades",
        "descripcion": "Profesionales y sus especialidades registradas.",
        "venn":        "inner",
        "sql": """SELECT
        PR.nombre_profesional,
        PR.num_tarjeta_profesional,
        E.nombre_especialidad,
        E.descripcion_especialidad
        FROM PROFESIONALES PR
        INNER JOIN ESPECIALIDADES_PROFESIONALES EP ON PR.id_profesional = EP.id_profesional
        INNER JOIN ESPECIALIDADES E ON EP.id_especialidad = E.id_especialidad
        ORDER BY PR.nombre_profesional""",
    },
    {
        "id":          "pacientes_acudientes",
        "tipo":        "INNER JOIN",
        "titulo":      "Pacientes con Acudientes",
        "descripcion": "Muestra la relación paciente–acudiente con parentesco.",
        "venn":        "inner",
        "sql": """SELECT
        P.nombre_paciente,
        A.nombre_acudiente,
        A.parentesco_acudiente,
        A.celular_acudiente,
        PA.fecha_firma
        FROM PACIENTES_ACUDIENTES PA
        INNER JOIN PACIENTES P ON PA.id_paciente = P.id_paciente
        INNER JOIN ACUDIENTES A ON PA.id_acudiente = A.id_acudiente
        ORDER BY P.nombre_paciente""",
    },
    # LEFT JOIN
    {
        "id":          "pacientes_sin_citas",
        "tipo":        "LEFT JOIN",
        "titulo":      "Pacientes SIN citas",
        "descripcion": "Pacientes que nunca han tenido una cita registrada.",
        "venn":        "left_only",
        "sql": """SELECT
        P.id_paciente,
        P.nombre_paciente,
        P.num_documento_paciente,
        P.telefono_principal_paciente
        FROM PACIENTES P
        LEFT JOIN CITAS C ON P.id_paciente = C.id_paciente
        WHERE C.id_paciente IS NULL
        ORDER BY P.nombre_paciente""",
    },
    {
        "id":          "pacientes_todas_citas",
        "tipo":        "LEFT JOIN",
        "titulo":      "Todos los pacientes con sus citas",
        "descripcion": "Todos los pacientes, tengan o no cita registrada.",
        "venn":        "left",
        "sql": """SELECT
        P.nombre_paciente,
        C.id_cita,
        C.fecha_cita,
        C.motivo_cita
        FROM PACIENTES P
        LEFT JOIN CITAS C ON P.id_paciente = C.id_paciente
        ORDER BY P.nombre_paciente""",
    },
    {
        "id":          "prof_sin_horario",
        "tipo":        "LEFT JOIN",
        "titulo":      "Profesionales SIN horario asignado",
        "descripcion": "Profesionales que aún no tienen horario registrado.",
        "venn":        "left_only",
        "sql": """SELECT
        PR.id_profesional,
        PR.nombre_profesional,
        PR.telefono_profesional
        FROM PROFESIONALES PR
        LEFT JOIN HORARIOS H ON PR.id_profesional = H.id_profesional
        WHERE H.id_profesional IS NULL
        ORDER BY PR.nombre_profesional""",
    },
    # GROUP BY / Funciones de Grupo
    {
        "id":          "citas_por_profesional",
        "tipo":        "GROUP BY",
        "titulo":      "Citas por Profesional (COUNT + ORDER BY)",
        "descripcion": "Cuántas citas tiene cada profesional, de mayor a menor.",
        "venn":        "group",
        "sql": """SELECT
        PR.nombre_profesional,
        COUNT(*) AS total_citas,
        MIN(C.fecha_cita) AS primera_cita,
        MAX(C.fecha_cita) AS ultima_cita
        FROM CITAS C
        INNER JOIN PROFESIONALES PR ON C.id_profesional = PR.id_profesional
        GROUP BY PR.nombre_profesional
        ORDER BY total_citas DESC""",
    },
    {
        "id":          "citas_por_estado",
        "tipo":        "GROUP BY",
        "titulo":      "Citas por Estado",
        "descripcion": "Distribución de citas según su estado (programada, cancelada, etc.).",
        "venn":        "group",
        "sql": """SELECT
        EC.descripcion_estado_cita,
        COUNT(*) AS total
        FROM CITAS C
        INNER JOIN ESTADOS_CITAS EC ON C.id_estado_cita = EC.id_estado_cita
        GROUP BY EC.descripcion_estado_cita
        ORDER BY total DESC""",
    },
    {
        "id":          "pacientes_por_tipdoc",
        "tipo":        "GROUP BY",
        "titulo":      "Pacientes por Tipo de Documento",
        "descripcion": "Cuántos pacientes hay por cada tipo de documento de identidad.",
        "venn":        "group",
        "sql": """SELECT
        TD.nombre_tipo_documento,
        COUNT(*) AS total_pacientes
        FROM PACIENTES P
        INNER JOIN TIPOS_DOCUMENTOS TD ON P.id_tipo_documento = TD.id_tipo_documento
        GROUP BY TD.nombre_tipo_documento
        ORDER BY total_pacientes DESC""",
    },
    {
        "id":          "diagnosticos_frecuentes",
        "tipo":        "GROUP BY",
        "titulo":      "Diagnósticos más frecuentes",
        "descripcion": "Los diagnósticos que más veces han aparecido en historias clínicas.",
        "venn":        "group",
        "sql": """SELECT
        D.nombre_diagnostico,
        COUNT(*) AS frecuencia
        FROM DIAGNOSTICOS_HISTORIAS DH
        INNER JOIN DIAGNOSTICOS D ON DH.id_diagnostico = D.id_diagnostico
        GROUP BY D.nombre_diagnostico
        ORDER BY frecuencia DESC""",
    },
    {
        "id":          "remisiones_por_profesional",
        "tipo":        "GROUP BY",
        "titulo":      "Remisiones por Profesional",
        "descripcion": "Cuántas remisiones ha generado cada profesional.",
        "venn":        "group",
        "sql": """SELECT
        PR.nombre_profesional,
        COUNT(*) AS total_remisiones
        FROM REMISIONES R
        INNER JOIN PROFESIONALES PR ON R.id_profesional = PR.id_profesional
        GROUP BY PR.nombre_profesional
        ORDER BY total_remisiones DESC""",
    },
]

@joins_bp.route("/")
def lista():
    tipo_filtro = request.args.get("tipo", "")
    joins = JOINS_CATALOG
    if tipo_filtro:
        joins = [j for j in joins if j["tipo"] == tipo_filtro]
    tipos = sorted(set(j["tipo"] for j in JOINS_CATALOG))
    return render_template("joins/resultados.html",
                           joins=joins,
                           tipos=tipos,
                           tipo_filtro=tipo_filtro,
                           todos_los_joins=JOINS_CATALOG)

@joins_bp.route("/ejecutar/<join_id>", methods=["POST"])
def ejecutar_join(join_id):
    join_def = next((j for j in JOINS_CATALOG if j["id"] == join_id), None)
    if not join_def:
        return jsonify({"error": "JOIN no encontrado."}), 404
    
    try:
        with db.engine.connect() as conn:
            resultado = conn.execute(text(join_def["sql"]))
            columnas  = list(resultado.keys())
            filas     = [
                [str(v) if v is not None else "" for v in row]
                for row in resultado.fetchall()
            ]
        return jsonify({
            "titulo":   join_def["titulo"],
            "columnas": columnas,
            "filas":    filas,
            "total":    len(filas),
        })
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400