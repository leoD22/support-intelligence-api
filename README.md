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
## Uso de la API

### Documentación interactiva

Con el servidor en ejecución se puede acceder  `/docs`, donde FastAPI muestra la documentación de los endpoints y los schemas de entrada y salida.

### POST /classify 

Recibe un body JSON con el campo `text` y devuelve una respuesta JSON con la clasificación del ticket.


#### Request body
```json
{
  "text": "Factura de compra de equipo para la oficina"
}
```
	
#### Response body
```json
{
  "category": "billing",
  "priority": 1,
  "summary": "Factura de compra de equipo para la oficina",
  "entities": [
    "factura"
  ]
}
```

## Limitaciones

- La clasificación utiliza actualmente palabras clave asociadas a las entidades. En versiones futuras, esta responsabilidad se irá reemplazando mediante tecnologías de inteligencia artificial a medida que sean incorporadas al proyecto.

- `summary` actualmente devuelve el texto de entrada, no un resumen real.

- `entities` solo detecta una lista fija de palabras.

- La validación avanzada de entrada queda pendiente para una versión futura.