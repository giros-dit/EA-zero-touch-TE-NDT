import subprocess

def run_command(command):
    """Ejecuta un comando en el shell y espera a que finalice antes de continuar."""
    try:
        print(f"Ejecutando: {command}")
        result = subprocess.run(command, shell=True, check=True, text=True)
        print(f"Comando completado: {command}")
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar el comando: {e}")
        exit(1)

def main():
    # Paso 1: Levantar el escenario con VNX
    run_command("sudo vnx -f openstack_kolla_ansible-vlan-4n.xml -t")
    
    # Paso 2: Instalar Kubernetes
    run_command("sudo ./install-k8s-from-scratch-openstack -c")
    
    # Paso 3: Copiar la configuración de Kubernetes al host local
    run_command("ssh root@controller cat /root/.kube/config > ~/.kube/config")
    
    # Paso 4: Generar las subinterfaces br-vlan.XXXX
    run_command("sudo ./generatebrvlan.sh")
    
    # Paso 5: Crear alias para helm
    helm_alias = (
        "alias helm='docker run --network host -ti --rm -v $(pwd):/apps -w /apps "
        "-v ~/.kube:/root/.kube -v ~/.helm:/root/.helm "
        "-v ~/.config/helm:/root/.config/helm "
        "-v ~/.cache/helm:/root/.cache/helm "
        "alpine/helm:3.12.3'"
    )
    run_command(helm_alias)
    
    # Paso 6: Instalar Clabernetes en el clúster
    run_command(
        "helm upgrade --install --create-namespace --namespace c9s "
        "clabernetes oci://ghcr.io/srl-labs/clabernetes/clabernetes"
    )
    
    # Paso 7: Aplicar el namespace de la topología
    run_command("kubectl apply -f ./converted/_srv6-ns.yaml")

    # Paso 8: Crear los objetos NetworkAttachmentDefinition con createVLANScni.sh
    run_command("sudo ./createVLANScni.sh")
    
    # Paso 9: Aplicar el archivo de topología
    run_command("kubectl apply -f ./converted")
    
    # Confirmación final
    print("El despliegue del escenario, Kubernetes, Clabernetes y la configuración de la topología han sido completados exitosamente.")

if __name__ == "__main__":
    main()
