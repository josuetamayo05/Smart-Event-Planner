# 🏥 Planificador Inteligente de Eventos Hospitalarios (Kivy / KivyMD)

Aplicación **desktop** desarrollada en **Python + Kivy + KivyMD** para la planificación inteligente de eventos hospitalarios (cirugías, consultas, terapias, etc.) respetando:

- Disponibilidad de recursos físicos y humanos
- Reglas de co-requisito (recursos que deben ir juntos)
- Restricciones de exclusión mutua (recursos/eventos incompatibles en tiempo o día)

Toda la persistencia se realiza en un **único archivo JSON** (`database.json`), sin usar bases de datos relacionales.

---

## ✨ Características principales

- 📅 Gestión de **eventos hospitalarios**:
  - Cirugías programadas
  - Consultas especializadas
  - Exámenes diagnósticos
  - Terapias / rehabilitación

- ⚙️ Gestión de **recursos**:
  - Recursos físicos: quirófanos, salas de procedimientos, equipos de diagnóstico (tomógrafo, etc.)
  - Recursos humanos: cirujanos, anestesiólogos, enfermeras, cardiólogos, etc.

- 🧠 **Motor de planificación inteligente**:
  - Evita solapamiento de recursos en el tiempo
  - Aplica co-requisitos:
    - Un **quirófano** siempre requiere: 1 cirujano, 1 anestesiólogo, 2 enfermeras
    - Una **cirugía cardíaca** requiere: 1 cardiólogo + equipo de circulación extracorpórea (CEC)
  - Aplica exclusiones mutuas:
    - Un quirófano infeccioso no puede usarse el mismo día que cirugías de trasplante
    - El tomógrafo no puede usarse simultáneamente con terapia de radiación
  - Búsqueda de próximos huecos libres cumpliendo requisitos de recursos

- 🖥️ Interfaz moderna con **KivyMD**:
  - `MDNavigationDrawer` para navegar entre:
    - Dashboard
    - Eventos
    - Recursos
    - Calendario
    - Restricciones
  - Formulario de **Nuevo Evento** con validación en tiempo real (MDBanner + MDDialog)
  - Lista de eventos con **RecycleView** y búsqueda por texto
  - Calendario diario con **drag & drop** de eventos y validación de restricciones
  - Notificaciones tipo **toast**
  - Tema dinámico Claro/Oscuro

- 💾 Persistencia en **JSON**:
  - Archivo único `database.json`
  - Guardado automático asíncrono
  - Importación / exportación
  - Backups con marca de tiempo

---

## 🏗️ Arquitectura del proyecto

Estructura de carpetas recomendada (ya usada por este proyecto):

```text
Hospital_Kivy_App/
├── main.py                 # Punto de entrada principal (MDApp)
├── hospital.kv             # Layout principal Kivy/KivyMD
├── database.json           # "Base de datos" JSON única
├── requirements.txt        # Dependencias de Python
│
├── models/                 # Lógica de negocio / Dominio
│   ├── __init__.py
│   ├── database_manager.py # Gestor JSON (carga/guardado/backup)
│   ├── event.py            # Clase Event
│   ├── resource.py         # Clase Resource
│   ├── constraint.py       # Clase Violation (restricciones)
│   └── scheduler.py        # Motor de planificación / validación
│
├── views/                  # Pantallas Kivy/KivyMD
│   ├── __init__.py
│   ├── screens_manager.py  # MDNavigationLayout + ScreenManager
│   ├── dashboard_screen.py # Dashboard principal
│   ├── events_screen.py    # Lista y búsqueda de eventos
│   ├── resources_screen.py # Gestión de recursos (stub)
│   ├── calendar_screen.py  # Pantalla de calendario
│   ├── constraints_screen.py # Configuración de restricciones (stub)
│   └── new_event_screen.py # Formulario de nuevo evento
│
├── widgets/                # Widgets personalizados
│   ├── __init__.py
│   └── calendar_widget.py  # Calendario diario con drag & drop
│   # (otros widgets opcionales)
│
├── utils/                  # Funciones auxiliares
│   ├── __init__.py
│   ├── validators.py       # Validaciones genéricas (opcional)
│   ├── date_utils.py       # Manejo de fechas/horas (opcional)
│   ├── json_utils.py       # Helpers JSON (opcional)
│   └── notifications.py    # Abstracción de toasts/snackbars (opcional)
│
└── assets/                 # Recursos estáticos
    ├── icons/              # Iconos
    ├── fonts/              # Fuentes
    └── images/             # Imágenes
