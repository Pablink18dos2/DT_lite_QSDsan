# Prompt: Genera la estructura `.claude/` para mi proyecto

> **Instrucciones para Claude Code:** Copia y pega todo el contenido de este archivo como prompt en Claude Code dentro del directorio raíz de tu proyecto.

---

## Prompt

Necesito que analices mi proyecto actual y generes la estructura completa de configuración para Claude Code. Antes de crear los archivos, hazme las preguntas necesarias para personalizar el contenido. Si ya puedes inferir algo del código existente, úsalo directamente.

### Paso 1 — Preguntas previas

Antes de generar nada, analiza el proyecto (lee `package.json`, `Cargo.toml`, `pyproject.toml`, `go.mod`, `Makefile`, `README.md`, o lo que exista) y luego hazme estas preguntas para lo que NO puedas inferir:

1. **Lenguaje y framework principal** — ¿Cuál es el stack? (si no lo puedes detectar automáticamente)
2. **Estilo de código** — ¿Hay un linter/formatter configurado? ¿Alguna convención especial (tabs vs spaces, max line length, naming conventions)?
3. **Estrategia de testing** — ¿Qué framework de tests usan? ¿Cobertura mínima esperada? ¿Tests unitarios, integración, e2e?
4. **Convenciones de API** — ¿REST, GraphQL, gRPC? ¿Versionado de API? ¿Formato de errores?
5. **Flujo de deploy** — ¿Cómo se despliega? (Docker, Kubernetes, Vercel, AWS, manual, CI/CD pipeline?)
6. **Branching strategy** — ¿Git flow, trunk-based, GitHub flow?
7. **Personas del equipo** — ¿Hay roles específicos para los que Claude debería actuar diferente? (reviewer, auditor de seguridad, etc.)
8. **Permisos especiales** — ¿Hay comandos que Claude NO debería ejecutar nunca? (ej: `rm -rf`, deploy a producción, etc.)
9. **Aspectos de seguridad** — ¿Hay secretos, variables de entorno, o patrones que Claude debe tener especial cuidado de no exponer?
10. **Idioma de trabajo** — ¿Las instrucciones y comentarios deben ser en español, inglés u otro idioma?
11. **Docker** — ¿El proyecto ya tiene Dockerfile? ¿Necesita servicios auxiliares (base de datos, cache, colas, etc.)? ¿Qué puerto(s) expone la aplicación? ¿Hay variables de entorno necesarias para arrancar?
12. **Base image preferida** — ¿Alguna preferencia de imagen base? (alpine, slim, distroless, ubuntu) ¿Multi-stage build?
13. **Orquestación** — ¿Docker Compose es suficiente o usan Kubernetes/Swarm/ECS?

### Paso 2 — Genera esta estructura de archivos

Con las respuestas (o con valores inferidos + marcadores `[TODO: ...]` para lo que no sepas), genera **todos** estos archivos:

```
your-project/
├── CLAUDE.md
├── CLAUDE.local.md
├── Dockerfile
├── .dockerignore
├── docker-compose.yml
├── docker-compose.override.yml      ← personal, gitignored
└── .claude/
    ├── settings.json
    ├── settings.local.json
    ├── commands/
    │   ├── review.md
    │   ├── fix-issue.md
    │   ├── deploy.md
    │   └── docker.md
    ├── rules/
    │   ├── code-style.md
    │   ├── testing.md
    │   ├── api-conventions.md
    │   └── docker.md
    ├── skills/
    │   ├── security-review/
    │   │   └── SKILL.md
    │   ├── deploy/
    │   │   └── SKILL.md
    │   └── dockerize/
    │       └── SKILL.md
    └── agents/
        ├── code-reviewer.md
        └── security-auditor.md
```

### Paso 3 — Contenido de cada archivo

A continuación el contenido base que debes usar. **Adapta todo** al proyecto real detectado. Donde veas `[TODO: ...]`, reemplázalo con lo que hayas inferido o déjalo como marcador si no lo sabes.

---

#### `CLAUDE.md` — Instrucciones de equipo (se commitea)

```markdown
# Instrucciones del Proyecto para Claude

## Descripción
[TODO: Describe brevemente qué hace este proyecto, su propósito y contexto]

## Stack Tecnológico
- Lenguaje: [TODO: detectar del proyecto]
- Framework: [TODO: detectar del proyecto]
- Base de datos: [TODO: detectar o preguntar]
- Infraestructura: [TODO: detectar o preguntar]

## Estructura del Proyecto
[TODO: generar un árbol resumido de los directorios principales del proyecto]

## Convenciones Generales
- Idioma del código: [TODO: inglés/español]
- Formato de commits: [TODO: Conventional Commits / otro]
- Branching: [TODO: git flow / trunk-based / github flow]
- PRs: [TODO: requiere review? cuántos approvals?]

## Comandos Clave
- Instalar dependencias: `[TODO: npm install / pip install / cargo build]`
- Ejecutar en desarrollo: `[TODO: npm run dev / cargo run]`
- Ejecutar tests: `[TODO: npm test / pytest / cargo test]`
- Lint / Format: `[TODO: eslint / black / rustfmt]`
- Build producción: `[TODO: npm run build / cargo build --release]`

## Reglas Importantes
- NO hacer commits directamente a `main` o `master`
- NO exponer secretos, claves API ni tokens en el código
- Siempre ejecutar tests antes de proponer cambios
- [TODO: añadir reglas específicas del equipo]

## Patrones del Proyecto
[TODO: describir patrones arquitectónicos usados — MVC, hexagonal, clean architecture, etc.]

## Docker
- Arrancar entorno completo: `docker compose up -d`
- Solo la app: `docker compose up -d app`
- Ver logs: `docker compose logs -f app`
- Reconstruir: `docker compose up -d --build`
- Parar todo: `docker compose down`
- Entrar al contenedor: `docker compose exec app sh`
- Puerto de la app: [TODO: 3000]
- Servicios auxiliares: [TODO: postgres, redis, etc.]

## Dependencias Importantes
[TODO: listar las dependencias clave y para qué se usan]
```

---

#### `CLAUDE.local.md` — Overrides personales (gitignored)

```markdown
# Mis Preferencias Personales (NO commitear)

## Estilo de Respuesta
- Respóndeme en: [TODO: español / inglés]
- Nivel de detalle: [TODO: conciso / detallado / intermedio]
- Cuando propongas código, incluye comentarios explicativos: [TODO: sí / no]

## Mi Entorno Local
- Sistema operativo: [TODO: macOS / Linux / Windows + WSL]
- Editor: [TODO: VS Code / Neovim / IntelliJ]
- Terminal: [TODO: zsh / bash / fish]
- Node version: [TODO: si aplica]
- Python version: [TODO: si aplica]

## Mis Alias y Atajos
[TODO: listar alias de git o terminal que uses frecuentemente]

## Contexto Personal
- Mi rol en el equipo: [TODO: frontend dev / backend dev / fullstack / tech lead]
- Áreas donde necesito más ayuda: [TODO: testing / performance / seguridad / CSS]
- Áreas donde soy experto: [TODO: listar]
```

---

#### `.claude/settings.json` — Permisos y config (se commitea)

```json
{
  "permissions": {
    "allow": [
      "Read",
      "Write",
      "Edit",
      "Bash(npm run *)",
      "Bash(npx *)",
      "Bash(git status)",
      "Bash(git diff *)",
      "Bash(git log *)",
      "Bash(git branch *)"
    ],
    "deny": [
      "Bash(rm -rf *)",
      "Bash(git push --force *)",
      "Bash(git push origin main)",
      "Bash(git push origin master)",
      "Bash(DROP TABLE *)",
      "Bash(kubectl delete *)",
      "Bash(docker system prune -a *)",
      "Bash(docker rm -f $(docker ps -aq))"
    ]
  },
  "model": "sonnet",
  "customInstructions": "Sigue siempre las reglas definidas en .claude/rules/. Antes de hacer cualquier cambio, ejecuta los tests existentes."
}
```

---

#### `.claude/settings.local.json` — Permisos personales (gitignored)

```json
{
  "permissions": {
    "allow": [
      "Bash(docker *)",
      "Bash(docker compose *)",
      "Bash(code *)"
    ]
  }
}
```

---

#### `.claude/commands/review.md` → `/project:review`

```markdown
# Code Review

Revisa los cambios actuales del proyecto como un reviewer senior estricto pero constructivo.

## Instrucciones

1. Ejecuta `git diff --staged` (o `git diff` si no hay staged) para ver los cambios
2. Para cada archivo modificado, evalúa:
   - ¿El código sigue las convenciones de `.claude/rules/code-style.md`?
   - ¿Hay tests para los cambios? ¿Son suficientes?
   - ¿Hay problemas de seguridad? (inyecciones, datos sensibles expuestos, etc.)
   - ¿La lógica es clara y mantenible?
   - ¿Hay edge cases no cubiertos?
3. Presenta tu review en este formato:
   - **Resumen**: qué hacen los cambios en 1-2 frases
   - **Aprobado / Cambios requeridos / Comentarios**
   - **Hallazgos**: listados por severidad (crítico → sugerencia)
4. Si todo está bien, sugiere un mensaje de commit siguiendo Conventional Commits

$ARGUMENTS
```

---

#### `.claude/commands/fix-issue.md` → `/project:fix-issue`

```markdown
# Arreglar Issue

Recibe un número o descripción de issue y trabaja en solucionarlo.

## Instrucciones

1. Lee y comprende el issue: $ARGUMENTS
2. Localiza los archivos relevantes en el proyecto
3. Antes de hacer cambios:
   - Ejecuta los tests actuales para confirmar que pasan
   - Identifica la causa raíz
4. Implementa la solución siguiendo las convenciones del proyecto
5. Escribe o actualiza tests que cubran el fix
6. Ejecuta todos los tests y confirma que pasan
7. Presenta un resumen de los cambios con el formato:
   - **Issue**: descripción breve
   - **Causa raíz**: qué causaba el problema
   - **Solución**: qué se cambió y por qué
   - **Tests**: qué tests se añadieron/modificaron
   - **Commit sugerido**: mensaje en Conventional Commits

$ARGUMENTS
```

---

#### `.claude/commands/deploy.md` → `/project:deploy`

```markdown
# Pre-Deploy Checklist

Valida que todo está listo para desplegar.

## Instrucciones

1. Verifica el entorno de deploy: $ARGUMENTS (staging / production)
2. Ejecuta esta checklist:
   - [ ] Todos los tests pasan
   - [ ] No hay warnings del linter
   - [ ] El build de producción se genera sin errores
   - [ ] No hay secretos hardcodeados en el código
   - [ ] Las migraciones de BD están preparadas (si aplica)
   - [ ] El CHANGELOG está actualizado
   - [ ] La versión está bumpeada (si aplica)
3. Si algo falla, detalla qué y sugiere cómo arreglarlo
4. Si todo pasa, muestra el comando o pasos exactos para desplegar

$ARGUMENTS
```

---

#### `.claude/rules/code-style.md`

```markdown
# Reglas de Estilo de Código

## Generales
- [TODO: tabs o spaces? cuántos?]
- [TODO: max longitud de línea]
- [TODO: comillas simples o dobles]
- [TODO: punto y coma sí o no (JS/TS)]
- Nombres de variables y funciones: [TODO: camelCase / snake_case / PascalCase]
- Nombres de archivos: [TODO: kebab-case / camelCase / snake_case]

## Imports
- [TODO: orden de imports — stdlib, third-party, local]
- [TODO: imports absolutos vs relativos]

## Funciones
- Preferir funciones pequeñas (< 30 líneas idealmente)
- Una función = una responsabilidad
- [TODO: arrow functions vs function declarations]

## Manejo de Errores
- [TODO: try/catch, Result types, error boundaries, etc.]
- Siempre loggear errores con contexto suficiente
- Nunca silenciar errores con catch vacíos

## Comentarios
- Comentar el "por qué", no el "qué"
- [TODO: idioma de los comentarios]
- Los TODOs deben incluir contexto: `// TODO(nombre): descripción del pendiente`

## Tipos (si aplica)
- [TODO: TypeScript strict mode? tipos explícitos vs inferidos?]
- [TODO: evitar `any`? usar `unknown`?]
```

---

#### `.claude/rules/testing.md`

```markdown
# Reglas de Testing

## Framework
- Framework de tests: [TODO: jest / vitest / pytest / go test / cargo test]
- Framework de e2e: [TODO: playwright / cypress / selenium / ninguno]

## Cobertura
- Cobertura mínima: [TODO: 80% / 90% / no hay mínimo]
- Todo bug fix debe incluir un test de regresión

## Estructura de Tests
- Ubicación: [TODO: junto al archivo (__tests__/) / carpeta separada (tests/)]
- Naming: [TODO: *.test.ts / *.spec.ts / test_*.py]
- Patrón: Arrange-Act-Assert (AAA)

## Mocking
- [TODO: cuándo es aceptable mockear? qué no se debe mockear?]
- [TODO: librería de mocking preferida]

## Datos de Test
- Usar factories o fixtures, nunca datos hardcodeados repetidos
- [TODO: hay seeds de base de datos? cómo se manejan?]

## Tests que Claude debe ejecutar
- Antes de cualquier cambio: ejecutar test suite completa
- Después de cambios: ejecutar tests afectados + suite completa
- Comando: `[TODO: npm test / pytest / cargo test]`
```

---

#### `.claude/rules/api-conventions.md`

```markdown
# Convenciones de API

## Tipo de API
- [TODO: REST / GraphQL / gRPC / tRPC]

## REST (si aplica)
- Base URL: [TODO: /api/v1]
- Naming: [TODO: plural nouns, kebab-case — /api/v1/user-profiles]
- Métodos HTTP:
  - GET: lectura (nunca muta estado)
  - POST: creación
  - PUT/PATCH: actualización
  - DELETE: eliminación
- Códigos de respuesta estándar: 200, 201, 204, 400, 401, 403, 404, 422, 500

## Formato de Respuesta
```json
{
  "data": {},
  "meta": { "page": 1, "total": 100 },
  "errors": [{ "code": "VALIDATION_ERROR", "message": "...", "field": "email" }]
}
```

## Autenticación
- [TODO: JWT / OAuth / API Keys / Session]

## Versionado
- [TODO: URL path (/v1/) / header (Accept-Version) / query param]

## Rate Limiting
- [TODO: hay rate limiting? cuáles son los límites?]

## Documentación
- [TODO: OpenAPI/Swagger / GraphQL schema / Protobuf definitions]
```

---

#### `.claude/skills/security-review/SKILL.md`

```markdown
# Skill: Security Review

## Descripción
Revisión automática de seguridad del código.

## Cuándo se Activa
Se activa automáticamente cuando se detectan cambios en:
- Archivos de autenticación o autorización
- Manejo de tokens, sesiones, o credenciales
- Endpoints de API nuevos o modificados
- Queries a base de datos
- Manejo de inputs del usuario
- Configuración de CORS, CSP, o headers de seguridad

## Checklist de Seguridad
- [ ] No hay secretos hardcodeados (API keys, passwords, tokens)
- [ ] Los inputs del usuario están validados y sanitizados
- [ ] Las queries usan parametrización (no concatenación de strings)
- [ ] La autenticación se verifica en cada endpoint protegido
- [ ] Los permisos se validan (autorización)
- [ ] Los datos sensibles se loggean de forma segura (sin PII)
- [ ] Las dependencias no tienen vulnerabilidades conocidas
- [ ] CORS está configurado restrictivamente
- [ ] Los headers de seguridad están presentes (CSP, HSTS, etc.)

## Acciones
1. Escanear archivos modificados buscando los patrones anteriores
2. Ejecutar `[TODO: npm audit / pip audit / cargo audit]` si aplica
3. Reportar hallazgos con severidad: CRÍTICO / ALTO / MEDIO / BAJO
```

---

#### `.claude/skills/deploy/SKILL.md`

```markdown
# Skill: Deploy

## Descripción
Automatización y validación del proceso de deploy.

## Cuándo se Activa
Se activa cuando el usuario menciona deploy, despliegue, release, o publicar.

## Entornos
- **staging**: [TODO: URL y método de deploy]
- **production**: [TODO: URL y método de deploy]

## Pre-requisitos
- Todos los tests pasan
- Build exitoso
- No hay vulnerabilidades críticas
- [TODO: changelog actualizado? version bump? tag de git?]

## Proceso de Deploy
### Staging
```bash
[TODO: comandos de deploy a staging]
```

### Production
```bash
[TODO: comandos de deploy a producción]
```

## Rollback
```bash
[TODO: comandos de rollback]
```

## Monitoreo Post-Deploy
- [TODO: URL del dashboard de monitoreo]
- [TODO: qué métricas verificar después del deploy]
- [TODO: tiempo de espera antes de dar por bueno el deploy]
```

---

#### `.claude/agents/code-reviewer.md`

```markdown
# Agente: Code Reviewer

## Rol
Eres un code reviewer senior con experiencia en [TODO: stack del proyecto]. Tu objetivo es asegurar la calidad del código, la mantenibilidad y el cumplimiento de las convenciones del equipo.

## Personalidad
- Estricto pero constructivo
- Siempre explicas el "por qué" detrás de cada sugerencia
- Priorizas: seguridad > corrección > performance > estilo
- Celebras el buen código cuando lo ves

## Reglas
- Sigue las convenciones de `.claude/rules/`
- Nunca apruebes código sin tests
- Siempre verifica que el código compile/pase lint antes de aprobar
- Sugiere mejoras pero distingue entre "blocker" y "nit"

## Formato de Review
```
### Resumen
[Qué hacen estos cambios en 1-2 frases]

### Veredicto: ✅ Aprobado / ⚠️ Cambios Menores / ❌ Cambios Requeridos

### Hallazgos
🔴 **Crítico**: [descripción]
🟡 **Sugerencia**: [descripción]
🟢 **Bien hecho**: [algo positivo del código]
```
```

---

#### `.claude/agents/security-auditor.md`

```markdown
# Agente: Security Auditor

## Rol
Eres un auditor de seguridad especializado en aplicaciones [TODO: web/móviles/backend]. Tu objetivo es encontrar vulnerabilidades antes de que lleguen a producción.

## Personalidad
- Paranoico por diseño (asumir que todo input es malicioso)
- Metódico y exhaustivo
- Comunica riesgos en términos de impacto de negocio, no solo técnicos

## Checklist OWASP Top 10
1. Broken Access Control
2. Cryptographic Failures
3. Injection
4. Insecure Design
5. Security Misconfiguration
6. Vulnerable Components
7. Authentication Failures
8. Data Integrity Failures
9. Logging & Monitoring Failures
10. Server-Side Request Forgery (SSRF)

## Formato de Reporte
```
### 🔒 Auditoría de Seguridad

**Archivo**: [ruta]
**Severidad**: CRÍTICA / ALTA / MEDIA / BAJA / INFO
**Categoría OWASP**: [número y nombre]

**Descripción**: [qué se encontró]
**Impacto**: [qué podría pasar si se explota]
**Recomendación**: [cómo arreglarlo con ejemplo de código]
```

## Herramientas
- Ejecutar `[TODO: herramienta de audit de dependencias]`
- Buscar patrones peligrosos con grep/ripgrep
- Verificar configuraciones de seguridad en archivos de config
```

---

#### `Dockerfile` — Imagen de producción multi-stage

```dockerfile
# ============================================================
# Dockerfile — Multi-stage build
# [TODO: adaptar a tu stack real]
# ============================================================

# ---- Stage 1: Dependencias ----
# [TODO: elegir la imagen base apropiada]
# Node:    FROM node:20-alpine AS deps
# Python:  FROM python:3.12-slim AS deps
# Go:      FROM golang:1.22-alpine AS deps
# Rust:    FROM rust:1.78-slim AS deps
FROM [TODO: imagen_base] AS deps

WORKDIR /app

# [TODO: copiar solo los ficheros de dependencias para cachear mejor]
# Node:    COPY package.json package-lock.json ./
# Python:  COPY requirements.txt pyproject.toml ./
# Go:      COPY go.mod go.sum ./
# Rust:    COPY Cargo.toml Cargo.lock ./
COPY [TODO: fichero_dependencias] ./

# [TODO: instalar dependencias]
# Node:    RUN npm ci --omit=dev
# Python:  RUN pip install --no-cache-dir -r requirements.txt
# Go:      RUN go mod download
# Rust:    RUN cargo fetch
RUN [TODO: comando_instalar_deps]

# ---- Stage 2: Build ----
FROM deps AS build

WORKDIR /app
COPY . .

# [TODO: comando de build]
# Node:    RUN npm run build
# Go:      RUN CGO_ENABLED=0 go build -o /app/server ./cmd/server
# Rust:    RUN cargo build --release
RUN [TODO: comando_build]

# ---- Stage 3: Runtime (imagen mínima) ----
# [TODO: usar imagen mínima para producción]
# Node:    FROM node:20-alpine AS runtime
# Python:  FROM python:3.12-slim AS runtime
# Go:      FROM gcr.io/distroless/static-debian12 AS runtime
# Rust:    FROM debian:bookworm-slim AS runtime
FROM [TODO: imagen_runtime] AS runtime

# Seguridad: usuario no-root
RUN addgroup --system --gid 1001 appgroup && \
    adduser --system --uid 1001 --ingroup appgroup appuser

WORKDIR /app

# [TODO: copiar artefactos del build]
# Node:    COPY --from=build /app/dist ./dist
#          COPY --from=deps /app/node_modules ./node_modules
# Go:      COPY --from=build /app/server ./server
# Rust:    COPY --from=build /app/target/release/myapp ./myapp
COPY --from=build [TODO: origen] [TODO: destino]

# [TODO: copiar dependencias de runtime si hace falta]
# COPY --from=deps [TODO: origen] [TODO: destino]

USER appuser

# [TODO: puerto(s) que expone tu aplicación]
EXPOSE [TODO: 3000]

# [TODO: healthcheck]
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD [TODO: curl -f http://localhost:3000/health || exit 1]

# [TODO: comando de arranque]
# Node:    CMD ["node", "dist/index.js"]
# Python:  CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
# Go:      CMD ["./server"]
# Rust:    CMD ["./myapp"]
CMD [TODO: comando_arranque]
```

---

#### `.dockerignore` — Excluir del contexto de build

```
# Control de versiones
.git
.gitignore

# Dependencias (se instalan en el build)
node_modules
__pycache__
*.pyc
.venv
venv
target/debug

# IDE y editor
.vscode
.idea
*.swp
*.swo
*~

# Claude Code (no necesario en la imagen)
CLAUDE.md
CLAUDE.local.md
.claude/

# Docker (evitar recursión)
Dockerfile
docker-compose*.yml
.dockerignore

# Tests y docs (no van a producción)
tests/
test/
__tests__/
docs/
*.test.*
*.spec.*
coverage/

# Entorno y secretos
.env
.env.*
!.env.example

# OS
.DS_Store
Thumbs.db

# Logs y temporales
*.log
tmp/
temp/
```

---

#### `docker-compose.yml` — Orquestación de servicios (se commitea)

```yaml
# docker-compose.yml — Configuración base compartida por el equipo
# Para overrides locales usa docker-compose.override.yml (gitignored)

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
      target: runtime                    # usa el stage final
    image: "[TODO: nombre-del-proyecto]:latest"
    container_name: "[TODO: nombre-del-proyecto]-app"
    restart: unless-stopped
    ports:
      - "${APP_PORT:-[TODO: 3000]}:[TODO: 3000]"
    environment:
      - NODE_ENV=production              # [TODO: adaptar a tu stack]
      - DATABASE_URL=${DATABASE_URL:-[TODO: postgres://user:pass@db:5432/mydb]}
      - REDIS_URL=${REDIS_URL:-redis://cache:6379}
    env_file:
      - .env                             # secretos locales (gitignored)
    depends_on:
      db:
        condition: service_healthy
      cache:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "[TODO: curl -f http://localhost:3000/health || exit 1]"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 15s
    networks:
      - app-network

  # [TODO: eliminar si no usas base de datos]
  db:
    image: postgres:16-alpine            # [TODO: cambiar si usas MySQL, Mongo, etc.]
    container_name: "[TODO: nombre-del-proyecto]-db"
    restart: unless-stopped
    volumes:
      - db-data:/var/lib/postgresql/data
      # - ./scripts/init.sql:/docker-entrypoint-initdb.d/init.sql  # [TODO: si tienes script de init]
    environment:
      POSTGRES_USER: ${DB_USER:-[TODO: user]}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-[TODO: password]}
      POSTGRES_DB: ${DB_NAME:-[TODO: mydb]}
    ports:
      - "${DB_PORT:-5432}:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-[TODO: user]}"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - app-network

  # [TODO: eliminar si no usas cache/Redis]
  cache:
    image: redis:7-alpine
    container_name: "[TODO: nombre-del-proyecto]-cache"
    restart: unless-stopped
    volumes:
      - cache-data:/data
    ports:
      - "${REDIS_PORT:-6379}:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - app-network

volumes:
  db-data:
    driver: local
  cache-data:
    driver: local

networks:
  app-network:
    driver: bridge
```

---

#### `docker-compose.override.yml` — Overrides de desarrollo (gitignored)

```yaml
# docker-compose.override.yml — Solo desarrollo local
# Este archivo se aplica automáticamente con `docker compose up`
# NO commitear — cada dev puede tener el suyo

services:
  app:
    build:
      target: deps                       # usa stage de desarrollo con deps completas
    volumes:
      - .:/app                           # hot-reload: monta código fuente
      - /app/node_modules               # [TODO: adaptar — evita pisar deps del contenedor]
    ports:
      - "${APP_PORT:-[TODO: 3000]}:[TODO: 3000]"
      - "${DEBUG_PORT:-9229}:9229"       # [TODO: puerto de debug si aplica]
    environment:
      - NODE_ENV=development             # [TODO: adaptar a tu stack]
      - LOG_LEVEL=debug
    command: [TODO: "npm", "run", "dev"]  # [TODO: comando de dev con hot-reload]

  db:
    ports:
      - "5432:5432"                      # exponer DB para herramientas locales

  # [TODO: Añadir servicios de desarrollo extra]
  # adminer:
  #   image: adminer
  #   ports:
  #     - "8080:8080"
```

---

#### `.env.example` — Variables de entorno de referencia (se commitea)

```bash
# .env.example — Copia este archivo como .env y rellena los valores
# cp .env.example .env

# ── App ──────────────────────────────────────
APP_PORT=[TODO: 3000]
NODE_ENV=development                    # [TODO: adaptar a tu stack]
LOG_LEVEL=debug

# ── Base de datos ────────────────────────────
DATABASE_URL=[TODO: postgres://user:password@localhost:5432/mydb]
DB_USER=[TODO: user]
DB_PASSWORD=[TODO: password]
DB_NAME=[TODO: mydb]
DB_PORT=5432

# ── Cache ────────────────────────────────────
REDIS_URL=redis://localhost:6379
REDIS_PORT=6379

# ── Secretos ─────────────────────────────────
# [TODO: añadir API keys, JWT secrets, etc.]
# JWT_SECRET=
# API_KEY=
# THIRD_PARTY_SECRET=

# ── Servicios externos ──────────────────────
# [TODO: URLs de servicios de los que dependes]
# SMTP_HOST=
# S3_BUCKET=
```

---

#### `.claude/commands/docker.md` → `/project:docker`

```markdown
# Docker Management

Gestiona el entorno Docker del proyecto.

## Instrucciones

Según la acción solicitada ($ARGUMENTS), ejecuta lo que corresponda:

### `up` — Arrancar el entorno
1. Verifica que Docker/Docker Compose están instalados: `docker compose version`
2. Verifica que existe `.env` (si no, cópialo de `.env.example` y avisa)
3. Ejecuta `docker compose up -d --build`
4. Espera a que todos los healthchecks pasen
5. Muestra el estado: `docker compose ps`
6. Muestra los URLs de acceso (app, adminer, etc.)

### `down` — Parar el entorno
1. Ejecuta `docker compose down`
2. Confirma que todos los contenedores están parados

### `logs` — Ver logs
1. Ejecuta `docker compose logs -f --tail=100 [servicio]`

### `rebuild` — Reconstruir desde cero
1. Ejecuta `docker compose down`
2. Ejecuta `docker compose build --no-cache`
3. Ejecuta `docker compose up -d`
4. Verifica healthchecks

### `status` — Estado completo
1. `docker compose ps` — contenedores activos
2. `docker compose top` — procesos
3. `docker system df` — uso de disco
4. Verificar healthchecks de cada servicio

### `shell` — Entrar a un contenedor
1. Ejecuta `docker compose exec [servicio] /bin/sh`

### `clean` — Limpiar (con confirmación)
1. PREGUNTA antes de ejecutar: "Esto eliminará contenedores parados, imágenes huérfanas y caché de build. ¿Confirmas?"
2. Si confirma: `docker compose down -v && docker system prune -f`

$ARGUMENTS
```

---

#### `.claude/rules/docker.md`

```markdown
# Reglas de Docker

## Dockerfile
- Siempre usar multi-stage builds para separar build de runtime
- La imagen final debe usar un usuario NO-root (`appuser`)
- Nunca copiar `.env`, secretos, ni `.git` al contexto de build
- Verificar que `.dockerignore` excluye todo lo innecesario
- Ordenar las instrucciones de menos a más cambiante (cacheo de capas)
- Copiar primero ficheros de dependencias, luego `RUN install`, luego el código
- Siempre incluir `HEALTHCHECK`
- Etiquetar con `LABEL` el maintainer y la versión
- Preferir imágenes `-alpine` o `-slim` salvo que haya incompatibilidades
- [TODO: imagen base preferida del equipo]

## Docker Compose
- `docker-compose.yml` es la configuración base y se commitea
- `docker-compose.override.yml` es personal y va en `.gitignore`
- Todo secreto va en `.env` (gitignored), nunca hardcodeado en el compose
- Siempre definir `healthcheck` en cada servicio
- Usar `depends_on` con `condition: service_healthy`
- Siempre nombrar los contenedores (`container_name`) para facilitar debugging
- Los volúmenes de datos deben ser named volumes, no bind mounts para datos persistentes

## Seguridad
- Nunca ejecutar contenedores como root en producción
- No exponer puertos de base de datos al host en producción
- Escanear imágenes periódicamente: `docker scout cves [imagen]`
- No usar `latest` como tag en producción — usar versiones fijadas
- [TODO: registry privado del equipo? política de tags?]

## Desarrollo Local
- Usar bind mounts para hot-reload en desarrollo (override)
- El `docker-compose.override.yml` puede exponer puertos de debug
- Comandos útiles:
  - Arrancar: `docker compose up -d`
  - Ver logs: `docker compose logs -f app`
  - Reconstruir: `docker compose up -d --build`
  - Entrar: `docker compose exec app sh`
  - Parar: `docker compose down`
  - Limpiar todo: `docker compose down -v`
```

---

#### `.claude/skills/dockerize/SKILL.md`

```markdown
# Skill: Dockerize

## Descripción
Detecta y resuelve problemas de Docker, optimiza imágenes y mantiene la containerización sana.

## Cuándo se Activa
Se activa automáticamente cuando:
- Se modifican `Dockerfile`, `docker-compose.yml` o `.dockerignore`
- Se añaden nuevas dependencias al proyecto
- Se cambian puertos, variables de entorno, o configuración de servicios
- El usuario menciona Docker, contenedores, imágenes, o compose

## Validaciones Automáticas
1. **Dockerfile lint**: verificar buenas prácticas
   - ¿Multi-stage? ¿Usuario no-root? ¿Healthcheck?
   - ¿El `.dockerignore` excluye todo lo necesario?
   - ¿Las capas están ordenadas para cacheo óptimo?
2. **Compose lint**: verificar la configuración
   - ¿Todos los servicios tienen healthcheck?
   - ¿Las variables sensibles usan `.env`, no están hardcodeadas?
   - ¿Los `depends_on` usan `condition: service_healthy`?
3. **Tamaño de imagen**: comprobar que no sea excesivamente grande
   - Ejecutar `docker images` y comparar tamaño
   - Sugerir optimizaciones si > [TODO: 500MB]
4. **Seguridad**:
   - Ejecutar `docker scout cves` si está disponible
   - Verificar que no se copian secretos al build context

## Acciones
- Si se añade una dependencia de sistema: actualizar Dockerfile
- Si se cambia un puerto: actualizar `EXPOSE`, compose y `.env.example`
- Si se añade un servicio (ej: nuevo microservicio): generar su sección en compose
- Siempre mantener `.env.example` sincronizado con las variables reales usadas
```

---

### Paso 4 — Configurar `.gitignore`

Añade estas líneas al `.gitignore` del proyecto si no existen:

```
# Claude Code - archivos personales
CLAUDE.local.md
.claude/settings.local.json

# Docker - overrides locales
docker-compose.override.yml

# Variables de entorno (secretos)
.env
.env.local
.env.*.local
!.env.example
```

---

### Paso 5 — Verificación final

Después de crear todos los archivos:

1. Muéstrame un `tree` de la estructura generada
2. Lista los `[TODO: ...]` que quedaron pendientes para que los complete
3. Confirma que `.gitignore` está actualizado
4. Haz un resumen de qué archivos se commitean y cuáles no
5. Verifica Docker:
   - Ejecuta `docker build -t test-build .` y confirma que compila sin errores
   - Ejecuta `docker compose config` y confirma que el compose es válido
   - Si el build falla, arréglalo antes de terminar

---

**¡Empieza analizando el proyecto y haciéndome las preguntas del Paso 1!**
