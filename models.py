from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (
    Column, Number, VARCHAR2, Date, BLOB, TIMESTAMP,
    ForeignKey, CheckConstraint, PrimaryKeyConstraint, ForeignKeyConstraint,
    String, Integer, LargeBinary, DateTime, Text,
)
from sqlalchemy.orm import relationship

db = SQLAlchemy()

Num = lambda p=None, s=None: db.Column(db.Numeric(p, s))
Str = lambda n: db.Column(db.String(n))

# ---> Sin FK
class TiposDocumentos(db.Model):
    __tablename__ = "TIPOS_DOCUMENTOS"
    id_tipo_documento = db.Column(db.Numeric, primary_key=True)
    nombre_tipo_documento = db.Column(db.String(50), nullable=False)

    pacientes = relationship("Pacientes", back_populates="tipo_documento")

class Especialidades(db.Model):
    __tablename__ = "ESPECIALIDADES"
    id_especialidad = db.Column(db.Numeric, primary_key=True)
    nombre_especialidad = db.Column(db.String(100), nullable=False)
    descripcion_especialidad = db.Column(db.String(250))

    profesionales = relationship("EspecialidadesProfesionales", back_populates="especialidad")

class EstadosCitas(db.Model):
    __tablename__ = "ESTADOS_CITAS"
    id_estado_cita = db.Column(db.Numeric, primary_key=True)
    descripcion_estado_cita = db.Column(db.String(50), nullable=False)

    citas = relationship("Citas", back_populates="estado_cita")

class TiposCitas(db.Model):
    __tablename__ = "TIPOS_CITAS"
    id_tipo_cita = db.Column(db.Numeric, primary_key=True)
    nombre_tipo_cita = db.Column(db.String(50), nullable=False)

    citas = relationship("Citas", back_populates="tipo_cita")

class Consultorios(db.Model):
    __tablename__ = "CONSULTORIOS"
    id_consultorio = db.Column(db.Numeric, primary_key=True)
    nombre_consultorio = db.Column(db.String(100), nullable=False)
    descripcion_consultorio = db.Column(db.String(250), nullable=False)

    citas = relationship("Citas", back_populates="consultorio")

class Acudientes(db.Model):
    __tablename__ = "ACUDIENTES"
    id_acudiente = db.Column(db.Numeric, primary_key=True)
    nombre_acudiente = db.Column(db.String(100), nullable=False)
    celular_acudiente = db.Column(db.String(15), nullable=False)
    parentesco_acudiente = db.Column(db.String(50), nullable=False)

    pacientes = relationship("PacientesAcudientes", back_populates="acudiente")

class Diagnosticos(db.Model):
    __tablename__ = "DIAGNOSTICOS"
    id_diagnostico = db.Column(db.Numeric, primary_key=True)
    nombre_diagnostico = db.Column(db.String(100), nullable=False)

    historias = relationship("DiagnosticosHistorias", back_populates="diagnostico")

class PresentacionesMedicamentos(db.Model):
    __tablename__ = "PRESENTACIONES_MEDICAMENTOS"
    id_presentacion_medicamento = db.Column(db.Numeric, primary_key=True)
    nombre_presentacion_medicamento = db.Column(db.String(50), nullable=False)
    concentracion_medicamento = db.Column(db.String(50), nullable=False)

    tratamientos = relationship("Tratamientos", back_populates="presentacion_medicamento")

class TiposTerapias(db.Model):
    __tablename__ = "TIPOS_TERAPIAS"
    id_tipo_terapia = db.Column(db.Numeric, primary_key=True)
    nombre_tipo_terapia = db.Column(db.String(50), nullable=False)
    duracion_sesion_terapia = db.Column(db.Numeric(3), nullable=False)

    tratamientos = relationship("Tratamientos", back_populates="tipo_terapia")

class DiasSemanas(db.Model):
    __tablename__ = "DIAS_SEMANAS"
    id_dia_semana = db.Column(db.Numeric, primary_key=True)
    nombre_dia_semana = db.Column(db.String(20), nullable=False)

    horarios = relationship("Horarios", back_populates="dia_semana")


# ---> salen varias relaciones
class Profesionales(db.Model):
    __tablename__ = "PROFESIONALES"
    id_profesional = db.Column(db.Numeric, primary_key=True)
    nombre_profesional = db.Column(db.String(150), nullable=False)
    num_documento_profesional = db.Column(db.String(50), nullable=False)
    num_tarjeta_profesional = db.Column(db.String(50), nullable=False)
    telefono_profesional = db.Column(db.String(15), nullable=False)
    direccion_profesional = db.Column(db.String(150))
    correo_electronico_profesional = db.Column(db.String(150))

    especialidades = relationship("EspecialidadesProfesionales", back_populates="profesional")
    horarios       = relationship("Horarios",    back_populates="profesional")
    citas          = relationship("Citas",       back_populates="profesional")
    remisiones     = relationship("Remisiones",  back_populates="profesional")
    formulas       = relationship("FormulasMedicas", back_populates="profesional")

# ---> Tablas con multipes relaciones, con FK
class Pacientes(db.Model):
    __tablename__ = "PACIENTES"
    id_paciente = db.Column(db.Numeric, primary_key=True)
    id_tipo_documento = db.Column(db.Numeric, ForeignKey("TIPOS_DOCUMENTOS.id_tipo_documento"))
    nombre_paciente = db.Column(db.String(50), nullable=False)
    num_documento_paciente = db.Column(db.String(50), nullable=False)
    telefono_principal_paciente = db.Column(db.String(15), nullable=False)
    telefono_alterno_paciente = db.Column(db.String(15))
    fecha_nacimiento_paciente = db.Column(db.Date)
    direccion_paciente = db.Column(db.String(150))
    correo_electronico_paciente = db.Column(db.String(150))

    tipo_documento = relationship("TiposDocumentos", back_populates="pacientes")
    historias = relationship("HistoriasClinicas", back_populates="paciente")
    citas = relationship("Citas", back_populates="paciente")
    acudientes = relationship("PacientesAcudientes", back_populates="paciente")

