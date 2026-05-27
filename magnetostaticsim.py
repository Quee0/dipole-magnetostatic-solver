import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors

field_density = 12
u0 = 4*np.pi*(10**(-7))

x = np.linspace(-0.5,0.5,field_density)
y = np.linspace(-0.5,0.5,field_density)
z = np.linspace(-0.5,0.5,field_density)

#Dipole position vector
rmx = 0
rmy = 0
rmz = 0

#Dipole moment vector
mx = 1
my = 1
mz = 0

X, Y, Z = np.meshgrid(x, y, z)
rx = X - rmx
ry = Y - rmy
rz = Z - rmz
r_mod = np.sqrt(np.square(rx)+np.square(ry)+np.square(rz))

Bx = ((u0)/(4*np.pi*np.power(r_mod, 3)))*(((3*mx*rx*rx)/(r_mod**2))+((3*my*rx*ry)/(r_mod**2))+((3*mz*rz*rx)/(r_mod**2))-mx)
By = ((u0)/(4*np.pi*np.power(r_mod, 3)))*(((3*mx*rx*ry)/(r_mod**2))+((3*my*ry*ry)/(r_mod**2))+((3*mz*rz*ry)/(r_mod**2))-my)
Bz = ((u0)/(4*np.pi*np.power(r_mod, 3)))*(((3*mx*rx*rz)/(r_mod**2))+((3*my*ry*rz)/(r_mod**2))+((3*mz*rz*rz)/(r_mod**2))-mz)

B_mod = np.sqrt(np.square(Bx)+np.square(By)+np.square(Bz))

B_flat = B_mod.flatten()
norm = mcolors.Normalize(vmin=B_flat.min(), vmax=B_flat.max()/50)
cmap = cm.RdPu
kolory = cmap(norm(B_flat))

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

ax.quiver3D(X, Y, Z, Bx, By, Bz, length=0.05, normalize=True, colors=kolory)

plt.tight_layout(pad=0)
plt.show()