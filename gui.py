import customtkinter
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import solver
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

gui_field_density = 5
gui_vector_size = 0.02
gui_field_size = 0.2
gui_streamplot_Z = 0
u0 = 4*np.pi*(10**(-7))

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("Dipole Magnetostatic Solver")
        self.geometry("1280x720")
        self.grid_columnconfigure((0, 1), weight=1)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        # SIDEBAR
        self.sidebar_frame = customtkinter.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")

        self.tittle = customtkinter.CTkLabel(self.sidebar_frame, text="Parameters", font=customtkinter.CTkFont(weight="bold"))
        self.tittle.pack(pady=(20, 10))

        self.slider = customtkinter.CTkSlider(self.sidebar_frame, from_=4, to=40)
        self.slider.pack(pady=(0, 20), padx=20)

        self.button = customtkinter.CTkButton(self.sidebar_frame, text="Solve", command=self.update_button_callback)
        self.button.pack(padx=10, pady=10, fill="x")

        #FIGURES
        self.fig = plt.figure(figsize=(12, 6))

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

    def generate_plots(self):
        data = solver.solve(gui_field_density, gui_vector_size, gui_field_size, gui_streamplot_Z)
        
        B_mod = np.sqrt(np.square(data.Bx_c)+np.square(data.By_c)+np.square(data.Bz_c))
        B_flat = B_mod.flatten()
        norm = mcolors.Normalize(vmin=B_flat.min(), vmax=B_flat.max()/10)
        cmap = cm.RdPu
        vector_colors = cmap(norm(B_flat))

        self.fig.clf()
        ax1 = self.fig.add_subplot(121, projection='3d')

        ax1.quiver3D(data.X, data.Y, data.Z, data.Bx_c, data.By_c, data.Bz_c, length=gui_vector_size, normalize=True, colors=vector_colors)
        for i in range(len(data.m_arr)):
            ax1.quiver3D(data.m_arr[i][0], data.m_arr[i][1], data.m_arr[i][2], data.m_arr[i][3], data.m_arr[i][4], data.m_arr[i][5], length=gui_vector_size*2, normalize=True, color='red')

        plt.tight_layout(pad=0)
        z_index = (np.abs(data.z - gui_streamplot_Z)).argmin() 

        Bx_2d = data.Bx_c[:, :, z_index]
        By_2d = data.By_c[:, :, z_index]
        B_mod_2d = B_mod[:, :, z_index]

        ax2 = self.fig.add_subplot(1,2,2)
        ax2.set_aspect('equal')
        strm = ax2.streamplot(data.x, data.y, Bx_2d, By_2d, color=np.log10(B_mod_2d), cmap=cm.RdPu, linewidth=1.5, density=1.5)
        for m in data.m_arr:
            ax2.plot(m[0], m[1], 'ro', markersize=5)

        plt.tight_layout()
        # plt.show()
        self.canvas.draw()


    def update_button_callback(self):
        self.generate_plots()