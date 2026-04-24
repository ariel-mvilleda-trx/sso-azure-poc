"""
API B Backend - Valida ID Tokens JWT emitidos por Azure Entra ID (CIAM)
Segunda API para demostrar autenticación multi-API
"""

import os
from typing import Optional

import httpx
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

# Cargar variables de entorno desde .env
load_dotenv()

app = FastAPI(title="Protected API B")

# ============================================
# CONFIGURACIÓN DESDE VARIABLES DE ENTORNO
# ============================================
TENANT_ID = os.getenv("TENANT_ID")
API_B_CLIENT_ID = os.getenv("API_B_CLIENT_ID")
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS", "http://localhost:5500,http://127.0.0.1:5500"
).split(",")

# CORS - Configurar según tus dominios en producción
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# Audiences válidos (Azure puede usar el client_id o api://{client_id})
VALID_AUDIENCES = [
    API_B_CLIENT_ID,
    f"api://{API_B_CLIENT_ID}",
]

# JWKS URL para obtener las claves públicas
JWKS_URL = f"https://{TENANT_ID}.ciamlogin.com/{TENANT_ID}/discovery/v2.0/keys"

# Issuer esperado en los tokens
ISSUER = f"https://{TENANT_ID}.ciamlogin.com/{TENANT_ID}/v2.0"

# Cache de las claves JWKS
_jwks_cache: Optional[dict] = None


async def get_jwks():
    """Obtiene las claves públicas de Azure para validar tokens"""
    global _jwks_cache
    if _jwks_cache is None:
        async with httpx.AsyncClient() as client:
            response = await client.get(JWKS_URL, timeout=10.0)
            response.raise_for_status()
            _jwks_cache = response.json()
    return _jwks_cache


async def validate_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> dict:
    """Valida el Access Token JWT y retorna los claims del usuario"""
    token = credentials.credentials

    try:
        jwks = await get_jwks()
        unverified_header = jwt.get_unverified_header(token)

        # Buscar la key correcta por kid
        rsa_key = None
        for key in jwks.get("keys", []):
            if key.get("kid") == unverified_header.get("kid"):
                rsa_key = key
                break

        if not rsa_key:
            raise HTTPException(status_code=401, detail="Signing key not found")

        # Intentar validar con cada audience válido
        payload = None
        last_error = None
        for audience in VALID_AUDIENCES:
            try:
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=["RS256"],
                    audience=audience,
                    issuer=ISSUER,
                )
                break
            except JWTError as e:
                last_error = e
                continue

        if not payload:
            raise last_error or JWTError("Invalid audience")

        return payload

    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")


@app.get("/")
def root():
    return {"message": "API B is running", "docs": "/docs"}


@app.get("/debug-token")
async def debug_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Debug: ver contenido del token"""
    token = credentials.credentials
    try:
        header = jwt.get_unverified_header(token)
        claims = jwt.get_unverified_claims(token)
        return {
            "header": header,
            "issuer": claims.get("iss"),
            "audience": claims.get("aud"),
            "expected_issuer": ISSUER,
            "expected_audiences": VALID_AUDIENCES,
            "has_nonce": "nonce" in header,
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/me")
async def get_current_user(claims: dict = Security(validate_token)):
    """Retorna información del usuario autenticado desde API B"""
    return {
        "source": "API B",
        "token_claims": claims,
        "user_id": claims.get("sub"),
        "email": claims.get("preferred_username"),
        "name": claims.get("name"),
    }


@app.get("/protected")
async def protected_endpoint(claims: dict = Security(validate_token)):
    """Endpoint protegido de ejemplo"""
    return {
        "source": "API B",
        "message": f"Hello from API B, {claims.get('name', 'user')}!",
        "user_id": claims.get("sub"),
    }


if __name__ == "__main__":
    uvicorn.run(app, port=int(os.getenv("PORT_B", 8002)), host="0.0.0.0")
