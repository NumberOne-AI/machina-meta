# Environment Variables Reference

This document describes all environment variables expected by the dem2 backend services.

## Database

POSTGRES_HOST: PostgreSQL server hostname
POSTGRES_PORT: PostgreSQL server port
POSTGRES_USER: PostgreSQL username (required)
POSTGRES_PASSWORD: PostgreSQL password (required)
POSTGRES_DB: PostgreSQL database name (required)

DYNACONF_NEO4J_DB__HOST: Neo4j server hostname
DYNACONF_NEO4J_DB__PORT: Neo4j bolt port
DYNACONF_NEO4J_DB__USER: Neo4j username
DYNACONF_NEO4J_DB__PASSWORD: Neo4j password (required)

DYNACONF_REDIS_DB__HOST: Redis connection URL

DYNACONF_QDRANT__HOST: Qdrant server hostname
DYNACONF_QDRANT__PORT: Qdrant server port

## Authentication & Security

DYNACONF_AUTH__JWT_SECRET_KEY: JWT token signing secret, min 32 characters (required)
DYNACONF_GOOGLE_AUTH__CLIENT_SECRET: Google OAuth client secret (required)
DYNACONF_CALENDAR__OAUTH_CLIENT_ID: Google Calendar OAuth client ID
DYNACONF_CALENDAR__OAUTH_CLIENT_SECRET: Google Calendar OAuth client secret

## LLM API Keys

OPENAI_API_KEY: OpenAI API key
DYNACONF_OPENAI__API_KEY: OpenAI API key for dynaconf config
GOOGLE_API_KEY: Google AI (Gemini) API key
GEMINI_API_KEY: Gemini API key (alternative)
SERPER_API_KEY: Serper search API key
GOOGLE_SEARCH_API_KEY: Google Custom Search API key
VISION_AGENT_API_KEY: Vision agent API key

## Services

DYNACONF_MEDCAT__HOST: Medical catalog service hostname
DYNACONF_MEDCAT__PORT: Medical catalog service port

## Frontend

NEXT_PUBLIC_API_URL: Backend API base URL
NEXT_PUBLIC_API_BASE_URL: Backend base URL
NEXT_PUBLIC_WS_URL: WebSocket URL
NEXT_PUBLIC_BASE_URL: Frontend base URL
NEXT_PUBLIC_APP_NAME: Application display name
NEXT_PUBLIC_LOGIN_APP_NAME: Login page app name

## Testing

USER_GOOGLE_SSO_PASSWORD: Test user Google SSO password

## System

SSL_CERT_FILE: SSL certificate file path
TZ: Timezone (recommended: UTC)
