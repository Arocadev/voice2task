<div align="center">

# Voice2Task — Backend

**API REST para Voice2Task**  
*REST API for Voice2Task*

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue?logo=postgresql)](https://postgresql.org)
[![Tests](https://img.shields.io/badge/tests-93%20passing-brightgreen)](https://github.com/ArocaDev/voice2task)
[![Docker](https://img.shields.io/badge/Docker-ready-blue?logo=docker)](https://docker.com)

</div>

---

## ¿Qué es esto?

Backend de Voice2Task — la app Android que convierte notas de voz en tareas estructuradas con IA. Recibe el audio grabado por la app, lo transcribe con Groq Whisper, extrae la tarea con un LLM y la devuelve estructurada al cliente. Gestiona autenticación, usuarios, tareas, listas e integraciones con Trello y Notion.

---

## 🗺️ Diagramas

### Arquitectura del sistema

![Arquitectura](assets/voice2task_arquitectura.svg)

### Flujo de audio a tarea

![Flujo de audio](assets/voice2task_flujo_audio.svg)

---

## ✨ Funcionalidades

- Recepción y procesamiento de audio OGG/Opus
- Transcripción con **Groq Whisper Large V3 Turbo**
- Extracción estructurada con LLM — título, descripción, fecha límite, prioridad
- Auth completo con **JWT** (access + refresh tokens) y **BCrypt**
- CRUD completo de usuarios, listas y tareas
- Rate limiting con **SlowAPI**
- Integración con **Trello API** y **Notion API**
- Documentación automática en `/docs` (Swagger) y `/redoc`
- **93 tests** con Pytest
- Docker Compose para desarrollo local

---

## 🛠️ Stack tecnológico

| Capa | Tecnología |
|------|-----------|
| Framework | FastAPI |
| Lenguaje | Python 3.11 |
| Base de datos | PostgreSQL 16 |
| ORM | SQLAlchemy 2.0 |
| Migraciones | Alembic |
| Auth | JWT + BCrypt |
| Transcripción | Groq Whisper Large V3 Turbo |
| LLM | Groq (openai/gpt-oss-120b) |
| Rate limiting | SlowAPI |
| Tests | Pytest (93 tests) |
| Contenedores | Docker + Docker Compose |

---

## 📁 Estructura

```
voice2task/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── auth.py         # Login, registro, refresh
│   │       ├── tasks.py        # CRUD tareas
│   │       ├── lists.py        # CRUD listas
│   │       ├── audio.py        # Recepción y procesamiento de audio
│   │       └── integrations.py # Trello y Notion
│   ├── core/
│   │   ├── config.py           # Variables de entorno
│   │   ├── security.py         # JWT + BCrypt
│   │   └── database.py         # SQLAlchemy engine + sesión
│   ├── models/                 # Modelos SQLAlchemy
│   ├── schemas/                # Schemas Pydantic
│   └── services/
│       ├── llm_service.py      # Groq Whisper + extracción LLM
│       ├── trello_service.py   # Integración Trello
│       └── notion_service.py   # Integración Notion
├── tests/                      # 93 tests Pytest
├── alembic/                    # Migraciones de base de datos
├── docker-compose.yml
├── Dockerfile
└── main.py
```

---

## 🚀 Instalación

```bash
git clone https://github.com/ArocaDev/voice2task
cd voice2task

cp .env.example .env
# Edita .env con tus credenciales (GROQ_API_KEY, DATABASE_URL, SECRET_KEY)

docker compose up db -d

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

alembic upgrade head
uvicorn main:app --reload
```

Docs disponibles en `http://localhost:8000/docs`

---

## 🧪 Tests

```bash
pytest -v
```

93 tests cubriendo endpoints de auth, tareas, listas y procesamiento de audio.

---

## ⚙️ Variables de entorno

```env
DATABASE_URL=postgresql://user:password@localhost:5432/voice2task
SECRET_KEY=tu-secret-key
GROQ_API_KEY=tu-groq-api-key
GROQ_MODEL=openai/gpt-oss-120b
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
```

---

## 🗺️ Roadmap

- [x] Auth completo (JWT + refresh tokens)
- [x] Transcripción con Groq Whisper
- [x] Extracción estructurada con LLM
- [x] Integraciones Trello y Notion
- [x] Rate limiting
- [x] 93 tests
- [ ] Deploy en Sentinel (plataforma propia)

---

## 🔗 Repositorios del proyecto

| Componente | Repositorio |
|---|---|
| Backend API REST (este repo) | [voice2task](https://github.com/ArocaDev/voice2task) |
| App Android | [voice2task-android](https://github.com/ArocaDev/voice2task-android) |
| Landing web | [voice2task-web](https://github.com/ArocaDev/voice2task-web) |

---

## 👤 Autor

**Alejandro Rodríguez Calabuig**  
[github.com/ArocaDev](https://github.com/ArocaDev) · [LinkedIn](https://linkedin.com/in/alejandro-rodriguez-calabuig-a871a1230)

---

## 📄 Licencia

Proyecto personal en desarrollo. No licenciado para uso comercial.
