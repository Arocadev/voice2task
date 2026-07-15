<div align="center">

# Voice2Task — Backend

**API REST para app de captura de tareas por voz con IA**  
*REST API for AI-powered voice-to-task Android app*

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue?logo=postgresql)](https://postgresql.org)
[![Groq](https://img.shields.io/badge/AI-Groq-orange)](https://console.groq.com)
[![Docker](https://img.shields.io/badge/Docker-ready-blue?logo=docker)](https://docker.com)

> Evolución del proyecto [bot-to-trello](https://github.com/ArocaDev/bot-to-trello): de un bot de Telegram a un producto propio independiente.

</div>

---

## ¿Qué es Voice2Task?

Voice2Task es una app Android que convierte notas de voz en tareas estructuradas usando inteligencia artificial. Este repositorio contiene el backend: la API REST que gestiona la autenticación, el almacenamiento de tareas y el procesamiento de audio con Whisper y Groq.

---

## ✨ Funcionalidades

### 🔐 Autenticación JWT
Registro, login y cambio de contraseña con cifrado BCrypt. Tokens con expiración configurable.

### 🎙️ Procesamiento de audio
El audio se transcribe con Whisper Large V3 Turbo y se envía a Groq, que extrae título, descripción, fecha límite y prioridad de la tarea de forma estructurada.

### ✅ Flujo de confirmación
La IA propone la tarea, el usuario la revisa y la confirma antes de que se guarde. Nunca se guarda nada sin confirmación explícita.

### 📋 Gestión de tareas y listas
CRUD completo con soporte para listas, prioridades (BAJA / MEDIA / ALTA), fechas límite, estados de completado y marcado como importante.

### 🛡️ Seguridad
Rate limiting en endpoints de autenticación, validación de tipo y tamaño de audio, headers de seguridad y CORS restringido.

### 📊 Trazabilidad
Tabla de procesamiento de audio con registro de estados y errores para cada transcripción.

### 📖 Documentación automática
Swagger / OpenAPI disponible en `/docs`.

---

## 🛠️ Stack tecnológico

| Capa | Tecnología |
|------|-----------|
| Framework | Python 3.11 + FastAPI |
| Seguridad | JWT (python-jose) + BCrypt |
| ORM | SQLAlchemy 2.0 |
| Migraciones | Alembic |
| Base de datos | PostgreSQL 16 |
| Validación | Pydantic v2 |
| Transcripción | Groq Whisper Large V3 Turbo |
| IA | Groq API (`openai/gpt-oss-120b`) |
| Rate limiting | SlowAPI |
| Despliegue | Docker + Docker Compose |

---

## 📁 Estructura del proyecto

```
backend/
├── app/
│   ├── api/
│   │   ├── auth.py           # Registro, login y cambio de contraseña
│   │   ├── listas.py         # CRUD de listas
│   │   └── tareas.py         # CRUD tareas + endpoint de audio
│   ├── core/
│   │   ├── config.py         # Variables de entorno con Pydantic Settings
│   │   ├── security.py       # JWT, BCrypt
│   │   └── deps.py           # Dependencia get_current_user
│   ├── db/
│   │   └── database.py       # Conexión SQLAlchemy + get_db
│   ├── models/
│   │   ├── usuario.py        # Modelo Usuario
│   │   └── tarea.py          # Modelos Tarea, Lista y ProcesamientoAudio
│   ├── schemas/
│   │   ├── auth.py           # DTOs de autenticación
│   │   └── tarea.py          # DTOs de tareas y procesamiento
│   └── services/
│       ├── llm_service.py    # Extracción de tarea con Groq
│       └── tarea_service.py  # Lógica de negocio
├── tests/
│   ├── conftest.py
│   ├── test_llm_service.py   # 28 tests unitarios
│   ├── test_schemas.py       # 22 tests unitarios
│   └── test_integration.py   # 43 tests de integración
├── main.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

---

## 🔗 Endpoints principales

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/auth/registro` | Registro de usuario |
| POST | `/api/auth/login` | Login con JWT |
| POST | `/api/auth/cambiar-password` | Cambiar contraseña |
| GET | `/api/listas/` | Listar listas del usuario |
| POST | `/api/listas/` | Crear lista |
| DELETE | `/api/listas/{id}` | Eliminar lista |
| GET | `/api/tareas/` | Listar tareas (filtros por lista, estado, importancia) |
| POST | `/api/tareas/` | Crear tarea manual |
| POST | `/api/tareas/audio` | Subir audio → transcribir → proponer tarea |
| POST | `/api/tareas/confirmar` | Guardar tarea confirmada |
| PUT | `/api/tareas/{id}` | Editar tarea |
| PUT | `/api/tareas/{id}/completar` | Marcar como completada |
| PUT | `/api/tareas/{id}/importante` | Marcar como importante |
| DELETE | `/api/tareas/{id}` | Eliminar tarea |

Documentación completa en `/docs` (Swagger UI).

---

## 🧪 Tests

```bash
venv\Scripts\python.exe -m pytest tests/ -v   # Windows
python -m pytest tests/ -v                     # Mac/Linux
```

93 tests: 28 unitarios de LLM service, 22 de schemas y 43 de integración. Usan SQLite para evitar dependencia de PostgreSQL en CI.

---

## 🚀 Instalación local

```bash
git clone https://github.com/ArocaDev/voice2task.git
cd voice2task/backend

python -m venv venv
venv\Scripts\activate       # Windows
source venv/bin/activate    # Mac/Linux

pip install -r requirements.txt

cp .env.example .env
# Edita .env con tus credenciales

uvicorn main:app --reload
```

API disponible en `http://127.0.0.1:8000` · Swagger en `http://127.0.0.1:8000/docs`

---

## 🐳 Despliegue con Docker

```bash
docker compose up db -d
docker compose up backend
```

---

## 🔑 Variables de entorno

```env
DATABASE_URL=postgresql://user:password@localhost:5432/voice2task
SECRET_KEY=tu_clave_secreta
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_DAYS=7
GROQ_API_KEY=tu_groq_api_key
WHISPER_MODEL=whisper-large-v3-turbo
GROQ_MODEL=openai/gpt-oss-120b
```

---

## 🗺️ Roadmap

- [ ] Despliegue en Railway con dominio aroca.dev
- [ ] WebSockets para sincronización en tiempo real
- [ ] Redis + Celery para procesamiento asíncrono de audio
- [ ] Observabilidad y métricas
- [ ] Reintentos automáticos en llamadas a Groq

---

## 🔗 Repositorios del proyecto

| Componente | Repositorio |
|---|---|
| Backend (este repo) | [voice2task](https://github.com/ArocaDev/voice2task) |
| App Android | [voice2task-android](https://github.com/ArocaDev/voice2task-android) |
| Landing web | [voice2task-web](https://github.com/ArocaDev/voice2task-web) |

---

## 👤 Autor

**Alejandro Rodríguez Calabuig**  
[github.com/ArocaDev](https://github.com/ArocaDev) · [LinkedIn](https://linkedin.com/in/alejandro-rodriguez-calabuig-a871a1230)

---

## 📄 Licencia

Proyecto personal en desarrollo. No licenciado para uso comercial.  
*Personal project under development. Not licensed for commercial use.*
