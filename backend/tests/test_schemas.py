"""
Tests unitarios para app/schemas/auth.py y app/schemas/tarea.py
Validan que los schemas aceptan y rechazan los inputs correctamente.
"""

import pytest
from pydantic import ValidationError
from app.schemas.auth import RegistroRequest, LoginRequest
from app.schemas.tarea import TareaCreate, TareaUpdate


# ── RegistroRequest ────────────────────────────────────────────────────────────

class TestRegistroRequest:

    def test_valido(self):
        r = RegistroRequest(username="alex123", email="alex@gmail.com", password="password123")
        assert r.username == "alex123"
        assert r.email == "alex@gmail.com"

    def test_email_normalizado_a_minusculas(self):
        r = RegistroRequest(username="alex", email="ALEX@GMAIL.COM", password="password123")
        assert r.email == "alex@gmail.com"

    def test_username_muy_corto(self):
        with pytest.raises(ValidationError, match="al menos 3 caracteres"):
            RegistroRequest(username="ab", email="a@b.com", password="password123")

    def test_username_muy_largo(self):
        with pytest.raises(ValidationError, match="50 caracteres"):
            RegistroRequest(username="a" * 51, email="a@b.com", password="password123")

    def test_username_caracteres_invalidos(self):
        with pytest.raises(ValidationError, match="letras, números"):
            RegistroRequest(username="alex!", email="a@b.com", password="password123")

    def test_username_con_guion_valido(self):
        r = RegistroRequest(username="alex-dev", email="a@b.com", password="password123")
        assert r.username == "alex-dev"

    def test_username_con_guion_bajo_valido(self):
        r = RegistroRequest(username="alex_dev", email="a@b.com", password="password123")
        assert r.username == "alex_dev"

    def test_password_muy_corta(self):
        with pytest.raises(ValidationError, match="al menos 8 caracteres"):
            RegistroRequest(username="alex", email="a@b.com", password="abc123")

    def test_password_muy_larga(self):
        with pytest.raises(ValidationError, match="128 caracteres"):
            RegistroRequest(username="alex", email="a@b.com", password="a" * 129)

    def test_email_invalido(self):
        with pytest.raises(ValidationError):
            RegistroRequest(username="alex", email="no-es-email", password="password123")

    def test_email_muy_largo(self):
        with pytest.raises(ValidationError):
            RegistroRequest(username="alex", email="a" * 250 + "@b.com", password="password123")


# ── LoginRequest ───────────────────────────────────────────────────────────────

class TestLoginRequest:

    def test_valido(self):
        r = LoginRequest(email="alex@gmail.com", password="password123")
        assert r.email == "alex@gmail.com"

    def test_email_normalizado(self):
        r = LoginRequest(email="ALEX@GMAIL.COM", password="password123")
        assert r.email == "alex@gmail.com"

    def test_email_invalido(self):
        with pytest.raises(ValidationError):
            LoginRequest(email="noesmail", password="password123")

    def test_password_muy_larga_devuelve_error_generico(self):
        with pytest.raises(ValidationError, match="Credenciales incorrectas"):
            LoginRequest(email="a@b.com", password="a" * 129)


# ── TareaCreate ────────────────────────────────────────────────────────────────

class TestTareaCreate:

    def test_valido_minimo(self):
        t = TareaCreate(titulo="Comprar pan")
        assert t.titulo == "Comprar pan"
        assert t.prioridad.value == "MEDIA"

    def test_titulo_vacio_falla(self):
        with pytest.raises(ValidationError, match="vacío"):
            TareaCreate(titulo="")

    def test_titulo_solo_espacios_falla(self):
        with pytest.raises(ValidationError, match="vacío"):
            TareaCreate(titulo="   ")

    def test_titulo_muy_largo(self):
        with pytest.raises(ValidationError):
            TareaCreate(titulo="a" * 256)

    def test_titulo_se_limpia(self):
        t = TareaCreate(titulo="  Comprar pan  ")
        assert t.titulo == "Comprar pan"

    def test_descripcion_muy_larga(self):
        with pytest.raises(ValidationError, match="2000 caracteres"):
            TareaCreate(titulo="Tarea", descripcion="x" * 2001)

    def test_prioridad_alta(self):
        from app.models.tarea import Prioridad
        t = TareaCreate(titulo="Tarea", prioridad=Prioridad.ALTA)
        assert t.prioridad == Prioridad.ALTA

    def test_con_lista_id(self):
        t = TareaCreate(titulo="Tarea", lista_id=5)
        assert t.lista_id == 5


# ── TareaUpdate ────────────────────────────────────────────────────────────────

class TestTareaUpdate:

    def test_todos_none_valido(self):
        t = TareaUpdate()
        assert t.titulo is None
        assert t.prioridad is None

    def test_titulo_vacio_falla(self):
        with pytest.raises(ValidationError, match="vacío"):
            TareaUpdate(titulo="")

    def test_titulo_solo_espacios_falla(self):
        with pytest.raises(ValidationError, match="vacío"):
            TareaUpdate(titulo="   ")

    def test_titulo_valido(self):
        t = TareaUpdate(titulo="Nuevo título")
        assert t.titulo == "Nuevo título"

    def test_importante_true(self):
        t = TareaUpdate(importante=True)
        assert t.importante is True

    def test_importante_false(self):
        t = TareaUpdate(importante=False)
        assert t.importante is False

    def test_descripcion_muy_larga(self):
        with pytest.raises(ValidationError, match="2000 caracteres"):
            TareaUpdate(descripcion="x" * 2001)

    def test_solo_campos_enviados(self):
        t = TareaUpdate(titulo="Solo título")
        datos = t.model_dump(exclude_unset=True)
        assert "titulo" in datos
        assert "prioridad" not in datos