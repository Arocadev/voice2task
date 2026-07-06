"""
JWT Blacklist — tokens invalidados en logout.

Implementación en memoria para desarrollo.
En producción: sustituir _blacklist por Redis (recomendado) o tabla BD.

Uso:
    from app.core.blacklist import blacklist_token, is_token_blacklisted

    blacklist_token(jti, exp)          # al hacer logout
    is_token_blacklisted(jti)          # en get_current_user
"""

import time
from typing import Set, Dict

# { jti: exp_timestamp }
_blacklist: Dict[str, float] = {}


def blacklist_token(jti: str, exp: float) -> None:
    """Añade un token a la blacklist."""
    _blacklist[jti] = exp
    _purge_expired()


def is_token_blacklisted(jti: str) -> bool:
    """Devuelve True si el token está en la blacklist."""
    return jti in _blacklist


def _purge_expired() -> None:
    """Elimina tokens expirados para no crecer indefinidamente."""
    now = time.time()
    expirados = [jti for jti, exp in _blacklist.items() if exp < now]
    for jti in expirados:
        del _blacklist[jti]