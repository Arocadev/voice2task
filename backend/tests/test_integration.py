"""
Tests de integración para los endpoints principales.
Usan TestClient de FastAPI con base de datos SQLite en memoria.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from slowapi import Limiter
from slowapi.util import get_remote_address

from main import app
from app.db.database import Base, get_db

# ── Base de datos en memoria para tests ───────────────────────────────────────

SQLALCHEMY_TEST_URL = "sqlite:///./test.db"

engine_test = create_engine(
    SQLALCHEMY_TEST_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine_test)
    yield
    Base.metadata.drop_all(bind=engine_test)


client = TestClient(app)


# ── Helpers ────────────────────────────────────────────────────────────────────

def registrar_y_login(username="testuser", email="test@test.com", password="password123"):
    client.post("/api/auth/registro", json={
        "username": username, "email": email, "password": password
    })
    r = client.post("/api/auth/login", json={"email": email, "password": password})
    return r.json()["access_token"]


def headers(token):
    return {"Authorization": f"Bearer {token}"}


# ── Auth ───────────────────────────────────────────────────────────────────────

class TestAuth:

    def test_registro_exitoso(self):
        r = client.post("/api/auth/registro", json={
            "username": "newuser", "email": "new@test.com", "password": "password123"
        })
        assert r.status_code == 201
        assert r.json()["username"] == "newuser"

    def test_registro_email_duplicado(self):
        client.post("/api/auth/registro", json={
            "username": "user1", "email": "dup@test.com", "password": "password123"
        })
        r = client.post("/api/auth/registro", json={
            "username": "user2", "email": "dup@test.com", "password": "password123"
        })
        assert r.status_code == 400
        assert "email" in r.json()["detail"].lower()

    def test_registro_username_duplicado(self):
        client.post("/api/auth/registro", json={
            "username": "sameuser", "email": "a@test.com", "password": "password123"
        })
        r = client.post("/api/auth/registro", json={
            "username": "sameuser", "email": "b@test.com", "password": "password123"
        })
        assert r.status_code == 400
        assert "username" in r.json()["detail"].lower()

    def test_login_exitoso(self):
        client.post("/api/auth/registro", json={
            "username": "loginuser", "email": "login@test.com", "password": "password123"
        })
        r = client.post("/api/auth/login", json={
            "email": "login@test.com", "password": "password123"
        })
        assert r.status_code == 200
        assert "access_token" in r.json()

    def test_login_password_incorrecta(self):
        client.post("/api/auth/registro", json={
            "username": "user3", "email": "c@test.com", "password": "password123"
        })
        r = client.post("/api/auth/login", json={
            "email": "c@test.com", "password": "wrongpassword"
        })
        assert r.status_code == 401

    def test_login_email_inexistente(self):
        r = client.post("/api/auth/login", json={
            "email": "noexiste@test.com", "password": "password123"
        })
        assert r.status_code == 401

    def test_me_con_token_valido(self):
        token = registrar_y_login("meuser", "me@test.com")
        r = client.get("/api/auth/me", headers=headers(token))
        assert r.status_code == 200
        assert r.json()["username"] == "meuser"

    def test_me_sin_token(self):
        r = client.get("/api/auth/me")
        assert r.status_code == 403

    def test_logout_invalida_token(self):
        token = registrar_y_login("logoutuser", "logout@test.com")
        r = client.post("/api/auth/logout", headers=headers(token))
        assert r.status_code == 204
        r2 = client.get("/api/auth/me", headers=headers(token))
        assert r2.status_code == 401

    def test_registro_password_corta(self):
        r = client.post("/api/auth/registro", json={
            "username": "user4", "email": "d@test.com", "password": "abc"
        })
        assert r.status_code == 422
        assert "8" in r.json()["detail"]

    def test_registro_username_corto(self):
        r = client.post("/api/auth/registro", json={
            "username": "ab", "email": "e@test.com", "password": "password123"
        })
        assert r.status_code == 422


# ── Listas ─────────────────────────────────────────────────────────────────────

class TestListas:

    def test_crear_lista(self):
        token = registrar_y_login("listuser", "list@test.com")
        r = client.post("/api/listas/", json={"nombre": "Mi lista"}, headers=headers(token))
        assert r.status_code == 201
        assert r.json()["nombre"] == "Mi lista"

    def test_listar_listas_propias(self):
        token = registrar_y_login("listuser2", "list2@test.com")
        client.post("/api/listas/", json={"nombre": "Lista A"}, headers=headers(token))
        client.post("/api/listas/", json={"nombre": "Lista B"}, headers=headers(token))
        r = client.get("/api/listas/", headers=headers(token))
        assert r.status_code == 200
        assert len(r.json()) == 2

    def test_listas_aisladas_entre_usuarios(self):
        token1 = registrar_y_login("iso1", "iso1@test.com")
        token2 = registrar_y_login("iso2", "iso2@test.com")
        client.post("/api/listas/", json={"nombre": "Lista user1"}, headers=headers(token1))
        r = client.get("/api/listas/", headers=headers(token2))
        assert r.status_code == 200
        assert len(r.json()) == 0

    def test_eliminar_lista(self):
        token = registrar_y_login("dellist", "dellist@test.com")
        r = client.post("/api/listas/", json={"nombre": "Borrar"}, headers=headers(token))
        lista_id = r.json()["id"]
        r2 = client.delete(f"/api/listas/{lista_id}", headers=headers(token))
        assert r2.status_code == 204

    def test_no_puede_eliminar_lista_ajena(self):
        token1 = registrar_y_login("own1", "own1@test.com")
        token2 = registrar_y_login("own2", "own2@test.com")
        r = client.post("/api/listas/", json={"nombre": "Lista ajena"}, headers=headers(token1))
        lista_id = r.json()["id"]
        r2 = client.delete(f"/api/listas/{lista_id}", headers=headers(token2))
        assert r2.status_code == 404


# ── Tareas ─────────────────────────────────────────────────────────────────────

class TestTareas:

    def test_crear_tarea(self):
        token = registrar_y_login("taskuser", "task@test.com")
        r = client.post("/api/tareas/", json={"titulo": "Mi tarea"}, headers=headers(token))
        assert r.status_code == 201
        assert r.json()["titulo"] == "Mi tarea"
        assert r.json()["importante"] is False

    def test_listar_tareas(self):
        token = registrar_y_login("taskuser2", "task2@test.com")
        client.post("/api/tareas/", json={"titulo": "Tarea 1"}, headers=headers(token))
        client.post("/api/tareas/", json={"titulo": "Tarea 2"}, headers=headers(token))
        r = client.get("/api/tareas/", headers=headers(token))
        assert r.status_code == 200
        assert len(r.json()) == 2

    def test_tareas_aisladas_entre_usuarios(self):
        token1 = registrar_y_login("tiso1", "tiso1@test.com")
        token2 = registrar_y_login("tiso2", "tiso2@test.com")
        client.post("/api/tareas/", json={"titulo": "Tarea user1"}, headers=headers(token1))
        r = client.get("/api/tareas/", headers=headers(token2))
        assert len(r.json()) == 0

    def test_completar_tarea(self):
        token = registrar_y_login("compuser", "comp@test.com")
        r = client.post("/api/tareas/", json={"titulo": "Completar"}, headers=headers(token))
        tarea_id = r.json()["id"]
        r2 = client.put(f"/api/tareas/{tarea_id}/completar", headers=headers(token))
        assert r2.status_code == 200
        assert r2.json()["completada"] is True

    def test_marcar_importante(self):
        token = registrar_y_login("impuser", "imp@test.com")
        r = client.post("/api/tareas/", json={"titulo": "Importante"}, headers=headers(token))
        tarea_id = r.json()["id"]
        r2 = client.put(f"/api/tareas/{tarea_id}/importante?importante=true", headers=headers(token))
        assert r2.status_code == 200
        assert r2.json()["importante"] is True

    def test_listar_importantes(self):
        token = registrar_y_login("implist", "implist@test.com")
        r1 = client.post("/api/tareas/", json={"titulo": "Normal"}, headers=headers(token))
        r2 = client.post("/api/tareas/", json={"titulo": "Importante"}, headers=headers(token))
        client.put(f"/api/tareas/{r2.json()['id']}/importante?importante=true", headers=headers(token))
        r = client.get("/api/tareas/importantes", headers=headers(token))
        assert len(r.json()) == 1
        assert r.json()[0]["titulo"] == "Importante"

    def test_editar_tarea(self):
        token = registrar_y_login("edituser", "edit@test.com")
        r = client.post("/api/tareas/", json={"titulo": "Original"}, headers=headers(token))
        tarea_id = r.json()["id"]
        r2 = client.patch(f"/api/tareas/{tarea_id}", json={"titulo": "Editado"}, headers=headers(token))
        assert r2.status_code == 200
        assert r2.json()["titulo"] == "Editado"

    def test_buscar_tareas(self):
        token = registrar_y_login("searchuser", "search@test.com")
        client.post("/api/tareas/", json={"titulo": "Comprar pan"}, headers=headers(token))
        client.post("/api/tareas/", json={"titulo": "Llamar al médico"}, headers=headers(token))
        r = client.get("/api/tareas/buscar?q=comprar", headers=headers(token))
        assert r.status_code == 200
        assert r.json()["total"] == 1
        assert "pan" in r.json()["tareas"][0]["titulo"].lower()

    def test_filtrar_completadas(self):
        token = registrar_y_login("filtuser", "filt@test.com")
        r1 = client.post("/api/tareas/", json={"titulo": "Pendiente"}, headers=headers(token))
        r2 = client.post("/api/tareas/", json={"titulo": "Completada"}, headers=headers(token))
        client.put(f"/api/tareas/{r2.json()['id']}/completar", headers=headers(token))
        r = client.get("/api/tareas/?completada=true", headers=headers(token))
        assert len(r.json()) == 1
        assert r.json()[0]["completada"] is True

    def test_eliminar_tarea(self):
        token = registrar_y_login("deluser", "del@test.com")
        r = client.post("/api/tareas/", json={"titulo": "Borrar"}, headers=headers(token))
        tarea_id = r.json()["id"]
        r2 = client.delete(f"/api/tareas/{tarea_id}", headers=headers(token))
        assert r2.status_code == 204

    def test_no_puede_editar_tarea_ajena(self):
        token1 = registrar_y_login("eown1", "eown1@test.com")
        token2 = registrar_y_login("eown2", "eown2@test.com")
        r = client.post("/api/tareas/", json={"titulo": "Ajena"}, headers=headers(token1))
        tarea_id = r.json()["id"]
        r2 = client.patch(f"/api/tareas/{tarea_id}", json={"titulo": "Hackeada"}, headers=headers(token2))
        assert r2.status_code == 404

    def test_titulo_vacio_falla(self):
        token = registrar_y_login("valuser", "val@test.com")
        r = client.post("/api/tareas/", json={"titulo": ""}, headers=headers(token))
        assert r.status_code == 422