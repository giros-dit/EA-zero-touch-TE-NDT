#!/usr/bin/env python3
import json
import subprocess
import shlex
import argparse
import time
import os

LOGTS = os.environ.get('LOGTS', 'false').lower() == 'true'


def ssh_ru(cmd, flow_id=None):
    """
    Ejecuta un comando de shell en RU vía SSH, asegurando rutas a /usr/sbin y /sbin.
    Versión mejorada que trackea timestamps para experimentos.
    """
    # Timestamp preciso justo antes de iniciar SSH
    start_time = time.time()
    
    remote_cmd = f"PATH=$PATH:/usr/sbin:/sbin {cmd}"
    
    if flow_id and LOGTS:
        print(f"[src] Iniciando comando SSH para flujo {flow_id} en timestamp: {start_time}")
    
    try:
        proc = subprocess.run(
            ['ssh', '-o', 'StrictHostKeyChecking=no', 
             '-o', 'ConnectTimeout=10',
             'root@ru.across-tc32.svc.cluster.local', remote_cmd],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30  # Timeout de 30 segundos
        )
        
        # Timestamp inmediatamente después de que SSH retorne
        completion_time = time.time()
        
        # Solo marcar como exitoso si el return code es 0
        if proc.returncode == 0:
            if flow_id and LOGTS:
                print(f"[src] OK Comando SSH exitoso para flujo {flow_id}")
                print(f"[src]    Timestamp de éxito: {completion_time}")
                print(f"[src]    Duración total: {completion_time - start_time:.3f}s")
                # Imprimir para que pueda ser parseado por acrosstc32_routing.py
                print(f"ssh_success: {completion_time}")
        else:
            if flow_id:
                print(f"[src]   Comando SSH falló para flujo {flow_id}")
                print(f"[src]   Return code: {proc.returncode}")
    
    except subprocess.TimeoutExpired:
        if flow_id:
            print(f"[src] ⚠ Timeout SSH para flujo {flow_id} después de 30s")
        
        class FakeProc:
            def __init__(self):
                self.returncode = -1
                self.stdout = b''
                self.stderr = b'SSH timeout after 30 seconds'
        
        proc = FakeProc()
    
    except Exception as e:
        if flow_id:
            print(f"[src] ✗ Error SSH para flujo {flow_id}: {e}")
        
        class FakeProc:
            def __init__(self, error):
                self.returncode = -1
                self.stdout = b''
                self.stderr = str(error).encode()
        
        proc = FakeProc(e)
    
    return proc


def load_loopbacks(path='/app/networkinfo.json'):
    """
    Carga el JSON de networkinfo y retorna un dict nodo->loopback (sin máscara).
    """
    with open(path) as f:
        data = json.load(f)
    return {n: lp.split('/')[0] for n, lp in data.get('loopbacks', {}).items()}


def route_exists_for_dest(dest):
    """
    Comprueba remotamente si ya existe alguna ruta para el destino específico.
    """
    cmd = f"/usr/sbin/ip -6 route show to {shlex.quote(dest)}"
    proc = ssh_ru(cmd)
    
    print(f"[src] Verificando ruta existente para {dest}:")
    print(f"[src]   Comando: {cmd}")
    print(f"[src]   Return code: {proc.returncode}")
    print(f"[src]   Stdout: '{proc.stdout.decode().strip()}'")
    print(f"[src]   Stderr: '{proc.stderr.decode().strip()}'")
    
    if proc.returncode != 0:
        print(f"[src]   → Comando falló, asumiendo que no existe ruta")
        return False
    
    stdout = proc.stdout.decode().strip()
    exists = len(stdout) > 0
    print(f"[src]   → Ruta existe: {exists}")
    return exists


def main():
    p = argparse.ArgumentParser(description="Instala rutas SRv6 en RU usando iproute2 directamente.")
    p.add_argument("dest_prefix", help="Prefijo IPv6 del flujo, p.ej. fd00:0:2::2/64")
    p.add_argument("path_json", help="JSON-encoded list de nodos de la ruta")
    p.add_argument("--replace", action="store_true", help="Usar replace en lugar de add")
    p.add_argument("--high-occupancy", action="store_true", help="Indica si la ruta usa nodos con alta ocupación")
    args = p.parse_args()

    # Debug logging de argumentos de entrada
    print(f"[src] Args: dest_prefix={args.dest_prefix}, replace={args.replace}, "
          f"high_occupancy={args.high_occupancy}, path_json={args.path_json}")

    dest = args.dest_prefix.split('/')[0]
    path = json.loads(args.path_json)

    # Mostrar aviso si la ruta usa nodos con alta ocupación
    if args.high_occupancy:
        print(f"[src] AVISO: La ruta para {dest} usa nodos con alta ocupación (entre 80% y 95%)")

    print(f"[src] Cargando /app/networkinfo.json...")
    lbs = load_loopbacks()
    print(f"[src] Loopbacks: {lbs}\n")

    # Determinar método: add o replace
    # Si se pasa --replace O si ya existe una ruta para este destino, usar replace
    use_replace = args.replace or route_exists_for_dest(dest)
    method = "replace" if use_replace else "add"
    
    print(f"[src] → Determinando método de ruta:")
    print(f"[src]   - args.replace: {args.replace}")
    print(f"[src]   - route_exists_for_dest({dest}): {route_exists_for_dest(dest)}")
    print(f"[src]   - Método elegido: {method}")

    # Construir comando de ruta SRv6
    segs = ','.join(lbs[n] for n in path[1:])
    cmd_route = (
        f"/usr/sbin/ip -6 route {method} {dest} "
        f"encap seg6 mode encap segs {segs} dev eth1"
    )
    
    print(f"[src] Instalando ruta: {cmd_route}")
    
    # Usar la versión mejorada de ssh_ru con timestamps
    res_route = ssh_ru(cmd_route, flow_id=dest)
    
    # Imprimir información básica
    print(f"[src]   return {res_route.returncode}, stdout: {res_route.stdout.decode().strip()}, stderr: {res_route.stderr.decode().strip()}")

    # Si el comando falló con 'add' porque la ruta ya existe, intentar con 'replace'
    if res_route.returncode != 0 and method == "add" and "File exists" in res_route.stderr.decode():
        print(f"[src] → Comando 'add' falló porque ruta existe, reintentando con 'replace'")
        cmd_route_replace = (
            f"/usr/sbin/ip -6 route replace {dest} "
            f"encap seg6 mode encap segs {segs} dev eth1"
        )
        print(f"[src] Reintentando: {cmd_route_replace}")
        
        res_route = ssh_ru(cmd_route_replace, flow_id=dest)
        print(f"[src]   return {res_route.returncode}, stdout: {res_route.stdout.decode().strip()}, stderr: {res_route.stderr.decode().strip()}")

    print(f"[src] Done: flow {dest} → path={path}")

if __name__ == '__main__':
    main()