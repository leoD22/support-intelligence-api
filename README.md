# Support Intelligence API

API para clasificación y procesamiento de tickets de soporte.

Esta API utiliza FastAPI y reglas simples para clasificar tickets. Como respuesta devuelve los campos `category`, `priority`, `summary` y `entities`.

## Tecnologías

- FastAPI: creación de los endpoints de la API.
- Pydantic: definición y validación básica de los contratos de entrada y salida.
- Uvicorn: servidor ASGI para ejecutar la aplicación.

## Cómo ejecutar el proyecto

### Primera instalación

Crear un entorno virtual en la carpeta del proyecto:

```bash
python -m venv .venv
```

Activar el entorno virtual:

```bash
source .venv/Scripts/activate
```

Instalar las dependencias necesarias:

```bash
python -m pip install -r requirements.txt
```

### Ejecutar la API

Con el entorno virtual activado:

```bash
uvicorn app.main:app --reload
```
