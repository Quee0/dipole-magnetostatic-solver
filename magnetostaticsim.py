import numpy as np
import matplotlib.pyplot as plt

x = np.linspace(1,100)
y = np.linspace(1,100)

X, Y = np.meshgrid(x, y)

Z = np.sin(X+Y)

fig = plt.figure()

ax = fig.add_subplot(111, projection='3d')

ax.plot_surface(X, Y, Z, cmap='viridis')

plt.show()