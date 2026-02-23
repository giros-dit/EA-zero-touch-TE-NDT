import sys
import os
import json

def iniciaficheros():
    os.makedirs('./conf/r11', exist_ok=True)
    with open('./conf/r11/script.sh', 'w') as f:
        f.write("#!/bin/bash\n")

    os.makedirs('./conf/r12', exist_ok=True)
    with open('./conf/r12/script.sh', 'w') as f:
        f.write("#!/bin/bash\n")

    os.makedirs('./conf/r13', exist_ok=True)
    with open('./conf/r13/script.sh', 'w') as f:
        f.write("#!/bin/bash\n")

def cargarjson(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    return data

VLAN_IPv6_gNB = {
    111: "fd00:0:2::/127",
    112: "fd00:0:2::2/127",
    113: "fd00:0:2::4/127",
    121: "fd00:0:3::/127",
    122: "fd00:0:3::2/127",
    123: "fd00:0:3::4/127"
}

VLAN_IPv6_UPF = {
    111: "fd00:0:1::/127",
    112: "fd00:0:1::2/127",
    113: "fd00:0:1::4/127",
    121: "fd00:0:1::6/127",
    122: "fd00:0:1::8/127",
    123: "fd00:0:1::a/127"
}

def createupf(vlan, routers, method):
    
    VLAN = int(vlan)

    if VLAN < 120:
        if routers:
            segments = [r for r in routers] + [f'fcff:11::1']
        else:
            segments = [f'fcff:11::1']

    elif VLAN < 130:
        if routers:
            segments = [r for r in routers] + [f'fcff:12::1']
        else:
            segments = [f'fcff:12::1']

    else:
        print("VLAN not supported")
        sys.exit(1)
    
    ipgNB=VLAN_IPv6_gNB[VLAN]
    
    comandoupf = f"sudo docker exec clab-srv6-r13 ip -6 route {method} {ipgNB} encap seg6 mode encap segs {','.join(segments)} dev eth3.{VLAN}"
    
    return comandoupf

def creategnb(VLAN, routers ,method):
    
    if routers:
        segments = [r for r in routers] + [f'fcff:13::1']
    else:
        segments = [f'fcff:13::1']
    
    if VLAN < 120:
        rp = 11
    elif VLAN < 130:
        rp = 12
    else:
        print("VLAN not supported")
        sys.exit(1)

    ipUPF=VLAN_IPv6_UPF[VLAN]
    
    comandognb = f"sudo docker exec clab-srv6-r{rp} ip -6 route {method} {ipUPF} encap seg6 mode encap segs {','.join(segments)} dev eth3.{VLAN}"
    
    return comandognb

def save(command, file):
    with open(file, 'a') as f:
        f.write(command + "\n")

def getNombrefichero(VLAN):
    if(VLAN < 120):
        return "r11"
    elif(VLAN < 130):
        return "r12"

def getMethod(conf_old, vlan, routers):
    if vlan not in conf_old:
        return "add"
    if conf_old[vlan] != routers:
        return "replace"

def execute():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.system(f"sudo chmod +x {script_dir}/conf/r11/script.sh")
    os.system(f"sudo chmod +x {script_dir}/conf/r12/script.sh")
    os.system(f"sudo chmod +x {script_dir}/conf/r13/script.sh")
    os.system(f"sudo {script_dir}/conf/r11/script.sh")
    os.system(f"sudo {script_dir}/conf/r12/script.sh")
    os.system(f"sudo {script_dir}/conf/r13/script.sh")

def main():
    iniciaficheros()
    conf = cargarjson('./VLANtunnels.json')
    
    # Intentar cargar VLANtunnelsold.json si existe
    if os.path.exists('./VLANtunnelsold.json'):
        conf_old = cargarjson('./VLANtunnelsold.json')
    else:
        conf_old = {}

    # Recorrer fichero json
    for vlan, routers in conf.items():
        print(f"Processing VLAN: {vlan}")
        
        # Obtener VLAN y camino de routers del json de una VLAN
        VLAN = int(vlan)
        routersupfgnb = routers.get("fw", [])
        if routersupfgnb and routers.get("same_path", False):
            routersgnbupf = routersupfgnb[::-1]
        else:
            routersgnbupf = routers.get("rt", [])

        # Decidir si es r11 o r12 el fichero a modificar
        routerAcceso = getNombrefichero(VLAN)
        print(f"Router access file: {routerAcceso}")
        

        # Comprobar si la configuración ha cambiado
        if vlan not in conf_old or conf_old[vlan] != routers:
            # Crear comandos para cada fichero
            action = getMethod(conf_old, vlan, routers)
            commandr13 = createupf(VLAN, routersupfgnb, action)
            commandgnb = creategnb(VLAN, routersgnbupf, action)
            print(f"Command for r13: {commandr13}")
            print(f"Command for gNB: {commandgnb}")
            #Crear ficheros script.sh
            scriptr13 = './conf/r13/script.sh'
            scriptgnb = f'./conf/{routerAcceso}/script.sh'
            print(f"Configuration changed for VLAN: {vlan}")
            save(commandgnb, scriptgnb)
            save(commandr13, scriptr13)
        else:
            print(f"No changes for VLAN: {vlan}")
        
    execute()

    # Borrar el contenido de los ficheros script.sh
    directories = ['./conf/r11', './conf/r12', './conf/r13']
    for directory in directories:
        script_path = os.path.join(directory, 'script.sh')
        if os.path.exists(script_path):
            with open(script_path, 'w') as script_file:
                script_file.write('')

if __name__ == "__main__":
    main()
