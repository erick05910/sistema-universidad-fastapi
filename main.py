from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from typing import List, Optional

from database import engine, crear_bd_tablas, obtener_sesion
from models import Estudiante, Curso, Matricula

app = FastAPI(
    title="Sistema de Gestión Universitaria",
    description="API para gestionar estudiantes, cursos y matrículas",
    version="1.0.0"
)


@app.on_event("startup")
def iniciar_aplicacion():
    crear_bd_tablas()


# ==================== 👨‍🎓 GESTIÓN DE ESTUDIANTES ====================

@app.post("/estudiantes/", response_model=Estudiante, tags=["Estudiantes"])
def crear_estudiante(estudiante: Estudiante, sesion: Session = Depends(obtener_sesion)):
    """
    CREAR NUEVO ESTUDIANTE
    - Valida que la cédula sea única
    - Semestre debe estar entre 1 y 12
    """
    # Validar cédula única
    existente = sesion.exec(select(Estudiante).where(Estudiante.cedula == estudiante.cedula)).first()
    if existente:
        raise HTTPException(status_code=400, detail="❌ La cédula ya está registrada")

    sesion.add(estudiante)
    sesion.commit()
    sesion.refresh(estudiante)
    return estudiante


@app.get("/estudiantes/", response_model=List[Estudiante], tags=["Estudiantes"])
def listar_estudiantes(
        semestre: Optional[int] = None,
        sesion: Session = Depends(obtener_sesion)
):
    """
    LISTAR ESTUDIANTES
    - Filtro opcional por semestre
    - Retorna lista completa si no hay filtro
    """
    consulta = select(Estudiante)
    if semestre:
        consulta = consulta.where(Estudiante.semestre == semestre)
    estudiantes = sesion.exec(consulta).all()
    return estudiantes


@app.get("/estudiantes/{estudiante_id}", response_model=Estudiante, tags=["Estudiantes"])
def obtener_estudiante(estudiante_id: int, sesion: Session = Depends(obtener_sesion)):
    """
    OBTENER ESTUDIANTE POR ID
    - Retorna error 404 si no existe
    """
    estudiante = sesion.get(Estudiante, estudiante_id)
    if not estudiante:
        raise HTTPException(status_code=404, detail="❌ Estudiante no encontrado")
    return estudiante


@app.put("/estudiantes/{estudiante_id}", response_model=Estudiante, tags=["Estudiantes"])
def actualizar_estudiante(
        estudiante_id: int,
        datos_actualizacion: Estudiante,
        sesion: Session = Depends(obtener_sesion)
):
    """
    ACTUALIZAR ESTUDIANTE
    - Valida cédula única si se modifica
    - Actualiza todos los campos
    """
    estudiante_db = sesion.get(Estudiante, estudiante_id)
    if not estudiante_db:
        raise HTTPException(status_code=404, detail="❌ Estudiante no encontrado")

    # Validar cédula única si se cambia
    if datos_actualizacion.cedula != estudiante_db.cedula:
        existente = sesion.exec(select(Estudiante).where(Estudiante.cedula == datos_actualizacion.cedula)).first()
        if existente:
            raise HTTPException(status_code=400, detail="❌ La cédula ya está registrada")

    # Actualizar campos
    estudiante_db.cedula = datos_actualizacion.cedula
    estudiante_db.nombre = datos_actualizacion.nombre
    estudiante_db.email = datos_actualizacion.email
    estudiante_db.semestre = datos_actualizacion.semestre

    sesion.add(estudiante_db)
    sesion.commit()
    sesion.refresh(estudiante_db)
    return estudiante_db


@app.delete("/estudiantes/{estudiante_id}", tags=["Estudiantes"])
def eliminar_estudiante(estudiante_id: int, sesion: Session = Depends(obtener_sesion)):
    """
    ELIMINAR ESTUDIANTE
    - Elimina en cascada todas sus matrículas
    - Retorna confirmación
    """
    estudiante = sesion.get(Estudiante, estudiante_id)
    if not estudiante:
        raise HTTPException(status_code=404, detail="❌ Estudiante no encontrado")

    # Eliminar matrículas del estudiante (cascada)
    matriculas = sesion.exec(select(Matricula).where(Matricula.estudiante_id == estudiante_id)).all()
    for matricula in matriculas:
        sesion.delete(matricula)

    sesion.delete(estudiante)
    sesion.commit()
    return {"mensaje": "✅ Estudiante eliminado correctamente"}


# ==================== 📚 GESTIÓN DE CURSOS ====================

@app.post("/cursos/", response_model=Curso, tags=["Cursos"])
def crear_curso(curso: Curso, sesion: Session = Depends(obtener_sesion)):
    """
    CREAR NUEVO CURSO
    - Valida que el código sea único
    - Créditos deben estar entre 1 y 10
    """
    existente = sesion.exec(select(Curso).where(Curso.codigo == curso.codigo)).first()
    if existente:
        raise HTTPException(status_code=400, detail="❌ El código del curso ya existe")

    sesion.add(curso)
    sesion.commit()
    sesion.refresh(curso)
    return curso


@app.get("/cursos/", response_model=List[Curso], tags=["Cursos"])
def listar_cursos(
        creditos: Optional[int] = None,
        codigo: Optional[str] = None,
        sesion: Session = Depends(obtener_sesion)
):
    """
    LISTAR CURSOS
    - Filtros opcionales por créditos y código
    - Búsqueda parcial en código
    """
    consulta = select(Curso)
    if creditos:
        consulta = consulta.where(Curso.creditos == creditos)
    if codigo:
        consulta = consulta.where(Curso.codigo.contains(codigo))
    cursos = sesion.exec(consulta).all()
    return cursos


@app.get("/cursos/{curso_id}", response_model=Curso, tags=["Cursos"])
def obtener_curso(curso_id: int, sesion: Session = Depends(obtener_sesion)):
    """
    OBTENER CURSO POR ID
    - Retorna error 404 si no existe
    """
    curso = sesion.get(Curso, curso_id)
    if not curso:
        raise HTTPException(status_code=404, detail="❌ Curso no encontrado")
    return curso


@app.put("/cursos/{curso_id}", response_model=Curso, tags=["Cursos"])
def actualizar_curso(
        curso_id: int,
        datos_actualizacion: Curso,
        sesion: Session = Depends(obtener_sesion)
):
    """
    ACTUALIZAR CURSO
    - Valida código único si se modifica
    - Actualiza todos los campos
    """
    curso_db = sesion.get(Curso, curso_id)
    if not curso_db:
        raise HTTPException(status_code=404, detail="❌ Curso no encontrado")

    # Validar código único si se cambia
    if datos_actualizacion.codigo != curso_db.codigo:
        existente = sesion.exec(select(Curso).where(Curso.codigo == datos_actualizacion.codigo)).first()
        if existente:
            raise HTTPException(status_code=400, detail="❌ El código del curso ya existe")

    # Actualizar campos
    curso_db.codigo = datos_actualizacion.codigo
    curso_db.nombre = datos_actualizacion.nombre
    curso_db.creditos = datos_actualizacion.creditos
    curso_db.horario = datos_actualizacion.horario

    sesion.add(curso_db)
    sesion.commit()
    sesion.refresh(curso_db)
    return curso_db


@app.delete("/cursos/{curso_id}", tags=["Cursos"])
def eliminar_curso(curso_id: int, sesion: Session = Depends(obtener_sesion)):
    """
    ELIMINAR CURSO
    - Elimina en cascada todas sus matrículas
    - Retorna confirmación
    """
    curso = sesion.get(Curso, curso_id)
    if not curso:
        raise HTTPException(status_code=404, detail="❌ Curso no encontrado")

    # Eliminar matrículas del curso (cascada)
    matriculas = sesion.exec(select(Matricula).where(Matricula.curso_id == curso_id)).all()
    for matricula in matriculas:
        sesion.delete(matricula)

    sesion.delete(curso)
    sesion.commit()
    return {"mensaje": "✅ Curso eliminado correctamente"}


# ==================== 🎫 GESTIÓN DE MATRÍCULAS ====================

@app.post("/matriculas/", tags=["Matrículas"])
def matricular_estudiante(
        estudiante_id: int,
        curso_id: int,
        sesion: Session = Depends(obtener_sesion)
):
    """
    MATRICULAR ESTUDIANTE EN CURSO
    - Valida que no exista matrícula duplicada
    - Verifica que existan estudiante y curso
    """
    # Verificar si ya está matriculado
    existente = sesion.exec(
        select(Matricula).where(
            Matricula.estudiante_id == estudiante_id,
            Matricula.curso_id == curso_id
        )
    ).first()

    if existente:
        raise HTTPException(status_code=400, detail="❌ El estudiante ya está matriculado en este curso")

    # Verificar que existan estudiante y curso
    estudiante = sesion.get(Estudiante, estudiante_id)
    if not estudiante:
        raise HTTPException(status_code=404, detail="❌ Estudiante no encontrado")

    curso = sesion.get(Curso, curso_id)
    if not curso:
        raise HTTPException(status_code=404, detail="❌ Curso no encontrado")

    # Crear matrícula
    matricula = Matricula(estudiante_id=estudiante_id, curso_id=curso_id)
    sesion.add(matricula)
    sesion.commit()
    sesion.refresh(matricula)

    return {
        "mensaje": "✅ Estudiante matriculado exitosamente",
        "estudiante": estudiante.nombre,
        "curso": curso.nombre
    }


@app.delete("/matriculas/{estudiante_id}/{curso_id}", tags=["Matrículas"])
def desmatricular_estudiante(
        estudiante_id: int,
        curso_id: int,
        sesion: Session = Depends(obtener_sesion)
):
    """
    DESMATRICULAR ESTUDIANTE DE CURSO
    - Elimina la relación de matrícula
    - Retorna confirmación
    """
    matricula = sesion.exec(
        select(Matricula).where(
            Matricula.estudiante_id == estudiante_id,
            Matricula.curso_id == curso_id
        )
    ).first()

    if not matricula:
        raise HTTPException(status_code=404, detail="❌ Matrícula no encontrada")

    sesion.delete(matricula)
    sesion.commit()
    return {"mensaje": "✅ Estudiante desmatriculado exitosamente"}


# ==================== 🔍 CONSULTAS Y REPORTES ====================

@app.get("/estudiantes/{estudiante_id}/cursos", tags=["Consultas"])
def cursos_del_estudiante(estudiante_id: int, sesion: Session = Depends(obtener_sesion)):
    """
    CONSULTAR CURSOS DE UN ESTUDIANTE
    - Retorna estudiante y lista de sus cursos matriculados
    """
    estudiante = sesion.get(Estudiante, estudiante_id)
    if not estudiante:
        raise HTTPException(status_code=404, detail="❌ Estudiante no encontrado")

    # Obtener matrículas del estudiante
    matriculas = sesion.exec(select(Matricula).where(Matricula.estudiante_id == estudiante_id)).all()

    # Obtener cursos de las matrículas
    cursos = []
    for matricula in matriculas:
        curso = sesion.get(Curso, matricula.curso_id)
        if curso:
            cursos.append(curso)

    return {
        "estudiante": estudiante,
        "cursos_matriculados": cursos,
        "total_cursos": len(cursos)
    }


@app.get("/cursos/{curso_id}/estudiantes", tags=["Consultas"])
def estudiantes_del_curso(curso_id: int, sesion: Session = Depends(obtener_sesion)):
    """
    CONSULTAR ESTUDIANTES DE UN CURSO
    - Retorna curso y lista de estudiantes matriculados
    """
    curso = sesion.get(Curso, curso_id)
    if not curso:
        raise HTTPException(status_code=404, detail="❌ Curso no encontrado")

    # Obtener matrículas del curso
    matriculas = sesion.exec(select(Matricula).where(Matricula.curso_id == curso_id)).all()

    # Obtener estudiantes de las matrículas
    estudiantes = []
    for matricula in matriculas:
        estudiante = sesion.get(Estudiante, matricula.estudiante_id)
        if estudiante:
            estudiantes.append(estudiante)

    return {
        "curso": curso,
        "estudiantes_matriculados": estudiantes,
        "total_estudiantes": len(estudiantes)
    }


@app.get("/", tags=["Sistema"])
def estado_sistema():
    """
    ESTADO DEL SISTEMA
    - Health check de la aplicación
    """
    return {
        "mensaje": "✅ Sistema de Gestión Universitaria funcionando correctamente",
        "version": "1.0.0",
        "endpoints_disponibles": 15
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000) 
 
 
 
 
 
 
