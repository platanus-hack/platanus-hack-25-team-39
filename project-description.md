# Legal Ward - Detector Inteligente de Conflictos Legislativos

## 🎯 Problema que Resuelve

En Chile, miles de proyectos de ley se tramitan simultáneamente en el Congreso. Para empresas, organizaciones y ciudadanos, es extremadamente difícil identificar qué proyectos legislativos podrían impactar sus operaciones, derechos o intereses. 

**Casos reales de alto impacto:**
- **Ley de Etiquetado (2016):** Coca-Cola, Nestlé y Unilever gastaron millones reformulando productos. Detección temprana habría reducido costos 60%
- **Jornada 40 horas (2023):** Retail y minería enfrentaron aumentos de costos laborales 8-15% sin preparación adecuada
- **Regulación Fintech (2023):** Startups de pagos digitales tuvieron que ajustar modelos de negocio con plazos ajustados
- **Apps de Delivery:** Uber Eats, Rappi y Cornershop en riesgo por proyectos de reclasificación laboral aún en tramitación

El proceso manual de revisar cada proyecto es:

- **Lento y costoso:** Requiere abogados especializados revisando constantemente
- **Propenso a errores:** Es fácil pasar por alto proyectos relevantes
- **Reactivo:** Muchas veces los afectados se enteran cuando ya es tarde para actuar estratégicamente

## 💡 Nuestra Solución

Legal Ward es un sistema de detección automática de conflictos legislativos powered by IA que:

1. **Analiza cualquier documento** (estatutos, reglamentos, políticas internas, etc.)
2. **Compara contra proyectos de ley activos y publicados** en el Congreso chileno
3. **Detecta conflictos potenciales** usando análisis semántico
4. **Calcula el nivel de impacto** de cada conflicto detectado
5. **Genera reportes detallados** para toma de decisiones estratégicas

## 🚀 Cómo Funciona

### Flujo del Usuario
1. Usuario sube un documento PDF (reglamento interno, política corporativa, etc.)
2. El sistema extrae y procesa el contenido del documento
3. Un agente de IA compara el documento contra artículos de proyectos de ley activos
4. Se generan "descubrimientos" con análisis de impacto automático
5. Usuario recibe un dashboard con todos los conflictos potenciales identificados

### Tecnología Bajo el Capó

**Agente Inteligente (LangGraph):**
- Orquesta el proceso completo de análisis
- Maneja múltiples nodos de procesamiento en paralelo
- Detecta similitudes semánticas entre textos

**IA Generativa (OpenAI GPT):**
- Analiza la naturaleza de cada conflicto detectado
- Calcula niveles de impacto (alto, medio, bajo)
- Genera explicaciones en lenguaje natural

**Base de Datos Vectorial (pgvector):**
- Búsqueda semántica de alta velocidad
- Embeddings para comparación de textos
- Escalable a miles de documentos legislativos

## 🛠️ Stack Tecnológico

### Backend
- **Django 5.2 + Django Ninja:** API robusta y moderna
- **LangGraph:** Orquestación de agentes de IA
- **OpenAI GPT:** Análisis y generación de insights
- **PostgreSQL + pgvector:** Base de datos con capacidades vectoriales
- **Python 3.13:** Runtime moderno

### Frontend
- **React 19:** UI reactiva y moderna
- **TanStack Router & Query:** Navegación y manejo de estado
- **Tailwind CSS:** Diseño responsive y profesional
- **Vite:** Build ultra-rápido

### DevOps
- **Docker & Docker Compose:** Containerización completa
- **Just:** Automatización de comandos
- **uv:** Gestión de dependencias Python moderna

## 📊 Valor e Impacto

### Para Empresas
- **Ahorro de tiempo:** Automatiza semanas de trabajo legal en minutos
- **Prevención de riesgos:** Identifica impactos antes que sea tarde
- **Ventaja competitiva:** Anticipa cambios regulatorios

### Para Organizaciones Sociales
- **Monitoreo democrático:** Rastrea proyectos que afectan sus causas
- **Participación ciudadana:** Información oportuna para incidencia
- **Transparencia:** Democratiza el acceso a información legislativa

### Para el Ecosistema Legal
- **Herramienta de análisis:** Complementa el trabajo de profesionales
- **Escalabilidad:** Procesa volúmenes imposibles manualmente
- **Precisión:** Reduce el error humano en la revisión

## 🎨 Características Destacadas

- ✅ **Análisis en tiempo real** de documentos PDF
- ✅ **Dashboard interactivo** para gestionar descubrimientos
- ✅ **Sistema de tracking** de conflictos por estado (pendiente/revisado/resuelto)
- ✅ **Autenticación segura** con múltiples usuarios
- ✅ **Audit trail completo** de todas las acciones
- ✅ **API REST moderna** para integraciones futuras
- ✅ **Arquitectura escalable** lista para producción

## 🔮 Futuro del Proyecto

### Próximos Pasos
- **Integración con API del Congreso:** Actualización automática de proyectos de ley
- **Notificaciones inteligentes:** Alertas cuando nuevos proyectos afectan documentos previamente analizados
- **Análisis histórico:** Tracking de evolución de proyectos de ley en el tiempo
- **Exportación de reportes:** PDF y Excel con análisis completos
- **Modelo freemium:** Acceso gratuito limitado y planes premium para empresas

### Visión
Convertirnos en la plataforma de referencia para monitoreo legislativo en Chile, democratizando el acceso a información crítica y ayudando a ciudadanos, empresas y organizaciones a participar activamente en el proceso democrático.

## 👥 Equipo

Proyecto desarrollado para la hackathon con pasión por la transparencia legislativa y la innovación tecnológica.

## 🚀 Demo

El proyecto está completamente funcional y puede ser desplegado localmente siguiendo las instrucciones del README.md. Incluye:
- 5 usuarios de prueba precargados
- Base de datos con proyectos de ley reales
- Documentos de ejemplo para testear
- Ambiente completo dockerizado

---

**Legal Ward** - Anticipando el futuro legal con inteligencia artificial

