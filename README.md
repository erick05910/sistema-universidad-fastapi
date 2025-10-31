# 🏫 Sistema de Gestión Universitaria

Sistema completo para gestión de estudiantes, cursos y matrículas desarrollado con **FastAPI** y **SQLModel**.

## 🚀 Características

- **Gestión Completa** de Estudiantes, Cursos y Matrículas
- **API RESTful** con 15+ endpoints
- **Base de Datos SQLite** con relaciones N:M
- **Validaciones de Negocio** integradas
- **Documentación Automática** con Swagger UI
- **CRUD Completo** para todas las entidades

## 📋 Requisitos

- Python 3.8+
- pip (gestor de paquetes de Python)

## 🛠️ Instalación

```bash
git clone https://github.com/erick05910/sistema-universidad-fastapi.git
cd sistema-universidad-fastapi
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
