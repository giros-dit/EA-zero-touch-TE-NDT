# Pruebas manuales algoritmo

## Intro

Para llevar a cabo estas pruebas se han empleado unos archivos JSON que simulan el estado de la red. Además, se incluye el estado del json de los flujos, para comprobar los resultados. Se explica al inicio de la red cual es el experimento, el estado de la red, el estado esperado y el estado conseguido. Se han creado flujos de caudales acordes para llegar a los distintos estados del algoritmo. Mencionar que para poder replicar el resultado de estos test solo es necesario recrear este estado de la red y generar un nuevo flujo para poder replicar estas pruebas.

## Tabla de Experimentos

| Escenarios     | # flujos existentes | # flujos añadidos | Incremento de la utilización | Routers activos     |
|----------------|---------------------|-------------------|------------------------------|---------------------|
| Escenario 1    | 0                   | 1                 | 25%                          | [r1, r2, r3, r4]    |
| Escenario 2    | 1                   | 1                 | 80%                          | [r1, r2, r3, r4]    |
| Escenario 3    | 3                   | 1                 | 10%                          | [r1, r2, r3, r4]    |
| Escenario 4    | 5                   | 1                 | 12%                          | [r1, r2, r3, r4]    |
| Escenario 5    | 6                   | 1                 | 1%                           | [r1, r2, r3, r4]    |
| Escenario 6    | 4                   | 0                 | 0%                           | [r2, r3, r4]        |
| Escenario 7    | 4                   | 1                 | 10%                          | [r2, r3, r4]        |

## Escenario 1 Primer flujo

### Explicación

Se va a probar añadir un flujo a la red cuando no hay ningún tráfico cursando por esta.

### Estado inicial de la red

No se esta cursando tráfico actualmente, por lo que el consumo de cada router por encaminar tráfico es 0.

| Router   | Utilización (%) |
|----------|-----------------|
| r1       | 0.0             |
| r2       | 0.0             |
| r3       | 0.0             |
| r4       | 0.0             |

| Routers inactivos |
|-------------------|
| []                |

### Resultado esperado

Se espera que conociendo que asigna por el menor identificador, cuando los dos caminos tienen el mismo coste, asigen el camino el camino r2 → r1 antes que el camino r4 → r3.

### Contenido de flows.json

```json
{
    "flows": [
        {
            "_id": "1",
            "version": 1,
            "route": [
                "ru",
                "r2",
                "r1",
                "rg"
            ]
        }
    ],
    "inactive_routers": [],
    "router_utilization": {
        "r1": 0.0,
        "r2": 0.0,
        "r3": 0.0,
        "r4": 0.0
    }
}
```

### Resultado obtenido

Se cumple con el resultado esperado, ya que asigna ese camino aún, cambiando el orden de asignación de los nodos en la creación del grafo.

## Escenario 2 Segundo flujo

### Explicación

Se va a probar añadir un flujo a la red cuando ya hay un flujo cursando por esta

### Estado inicial de la red

| Router   | Utilización (%) |
|----------|-----------------|
| r1       | 25.0            |
| r2       | 25.0            |
| r3       | 0.0             |
| r4       | 0.0             |

| Flujo    | Utilización (%) |
|----------|-----------------|
| 1        | 25.0            |

| Routers inactivos |
|-------------------|
| []                |

### Resultado esperado

Se espera que ya que el consumo energético es menor si se cursa por el camino r4 → r3, se encamine por este camino

### Contenido de flows.json

```json

{
    "flows": [
        {
            "_id": "1",
            "version": 1,
            "route": [
                "ru",
                "r2",
                "r1",
                "rg"
            ]
        },
        {
            "_id": "2",
            "version": 1,
            "route": [
                "ru",
                "r4",
                "r3",
                "rg"
            ]
        }
    ],
    "inactive_routers": [],
    "router_utilization": {
        "r1": 0.25,
        "r2": 0.25,
        "r3": 0.0,
        "r4": 0.0
    }
}

```

### Resultado obtenido

Se obtiene el resultado esperado, ya que se asigna el camino por los routers que implica menor incremento de coste energético.

## Escenario 3 Estado previo al primer umbral

### Explicación

Se va a probar la correcta asignación de un flujo cuando un camino de la red ya supera el primer umbral de utilización.

### Estado inicial de la red


| Router   | Utilización (%) |
|----------|-----------------|
| r1       | 75.0            |
| r2       | 75.0            |
| r3       | 80.0            |
| r4       | 80.0            |

| Flujo    | Utilización (%) |
|----------|-----------------|
| 1        | 25.0            |
| 2        | 80.0            |
| 3        | 50.0            |

| Routers inactivos |
|-------------------|
| []                |

### Resultado esperado

Se espera que ya que el consumo energético es menor si se cursa por el camino r2 → r1, se encamine por este camino con normalidad ya que existe un camino sin superar el primer umbral.

### Contenido de flows.json

```json

{
    "flows": [
        {
            "_id": "1",
            "version": 1,
            "route": [
                "ru",
                "r2",
                "r1",
                "rg"
            ]
        },
        {
            "_id": "2",
            "version": 1,
            "route": [
                "ru",
                "r4",
                "r3",
                "rg"
            ]
        },
        {
            "_id": "3",
            "version": 1,
            "route": [
                "ru",
                "r2",
                "r1",
                "rg"
            ]
        },
        {
            "_id": "4",
            "version": 1,
            "route": [
                "ru",
                "r2",
                "r1",
                "rg"
            ]
        }
    ],
    "inactive_routers": [],
    "router_utilization": {
        "r1": 0.75,
        "r2": 0.75,
        "r3": 0.8,
        "r4": 0.8
    }
}

```

### Resultado obtenido

Se obtiene el resultado esperado, ya que se asigna el camino por los routers que implica menor incremento de coste energético, que además se encuentan por debajo del primer umbral.

## Escenario 4 Todos los caminos superan el primer umbral

### Explicación

Se va a probar la correcta asignación de un flujo cuando todos los caminos de la red ya superan el primer umbral de utilización.

### Estado inicial de la red


| Router   | Utilización (%) |
|----------|-----------------|
| r1       | 85.0            |
| r2       | 85.0            |
| r3       | 80.0            |
| r4       | 80.0            |

| Flujo    | Utilización (%) |
|----------|-----------------|
| 1        | 25.0            |
| 2        | 80.0            |
| 3        | 50.0            |
| 4        | 10.0            |

| Routers inactivos |
|-------------------|
| []                |

### Resultado esperado

Se espera que ya que el consumo energético es menor si se cursa por el camino r4 → r3, se encamine por este camino y además se envie un aviso de que se esta sobrepasando el 80%.

### Contenido de flows.json

```json

{
    "flows": [
        {
            "_id": "1",
            "version": 1,
            "route": [
                "ru",
                "r2",
                "r1",
                "rg"
            ]
        },
        {
            "_id": "2",
            "version": 1,
            "route": [
                "ru",
                "r4",
                "r3",
                "rg"
            ]
        },
        {
            "_id": "3",
            "version": 1,
            "route": [
                "ru",
                "r2",
                "r1",
                "rg"
            ]
        },
        {
            "_id": "4",
            "version": 1,
            "route": [
                "ru",
                "r2",
                "r1",
                "rg"
            ]
        },
        {
            "_id": "5",
            "version": 1,
            "route": [
                "ru",
                "r4",
                "r3",
                "rg"
            ]
        }
    ],
    "inactive_routers": [],
    "router_utilization": {
        "r1": 0.85,
        "r2": 0.85,
        "r3": 0.8,
        "r4": 0.8
    }
}

```

### Resultado obtenido

Se obtiene el resultado esperado, ya que se asigna el camino por los routers que implica menor incremento de coste energético, y además se envía la notificación de que se esta superando el primer umbral.

![sorpaso_primer_umbral](<Captura desde 2025-03-25 11-50-10.png>)

## Escenario 4 Un solo camino supera el segundo umbral

### Explicación

Se va a probar la correcta asignación de un flujo cuando un caminos de la red ya supera el segundo umbral de utilización.

### Estado inicial de la red


| Router   | Utilización (%) |
|----------|-----------------|
| r1       | 85.0            |
| r2       | 85.0            |
| r3       | 97.0            |
| r4       | 97.0            |

| Flujo    | Utilización (%) |
|----------|-----------------|
| 1        | 25.0            |
| 2        | 80.0            |
| 3        | 50.0            |
| 4        | 10.0            |
| 5        | 17.0            |

| Routers inactivos |
|-------------------|
| []                |

### Resultado esperado

Se espera que ya que el consumo energético es menor si se cursa por el camino r2 → r1, se encamine por este camino, que además está por debajo del segundo umbral.

### Contenido de flows.json


```json

{
    "flows": [
        {
            "_id": "1",
            "version": 1,
            "route": [
                "ru",
                "r2",
                "r1",
                "rg"
            ]
        },
        {
            "_id": "2",
            "version": 1,
            "route": [
                "ru",
                "r4",
                "r3",
                "rg"
            ]
        },
        {
            "_id": "3",
            "version": 1,
            "route": [
                "ru",
                "r2",
                "r1",
                "rg"
            ]
        },
        {
            "_id": "4",
            "version": 1,
            "route": [
                "ru",
                "r2",
                "r1",
                "rg"
            ]
        },
        {
            "_id": "5",
            "version": 1,
            "route": [
                "ru",
                "r4",
                "r3",
                "rg"
            ]
        },
        {
            "_id": "6",
            "version": 1,
            "route": [
                "ru",
                "r2",
                "r1",
                "rg"
            ]
        }
    ],
    "inactive_routers": [],
    "router_utilization": {
        "r1": 0.85,
        "r2": 0.85,
        "r3": 0.97,
        "r4": 0.97
    }
}

```

### Resultado obtenido

Se obtiene el resultado esperdo, encaminando el flujo 6 por el camino de menor coste energético pero sobrepasando el umbral del 80%.

## Escenario 5 Todos los caminos superan el segundo umbral

### Explicación

Se va a probar la correcta asignación de un flujo cuando un caminos de la red ya supera el segundo umbral de utilización.

### Estado inicial de la red


| Router   | Utilización (%) |
|----------|-----------------|
| r1       | 97.0            |
| r2       | 97.0            |
| r3       | 97.0            |
| r4       | 97.0            |

| Flujo    | Utilización (%) |
|----------|-----------------|
| 1        | 25.0            |
| 2        | 80.0            |
| 3        | 50.0            |
| 4        | 10.0            |
| 5        | 17.0            |

| Routers inactivos |
|-------------------|
| []                |

### Resultado esperado

Se espera que ya que el consumo energético es menor si se cursa por el camino r2 → r1, se encamine por este camino, que además está por debajo del segundo umbral.

### Contenido de flows.json

```json

{
    "flows": [
        {
            "_id": "1",
            "version": 1,
            "route": [
                "ru",
                "r2",
                "r1",
                "rg"
            ]
        },
        {
            "_id": "2",
            "version": 1,
            "route": [
                "ru",
                "r4",
                "r3",
                "rg"
            ]
        },
        {
            "_id": "3",
            "version": 1,
            "route": [
                "ru",
                "r2",
                "r1",
                "rg"
            ]
        },
        {
            "_id": "4",
            "version": 1,
            "route": [
                "ru",
                "r2",
                "r1",
                "rg"
            ]
        },
        {
            "_id": "5",
            "version": 1,
            "route": [
                "ru",
                "r4",
                "r3",
                "rg"
            ]
        },
        {
            "_id": "6",
            "version": 1,
            "route": [
                "ru",
                "r2",
                "r1",
                "rg"
            ]
        },
        {
            "_id": "7",
            "version": 1
        }
    ],
    "inactive_routers": [],
    "router_utilization": {
        "r1": 0.97,
        "r2": 0.97,
        "r3": 0.97,
        "r4": 0.97
    }
}

```

### Resultado obtenido

Como todos routers están por encima del 95% de capacidad, al flujo 7 no se le asigna una ruta y salta el aviso correspondiente.

![No se asigna ruta al flujo 7](<Captura desde 2025-03-25 11-50-58.png>)

## Escenario 6 Caida de router

### Explicación

Se va a probar la correcta reasignación de las rutas cuando hay un router caido.

### Estado inicial de la red


| Router   | Utilización (%) |
|----------|-----------------|
| r1       | 40.0            |
| r2       | 40.0            |
| r3       | 40.0            |
| r4       | 40.0            |

| Flujo    | Utilización (%) |
|----------|-----------------|
| 1        | 20.0            |
| 2        | 20.0            |
| 3        | 20.0            |
| 4        | 20.0            |


| Routers inactivos |
|-------------------|
| []                |

#### Estado del flows.json inicialmente

```json
{
    "flows": [
        {
            "_id": "1",
            "version": 1,
            "route": [
                "ru",
                "r2",
                "r1",
                "rg"
            ]
        },
        {
            "_id": "2",
            "version": 1,
            "route": [
                "ru",
                "r4",
                "r3",
                "rg"
            ]
        },
        {
            "_id": "3",
            "version": 1,
            "route": [
                "ru",
                "r2",
                "r1",
                "rg"
            ]
        },
        {
            "_id": "4",
            "version": 1,
            "route": [
                "ru",
                "r4",
                "r3",
                "rg"
            ]
        }
    ],
    "inactive_routers": [],
    "router_utilization": {
        "r1": 0.4,
        "r2": 0.4,
        "r3": 0.4,
        "r4": 0.4
    }
}

```

### Pasos para replicación del test

Una vez tenemos este estado de la red se procede a pausar la actualización de TimeStamps del router r1

### Resultado esperado

Se espera que ya que el consumo energético es menor si se cursa por el camino r2 → r1, se encamine por este camino, que además está por debajo del segundo umbral.

### Contenido de flows.json 

```json

{
    "flows": [
        {
            "_id": "1",
            "version": 2,
            "route": [
                "ru",
                "r4",
                "r3",
                "rg"
            ]
        },
        {
            "_id": "2",
            "version": 1,
            "route": [
                "ru",
                "r4",
                "r3",
                "rg"
            ]
        },
        {
            "_id": "3",
            "version": 2,
            "route": [
                "ru",
                "r4",
                "r3",
                "rg"
            ]
        },
        {
            "_id": "4",
            "version": 1,
            "route": [
                "ru",
                "r4",
                "r3",
                "rg"
            ]
        }
    ],
    "inactive_routers": [
        "r1"
    ],
    "router_utilization": {
        "r1": 0.4,
        "r2": 0.0,
        "r3": 0.4,
        "r4": 0.4
    }
}

```

### Resultado obtenido

Se han reasignado correctamente las rutas de los flujos cuya ruta contenia el router r1. 

![alt text](<Captura desde 2025-03-25 12-11-53.png>)

## Escenario 7 añadir flujo con router caido

### Explicación

Se va a probar la correcta asignación de un flujo cuando un router no está disponible.

### Estado inicial de la red


| Router   | Utilización (%) |
|----------|-----------------|
| r2       | 0.0            |
| r3       | 80.0            |
| r4       | 80.0            |

| Flujo    | Utilización (%) |
|----------|-----------------|
| 1        | 20.0            |
| 2        | 20.0            |
| 3        | 20.0            |
| 4        | 20.0            |


| Routers inactivos |
|-------------------|
| [r1]              |

### Resultado esperado

Se espera que ya que el unico camino disponible es el camino que atraviesa los routers r4 → r3 y no asigne el camino por los routers r2 → r1.

### Contenido de flows.json

```json

{
    "flows": [
        {
            "_id": "1",
            "version": 2,
            "route": [
                "ru",
                "r4",
                "r3",
                "rg"
            ]
        },
        {
            "_id": "2",
            "version": 1,
            "route": [
                "ru",
                "r4",
                "r3",
                "rg"
            ]
        },
        {
            "_id": "3",
            "version": 2,
            "route": [
                "ru",
                "r4",
                "r3",
                "rg"
            ]
        },
        {
            "_id": "4",
            "version": 1,
            "route": [
                "ru",
                "r4",
                "r3",
                "rg"
            ]
        },
        {
            "_id": "5",
            "version": 1,
            "route": [
                "ru",
                "r4",
                "r3",
                "rg"
            ]
        }
    ],
    "inactive_routers": [
        "r1"
    ],
    "router_utilization": {
        "r1": 0.4,
        "r2": 0.0,
        "r3": 0.8,
        "r4": 0.8
    }
}

```

### Resultado obtenido

Se ha asignado correctamente el camino al flujo con identificador 5.

## Escenario 8 Derivada de energía distinta para cada router de caminos distintos

Para este experimento se va a simular un entorno de red real, donde las gráficas de incremento de consumo de los routers varian en función del % de utilización, para ello se van a tomar dos modelos de routers routers tipo A, para los routers r1 y r2, que tiene una gráfica escalón.

![grafica_routerA](grafica_routerA.png)
![grafica_routerB](grafica_routerB.png)

Se comprueba que se cumple el funcionamiento esperado, respetando los umbrales de decisión.

### Primer flujo 50%

```json
{
    "flows": [
        {
            "_id": "1",
            "version": 1,
            "route": [
                "ru",
                "r4",
                "r3",
                "rg"
            ]
        }
    ],
    "inactive_routers": [],
    "router_utilization": {
        "r1": 0.0,
        "r2": 0.0,
        "r3": 0.0,
        "r4": 0.0
    }
}
```
### Segundo flujo 33%

```json

{
    "flows": [
        {
            "_id": "1",
            "version": 1,
            "route": [
                "ru",
                "r4",
                "r3",
                "rg"
            ]
        },
        {
            "_id": "2",
            "version": 1,
            "route": [
                "ru",
                "r4",
                "r3",
                "rg"
            ]
        }
    ],
    "inactive_routers": [],
    "router_utilization": {
        "r1": 0.0,
        "r2": 0.0,
        "r3": 0.5,
        "r4": 0.5
    }
}

```
### Tercer flujo

```json

{
    "flows": [
        {
            "_id": "1",
            "version": 1,
            "route": [
                "ru",
                "r4",
                "r3",
                "rg"
            ]
        },
        {
            "_id": "2",
            "version": 1,
            "route": [
                "ru",
                "r4",
                "r3",
                "rg"
            ]
        },
        {
            "_id": "3",
            "version": 1,
            "route": [
                "ru",
                "r2",
                "r1",
                "rg"
            ]
        }
    ],
    "inactive_routers": [],
    "router_utilization": {
        "r1": 0.0,
        "r2": 0.0,
        "r3": 0.83,
        "r4": 0.83
    }
}

```
### Cuarto flujo

```json

{
    "flows": [
        {
            "_id": "1",
            "version": 1,
            "route": [
                "ru",
                "r4",
                "r3",
                "rg"
            ]
        },
        {
            "_id": "2",
            "version": 1,
            "route": [
                "ru",
                "r4",
                "r3",
                "rg"
            ]
        },
        {
            "_id": "3",
            "version": 1,
            "route": [
                "ru",
                "r2",
                "r1",
                "rg"
            ]
        },
        {
            "_id": "4",
            "version": 1,
            "route": [
                "ru",
                "r2",
                "r1",
                "rg"
            ]
        }
    ],
    "inactive_routers": [],
    "router_utilization": {
        "r1": 0.45,
        "r2": 0.45,
        "r3": 0.83,
        "r4": 0.83
    }
}

```

### Quinto flujo

```json

{
    "flows": [
        {
            "_id": "1",
            "version": 1,
            "route": [
                "ru",
                "r4",
                "r3",
                "rg"
            ]
        },
        {
            "_id": "2",
            "version": 1,
            "route": [
                "ru",
                "r4",
                "r3",
                "rg"
            ]
        },
        {
            "_id": "3",
            "version": 1,
            "route": [
                "ru",
                "r2",
                "r1",
                "rg"
            ]
        },
        {
            "_id": "4",
            "version": 1,
            "route": [
                "ru",
                "r2",
                "r1",
                "rg"
            ]
        },
        {
            "_id": "5",
            "version": 1,
            "route": [
                "ru",
                "r2",
                "r1",
                "rg"
            ]
        }
    ],
    "inactive_routers": [],
    "router_utilization": {
        "r1": 0.85,
        "r2": 0.85,
        "r3": 0.83,
        "r4": 0.83
    }
}

```

### Sexto flujo

```json

{
    "flows": [
        {
            "_id": "1",
            "version": 1,
            "route": [
                "ru",
                "r4",
                "r3",
                "rg"
            ]
        },
        {
            "_id": "2",
            "version": 1,
            "route": [
                "ru",
                "r4",
                "r3",
                "rg"
            ]
        },
        {
            "_id": "3",
            "version": 1,
            "route": [
                "ru",
                "r2",
                "r1",
                "rg"
            ]
        },
        {
            "_id": "4",
            "version": 1,
            "route": [
                "ru",
                "r2",
                "r1",
                "rg"
            ]
        },
        {
            "_id": "5",
            "version": 1,
            "route": [
                "ru",
                "r2",
                "r1",
                "rg"
            ]
        },
        {
            "_id": "6",
            "version": 1,
            "route": [
                "ru",
                "r4",
                "r3",
                "rg"
            ]
        }
    ],
    "inactive_routers": [],
    "router_utilization": {
        "r1": 0.97,
        "r2": 0.97,
        "r3": 0.83,
        "r4": 0.83
    }
}

```
### Septimo flujo

```json

{
    "flows": [
        {
            "_id": "1",
            "version": 1,
            "route": [
                "ru",
                "r4",
                "r3",
                "rg"
            ]
        },
        {
            "_id": "2",
            "version": 1,
            "route": [
                "ru",
                "r4",
                "r3",
                "rg"
            ]
        },
        {
            "_id": "3",
            "version": 1,
            "route": [
                "ru",
                "r2",
                "r1",
                "rg"
            ]
        },
        {
            "_id": "4",
            "version": 1,
            "route": [
                "ru",
                "r2",
                "r1",
                "rg"
            ]
        },
        {
            "_id": "5",
            "version": 1,
            "route": [
                "ru",
                "r2",
                "r1",
                "rg"
            ]
        },
        {
            "_id": "6",
            "version": 1,
            "route": [
                "ru",
                "r4",
                "r3",
                "rg"
            ]
        },
        {
            "_id": "7",
            "version": 1
        }
    ],
    "inactive_routers": [],
    "router_utilization": {
        "r1": 0.97,
        "r2": 0.97,
        "r3": 0.96,
        "r4": 0.96
    }
}

```
