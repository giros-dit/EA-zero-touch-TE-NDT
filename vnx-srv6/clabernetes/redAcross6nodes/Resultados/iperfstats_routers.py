import subprocess
import re
import time

# Archivo donde se guardarán los resultados
output_file = "iperf_results_r1r2.txt"

def run_iperf():
    cmd = "kubectl exec deploy/r1 -- docker exec r1 iperf -c fcff:2::1 -V"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    with open(output_file, "a") as f:
        f.write("Salida completa del comando:\n")
        f.write(result.stdout + "\n")
    
    return result.stdout


def calculate_statistics(values):
    if not values:
        return None, None, None
    return sum(values) / len(values), min(values), max(values)


# Expresión regular para extraer el ancho de banda
bandwidth_pattern = re.compile(r"\[ *\d+\] *0.0000-10.\d+ sec *\d+.\d+ GBytes *(\d+.\d+) Gbits/sec")

bandwidths_all = []

for i in range(10):
    print(f"Ejecutando iperf3... intento {i+1}/10")
    output = run_iperf()
    for line in output.split("\n"):
        bandwidth_match = bandwidth_pattern.search(line)
        if bandwidth_match:
            bandwidths_all.append(float(bandwidth_match.group(1)))  # Bandwidth in Gbits/sec
            with open(output_file, "a") as f:
                f.write(f"Bandwidth leído: {bandwidth_match.group(1)} Gbits/sec\n")
    if i < 9:
        time.sleep(10)

with open(output_file, "a") as f:
    f.write(f"Bandwidths: {bandwidths_all}\n")

if bandwidths_all:
    avg_bandwidth, min_bandwidth, max_bandwidth = calculate_statistics(bandwidths_all)
    with open(output_file, "a") as f:
        f.write(f"Bandwidth: media={avg_bandwidth} Gbits/sec, min={min_bandwidth} Gbits/sec, max={max_bandwidth} Gbits/sec\n")
    print(f"Bandwidth: media={avg_bandwidth} Gbits/sec, min={min_bandwidth} Gbits/sec, max={max_bandwidth} Gbits/sec")