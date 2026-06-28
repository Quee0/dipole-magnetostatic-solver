import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors

field_density = 15
vector_size = 0.02
field_size = 0.2
streamplot_Z = 0
u0 = 4*np.pi*(10**(-7))

def stworz_obsluge_sondy(ax, fig, tablica_x, tablica_y, dane_b):
    sonda_tekst = None
    sonda_punkt = None

    def onclick(event):
        nonlocal sonda_tekst, sonda_punkt
        
        if event.inaxes != ax: 
            return 
            
        cx, cy = event.xdata, event.ydata
        if cx is None or cy is None: 
            return

        ix = (np.abs(tablica_x - cx)).argmin()
        iy = (np.abs(tablica_y - cy)).argmin()
        b_wartosc = dane_b[iy, ix]

        if sonda_tekst: sonda_tekst.remove()
        if sonda_punkt: sonda_punkt.remove()

        sonda_punkt, = ax.plot(cx, cy, 'bo', markersize=6)
        
        sonda_tekst = ax.annotate(
            f'|B|: {b_wartosc:.2e} T\n(x: {cx:.2f}, y: {cy:.2f})', 
            (cx, cy), xytext=(10, 10), textcoords='offset points',
            bbox=dict(boxstyle="round,pad=0.5", fc="white", ec="black", alpha=0.9),
            arrowprops=dict(arrowstyle="->", connectionstyle="arc3")
        )
        fig.canvas.draw()

    return onclick

def generate_dipoles(center, ang, n, rad, m_mod):
    
    m_arr = []
    for phi in np.arange(0, 2 * np.pi, ang):
        dipole = [
            rad * np.cos(phi),
            rad * np.sin(phi),
            0,
            0,
            0,
            0
        ]

        if phi < np.pi:
            dipole[3] = m_mod*center[0] - dipole[0]
            dipole[4] = m_mod*center[1] - dipole[1]
            dipole[5] = m_mod*center[2] - dipole[2]
        else:
            dipole[3] = -(m_mod*center[0] - dipole[0])
            dipole[4] = -(m_mod*center[1] - dipole[1])
            dipole[5] = -(m_mod*center[2] - dipole[2])

        m_arr.append(dipole)
        
    return m_arr

def main():
    # m_arr  = [[0,0,0,0,0,1]]
    m_arr = generate_dipoles([0,0,0], (np.pi/12), [1,0,0], 0.1, 4)

    x = np.linspace(-field_size,field_size,field_density)
    y = np.linspace(-field_size,field_size,field_density)
    z = np.linspace(-field_size,field_size,field_density)

    X, Y, Z = np.meshgrid(x, y, z)

    Bx_c = np.zeros((field_density,field_density,field_density))
    By_c = np.zeros((field_density,field_density,field_density))
    Bz_c = np.zeros((field_density,field_density,field_density))

    for i in range(len(m_arr)):

        #Dipole position vector
        rmx = m_arr[i][0]
        rmy = m_arr[i][1]
        rmz = m_arr[i][2]

        #Dipole moment vector
        mx = m_arr[i][3]
        my = m_arr[i][4]
        mz = m_arr[i][5]

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
    norm = mcolors.Normalize(vmin=B_flat.min(), vmax=B_flat.max()/10)
    cmap = cm.RdPu
    vector_colors = cmap(norm(B_flat))

    fig = plt.figure()
    ax1 = fig.add_subplot(121, projection='3d')

    ax1.quiver3D(X, Y, Z, Bx_c, By_c, Bz_c, length=vector_size, normalize=True, colors=vector_colors)
    for i in range(len(m_arr)):
        ax1.quiver3D(m_arr[i][0], m_arr[i][1], m_arr[i][2], m_arr[i][3], m_arr[i][4], m_arr[i][5], length=vector_size*2, normalize=True, color='red')

    plt.tight_layout(pad=0)
    # ax.set_proj_type('ortho')
    # ax.view_init(elev=90, azim=-90)

    z_index = (np.abs(z - streamplot_Z)).argmin() 

    Bx_2d = Bx_c[:, :, z_index]
    By_2d = By_c[:, :, z_index]
    B_mod_2d = B_mod[:, :, z_index]

    ax2 = fig.add_subplot(1,2,2)
    ax2.set_aspect('equal')
    strm = ax2.streamplot(x, y, Bx_2d, By_2d, color=np.log10(B_mod_2d), cmap=cm.RdPu, linewidth=1.5, density=1.5)
    
    for m in m_arr:
        ax2.plot(m[0], m[1], 'ro', markersize=5)

    obsluga = stworz_obsluge_sondy(ax2, fig, x, y, B_mod_2d)
    fig.canvas.mpl_connect('button_press_event', obsluga)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__": main()