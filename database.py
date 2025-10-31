from sqlmodel import SQLModel, create_engine, Session

# Configuración de la base de datos
sqlite_url = "sqlite:///universidad.db"
engine = create_engine(sqlite_url, echo=True)

def crear_bd_tablas():
    SQLModel.metadata.create_all(engine)

def obtener_sesion():
    with Session(engine) as sesion:
        yield sesion 
 
