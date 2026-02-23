# Generador de NetworkInfo

Este script genera un archivo JSON con información de red (grafo de conectividad y direcciones loopback) a partir de una topología de Containerlab.

## Funcionamiento

El programa funciona en dos fases de filtrado:

1. **Filtro completo (`--full_filter`)**: Selecciona todos los nodos de tu topología que participarán en el análisis de conectividad
2. **Filtro final (`--final_filter`)**: De los nodos seleccionados en el paso anterior, escoge cuáles aparecerán en la salida final

### Fase 1: Selección de nodos para análisis

Por defecto, el programa asume que todos los nodos de red empiezan por "r" (r1, r2, r3, etc.). Si tu topología tiene nodos con nombres diferentes, debes modificar el filtro `--full_filter`.

**Ejemplos de filtros completos:**

```bash
# Topología con nodos r1, r2, r3... (valor por defecto)
python3 networkinfo.py /path/to/topology.clab.yml

# Topología con nodos router1, router2, router3...
python3 networkinfo.py /path/to/topology.clab.yml --full_filter "^(router.*)$"

# Topología mixta: nodos que empiecen por "r" o "router"
python3 networkinfo.py /path/to/topology.clab.yml --full_filter "^(r.*|router.*)$"

# Topología con nodos sw1, sw2... y rt1, rt2...
python3 networkinfo.py /path/to/topology.clab.yml --full_filter "^(sw.*|rt.*)$"
```

### Fase 2: Selección de nodos frontera

De todos los nodos seleccionados en la fase anterior, el filtro final determina cuáles son los nodos frontera que aparecerán en el resultado. Por defecto busca nodos llamados `ru`, `rg`, `rc` además de cualquier nodo numerado (r1, r2, etc.).

**Ejemplos de filtros finales:**

```bash
# Nodos frontera: ru, rg, rc + numerados (valor por defecto)
python3 networkinfo.py /path/to/topology.clab.yml

# Solo nodos numerados (r1, r2, r3...)
python3 networkinfo.py /path/to/topology.clab.yml --final_filter "^(r\d+)$"

# Nodos frontera personalizados: edge1, edge2, core
python3 networkinfo.py /path/to/topology.clab.yml --final_filter "^(edge\d+|core)$"

# Nodos frontera: upstream, gateway, customer + numerados
python3 networkinfo.py /path/to/topology.clab.yml --final_filter "^(r\d+|upstream|gateway|customer)$"
```

## Ejemplos de uso completos

### Topología estándar
Si tu topología tiene nodos como `r1`, `r2`, `r3`, `ru`, `rg`, `rc`:

```bash
python3 networkinfo.py /path/to/topology.yml
```

### Topología con prefijo "router"
Si tus nodos se llaman `router1`, `router2`, `routerUpstream`, `routerGateway`:

```bash
python3 networkinfo.py /path/to/topology.yml \
    --full_filter "^(router.*)$" \
    --final_filter "^(router\d+|routerUpstream|routerGateway)$"
```

### Topología mixta con nodos especiales
Si tienes nodos `sw1`, `sw2`, `border1`, `border2`, `core`:

```bash
python3 networkinfo.py /path/to/topology.yml \
    --full_filter "^(sw.*|border.*|core)$" \
    --final_filter "^(border.*|core)$"
```

## Parámetros

- `yaml_file`: **Obligatorio**. Ruta al archivo YAML de la topología Containerlab
- `--full_filter`: Expresión regular para seleccionar nodos en el análisis (default: `^(r.*)$`)
- `--final_filter`: Expresión regular para nodos que aparecen en la salida (default: `^(r\d+|ru|rg|rc)$`)
- `--output`: Archivo de salida JSON (default: `networkinfo.json`)

## Salida

El programa genera un archivo JSON con:
- **graph**: Grafo de conectividad con nodos y enlaces
- **loopbacks**: Direcciones IPv6 de loopback extraídas de las configuraciones

```json
{
  "graph": {
    "nodes": ["r1", "r2", "ru", "rg"],
    "edges": [
      {"source": "r1", "target": "r2", "cost": 0.0},
      {"source": "ru", "target": "r1", "cost": 0.0}
    ]
  },
  "loopbacks": {
    "r1": "2001:db8::1/128",
    "r2": "2001:db8::2/128",
    "ru": "2001:db8::100/128"
  }
}
```