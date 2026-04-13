# Azure Entra ID SSO POC

Proof of Concept para autenticación Single Sign-On con Azure Entra ID (CIAM).

## ¿Qué hace?

- **Frontend (SPA)**: Página HTML que autentica usuarios con Microsoft usando MSAL.js
- **Backend (API)**: Servicio FastAPI que valida tokens JWT y retorna información del usuario
- **Flow**: Usuario inicia sesión → obtiene token → llama API protegida

## Requisitos

- Docker y Docker Compose
- O: Python 3.12+ (sin Docker)

## Setup

### Opción 1: Con Docker (recomendado)

```bash
# Copiar template de variables
cp .env.example .env

# Editar .env con tus valores de Azure
# TENANT_ID, API_CLIENT_ID, CORS_ORIGINS

# Levantar servicios
docker-compose up --build
```

**Acceso**:
- Frontend: http://localhost:5500
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Opción 2: Local sin Docker

**Backend**:
```bash
# Ambiente virtual
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/macOS

# Instalar dependencias
pip install -r requirements.txt

# Configurar
cp .env.example .env
# Editar .env

# Ejecutar
python api.py
```

**Frontend**:
En otra terminal, servir el HTML (necesita CORS):

```bash
# Python
python -m http.server 5500

# O Node.js
npx http-server -p 5500
```

## Endpoints API

**Públicos**:
- `GET /` - Health check
- `GET /api/config` - Configuración pública

**Protegidos** (requieren Bearer token):
- `GET /me` - Info del usuario autenticado
- `GET /protected` - Endpoint de ejemplo
- `GET /debug-token` - Debug del token (temporalmente)

## Variables de Entorno

| Variable | Descripción |
|----------|-------------|
| `TENANT_ID` | ID del tenant CIAM en Azure |
| `API_CLIENT_ID` | Client ID de la app API |
| `CORS_ORIGINS` | Origins permitidos (ej: http://localhost:5500) |
| `PORT` | Puerto de la API (default: 8000) |

## Estructura

```
.
├── api.py              # Backend FastAPI
├── index.html          # Frontend SPA
├── requirements.txt    # Dependencias Python
├── Dockerfile          # Imagen Docker
├── docker-compose.yml  # Orquestación
├── nginx.conf          # Config Nginx
├── .env                # Variables (NO commitear)
├── .env.example        # Template
└── .dockerignore       # Archivos a excluir
```

## Testing

Desde el frontend, clickear "Iniciar Sesión" → Autenticarse con Microsoft → Usar botón "Llamar API /me"

## Detener

```bash
# Con Docker
docker-compose down

# Local
Ctrl+C en ambas terminales
```

---

**Última actualización**: 2026-04-13
