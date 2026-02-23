import numpy as np
import matplotlib.pyplot as plt

# Definir el rango de x (0 a 1 representa 0% a 100%)
x = np.linspace(0, 1, 1000)

# Crear la función escalón: 5 para x < 0.1 y 0.1 para x >= 0.1
y = np.where(x < 0.1, 5, 0.1)

# Dibujar la gráfica escalón
plt.step(x, y, where='post')
plt.xlabel('% Utilización Router')
plt.ylabel('Incremento de consumo')
plt.title('Coste encaminamiento Router tipo A') 
plt.grid(True)

# Guardar la gráfica en un archivo de imagen (por ejemplo, PNG)
plt.savefig('grafica_routerA.png', dpi=300)

plt.show()
