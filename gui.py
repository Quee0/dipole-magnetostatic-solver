import customtkinter
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import solver
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

gui_field_density = 5
gui_vector_size = 0.02
gui_field_size = 0.2
gui_streamplot_Z = 0
u0 = 4*np.pi*(10**(-7))

class Slider_with_entry(customtkinter.CTkFrame):
    def __init__(self, master, text_, from_ = 0, to = 100, number_of_steps_ = 100, def_val = 50):
        super().__init__(master)

        self.min_val = from_
        self.max_val = to

        self.grid_columnconfigure(1, weight=1)

        self.label = customtkinter.CTkLabel(self, text=text_)
        self.label.grid(row=0, column=0, padx=(10, 10), pady=10, sticky="w")

        self.slider = customtkinter.CTkSlider(self, from_=from_, to=to, number_of_steps=number_of_steps_, command=self._slider_event)
        self.slider.set(def_val)
        self.slider.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        self.entry_var = customtkinter.StringVar(value=f"{def_val:.2f}")
        self.entry = customtkinter.CTkEntry(self, width=60, textvariable=self.entry_var)
        self.entry.grid(row=0, column=2, padx=(10, 10), pady=10, sticky="e")

        # Binding
        self.entry.bind("<Return>", self._entry_event)
        self.entry.bind("<FocusOut>", self._entry_event)

    def _slider_event(self, value):
        self.entry_var.set(f"{value:.2f}")

    def _entry_event(self, event=None):
        try:
            value = float(self.entry_var.get())
            
            self.slider.set(value)
            self.entry_var.set(f"{value:.2f}") 

        except ValueError:
            self.entry_var.set(f"{self.slider.get():.2f}")

    def get(self):
        return float(self.entry_var.get())



class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        #WINDOW SETUP
        self.title("Dipole Magnetostatic Solver")
        self.geometry("1280x720")
        
        #GRID SETUP
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        # SIDEBAR
        self.sidebar_frame = customtkinter.CTkScrollableFrame(self, width=200)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")

        self.tittle = customtkinter.CTkLabel(self.sidebar_frame, text="Dipole Magnetostatic Solver", font=customtkinter.CTkFont(weight="bold"))
        self.tittle.pack(pady=10)

        # Options
        self.category_general_label = customtkinter.CTkLabel(self.sidebar_frame, text="General", font=customtkinter.CTkFont(weight="bold"), fg_color="#495057", corner_radius=20,)
        self.category_general_label.pack(pady=10)

        self.field_size_slider = Slider_with_entry(
            self.sidebar_frame, 
            text_="Field size", 
            from_=0.01, 
            to=50,
            number_of_steps_= 80-2, 
            def_val= 0.2, 
        )

        self.field_size_slider.pack(fill="x", padx=40, pady=10)

        self.field_density_slider = Slider_with_entry(
            self.sidebar_frame, 
            text_="Field density", 
            from_=2, 
            to=80,
            number_of_steps_= 80-2, 
            def_val= 40, 
        )
        self.field_density_slider.pack(fill="x", padx=40, pady=10)

        
        self.field_streamplot_Z_slider = Slider_with_entry(
            self.sidebar_frame, 
            text_="Streamplot Z level", 
            from_ = -10, 
            to = 10,
            number_of_steps_= 20/0.01, 
            def_val= 0, 
        )
        self.field_streamplot_Z_slider.pack(fill="x", padx=40, pady=10)

        self.category_dipoles_label = customtkinter.CTkLabel(self.sidebar_frame, text="Dipoles", font=customtkinter.CTkFont(weight="bold"), fg_color="#495057", corner_radius=20,)
        self.category_dipoles_label.pack(pady=10)

        self.category_visuals_label = customtkinter.CTkLabel(self.sidebar_frame, text="Visuals", font=customtkinter.CTkFont(weight="bold"), fg_color="#495057", corner_radius=20,)
        self.category_visuals_label.pack(pady=10)

        self.vector_size_slider = Slider_with_entry(
            self.sidebar_frame, 
            text_="Vector size", 
            from_=0.01, 
            to=1,
            number_of_steps_= 1/0.01, 
            def_val= 0.02, 
        )
        self.vector_size_slider.pack(fill="x", padx=40, pady=10)

        self.button = customtkinter.CTkButton(self.sidebar_frame, text="Solve", command=self.update_button_callback)
        self.button.pack(padx=30, pady=10, fill="x", side="bottom")

        #FIGURES
        self.figures_frame = customtkinter.CTkFrame(self)
        self.figures_frame.grid(row=0, column=1, sticky="ns")
        self.figures_frame.grid_columnconfigure(0, weight=1)
        self.figures_frame.grid_rowconfigure(0, weight=1)
        self.figures_frame.grid_rowconfigure(1, weight=0)

        self.fig = plt.figure(figsize=(11, 5.5))

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.figures_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=0, column=0, sticky="ns")

        #TOOLBAR
        toolbar = NavigationToolbar2Tk(self.canvas, self.figures_frame, pack_toolbar=False)
        toolbar.update()
        toolbar.grid(row=1, column=0, sticky="we")

    def generate_plots(self):

        gui_field_size = self.field_size_slider.get()
        gui_field_density = int(self.field_density_slider.get())
        gui_vector_size = self.vector_size_slider.get()
        gui_streamplot_Z = self.field_streamplot_Z_slider.get()

        data = solver.solve([[0,0,0,0,0,1]], gui_field_density, gui_vector_size, gui_field_size, gui_streamplot_Z)
        
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