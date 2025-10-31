from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List


class Estudiante(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    cedula: str = Field(unique=True, index=True, max_length=20)
    nombre: str = Field(max_length=100)
    email: str = Field(max_length=100)
    semestre: int = Field(ge=1, le=12)

    matriculas: List["Matricula"] = Relationship(back_populates="estudiante")


class Curso(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    codigo: str = Field(unique=True, index=True, max_length=20)
    nombre: str = Field(max_length=100)
    creditos: int = Field(ge=1, le=10)
    horario: str = Field(max_length=50)

    matriculas: List["Matricula"] = Relationship(back_populates="curso")


class Matricula(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    estudiante_id: int = Field(foreign_key="estudiante.id")
    curso_id: int = Field(foreign_key="curso.id")

    estudiante: Estudiante = Relationship(back_populates="matriculas")
    curso: Curso = Relationship(back_populates="matriculas") 
 
