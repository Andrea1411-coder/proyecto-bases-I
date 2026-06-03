from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (
    Column, Number, VARCHAR2, Date, BLOB, TIMESTAMP,
    ForeignKey, CheckConstraint, PrimaryKeyConstraint, ForeignKeyConstraint,
    String, Integer, LargeBinary, DateTime, Text,
)
from sqlalchemy.orm import relationship


db = SQLAlchemy()

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

class Tratamientos(db.Model):
    __tablename__ = "TRATAMIENTOS"
    id_tratamiento = db.Column(db.Numeric, primary_key=True)
    id_tipo_terapia = db.Column(db.Numeric, ForeignKey("TIPOS_TERAPIAS.id_tipo_terapia"))
    id_presentacion_medicamento = db.Column(db.Numeric, ForeignKey("PRESENTACIONES_MEDICAMENTOS.id_presentacion_medicamento"))
    nombre_tratamiento = db.Column(db.String(100), nullable=False)
    descripcion_tratamiento = db.Column(db.String(250), nullable=False)
    tipo_tratamiento = db.Column(db.String(20), nullable=False)

    tipo_terapia = relationship("TiposTerapias", back_populates="tratamientos")
    presentacion_medicamento = relationship("PresentacionesMedicamentos", back_populates="tratamientos")
    detalles_formulas = relationship("DetallesFormulas", back_populates="tratamientos")

# ---> Tablas que dependen de las anteriores

class HistoriasClinicas(db.Model):
    __tablename__ = "HISTORIAS_CLINICAS"
    id_historia_clinica = db.Column(db.Numeric, primary_key=True)
    id_paciente = db.Column(db.Numeric, ForeignKey("PACIENTES.id_paciente"))
    fecha_registro = db.Column(db.Date, nullable=False)
    observaciones = db.Column(db.String(250))

    paciente = relationship("Pacientes", back_populates="historias")
    diagnosticos = relationship("DiagnosticosHistorias", back_populates="historia_clinica")
    remisiones = relationship("Remisiones", back_populates="historia_clinica")
    formulas = relationship("FormulasMedicas", back_populates="historia_clinica")
    citas = relationship("Citas", back_populates="historia_clinica")

class Horarios(db.Model):
    __tablename__ = "HORARIOS"
    id_horario = db.Column(db.Numeric, primary_key=True)
    id_profesional = db.Column(db.Numeric, ForeignKey("PROFESIONALES.id_profesional"))
    id_dia_semana = db.Column(db.Numeric, ForeignKey("DIAS_SEMANAS.id_dia_semana"))
    hora_entrada = db.Column(db.TIMESTAMP, nullable=False)
    hora_salida = db.Column(db.TIMESTAMP, nullable=False)

    profesional = relationship("Profesionales", back_populates="horarios")
    dia_semana = relationship("DiasSemanas", back_populates="horarios")


class EspecialidadesProfesionales(db.Model):
    __tablename__ = "ESPECIALIDADES_PROFESIONALES"
    id_especialidad = db.Column(db.Numeric, db.ForeignKey("ESPECIALIDADES.id_especialidad"), primary_key=True)
    id_profesional = db.Column(db.Numeric, db.ForeignKey("PROFESIONALES.id_profesional"), primary_key=True)

    especialidad = relationship("Especialidades", back_populates="profesionales")
    profesional = relationship("Profesionales", back_populates="especialidades")

class PacientesAcudientes(db.Model):
    __tablename__ = "PACIENTES_ACUDIENTES"
    id_paciente = db.Column(db.Numeric, db.ForeignKey("PACIENTES.id_paciente"), primary_key=True)
    id_acudiente = db.Column(db.Numeric, db.ForeignKey("ACUDIENTES.id_acudiente"), primary_key=True)
    firma_acudiente = db.Column(db.LargeBinary)
    firma_paciente = db.Column(db.LargeBinary)
    fecha_firma = db.Column(db.Date)

    paciente = relationship("Pacientes", back_populates="acudientes")
    acudiente = relationship("Acudientes", back_populates="pacientes")

class DiagnosticosHistorias(db.Model):
    __tablename__ = "DIAGNOSTICOS_HISTORIAS"
    id_diagnostico = db.Column(db.Numeric, db.ForeignKey("DIAGNOSTICOS.id_diagnostico"), primary_key=True)
    id_historia_clinica = db.Column(db.Numeric, db.ForeignKey("HISTORIAS_CLINICAS.id_historia_clinica"), primary_key=True)

    diagnostico = relationship("Diagnosticos", back_populates="historias")
    historias_clinicas = relationship("HistoriasClinicas", back_populates="diagnosticos")

class Remisiones(db.Model):
    __tablename__ = "REMISIONES"
    id_remision = db.Column(db.Numeric, primary_key=True)
    id_historia_clinica = db.Column(db.Numeric, db.ForeignKey("HISTORIAS_CLINICAS.id_historia_clinica"), nullable=False)
    id_profesional = db.Column(db.Numeric, db.ForeignKey("PROFESIONALES.id_profesional"), nullable=False)
    motivo_remision = db.Column(db.String(200), nullable=False)
    fecha_remision = db.Column(db.Date, nullable=False)

    historia_clinica = relationship("HistoriasClinicas", back_populates="remisiones")
    profesional = relationship("Profesionales", back_populates="remisiones")

class FormulasMedicas(db.Model):
    __tablename__ = "FORMULAS_MEDICAS"
    id_formula_medica = db.Column(db.Numeric, primary_key=True)
    id_historia_clinica = db.Column(db.Numeric, db.ForeignKey("HISTORIAS_CLINICAS.id_historia_clinica"), nullable=False)
    id_profesional = db.Column(db.Numeric, db.ForeignKey("PROFESIONALES.id_profesional"), nullable=False)
    fecha_formula = db.Column(db.Date, nullable=False)
    indicacion_formula = db.Column(db.String(200), nullable=False)
    observaciones_formula = db.Column(db.String(250))

    historia_clinica = relationship("HistoriasClinicas", back_populates="formulas")
    profesional = relationship("Profesionales", back_populates="formulas")
    detalles = relationship("DetallesFormulas", back_populates="formula_medica")

class DetallesFormulas(db.Model):
    __tablename__ = "DETALLES_FORMULAS"
    id_formula_medica = db.Column(db.Numeric, db.ForeignKey("FORMULAS_MEDICAS.id_formula_medica"), primary_key=True)
    id_tratamiento = db.Column(db.Numeric, db.ForeignKey("TRATAMIENTOS.id_tratamiento"), primary_key=True)
    dosis_formula = db.Column(db.String(50), nullable=False)
    frecuencia_tratamiento_formula = db.Column(db.String(100), nullable=False)
    duracion_formula = db.Column(db.String(50), nullable=False)

    formula_medica = relationship("FormulasMedicas", back_populates="detalles")
    tratamientos = relationship("Tratamientos", back_populates="detalles_formulas")

class Citas(db.Model):
    __tablename__ = "CITAS"
    __table_args__ = (
        CheckConstraint("confirmacion_paciente_cita IN (0, 1)", name="cita_ck_confirmacion"),
    )
    id_cita = db.Column(db.Numeric, primary_key=True)
    id_paciente = db.Column(db.Numeric, db.ForeignKey("PACIENTES.id_paciente"), nullable=False)
    id_profesional = db.Column(db.Numeric, db.ForeignKey("PROFESIONALES.id_profesional"), nullable=False)
    id_consultorio = db.Column(db.Numeric, db.ForeignKey("CONSULTORIOS.id_consultorio"), nullable=False)
    id_tipo_cita = db.Column(db.Numeric, db.ForeignKey("TIPOS_CITAS.id_tipo_cita"), nullable=False)
    id_historia_clinica = db.Column(db.Numeric, db.ForeignKey("HISTORIAS_CLINICAS.id_historia_clinica"), nullable=False)
    id_estado_cita = db.Column(db.Numeric, db.ForeignKey("ESTADOS_CITAS.id_estado_cita"), nullable=False)
    motivo_cita = db.Column(db.String(200), nullable=False)
    fecha_cita = db.Column(db.Date, nullable=False)
    hora_inicio_cita = db.Column(db.TIMESTAMP, nullable=False)
    hora_fin_cita = db.Column(db.TIMESTAMP)
    confirmacion_paciente_cita = db.Column(db.Numeric(1))
    link_teleconsulta_cita = db.Column(db.String(250))
    observaciones_cita = db.Column(db.String(250))

    paciente = relationship("Pacientes", back_populates="citas")
    profesional = relationship("Profesionales", back_populates="citas")
    consultorio = relationship("Consultorios", back_populates="citas")
    tipo_cita = relationship("TiposCitas", back_populates="citas")
    estado_cita = relationship("EstadosCitas", back_populates="citas")
    historia_clinica = relationship("HistoriasClinicas", back_populates="citas")


#Mapa de tablas

TABLA_MODELOS = {
    "TIPOS_DOCUMENTOS": TiposDocumentos,
    "ESPECIALIDADES": Especialidades,
    "ESTADOS_CITAS": EstadosCitas,
    "TIPOS_CITAS": TiposCitas,
    "CONSULTORIOS": Consultorios,
    "ACUDIENTES": Acudientes,
    "DIAGNOSTICOS": Diagnosticos,
    "PRESENTACIONES_MEDICAMENTOS": PresentacionesMedicamentos,
    "TIPOS_TERAPIAS": TiposTerapias,
    "DIAS_SEMANAS": DiasSemanas,
    "PROFESIONALES": Profesionales,
    "PACIENTES": Pacientes,
    "TRATAMIENTOS": Tratamientos,
    "HISTORIAS_CLINICAS": HistoriasClinicas,
    "HORARIOS": Horarios,
    "ESPECIALIDADES_PROFESIONALES": EspecialidadesProfesionales,
    "PACIENTES_ACUDIENTES": PacientesAcudientes,
    "DIAGNOSTICOS_HISTORIAS": DiagnosticosHistorias,
    "REMISIONES": Remisiones,
    "FORMULAS_MEDICAS": FormulasMedicas,
    "DETALLES_FORMULAS": DetallesFormulas,
    "CITAS": Citas,
}