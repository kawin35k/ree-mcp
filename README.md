# ⚡ REE MCP Server

<div align="center">

[![CI/CD](https://github.com/ESJavadex/ree-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/ESJavadex/ree-mcp/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](http://mypy-lang.org/)

</div>

> Habla con la red eléctrica española a través de Claude - sin conocimientos técnicos

Un servidor **MCP (Model Context Protocol)** listo para producción que te permite consultar datos de electricidad en España usando lenguaje natural. Pregunta a Claude sobre demanda, generación, precios y emisiones - él se encarga de todos los detalles técnicos.

Construido con **Domain-Driven Design**, **Clean Architecture** y **testing exhaustivo** por [Javi Santos](https://www.linkedin.com/in/francisco-javier-santos-criado/) - Especialista en IA y Robótica con investigación publicada en visión por computador e interpretabilidad de LLMs.

> 💡 **¿Quieres aprender a construir proyectos así?** Únete a [La Escuela de IA](https://skool.com/la-escuela-de-ia-9955) - la comunidad donde aprenderás IA práctica, sin humo, con ejemplos reales en español.

---

## 🎯 ¿Por qué existe esto?

**Red Eléctrica de España (REE)** gestiona la red eléctrica española 24/7, publicando datos cada 5 minutos. Este servidor MCP hace esos datos accesibles mediante conversación natural con Claude.

### Por qué lo construí

*Por [Javi Santos](https://www.linkedin.com/in/francisco-javier-santos-criado/)*

Quería **democratizar el acceso** a datos críticos de infraestructura. En lugar de escribir scripts de Python, quería conversaciones como esta:

**Tú:** *"Comprueba qué pasó el 28 de abril de 2025"*

**Claude:** *Analiza datos de la red...*

🚨 **EVENTO CRÍTICO DETECTADO - 28 de Abril de 2025 a las 12:35h**

**Colapso Masivo de la Red:**
- **11.000 MW perdidos en 5 minutos** (caída del 43% de capacidad)
- El sistema cayó de 25.184 MW → 14.185 MW instantáneamente
- Compatible con escenario de apagón en cascada
- La recuperación tardó más de 10 horas

**Análisis:**
- 11:00-12:30: Sistema estable, sin avisos previos
- 12:30-12:35: Fallo catastrófico instantáneo
- 12:35-13:35: Degradación continua hasta mínimo de 9.635 MW
- Causa probable: Disparo de planta nuclear → colapso de frecuencia → cascada

*Este sería uno de los peores apagones de España en la historia moderna.*

---

**Ese es el poder de este servidor MCP.** Puedes investigar eventos en la red, analizar tendencias renovables vs fósiles, correlacionar precios con demanda, o seguir la descarbonización de España - todo mediante conversación natural con Claude.

Sin documentación de API. Sin scripts de Python. Solo pregunta.

---

## 🚀 Inicio Rápido

Funcional en 3 minutos:

### 1️⃣ Clonar e Instalar

```bash
# Clonar el repositorio
git clone https://github.com/ESJavadex/ree-mcp.git
cd ree-mcp

# Instalar uv (gestor rápido de paquetes Python)
curl -LsSf https://astral.sh/uv/install.sh | sh
# O en macOS: brew install uv

# Crear entorno virtual e instalar dependencias
uv venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

### 2️⃣ Configurar Token de API

```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar .env y añadir tu token (incluye token demo para pruebas)
# REE_API_TOKEN=tu_token_aqui
```

**Obtener un Token de API:**
- **Pruebas/Demo**: El repositorio incluye un token demo en `.env.example`
- **Producción**: Envía email a consultasios@ree.es para solicitar tu token de API de REE

### 3️⃣ Añadir a Claude Code

```bash
# Ejecutar el script de instalación (lee el token de .env automáticamente)
./INSTALL_COMMAND.sh

# Verificar instalación
claude mcp list
```

Deberías ver `ree-mcp: ✓ Connected` en la salida.

### 4️⃣ ¡Empieza a Usar Claude!

Abre Claude Code y prueba:
- *"Muéstrame la demanda eléctrica actual de España"*
- *"¿Cuál es el mix de generación ahora?"*
- *"Compara generación solar vs eólica hoy"*
- *"Busca indicadores de precio"*

---

## 💬 ¿Qué Puedes Preguntarle a Claude?

Una vez instalado, Claude puede responder preguntas como:

### 📊 Operaciones de la Red
- *"¿Cuál es la demanda eléctrica de España ahora mismo?"*
- *"Muéstrame el mix de generación al mediodía de ayer"*
- *"¿Cuánta energía exportó España el martes pasado?"*
- *"Compara la demanda de hoy con la semana pasada"*

### 🔍 Investigación y Análisis
- *"Investiga qué pasó el 28 de abril de 2025"* → Claude analiza eventos de colapso de red
- *"¿Hubo alguna actividad inusual en la red el mes pasado?"*
- *"Encuentra el día de pico de demanda este año y explica por qué"*
- *"Analiza la correlación entre generación eólica y precios"*

### 🌱 Renovables y Emisiones
- *"¿Cuánta energía solar está generando España?"*
- *"Compara generación renovable vs fósil esta semana"*
- *"¿Cuáles son las emisiones de CO₂ actuales?"*
- *"Muéstrame la tendencia de energía eólica en los últimos 30 días"*

### 💰 Análisis de Mercado
- *"¿Cuál es el precio SPOT de electricidad ahora?"*
- *"Encuentra las horas más baratas para consumir electricidad hoy"*
- *"Compara tarifas PVPC entre días laborables y fines de semana"*
- *"¿Cuándo fue la electricidad más cara este mes?"*

### 🔎 Descubrimiento
- *"Busca todos los indicadores relacionados con 'nuclear'"*
- *"¿Qué datos hay disponibles sobre generación hidroeléctrica?"*
- *"Muéstrame todos los indicadores relacionados con precios"*

Claude usa automáticamente las herramientas correctas, obtiene los datos y los presenta en contexto.

---

## 🛠️ Herramientas MCP Disponibles

El servidor proporciona **14 herramientas** organizadas por caso de uso:

### 🔍 Acceso de Bajo Nivel
- `get_indicator_data` - Datos de series temporales para cualquier indicador
- `list_indicators` - Listar 1.967+ indicadores con paginación
- `search_indicators` - Buscar indicadores por palabra clave

### ⚡ Demanda y Generación
- `get_demand_summary` - Resumen rápido de demanda
- `get_generation_mix` - Desglose de generación en un momento específico
- `get_generation_mix_timeline` - Desglose de generación a lo largo del tiempo

### 🌱 Renovables y Sostenibilidad
- `get_renewable_summary` - Análisis de generación renovable con % de demanda
- `get_carbon_intensity` - Emisiones de CO₂ por kWh con clasificación de calidad

### ⚙️ Operaciones de Red y Estabilidad
- `get_grid_stability` - Balance sincrónico vs renovable variable con análisis de inercia
- `get_storage_operations` - Eficiencia de almacenamiento por bombeo
- `get_international_exchanges` - Flujos eléctricos transfronterizos por país

### 💰 Mercado y Previsión
- `get_price_analysis` - Análisis de precios SPOT con comparación multipaís
- `compare_forecast_actual` - Métricas de precisión de previsión de demanda
- `get_peak_analysis` - Patrones de demanda pico y factores de carga

---

## 📖 IDs de Indicadores Comunes

Referencia rápida para indicadores frecuentes:

### ⚡ Demanda
- `1293` - Demanda Real (Peninsular) - *MW, actualizaciones cada 5 minutos*
- `2037` - Demanda Real Nacional - *MW, actualizaciones cada 5 minutos*
- `1292` - Previsión de Demanda - *MW, horaria*

### 🔋 Fuentes de Generación
- `549` - Nuclear - *MW, cada 5 minutos*
- `2038` - Eólica (Nacional) - *MW, cada 5 minutos*
- `1295` - Solar FV (Peninsular) - *MW, cada 5 minutos*
- `2041` - Ciclo Combinado (Nacional) - *MW, cada 5 minutos*
- `2042` - Hidráulica (Nacional) - *MW, cada 5 minutos*

### 💵 Precios
- `600` - Precio Mercado SPOT - *€/MWh, cada 15 minutos*
- `1013` - Tarifa PVPC - *€/MWh, horaria*

### 🌱 Emisiones
- `10355` - Emisiones de CO₂ - *tCO₂eq, cada 5 minutos*

---

## 🏗️ Arquitectura

Construido siguiendo **mejores prácticas de la industria**:

```
📦 ree-mcp
├── 🎯 domain/           # Lógica de negocio pura (SIN dependencias externas)
│   ├── entities/        # Indicator, IndicatorData, IndicatorValue
│   ├── value_objects/   # IndicatorId, DateTimeRange, TimeGranularity
│   ├── repositories/    # Interfaces abstractas
│   └── exceptions.py    # Errores específicos del dominio
├── 🚀 application/      # Casos de uso y DTOs
│   ├── use_cases/       # GetIndicatorData, ListIndicators, SearchIndicators
│   └── dtos/           # Objetos Request/Response
├── 🔧 infrastructure/   # Dependencias externas
│   ├── http/           # Cliente API REE con lógica de reintentos
│   ├── repositories/   # Implementaciones de repositorios
│   └── config/         # Gestión de configuración
└── 🌐 interface/       # Servidor MCP
    └── mcp_server.py   # Herramientas y recursos FastMCP
```

**Principios Clave:**
- ✅ **Domain-Driven Design (DDD)** - Separación clara de responsabilidades
- ✅ **Clean Architecture** - Dependencias apuntan hacia dentro
- ✅ **Principios SOLID** - Los 5 implementados
- ✅ **Type Safety** - 100% tipado con mypy en modo estricto
- ✅ **SIN Mocking** - Tests de dominio usan funciones puras
- ✅ **Testing Exhaustivo** - 59 tests (unitarios, integración, e2e)

---

## 🧪 Testing y Desarrollo

### Ejecutar Tests

```bash
# Todos los tests
pytest

# Solo tests unitarios (rápidos, sin dependencias externas)
pytest tests/unit/

# Con reporte de cobertura
pytest --cov=src/ree_mcp --cov-report=html
```

### Calidad de Código

```bash
# Type checking (modo estricto de mypy)
mypy src/ree_mcp/

# Linting
ruff check .

# Auto-corregir problemas
ruff check --fix .

# Formatear código
ruff format .
```

### Ejecutar Servidor en Modo Standalone

```bash
# Modo STDIO (para MCP)
python -m ree_mcp

# Modo HTTP (para testing)
python -c "from ree_mcp.interface.mcp_server import mcp; mcp.run(transport='http', port=8000)"
```

---

## 🎓 Aprende IA y Construye Más Proyectos

Este proyecto fue creado por **[Javi Santos](https://www.linkedin.com/in/francisco-javier-santos-criado/)**, Especialista en IA y Robótica con investigación publicada en:
- 🔬 Detección de gasas quirúrgicas usando Redes Neuronales Convolucionales
- 🧠 Interpretabilidad de Modelos de Lenguaje en escenarios de conocimiento diverso

### 📚 La Escuela de IA

¿Quieres aprender IA **sin humo** y construir proyectos como este?

Únete a **[La Escuela de IA](https://skool.com/la-escuela-de-ia-9955)** - la comunidad española de aprendizaje de IA donde encontrarás:

- 🎯 **Práctica real** - Construye proyectos reales de IA, no ejemplos de juguete
- 🇪🇸 **Contenido en español** - Por fin, educación en IA en tu idioma
- 🛠️ **Recursos prácticos** - Código, tutoriales y ejemplos hands-on
- 👥 **Comunidad activa** - Aprende con otros entusiastas de la IA hispanohablantes

👉 **[Únete a La Escuela de IA](https://skool.com/la-escuela-de-ia-9955)**

### 📺 Canal de YouTube

Suscríbete a **[JavadexAI](https://www.youtube.com/@JavadexAI)** para:
- 🎥 Tutoriales de IA y recorridos de proyectos
- 💡 Aplicaciones de LLMs y servidores MCP
- 🚀 Estrategias de implementación de IA en el mundo real

### 🤝 Conecta

- **LinkedIn**: [Javi Santos](https://www.linkedin.com/in/francisco-javier-santos-criado/)
- **YouTube**: [@JavadexAI](https://www.youtube.com/@JavadexAI)
- **Escuela de IA**: [skool.com/la-escuela-de-ia-9955](https://skool.com/la-escuela-de-ia-9955)

---

## ⚙️ Configuración Avanzada

### Variables de Entorno

Crea un archivo `.env` para personalizar el comportamiento:

```env
# Requerido
REE_API_TOKEN=tu_token_aqui

# Opcional (valores por defecto mostrados)
REE_API_BASE_URL=https://api.esios.ree.es
REQUEST_TIMEOUT=30
MAX_RETRIES=3
RETRY_BACKOFF_FACTOR=0,5
```

### Configuración Manual de Claude Code

Si prefieres configuración manual en lugar del script de instalación:

#### Opción 1: Instalación Local

1. Edita `.claude_mcp_config.json` con tu token
2. Actualiza la ruta del `command` si es necesario
3. En Claude Code, ejecuta `/config-mcp` y pega la configuración

#### Opción 2: Directo desde GitHub (uvx)

1. Edita `.claude_mcp_config_uvx.json` con tu token
2. En Claude Code, ejecuta `/config-mcp` y pega la configuración
3. No necesita instalación local - ¡se ejecuta directamente desde GitHub!

---

## 🔥 Características

### 🎯 Listo para Producción

- ✅ Reintentos automáticos con backoff exponencial
- ✅ Manejo exhaustivo de errores y validación
- ✅ Configuración type-safe con Pydantic
- ✅ Async/await para rendimiento óptimo
- ✅ Context managers para limpieza apropiada de recursos

### 🧪 Bien Testeado

- **59 tests exhaustivos** cubriendo todas las capas
- **Tests unitarios** - Lógica pura de dominio (¡sin mocks!)
- **Tests de integración** - Infraestructura con HTTP mockeado
- **Tests E2E** - Validación de flujos completos
- **Alta cobertura** de rutas críticas

### 📝 Mejores Prácticas

- **Rangos de Fechas**: Máximo 366 días por petición
- **Frescura de Datos**: Usa fechas de 3+ días atrás para datos más fiables
- **Granularidad Temporal**:
  - `raw` para detalle de 5 minutos
  - `hour` para monitorización estándar
  - `day` para tendencias a largo plazo
- **Límites de Tasa**: Máx. ~10 peticiones/segundo (reintentos automáticos en fallos)

---

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Este código sigue principios arquitectónicos estrictos:

- **Domain-Driven Design** - Mantén el dominio puro, sin dependencias externas
- **Clean Architecture** - Respeta los límites de capas
- **Principios SOLID** - Responsabilidad única, abierto/cerrado, etc.
- **SIN Mocking en Dominio** - Los tests de dominio deben ser puros
- **Type Safety** - Todo código debe pasar mypy en modo estricto
- **Testing** - Las nuevas características requieren tests

Ver `CLAUDE.md` para guía detallada de desarrolladores.

---

## 📄 Licencia

Este proyecto es con fines educativos e investigación. La API de REE es proporcionada por Red Eléctrica de España.

**MIT License con Descargo de Responsabilidad** - Ver archivo `LICENSE` para detalles completos.

⚠️ **Proyecto de Hobby**: Este software se proporciona "tal cual" sin garantías. No está garantizado que funcione perfectamente. Úsalo bajo tu propio riesgo.

---

## 🔗 Recursos

- **API eSios de REE**: https://api.esios.ree.es/
- **Portal REE**: https://www.esios.ree.es/
- **FastMCP**: https://github.com/jlowin/fastmcp
- **Model Context Protocol**: https://modelcontextprotocol.io/

---

## 💬 Soporte

### Problemas y Preguntas

- **Problemas del Servidor MCP**: [Abrir un issue](https://github.com/ESJavadex/ree-mcp/issues)
- **Preguntas sobre API REE**: consultasios@ree.es
- **Ayuda con FastMCP**: https://github.com/jlowin/fastmcp

### Aprende Más

- 📚 Únete a [La Escuela de IA](https://skool.com/la-escuela-de-ia-9955) para aprender IA en español
- 📺 Suscríbete a [JavadexAI en YouTube](https://www.youtube.com/@JavadexAI)
- 🤝 Conecta en [LinkedIn](https://www.linkedin.com/in/francisco-javier-santos-criado/)

---

<div align="center">

**Construido con ❤️ usando Domain-Driven Design y mejores prácticas modernas de Python**

⭐ **¡Dale una estrella al repo si te resulta útil!**

</div>
