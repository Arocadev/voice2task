# voice2task — Backend

> API REST para app de captura de tareas por voz con IA | REST API for AI-powered voice-to-task app

---

## Español

**Voice2Task** es una aplicación Android que convierte notas de voz en tareas estructuradas usando inteligencia artificial. Este repositorio contiene el backend: la API REST que gestiona la autenticación, el almacenamiento de tareas y el procesamiento de audio con Whisper y Groq.

> Evolución natural del proyecto [bot-to-trello](https://github.com/ArocaDev/bot-to-trello): de un bot de Telegram a un producto propio independiente.

---

### ✨ Funcionalidades

- 🔐 **Autenticación JWT** — registro, login, encriptación BCrypt
- 🎙️ **Procesamiento de audio** — transcripción con Whisper + extracción de tarea con Groq
- ✅ **Flujo de confirmación** — la IA propone, el usuario confirma antes de guardar
- 📋 **Gestión de tareas** — CRUD completo con prioridades, fechas y estados
- 🛡️ **Seguridad** — rate limiting en auth, validación de tipo y tamaño de audio, CORS restringido
- 📊 **Trazabilidad** — tabla de procesamiento de audio con estados y registro de errores
- 📖 **Documentación automática** — Swagger / OpenAPI disponible en `/docs`

---

### 🛠️ Stack tecnológico

| Capa | Tecnología |
|------|-----------|
| Framework | Python 3.11 + FastAPI |
| Seguridad | JWT (python-jose) + BCrypt |
| ORM | SQLAlchemy 2.0 |
| Migraciones | Alembic |
| Base de datos | PostgreSQL 16 |
| Validación | Pydantic v2 |
| Transcripción | OpenAI Whisper (`base`) |
| IA | Groq API (Qwen 3.6 27B) |
| Rate limiting | SlowAPI |
| Despliegue | Docker + Docker Compose |

---

### 📁 Estructura del proyecto

```
backend/
├── app/
│   ├── api/
│   │   ├── auth.py       # Registro y login con rate limiting
│   │   └── tareas.py     # CRUD tareas + endpoint de audio
│   ├── core/
│   │   ├── config.py     # Variables de entorno con Pydantic Settings
│   │   ├── security.py   # JWT, BCrypt
│   │   └── deps.py       # Dependencia get_current_user
│   ├── db/
│   │   └── database.py   # Conexión SQLAlchemy + get_db
│   ├── models/
│   │   ├── usuario.py    # Modelo Usuario
│   │   └── tarea.py      # Modelos Tarea y ProcesamientoAudio
│   ├── schemas/
│   │   ├── auth.py       # DTOs de autenticación
│   │   └── tarea.py      # DTOs de tareas y procesamiento
│   └── services/
│       ├── whisper_service.py  # Transcripción de audio
│       ├── llm_service.py      # Extracción de tarea con Groq
│       └── tarea_service.py    # Lógica de negocio
├── main.py               # Punto de entrada FastAPI
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

---

### 🔗 Endpoints principales

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/auth/registro` | Registro de usuario |
| POST | `/api/auth/login` | Login con JWT |
| GET | `/api/tareas/` | Listar tareas del usuario |
| POST | `/api/tareas/` | Crear tarea manual |
| POST | `/api/tareas/audio` | Subir audio → transcribir → proponer tarea |
| POST | `/api/tareas/confirmar` | Guardar tarea confirmada por el usuario |
| GET | `/api/tareas/{id}` | Detalle de tarea |
| PUT | `/api/tareas/{id}/completar` | Marcar como completada |
| DELETE | `/api/tareas/{id}` | Eliminar tarea |

Documentación completa en `/docs` (Swagger UI).

---

### 🚀 Instalación y arranque

```bash
# Clonar el repositorio
git clone https://github.com/ArocaDev/voice2task.git
cd voice2task/backend

# Crear entorno virtual
python -m venv venv
venv\Scripts\activate     # Windows
source venv/bin/activate  # Mac/Linux

# Instalar dependencias
pip install git+https://github.com/openai/whisper.git
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# Arrancar el servidor
uvicorn main:app --reload
```

API disponible en `http://127.0.0.1:8000` · Swagger en `http://127.0.0.1:8000/docs`

---

### 🐳 Despliegue con Docker

```bash
docker compose up db -d
docker compose up backend
```

---

### 🔑 Variables de entorno

```env
DATABASE_URL=postgresql://user:password@localhost:5432/voice2task
SECRET_KEY=tu_clave_secreta
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_DAYS=7
GROQ_API_KEY=tu_groq_api_key
WHISPER_MODEL=base
```

---

### 🔗 Repositorios del proyecto

| Componente | Repositorio |
|---|---|
| Backend (este repo) | [voice2task](https://github.com/ArocaDev/voice2task) |
| Landing web | [voice2task-web](https://github.com/ArocaDev/voice2task-web) |
| App Android | [voice2task-android](https://github.com/ArocaDev/voice2task-android) |

---

## 🌐 English

**Voice2Task** is an Android app that converts voice notes into structured tasks using artificial intelligence. This repository contains the backend: the REST API that handles authentication, task storage and audio processing with Whisper and Groq.

> Natural evolution of the [bot-to-trello](https://github.com/ArocaDev/bot-to-trello) project: from a Telegram bot to a standalone product.

---

### ✨ Features

- 🔐 **JWT Authentication** — registration, login, BCrypt encryption
- 🎙️ **Audio processing** — transcription with Whisper + task extraction with Groq
- ✅ **Confirmation flow** — AI proposes, user confirms before saving
- 📋 **Task management** — full CRUD with priorities, dates and statuses
- 🛡️ **Security** — rate limiting on auth, audio type and size validation, restricted CORS
- 📊 **Traceability** — audio processing table with states and error logging
- 📖 **Auto documentation** — Swagger / OpenAPI available at `/docs`

---

### 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | Python 3.11 + FastAPI |
| Security | JWT (python-jose) + BCrypt |
| ORM | SQLAlchemy 2.0 |
| Migrations | Alembic |
| Database | PostgreSQL 16 |
| Validation | Pydantic v2 |
| Transcription | OpenAI Whisper (`base`) |
| AI | Groq API (Qwen 3.6 27B) |
| Rate limiting | SlowAPI |
| Deployment | Docker + Docker Compose |

---

### 🚀 Getting Started

```bash
git clone https://github.com/ArocaDev/voice2task.git
cd voice2task/backend
python -m venv venv
source venv/bin/activate
pip install git+https://github.com/openai/whisper.git
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload
```

API at `http://127.0.0.1:8000` · Swagger at `http://127.0.0.1:8000/docs`

---

## 👤 Autor / Author

**Alejandro Rodríguez Calabuig** — [github.com/ArocaDev](https://github.com/ArocaDev) · [LinkedIn](https://linkedin.com/in/alejandro-rodriguez-calabuig-a871a1230)

---

## 📄 Licencia / License

Proyecto personal en desarrollo.  
Personal project under development.
