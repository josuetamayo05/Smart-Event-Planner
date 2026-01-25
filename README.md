# HospitalPlannerFlet

Planificador inteligente de eventos para hospitales, construido con **Python + Flet**, diseñado para organizar **eventos** (procedimientos, cirugías, consultas, etc.) y administrar **recursos** (humanos y físicos) con reglas que evitan conflictos de uso simultáneo.

---

## Tabla de contenido
- [Descripción](#descripción)
- [Capturas](#capturas)
- [Características](#características)
- [Tecnologías](#tecnologías)
- [Ejecución (Windows)](#ejecución-windows)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Notas](#notas)
- [Licencia](#licencia)

---

## Descripción

**HospitalPlannerFlet** es una aplicación de escritorio pensada para entornos hospitalarios que necesitan programar eventos y asignar recursos de forma consistente.  
El sistema permite gestionar:

- **Eventos** (inicio/fin, tipo, nombre, recursos asignados).
- **Recursos** (físicos y humanos) y sus atributos.
- **Calendario diario** con selección de slots.
- **Búsqueda global** de eventos y recursos.
- Un flujo de creación de eventos con validación para evitar colisiones.

> El motor de validación/reglas se encarga de detectar conflictos (por ejemplo, recursos no disponibles o uso simultáneo).  
> (La explicación completa de reglas y restricciones se puede ampliar en futuras versiones del README.)

---

## Capturas

> Las imágenes están en `HospitalPlannerFlet/assets/`.

### Login
![Login](assets/Login.png)

### Dashboard
> (Si luego agregas captura del dashboard, se puede incluir aquí.)

### Eventos
![Events](assets/Events.png)

### Nuevo Evento
![NewEvent](assets/NewEvent.png)

### Calendario
![Calendar](assets/Calendar.png)

### Recursos
![Resources](assets/Resources.png)

### Search
![Search](assets/Search.png)

---

## Características

- **Interfaz moderna (PC/Desktop)** hecha con Flet.
- **Gestión de eventos**
  - Crear / editar / eliminar eventos.
  - Validación antes de guardar (conflictos, datos inválidos, etc.).
- **Gestión de recursos**
  - Recursos físicos y humanos.
  - Campos como `kind`, `subtype`, `role`, `tags`, etc.
- **Calendario diario**
  - Visualización por día con slots clickeables.
  - Selección rápida de horarios.
- **Búsqueda**
  - Buscador global con filtro por: Todo / Eventos / Recursos.
- **Autenticación local**
  - Login por archivo (`users.json`) mediante `AuthManager`.

---

## Tecnologías

- **Python**
- **Flet** (UI de escritorio)
- Almacenamiento local mediante **JSON** (usuarios) y base local del proyecto

---

## Ejecución (Windows)

### Requisitos
- Windows
- Python instalado (recomendado 3.10+)
- El repositorio incluye un entorno virtual `venv` (según tu estructura)

### Pasos

1) Abre una terminal en la carpeta del repositorio.

2) Entra al directorio del proyecto:
```bat
cd HospitalPlannerFlet