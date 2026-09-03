"""Autenticação e sessão do Automatic1 Admin (feature 006).

Segredos por **variáveis de ambiente**, lidos por requisição (rotacionáveis e
testáveis): senha do operador, segredo de sessão e token de API. Nada é
persistido no banco (constituição IV).
"""
import hmac
import os

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

COOKIE_SESSAO = "automatic1_session"
_TTL_PADRAO = 8 * 60 * 60  # 8h


def _getenv(nome: str) -> str | None:
    valor = os.getenv(nome)
    return valor.strip() if valor else None


def esta_configurado() -> bool:
    """True quando senha e segredo de sessão existem (FR-007: nunca vazio)."""
    return bool(_getenv("AUTOMATIC1_ADMIN_PASSWORD") and _getenv("AUTOMATIC1_SESSION_SECRET"))


def senha_valida(senha: str) -> bool:
    """Compara a senha informada com a do ambiente de forma segura."""
    esperada = _getenv("AUTOMATIC1_ADMIN_PASSWORD")
    if not esperada or not senha:
        return False
    return hmac.compare_digest(esperada.encode(), senha.encode())


def _serializador() -> URLSafeTimedSerializer | None:
    segredo = _getenv("AUTOMATIC1_SESSION_SECRET")
    if not segredo:
        return None
    return URLSafeTimedSerializer(segredo, salt="automatic1-session")


def _ttl() -> int:
    try:
        return int(os.getenv("AUTOMATIC1_SESSION_TTL", str(_TTL_PADRAO)))
    except ValueError:
        return _TTL_PADRAO


def criar_sessao() -> str:
    """Gera o valor assinado do cookie de sessão ("" se não configurado)."""
    ser = _serializador()
    return ser.dumps({"op": 1}) if ser else ""


def sessao_valida(cookie: str | None) -> bool:
    """True se o cookie de sessão é assinado e não expirou."""
    if not cookie:
        return False
    ser = _serializador()
    if ser is None:
        return False
    try:
        ser.loads(cookie, max_age=_ttl())
        return True
    except (BadSignature, SignatureExpired):
        return False


def token_api_valido(token: str) -> bool:
    """Compara o token da API com o do ambiente de forma segura."""
    esperado = _getenv("AUTOMATIC1_API_TOKEN")
    if not esperado or not token:
        return False
    return hmac.compare_digest(esperado.encode(), token.encode())


def cookie_secure() -> bool:
    """Cookie com flag Secure quando atrás de HTTPS (ex.: deploy no Render)."""
    return os.getenv("AUTOMATIC1_COOKIE_SECURE", "0") == "1"
