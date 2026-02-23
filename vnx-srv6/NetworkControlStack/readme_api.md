# API de Gestión de Flujos

Esta API REST permite gestionar flujos de red y sus rutas asociadas. Está construida con Flask y se encarga de la creación, actualización, eliminación y listado de flujos de red.

## URL Base

La API está expuesta como un servicio de Kubernetes en el puerto 32500:

```
http://<IP_NODO_KUBERNETES>:32500
```

> **Nota**: Internamente la aplicación Flask ejecuta en el puerto 5000, pero el servicio de Kubernetes la expone en el puerto 32500.

## Autenticación

La API no requiere autenticación actualmente.

## Endpoints

### 1. Listar Flujos

Obtiene la lista de todos los flujos existentes.

```http
GET /flows
```

#### Respuesta Exitosa (200)

```json
{
  "flows": [
    {
      "_id": "2001:db8::1",
      "route": ["node1", "node2", "node3"],
      "timestamps": {
        "ts_api_created": 1642678123.456
      }
    }
  ]
}
```

#### Respuesta de Error (500)

```json
{
  "error": "Error interno del servidor",
  "flows": []
}
```

---

### 2. Crear Flujo

Crea un nuevo flujo para una IP específica, opcionalmente con una ruta definida.

```http
POST /flows/<encoded_ip>
```

#### Parámetros de URL

- `encoded_ip` (string, requerido): IP codificada para URL. Las barras (`/`) deben reemplazarse por guiones bajos (`_`).

#### Cuerpo de la Petición (Opcional)

```json
{
  "route": ["node1", "node2", "node3"]
}
```

#### Campos del Cuerpo

- `route` (array, opcional): Lista de nodos que definen la ruta del flujo.

#### Ejemplos

##### Crear flujo sin ruta específica

```bash
curl -X POST http://<IP_NODO_KUBERNETES>:32500/flows/2001:db8::1_64 \
  -H "Content-Type: application/json"
```

##### Crear flujo con ruta específica

```bash
curl -X POST http://<IP_NODO_KUBERNETES>:32500/flows/2001:db8::1_64 \
  -H "Content-Type: application/json" \
  -d '{"route": ["node1", "node2", "node3"]}'
```

#### Respuestas

##### Éxito (201)

```json
{
  "message": "Flujo 2001:db8::1 creado exitosamente"
}
```

##### Flujo ya existe (409)

```json
{
  "error": "El flujo 2001:db8::1 ya existe"
}
```

##### IP inválida (400)

```json
{
  "error": "IP inválida"
}
```

##### Error interno (500)

```json
{
  "error": "Error creando flujo: <detalle del error>"
}
```

---

### 3. Actualizar Flujo

Actualiza la ruta de un flujo existente.

```http
PUT /flows/<encoded_ip>
```

#### Parámetros de URL

- `encoded_ip` (string, requerido): IP codificada para URL.

#### Cuerpo de la Petición (Requerido)

```json
{
  "route": ["node1", "node4", "node5"]
}
```

#### Campos del Cuerpo

- `route` (array, requerido): Nueva lista de nodos para la ruta del flujo.

#### Ejemplo

```bash
curl -X PUT http://<IP_NODO_KUBERNETES>:32500/flows/2001:db8::1_64 \
  -H "Content-Type: application/json" \
  -d '{"route": ["node1", "node4", "node5"]}'
```

#### Respuestas

##### Éxito (200)

```json
{
  "message": "Flujo 2001:db8::1 actualizado exitosamente"
}
```

##### Flujo no encontrado (404)

```json
{
  "error": "El flujo 2001:db8::1 no existe"
}
```

##### Datos inválidos (400)

```json
{
  "error": "El campo 'route' es requerido y debe ser un array"
}
```

##### Content-Type incorrecto (400)

```json
{
  "error": "Content-Type debe ser application/json"
}
```

---

### 4. Eliminar Flujo

Elimina un flujo y su ruta asociada en la infraestructura de red.

```http
DELETE /flows/<encoded_ip>
```

#### Parámetros de URL

- `encoded_ip` (string, requerido): IP codificada para URL.

#### Ejemplo

```bash
curl -X DELETE http://<IP_NODO_KUBERNETES>:32500/flows/2001:db8::1_64
```

#### Respuestas

##### Éxito (200)

```json
{
  "message": "Flujo 2001:db8::1 y su ruta eliminados exitosamente"
}
```

##### Flujo no encontrado (404)

```json
{
  "error": "El flujo 2001:db8::1 no existe",
  "details": "<detalles adicionales>"
}
```

##### Error parcial (200)

```json
{
  "message": "Flujo 2001:db8::1 eliminado del registro",
  "warning": "Advertencia: no se pudo eliminar ruta en RU"
}
```

---

### 5. Health Check

Verifica el estado de salud del servicio.

```http
GET /health
```

#### Respuesta (200)

```json
{
  "status": "healthy"
}
```

## Codificación de IPs

Las direcciones IP en las URLs deben codificarse de la siguiente manera:

1. Aplicar URL encoding (`urllib.parse.quote`)
2. Reemplazar barras (`/`) por guiones bajos (`_`)

### Ejemplos de Codificación

| IP Original | IP Codificada |
|-------------|---------------|
| `2001:db8::1/64` | `2001%3Adb8%3A%3A1_64` |
| `fe80::1/128` | `fe80%3A%3A1_128` |
| `::1` | `%3A%3A1` |

## Variables de Entorno

La API requiere las siguientes variables de entorno:

- `S3_ENDPOINT`: Endpoint del servicio S3
- `S3_ACCESS_KEY`: Clave de acceso S3
- `S3_SECRET_KEY`: Clave secreta S3
- `S3_BUCKET`: Nombre del bucket S3
- `LOGTS`: (opcional) Habilita timestamps en logs (`true`/`false`, default: `false`)

## Características Especiales

### Timestamps

Si la variable `LOGTS` está establecida en `true`, la API añadirá timestamps automáticos a los flujos:

- `ts_api_created`: Timestamp de cuándo se creó el flujo vía API

### Recálculo Automático

Cuando se crea un flujo sin ruta específica, la API activa automáticamente un recálculo para determinar la mejor ruta disponible.

### Integración con Infraestructura

La API se integra con:

- **flows.py**: Script principal para gestión de flujos
- **src.py**: Script para instalación de rutas
- **pce.py**: Proceso de cálculo de rutas (ejecutado en paralelo)
- **RU (Route Unit)**: Unidad de enrutamiento donde se instalan las rutas físicas

## Códigos de Estado HTTP

- `200 OK`: Operación exitosa
- `201 Created`: Flujo creado exitosamente
- `400 Bad Request`: Datos de entrada inválidos
- `404 Not Found`: Recurso no encontrado
- `409 Conflict`: Flujo ya existe
- `500 Internal Server Error`: Error interno del servidor

## Logging

La API proporciona logging detallado de todas las operaciones, incluyendo:

- Comandos ejecutados
- Códigos de retorno
- Salidas de stdout/stderr
- Errores y excepciones

Los logs se configuran en nivel `INFO` por defecto.