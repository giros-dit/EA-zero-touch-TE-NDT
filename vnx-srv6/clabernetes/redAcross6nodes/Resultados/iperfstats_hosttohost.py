import subprocess
import re
import time

# Archivo donde se guardarán los resultados
output_file = "iperf_results.txt"

# Expresión regular para extraer retardo (jitter) y pérdida de paquetes del receiver
jitter_pattern = re.compile(r"\[ *5\] *0.00-10.00  sec .*? ([0-9.]+) ms .*? (\d+)/(\d+) \(([-0-9.]+)%\)  receiver")

def run_iperf():
    cmd = "kubectl exec deploy/hupf-h1 -- docker exec hupf-h1 iperf3 -c fd00:0:2::2 -V -u -b 100M -l 1000"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    with open(output_file, "a") as f:
        f.write("Salida completa del comando:\n")
        f.write(result.stdout + "\n")
        f.write("Errores:\n")
        f.write(result.stderr + "\n")
    
    return result.stdout

def extract_metrics(output):
    jitters = []
    lost_packets = []
    total_packets = []
    loss_percentages = []
    
    for line in output.split("\n"):
        jitter_match = jitter_pattern.search(line)
        
        if jitter_match:
            jitters.append(float(jitter_match.group(1)))  # Jitter
            lost_packets.append(int(jitter_match.group(2)))  # Paquetes perdidos
            total_packets.append(int(jitter_match.group(3)))  # Total de paquetes
            loss_percentages.append(float(jitter_match.group(4)))  # Pérdida en %
    
    return jitters, lost_packets, total_packets, loss_percentages

def calculate_statistics(values):
    if not values:
        return None, None, None
    return sum(values) / len(values), min(values), max(values)

jitters_all = []
lost_packets_all = []
total_packets_all = []
loss_percentages_all = []

for i in range(10):
    print(f"Ejecutando iperf3... intento {i+1}/10")
    output = run_iperf()
    jitters, lost_packets, total_packets, loss_percentages = extract_metrics(output)
    
    jitters_all.extend(jitters)
    lost_packets_all.extend(lost_packets)
    total_packets_all.extend(total_packets)
    loss_percentages_all.extend(loss_percentages)
    
    if i < 9:
        time.sleep(60)

with open(output_file, "a") as f:
    f.write(f"Jitters: {jitters_all}\n")
    f.write(f"Pérdida de paquetes (número): {lost_packets_all}\n")
    f.write(f"Total de paquetes enviados: {total_packets_all}\n")
    f.write(f"Pérdida de paquetes (%): {loss_percentages_all}\n")

if jitters_all:
    avg_jitter, min_jitter, max_jitter = calculate_statistics(jitters_all)
    with open(output_file, "a") as f:
        f.write(f"Jitter: media={avg_jitter} ms, min={min_jitter} ms, max={max_jitter} ms\n")
    print(f"Jitter: media={avg_jitter} ms, min={min_jitter} ms, max={max_jitter} ms")

if lost_packets_all:
    avg_lost, min_lost, max_lost = calculate_statistics(lost_packets_all)
    with open(output_file, "a") as f:
        f.write(f"Paquetes perdidos: media={avg_lost}, min={min_lost}, max={max_lost}\n")
    print(f"Paquetes perdidos: media={avg_lost}, min={min_lost}, max={max_lost}")

if loss_percentages_all:
    avg_loss, min_loss, max_loss = calculate_statistics(loss_percentages_all)
    with open(output_file, "a") as f:
        f.write(f"Pérdida de paquetes (%): media={avg_loss}%, min={min_loss}%, max={max_loss}%\n")
    print(f"Pérdida de paquetes (%): media={avg_loss}%, min={min_loss}%, max={max_loss}%")
