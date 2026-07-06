"""
Tests unitarios para app/services/llm_service.py
Cubren las funciones internas de validación sin llamar a la API de Groq.
"""

import pytest
from app.services.llm_service import (
    _limpiar_json,
    _validar_prioridad,
    _validar_fecha,
    _titulo_fallback,
)


# ── _limpiar_json ──────────────────────────────────────────────────────────────

class TestLimpiarJson:

    def test_json_limpio(self):
        entrada = '{"titulo": "Comprar pan", "prioridad": "ALTA"}'
        assert _limpiar_json(entrada) == entrada

    def test_elimina_think_tags(self):
        entrada = '<think>pensando...</think>{"titulo": "Tarea"}'
        resultado = _limpiar_json(entrada)
        assert "<think>" not in resultado
        assert '{"titulo": "Tarea"}' == resultado

    def test_elimina_fence_json(self):
        entrada = '```json\n{"titulo": "Tarea"}\n```'
        resultado = _limpiar_json(entrada)
        assert resultado == '{"titulo": "Tarea"}'

    def test_elimina_fence_sin_json(self):
        entrada = '```\n{"titulo": "Tarea"}\n```'
        resultado = _limpiar_json(entrada)
        assert resultado == '{"titulo": "Tarea"}'

    def test_extrae_json_de_texto(self):
        entrada = 'Aquí tienes la tarea: {"titulo": "Comprar"} espero que ayude'
        resultado = _limpiar_json(entrada)
        assert resultado == '{"titulo": "Comprar"}'

    def test_think_y_fence_combinados(self):
        entrada = '<think>razonando</think>\n```json\n{"titulo": "X"}\n```'
        resultado = _limpiar_json(entrada)
        assert resultado == '{"titulo": "X"}'

    def test_contenido_vacio(self):
        resultado = _limpiar_json("")
        assert resultado == ""


# ── _validar_prioridad ─────────────────────────────────────────────────────────

class TestValidarPrioridad:

    def test_alta(self):
        assert _validar_prioridad("ALTA") == "ALTA"

    def test_media(self):
        assert _validar_prioridad("MEDIA") == "MEDIA"

    def test_baja(self):
        assert _validar_prioridad("BAJA") == "BAJA"

    def test_minusculas(self):
        assert _validar_prioridad("alta") == "ALTA"

    def test_mixto(self):
        assert _validar_prioridad("Media") == "MEDIA"

    def test_invalido_devuelve_media(self):
        assert _validar_prioridad("URGENTE") == "MEDIA"

    def test_vacio_devuelve_media(self):
        assert _validar_prioridad("") == "MEDIA"

    def test_none_devuelve_media(self):
        assert _validar_prioridad(None) == "MEDIA"

    def test_con_espacios(self):
        assert _validar_prioridad("  ALTA  ") == "ALTA"


# ── _validar_fecha ─────────────────────────────────────────────────────────────

class TestValidarFecha:

    def test_fecha_valida(self):
        assert _validar_fecha("2026-12-31") == "2026-12-31"

    def test_fecha_null_string(self):
        assert _validar_fecha("null") is None

    def test_fecha_none(self):
        assert _validar_fecha(None) is None

    def test_fecha_vacia(self):
        assert _validar_fecha("") is None

    def test_fecha_none_string(self):
        assert _validar_fecha("none") is None

    def test_fecha_formato_incorrecto(self):
        assert _validar_fecha("31/12/2026") is None

    def test_fecha_año_muy_antiguo(self):
        assert _validar_fecha("1999-01-01") is None

    def test_fecha_año_muy_futuro(self):
        assert _validar_fecha("2200-01-01") is None

    def test_fecha_año_limite_inferior(self):
        assert _validar_fecha("2020-01-01") == "2020-01-01"

    def test_fecha_año_limite_superior(self):
        assert _validar_fecha("2100-12-31") == "2100-12-31"

    def test_fecha_invalida_texto(self):
        assert _validar_fecha("mañana") is None


# ── _titulo_fallback ───────────────────────────────────────────────────────────

class TestTituloFallback:

    def test_titulo_normal(self):
        assert _titulo_fallback("Comprar pan", "texto") == "Comprar pan"

    def test_titulo_vacio_usa_transcripcion(self):
        resultado = _titulo_fallback("", "Necesito comprar pan y leche mañana por la mañana")
        assert resultado == "Necesito comprar pan y leche mañana por la mañana"

    def test_titulo_vacio_transcripcion_larga(self):
        transcripcion = "una dos tres cuatro cinco seis siete ocho nueve diez once doce"
        resultado = _titulo_fallback("", transcripcion)
        palabras = resultado.split()
        assert len(palabras) <= 10

    def test_titulo_vacio_transcripcion_vacia(self):
        assert _titulo_fallback("", "") == "Tarea sin título"

    def test_titulo_solo_espacios(self):
        resultado = _titulo_fallback("   ", "Hacer la compra")
        assert resultado == "Hacer la compra"

    def test_titulo_muy_largo_se_trunca(self):
        titulo_largo = "x" * 300
        resultado = _titulo_fallback(titulo_largo, "transcripcion")
        assert len(resultado) <= 255

    def test_titulo_con_espacios_se_limpia(self):
        assert _titulo_fallback("  Comprar pan  ", "texto") == "Comprar pan"