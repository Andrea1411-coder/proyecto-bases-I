# Vista de tabla con los CRUD de las 22 tablas

from flask import (Blueprint, render_template, request, redirect, url_for, flash, jsonify)
from sqlalchemy import text, inspect
from models import db, TABLA_MODELOS
from config import Config

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

# Listado

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

    # Construir SELECT con WHERE
    where_clause = ""
    if filtro:
        where_clause = f" WHERE {filtro}"

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
            filas = [[str(v) if v is not None else "" for v in row[:-1]] for row in rows]
    except Exception as exc:
        error = str(exc)

    total_pages = max(1, (total + per_page - 1) // per_page)

    return render_template(
        "tablas/lista.html",
        nombre_tabla = nombre_tabla,
        tablas       = sorted(TABLA_MODELOS.keys()),
        columnas     = col_names,
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

        cols_str = ", ".join(valores.keys())
        vals_str = ", ".join([f":{k}" for k in valores.keys()])
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
    pk_valores = {pk: request.args.get(pk) or request.form.get(pk)
                  for pk in pks}
    where_clause = " AND ".join([f"{pk} = :{pk}" for pk in pks])

    if request.method == "POST":
        valores = {}
        for col in columnas:
            val = request.form.get(col["name"], "").strip()
            valores[col["name"]] = None if val == "" else val

        set_clause = ", ".join([
            f"{c['name']} = :{c['name']}"
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
                col_names = columnas_tabla(nombre_tabla)
                for i, col in enumerate(col_names):
                    valores_actuales[col["name"]] = "" if row[i] is None else str(row[i])
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