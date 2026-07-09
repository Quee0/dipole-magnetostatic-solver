import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors

u0 = 4*np.pi*(10**(-7))

class Field_data:
    def __init__(self, x, y, z, X, Y, Z, Bx_c, By_c, Bz_c, m_arr):
        self.x = x
        self.y = y
        self.z = z
        self.X = X
        self.Y = Y
        self.Z = Z
        self.Bx_c = Bx_c
        self.By_c = By_c
        self.Bz_c = Bz_c
        self.m_arr = m_arr

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

def solve(m_arr, field_density, vector_size, field_size, streamplot_Z):
    # m_arr  = [[0,0,0,0,0,1]]
    # m_arr = generate_dipoles([0,0,0], (np.pi/12), [1,0,0], 0.1, 4)

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

    data_pack = Field_data(x,y,z,X,Y,Z,Bx_c,By_c,Bz_c, m_arr)
    return data_pack