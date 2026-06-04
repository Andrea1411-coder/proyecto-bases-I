# Vista de tabla con los CRUD de las 22 tablas

from flask import (Blueprint, render_template, request, redirect, url_for, flash, jsonify)
from sqlalchemy import text, inspect
from models import db, TABLA_MODELOS
from config import Config
from datetime import date, datetime

tablas_bp = Blueprint("tablas", __name__)

def columnas_tabla(nombre_tabla: str) -> list[dict]:
    """Retorna datos de columnas de una tabla Oracle vía USER_TAB_COLUMNS."""
    sql = text("""
        SELECT COLUMN_NAME, DATA_TYPE, DATA_LENGTH, NULLABLE, COLUMN_ID
        FROM USER_TAB_COLUMNS
        WHERE TABLE_NAME = :t
        ORDER BY COLUMN_ID
    """)
    with db.engine.connect() as conn:
        rows = conn.execute(sql, {"t": nombre_tabla.upper()}).fetchall()
    return [
        {
            "name":     r[0],
            "type":     r[1],
            "length":   r[2],
            "nullable": r[3] == "Y",
        }
        for r in rows
    ]

def pk_tabla(nombre_tabla: str) -> list[str]:
    """Retorna los nombres de columnas PK de la tabla."""
    sql = text("""
        SELECT cc.COLUMN_NAME
        FROM USER_CONSTRAINTS c
        JOIN USER_CONS_COLUMNS cc
          ON c.CONSTRAINT_NAME = cc.CONSTRAINT_NAME
        WHERE c.TABLE_NAME      = :t
          AND c.CONSTRAINT_TYPE = 'P'
        ORDER BY cc.POSITION
    """)
    with db.engine.connect() as conn:
        rows = conn.execute(sql, {"t": nombre_tabla.upper()}).fetchall()
    return [r[0] for r in rows]


def formatear_valor(val, col_type):
    """Convierte valores de tablas a formato adecuado para mostrarlos.
       DATE     → DD-MM-YYYY
       TIMESTAMP → HH:MM:SS
       resto    → str normal
    """
    if val is None:
        return ""
 
    if col_type == "DATE":
        if isinstance(val, (date, datetime)):
            return val.strftime("%d-%m-%Y")
        s = str(val)[:10]                     
        partes = s.split("-")
        if len(partes) == 3:
            return f"{partes[2]}-{partes[1]}-{partes[0]}"
        return s
 
    if "TIMESTAMP" in col_type:
        if isinstance(val, datetime):
            return val.strftime("%H:%M:%S")
        s = str(val)
        if " " in s:
            return s.split(" ")[1][:8]
        return s[:8]
 
    return str(val)

def expr_valor(col_name: str, col_type: str, valor) -> str:
    """Convierte valores de tablas a formato adecuado para mostrarlos.
       DATE      → TO_DATE(:col, 'DD-MM-YYYY')
       TIMESTAMP → TO_TIMESTAMP(:col, 'HH24:MI:SS')
       resto     → :col
    """
    if valor is None:
        return f":{col_name}"
    if col_type == "DATE":
        return f"TO_DATE(:{col_name}, 'DD-MM-YYYY')"
    if "TIMESTAMP" in col_type:
        return f"TO_TIMESTAMP(:{col_name}, 'HH24:MI:SS')"
    return f":{col_name}"

@tablas_bp.route("/<nombre_tabla>")
def listar(nombre_tabla):
    nombre_tabla = nombre_tabla.upper()
    if nombre_tabla not in TABLA_MODELOS:
        flash(f"Tabla '{nombre_tabla}' no encontrada.", "danger")
        return redirect(url_for("index"))

    page      = request.args.get("page",   1,  type=int)
    filtro    = request.args.get("filtro", "",  type=str).strip()
    per_page  = Config.ROWS_PER_PAGE

    columnas  = columnas_tabla(nombre_tabla)
    pks       = pk_tabla(nombre_tabla)
    col_names = [c["name"] for c in columnas]
    col_types = {c["name"]: c["type"] for c in columnas}

    # Construir SELECT con WHERE
    where_clause = f" WHERE {filtro}" if filtro else ""
 
    count_sql = text(f"SELECT COUNT(*) FROM {nombre_tabla}{where_clause}")
    data_sql  = text(
        f"SELECT * FROM (SELECT a.*, ROWNUM rn FROM "
        f"(SELECT * FROM {nombre_tabla}{where_clause}) a "
        f"WHERE ROWNUM <= :fin) WHERE rn > :ini"
    )

    error = None
    filas = []
    total = 0

    try:
        with db.engine.connect() as conn:
            total = conn.execute(count_sql).scalar() or 0
            inicio = (page - 1) * per_page
            fin    = inicio + per_page
            rows   = conn.execute(data_sql, {"ini": inicio, "fin": fin}).fetchall()
            filas = [
                [
                    formatear_valor(row[i], col_types.get(col_names[i], ""))
                    for i in range(len(col_names))
                ]
                for row in rows
            ]
    except Exception as exc:
        error = str(exc)

    total_pages = max(1, (total + per_page - 1) // per_page)

    return render_template(
        "tablas/lista.html",
        nombre_tabla = nombre_tabla,
        tablas       = sorted(TABLA_MODELOS.keys()),
        columnas     = col_names,
        col_types    = col_types,
        filas        = filas,
        pks          = pks,
        page         = page,
        total_pages  = total_pages,
        total        = total,
        filtro       = filtro,
        error        = error,
    )

# Formulario INSERT / UPDATE

@tablas_bp.route("/<nombre_tabla>/nuevo", methods=["GET", "POST"])
def insertar(nombre_tabla):
    nombre_tabla = nombre_tabla.upper()
    columnas = columnas_tabla(nombre_tabla)
    pks      = pk_tabla(nombre_tabla)

    if request.method == "POST":
        valores = {}
        for col in columnas:
            val = request.form.get(col["name"], "").strip()
            if val == "":
                valores[col["name"]] = None
            else:
                valores[col["name"]] = val

        col_tipo_map = {c["name"]: c["type"] for c in columnas}
        cols_str = ", ".join(valores.keys())
        vals_str = ", ".join(
            expr_valor(k, col_tipo_map.get(k, ""), v)
            for k, v in valores.items()
        )
        sql = text(f"INSERT INTO {nombre_tabla} ({cols_str}) VALUES ({vals_str})")

        try:
            with db.engine.connect() as conn:
                conn.execute(sql, valores)
                conn.commit()
                flash("Registro insertado correctamente.", "success")
                return redirect(url_for("tablas.listar", nombre_tabla=nombre_tabla))
        except Exception as exc:
            flash(f"Error al insertar: {exc}", "danger")

    return render_template(
        "tablas/formulario.html",
        nombre_tabla = nombre_tabla,
        tablas       = sorted(TABLA_MODELOS.keys()),
        columnas     = columnas,
        pks          = pks,
        modo         = "INSERT",
        valores      = {},
    )

@tablas_bp.route("/<nombre_tabla>/editar", methods=["GET", "POST"])
def editar(nombre_tabla):
    nombre_tabla = nombre_tabla.upper()
    columnas = columnas_tabla(nombre_tabla)
    pks      = pk_tabla(nombre_tabla)

    # Construir WHERE por PKs
    pk_valores = {pk: request.args.get(pk) or request.form.get(pk) for pk in pks}
    where_clause = " AND ".join([f"{pk} = :{pk}" for pk in pks])

    if request.method == "POST":
        valores = {}
        for col in columnas:
            val = request.form.get(col["name"], "").strip()
            valores[col["name"]] = None if val == "" else val

        col_tipo_map = {c["name"]: c["type"] for c in columnas}
        set_clause = ", ".join([
            f"{c['name']} = {expr_valor(c['name'], col_tipo_map.get(c['name'],''), valores.get(c['name']))}"
            for c in columnas if c["name"] not in pks
        ])
        sql = text(f"UPDATE {nombre_tabla} SET {set_clause} WHERE {where_clause}")
        params = {**valores, **pk_valores}

        try:
            with db.engine.connect() as conn:
                conn.execute(sql, params)
                conn.commit()
                flash("Registro actualizado correctamente.", "success")
                return redirect(url_for("tablas.listar", nombre_tabla=nombre_tabla))
        except Exception as exc:
            flash(f"Error al actualizar: {exc}", "danger")

    # Cargar valores actuales
    sel_sql = text(f"SELECT * FROM {nombre_tabla} WHERE {where_clause}")
    valores_actuales = {}
    try:
        with db.engine.connect() as conn:
            row = conn.execute(sel_sql, pk_valores).fetchone()
            if row:
                for i, col in enumerate(columnas):
                    val = row[i]
                    if val is None:
                        valores_actuales[col["name"]] = ""
                    elif col["type"] == "DATE":
                        if isinstance(val, (date, datetime)):
                            valores_actuales[col["name"]] = val.strftime("%d-%m-%Y")
                        else:
                            s = str(val)[:10]
                            partes = s.split("-")
                            valores_actuales[col["name"]] = (
                                f"{partes[2]}-{partes[1]}-{partes[0]}"
                                if len(partes) == 3 else s
                            )
                    elif "TIMESTAMP" in col["type"]:
                        if isinstance(val, datetime):
                            valores_actuales[col["name"]] = val.strftime("%H:%M:%S")
                        else:
                            s = str(val)
                            valores_actuales[col["name"]] = (
                                s.split(" ")[1][:8] if " " in s else s[:8]
                            )
                    else:
                        valores_actuales[col["name"]] = str(val)
    except Exception as exc:
        flash(f"Error al cargar registro: {exc}", "danger")

    return render_template(
        "tablas/formulario.html",
        nombre_tabla  = nombre_tabla,
        tablas        = sorted(TABLA_MODELOS.keys()),
        columnas      = columnas,
        pks           = pks,
        pk_valores    = pk_valores,
        modo          = "UPDATE",
        valores       = valores_actuales,
    )

@tablas_bp.route("/<nombre_tabla>/eliminar", methods=["POST"])
def eliminar(nombre_tabla):
    nombre_tabla = nombre_tabla.upper()
    pks = pk_tabla(nombre_tabla)

    pk_valores   = {pk: request.form.get(pk) for pk in pks}
    where_clause = " AND ".join([f"{pk} = :{pk}" for pk in pks])
    sql = text(f"DELETE FROM {nombre_tabla} WHERE {where_clause}")

    try:
        with db.engine.connect() as conn:
            conn.execute(sql, pk_valores)
            conn.commit()
            flash("Registro eliminado correctamente.", "success")
    except Exception as exc:
        flash(f"Error al eliminar: {exc}", "danger")

    return redirect(url_for("tablas.listar", nombre_tabla=nombre_tabla))