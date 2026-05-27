import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors

field_density = 8
vector_size = 0.05
u0 = 4*np.pi*(10**(-7))

m_arr  = [[0,1,0],[0,1,0]]
rm_arr = [[0,-0.5,0],[0,0.5,0]];

x = np.linspace(-0.5,0.5,field_density)
y = np.linspace(-0.5,0.5,field_density)
z = np.linspace(-0.5,0.5,field_density)

X, Y, Z = np.meshgrid(x, y, z)

Bx_c = np.zeros((field_density,field_density,field_density))
By_c = np.zeros((field_density,field_density,field_density))
Bz_c = np.zeros((field_density,field_density,field_density))

for i in range(len(m_arr)):

    #Dipole position vector
    rmx = rm_arr[i][0]
    rmy = rm_arr[i][1]
    rmz = rm_arr[i][2]

    #Dipole moment vector
    mx = m_arr[i][0]
    my = m_arr[i][1]
    mz = m_arr[i][2]

    rx = X - rmx
    ry = Y - rmy
    rz = Z - rmz
    r_mod = np.sqrt(np.square(rx)+np.square(ry)+np.square(rz))

    Bx = ((u0)/(4*np.pi*np.power(r_mod, 3)))*(((3*mx*rx*rx)/(r_mod**2))+((3*my*rx*ry)/(r_mod**2))+((3*mz*rz*rx)/(r_mod**2))-mx)
    By = ((u0)/(4*np.pi*np.power(r_mod, 3)))*(((3*mx*rx*ry)/(r_mod**2))+((3*my*ry*ry)/(r_mod**2))+((3*mz*rz*ry)/(r_mod**2))-my)
    Bz = ((u0)/(4*np.pi*np.power(r_mod, 3)))*(((3*mx*rx*rz)/(r_mod**2))+((3*my*ry*rz)/(r_mod**2))+((3*mz*rz*rz)/(r_mod**2))-mz)

    Bx_c += Bx
    By_c += By
    Bz_c += Bz

B_mod = np.sqrt(np.square(Bx_c)+np.square(By_c)+np.square(Bz_c))

B_flat = B_mod.flatten()
norm = mcolors.Normalize(vmin=B_flat.min(), vmax=B_flat.max()/50)
cmap = cm.RdPu
vector_colors = cmap(norm(B_flat))

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

ax.quiver3D(X, Y, Z, Bx_c, By_c, Bz_c, length=0.05, normalize=True, colors=vector_colors)
for i in range(len(m_arr)):
    ax.quiver3D(rm_arr[i][0], rm_arr[i][1], rm_arr[i][2], m_arr[i][0], m_arr[i][1], m_arr[i][2], length=vector_size*4, normalize=True, color='red')

plt.tight_layout(pad=0)
# ax.set_proj_type('ortho')
# ax.view_init(elev=90, azim=-90)
plt.show()