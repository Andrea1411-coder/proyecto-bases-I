import os

class Config:
    # Datos de conexión (según VM)
    USUARIO   = os.getenv("DB_USER", "andrea_correa")
    PASSWORD  = os.getenv("DB_PASSWORD", "andrea123")
    HOST      = os.getenv("DB_HOST", "192.168.40.16")   # IP Windows Server
    PORT      = os.getenv("DB_PORT", "15021")     
    SERVICIO  = os.getenv("DB_SERVICE", "ALCP")             # siglas (SID)


    SQLALCHEMY_DATABASE_URI = (
        f"oracle+oracledb://{USUARIO}:{PASSWORD}"
        f"@{HOST}:{PORT}/?service_name={SERVICIO}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {      
        "pool_pre_ping": True,
        "pool_recycle": 1800,
    }
 
    SECRET_KEY = os.getenv("SECRET_KEY", "consultorio_uptc_2026")


    ROWS_PER_PAGE = 20
