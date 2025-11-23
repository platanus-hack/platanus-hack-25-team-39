**Current project logo:** project-logo.png
<img src="./project-logo.png" alt="Project Logo" width="200" />

# Legal Ward
## team-39 Platanus Hack Project

Sistema inteligente de detección de conflictos legislativos powered by IA.

Submission Deadline: 23rd Nov, 9:00 AM, Chile time.

Track: ☎️ legacy

team-39

- Felipe Mellado ([@Phiripp](https://github.com/Phiripp))
- Brayan Moreno ([@brayanmoreno](https://github.com/brayanmoreno))
- Tomás Werth ([@Tomas-Werth](https://github.com/Tomas-Werth))
- Tomás Morales ([@tom-morales](https://github.com/tom-morales))

## Descripción

Legal Ward analiza documentos PDF contra proyectos de ley activos del Congreso chileno, detectando automáticamente conflictos potenciales y calculando su nivel de impacto usando agentes de IA y modelos de lenguaje.

## Stack Tecnológico

### Backend
- **Django 5.2** - Framework web
- **Django Ninja** - API REST
- **LangGraph** - Orquestación de agentes IA
- **OpenAI** - Análisis de conflictos con LLM
- **PostgreSQL + pgvector** - Base de datos con búsqueda vectorial
- **Python 3.13** - Runtime

### Frontend
- **React 19** - Framework UI
- **TanStack Router** - Routing
- **TanStack Query** - Gestión de datos
- **Tailwind CSS** - Estilos
- **Vite** - Build tool
- **pnpm** - Package manager

## Prerequisitos

- Docker & Docker Compose
- [Just](https://github.com/casey/just) command runner
- [pnpm](https://pnpm.io/) para el frontend
- [uv](https://github.com/astral-sh/uv) para el backend
- API key de OpenAI

## Instalación

### 1. Instalar Dependencias del Backend

```bash
cd backend
uv lock
```

### 2. Instalar Dependencias del Frontend

```bash
cd frontend
pnpm install
```

### 3. Configurar API Key de OpenAI

Edita el archivo `local/conf/default` y agrega tu API key de OpenAI:

```bash
PROJECT_OPENAI_API_KEY=tu-api-key-aqui
```

**IMPORTANTE:** Necesitas una API key válida de OpenAI para procesar archivos.

### 4. Levantar el Entorno de Desarrollo

Desde la carpeta `local`:

```bash
cd local
just build && just up
```

Esto iniciará:
- PostgreSQL con pgvector (puerto 5432)
- Backend Django (puerto 8000)
- Frontend React (puerto 3000)

### 5. Ejecutar Migraciones

```bash
just migrate
```

Esto creará las tablas de la base de datos y cargará los proyectos de ley iniciales desde `backend/data/proyectos_ley/`.

## Desarrollo

### Comandos Disponibles

Desde la raíz del proyecto:

```bash
# Iniciar entorno local completo
just dev local

# Iniciar solo frontend
just dev frontend

# Construir imagen Docker del backend
just team-build
```

Desde la carpeta `local`:

```bash
# Construir y levantar servicios
just build && just up

# Levantar servicios
just up

# Detener servicios
just down

# Ver logs
just logs

# Ejecutar migraciones
just migrate
```

### Acceso a la Aplicación

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/api/docs
- **Django Admin:** http://localhost:8000/admin

### Credenciales de Prueba

Desde la carpeta local

```
just createsuperuser
```

crea una cuenta con un formato mail valido y contraseña.

## Cómo Funciona

1. **Subida de Documento:** El usuario sube un PDF a través del frontend
2. **Extracción de Texto:** El backend extrae texto de cada página usando PyMuPDF
3. **Procesamiento del Agente:** LangGraph orquesta el análisis:
   - Carga todos los proyectos de ley y artículos de la base de datos
   - Compara las páginas del documento contra artículos legislativos
   - Detecta conflictos potenciales usando similitud semántica
4. **Cálculo de Impacto:** OpenAI analiza cada conflicto y calcula niveles de impacto
5. **Almacenamiento:** Los conflictos se guardan como "descubrimientos" en la BD
6. **Revisión:** El usuario puede revisar, rastrear y gestionar los conflictos detectados

## Estructura del Proyecto

```
test-legal-ward/
├── backend/
│   ├── apps/
│   │   ├── conflict_detector/    # Lógica de detección de conflictos
│   │   │   ├── agent/            # Implementación del agente LangGraph
│   │   │   ├── api.py            # Endpoints de la API
│   │   │   ├── models.py         # Modelos de base de datos
│   │   │   └── services.py       # Lógica de negocio
│   │   ├── proyectos_ley/        # Gestión de proyectos legislativos
│   │   ├── users/                # Autenticación de usuarios
│   │   └── auditlog/             # Registro de auditoría
│   ├── conf/                     # Configuración de Django
│   ├── data/                     # Datos iniciales (proyectos de ley)
│   └── manage.py
├── frontend/
│   ├── src/
│   │   ├── routes/               # Rutas de la aplicación
│   │   ├── components/           # Componentes React
│   │   ├── services/             # Clientes API
│   │   └── contexts/             # Contextos React
│   └── package.json
└── local/
    ├── docker-compose.yml        # Setup de desarrollo local
    └── conf/
        └── default               # Variables de entorno
```

## Características Principales

- **Análisis con IA:** Usa OpenAI y LangGraph para detección inteligente de conflictos
- **Búsqueda Vectorial:** pgvector permite búsqueda por similitud semántica
- **Procesamiento Asíncrono:** Vistas async de Django para mejor rendimiento
- **Autenticación Segura:** Django Allauth para gestión de usuarios
- **Registro de Auditoría:** Log completo de todas las acciones
- **Gestión de Documentos:** Rastrea y administra todos los documentos analizados
- **Evaluación de Impacto:** Cálculo automático del nivel de impacto de cada conflicto

## Resolución de Problemas

### Error: "No se puede conectar a la base de datos"
Asegúrate de que los servicios de Docker estén corriendo:
```bash
cd local
docker-compose ps
```

### Error: "Invalid API key"
Verifica que hayas configurado correctamente `PROJECT_OPENAI_API_KEY` en `local/conf/default`.

### El frontend no carga
Asegúrate de haber ejecutado `pnpm install` en la carpeta `frontend/`.

### Las migraciones fallan
Asegúrate de que PostgreSQL esté corriendo y ejecuta:
```bash
cd local
just down
just up
just migrate
```

## Licencia

Proyecto creado para hackathon.

## Contribuidores

Desarrollado con dedicación para mejorar la transparencia legislativa en Chile.

