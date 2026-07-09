import sys
import customtkinter
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import solver
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

gui_field_density = 5
gui_vector_size = 0.02
gui_field_size = 0.2
gui_streamplot_Z = 0
u0 = 4*np.pi*(10**(-7))

standard_padx = 8
standard_pady = 5

class Slider_with_entry(customtkinter.CTkFrame):
    def __init__(self, master, text_, from_ = 0, to = 100, number_of_steps_ = 100, def_val = 50):
        super().__init__(master)

        self.min_val = from_
        self.max_val = to

        self.grid_columnconfigure(1, weight=1)

        self.label = customtkinter.CTkLabel(self, text=text_)
        self.label.grid(row=0, column=0, padx=standard_padx, pady=standard_pady, sticky="w")

        self.slider = customtkinter.CTkSlider(self, from_=from_, to=to, number_of_steps=number_of_steps_, command=self._slider_event)
        self.slider.set(def_val)
        self.slider.grid(row=0, column=1, padx=standard_padx, pady=standard_pady, sticky="ew")

        self.entry_var = customtkinter.StringVar(value=f"{def_val:.2f}")
        self.entry = customtkinter.CTkEntry(self, width=60, textvariable=self.entry_var)
        self.entry.grid(row=0, column=2, padx=standard_padx, pady=standard_pady, sticky="e")

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


class Label_with_entry(customtkinter.CTkFrame):
    def __init__(self, master, text_, def_val=""):
        super().__init__(master)

        self.grid_columnconfigure(1, weight=1)

        self.label = customtkinter.CTkLabel(self, text=text_)
        self.label.grid(row=0, column=0, padx=standard_padx, pady=standard_pady, sticky="w")

        self.entry_var = customtkinter.StringVar(value=str(def_val))

        self.entry = customtkinter.CTkEntry(self, textvariable=self.entry_var)
        self.entry.grid(row=0, column=1, padx=standard_padx, pady=standard_pady, sticky="ew")

    def get(self):
        return self.entry_var.get()
        
    def set(self, value):
        self.entry_var.set(str(value))


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        #WINDOW SETUP
        self.title("Dipole Magnetostatic Solver")
        self.geometry("1280x720")
        self.protocol("WM_DELETE_WINDOW", self.destructor)
        
        #GRID SETUP
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        # SIDEBAR
        self.sidebar_frame = customtkinter.CTkScrollableFrame(self, width=200)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")

        self.tittle = customtkinter.CTkLabel(self.sidebar_frame, text="Dipole Magnetostatic Solver", font=customtkinter.CTkFont(weight="bold"))
        self.tittle.pack(pady=standard_pady)

        self.solve_button = customtkinter.CTkButton(self.sidebar_frame, text="Solve", command=self.update_button_callback)
        self.solve_button.pack(padx=standard_padx, pady=standard_pady, fill="x")

        # Options
        self.category_general_label = customtkinter.CTkLabel(self.sidebar_frame, text="General", font=customtkinter.CTkFont(weight="bold"), fg_color="#495057", corner_radius=20,)
        self.category_general_label.pack(pady=standard_pady)

        self.field_size_slider = Slider_with_entry(
            self.sidebar_frame, 
            text_="Field size [m]", 
            from_=0.01, 
            to=50,
            number_of_steps_= 80-2, 
            def_val= 0.2, 
        )

        self.field_size_slider.pack(fill="x", padx=standard_padx, pady=standard_pady)

        self.field_density_slider = Slider_with_entry(
            self.sidebar_frame, 
            text_="Field density", 
            from_=2, 
            to=80,
            number_of_steps_= 80-2, 
            def_val= 40, 
        )
        self.field_density_slider.pack(fill="x", padx=standard_padx, pady=standard_pady)
        
        self.field_streamplot_Z_slider = Slider_with_entry(
            self.sidebar_frame, 
            text_="Streamplot Z level [m]", 
            from_ = -10, 
            to = 10,
            number_of_steps_= 20/0.01, 
            def_val= 0, 
        )
        self.field_streamplot_Z_slider.pack(fill="x", padx=standard_padx, pady=standard_pady)

        #Dipole options
        self.category_dipoles_label = customtkinter.CTkLabel(self.sidebar_frame, text="Dipoles", font=customtkinter.CTkFont(weight="bold"), fg_color="#495057", corner_radius=20,)
        self.category_dipoles_label.pack(pady=standard_pady)

        self.dipole_menu_button = customtkinter.CTkSegmentedButton(
            self.sidebar_frame, 
            values=["Magnetized Volume", "Independent Dipole"],
            command=self.change_dipole_mode
        )

        self.dipole_menu_button.pack(pady=standard_pady, padx=standard_padx, fill="x")
        self.dipole_menu_button.set("Magnetized Volume")

        self.dipol_menu_frame = customtkinter.CTkFrame(self.sidebar_frame)
        self.dipol_menu_frame.pack(fill="both", expand=True, padx=standard_padx, pady=(0, 20))

        # VOLUMETRIC
        self.frame_magnets = customtkinter.CTkFrame(self.dipol_menu_frame, fg_color="transparent")
        self.frame_magnets.pack(fill="both", expand=True)
        
        self.polar_cord = customtkinter.CTkCheckBox(self.frame_magnets, text="Use polar coordinate system")
        self.polar_cord.pack(padx=standard_padx, pady=standard_pady, fill='x')
        
        self.polar_swap = customtkinter.CTkCheckBox(self.frame_magnets, text="Swap polarity mid sweep")
        self.polar_swap.pack(padx=standard_padx, pady=standard_pady, fill='x')
        
        self.radius = Label_with_entry(
            self.frame_magnets,
            text_ = "Radius [m]",
            def_val = 0.2,
        )
        self.radius.pack(pady=standard_pady, fill="x")

        self.mag_count = Label_with_entry(
            self.frame_magnets,
            text_ = "Count",
            def_val = 6,
        )
        self.mag_count.pack(pady=standard_pady, fill="x")

        self.size_x = Label_with_entry(
            self.frame_magnets,
            text_ = "Size x [m]",
            def_val = 0.1,
        )
        self.size_x.pack(pady=standard_pady, fill="x")

        self.size_y = Label_with_entry(
            self.frame_magnets,
            text_ = "Size y [m]",
            def_val = 0.1,
        )
        self.size_y.pack(pady=standard_pady, fill="x")
        
        self.size_z = Label_with_entry(
            self.frame_magnets,
            text_ = "Size z [m]",
            def_val = 0.1,
        )
        self.size_z.pack(pady=standard_pady, fill="x")

        self.vol_resolution = Slider_with_entry(
            self.frame_magnets, 
            text_="Volumetric m's resolution", 
            from_ = 1, 
            to = 20,
            number_of_steps_= 19, 
            def_val= 5, 
        )
        self.vol_resolution.pack(fill="x", padx=standard_padx, pady=standard_pady)

        self.remanence_entry = Label_with_entry(
            self.frame_magnets,
            text_ = "Remanence [T]",
            def_val = 1.3,
        )
        self.remanence_entry.pack(pady=standard_pady, fill="x")

        self.mag_axis_combobox = customtkinter.CTkComboBox(
            self.frame_magnets, 
            values=["x", "y", "z"],
        )
        self.mag_axis_combobox.pack(pady=standard_pady)

        #INDEPENDENT DIPOLE
        self.frame_dipol = customtkinter.CTkFrame(self.dipol_menu_frame, fg_color="transparent")

        self.dip_mag_moment = Label_with_entry(
            self.frame_dipol,
            text_ = "Dipole magnetic moment [A*m^2]",
            def_val = 1,
        )
        self.dip_mag_moment.pack(pady=standard_pady, fill="x")

        self.dip_axis_combobox = customtkinter.CTkComboBox(
            self.frame_dipol,
            values=["x", "y", "z"],
        )
        self.dip_axis_combobox.pack(pady=standard_pady)

        self.dip_polar_setup = customtkinter.CTkCheckBox(self.frame_dipol, text="Use polar coordinate preset")
        self.dip_polar_setup.pack(padx=standard_padx, pady=standard_pady, fill='x')

        self.category_flux_label = customtkinter.CTkLabel(self.sidebar_frame, text="Compute flux", font=customtkinter.CTkFont(weight="bold"), fg_color="#495057", corner_radius=20,)
        self.category_flux_label.pack(pady=standard_pady)

        self.flux_result_label = customtkinter.CTkLabel(self.sidebar_frame, text="Flux: --- Wb", text_color="cyan", font=customtkinter.CTkFont(weight="bold", size=14))
        self.flux_result_label.pack(pady=standard_pady)

        self.flux_x = Label_with_entry(
            self.sidebar_frame,
            text_ = "Flux x size [m]",
            def_val = 0.1,
        )
        self.flux_x.pack(pady=standard_pady, fill="x")
        
        self.flux_z = Label_with_entry(
            self.sidebar_frame,
            text_ = "Flux z size [m]",
            def_val = 0.1,
        )
        self.flux_z.pack(pady=standard_pady, fill="x")

        self.flux_y_pos = Label_with_entry(
            self.sidebar_frame,
            text_ = "Flux y pos [m]",
            def_val = 0,
        )
        self.flux_y_pos.pack(pady=standard_pady, fill="x")

        self.flux_resolution = Label_with_entry(
            self.sidebar_frame,
            text_ = "Flux resolution [m]",
            def_val = 5,
        )
        self.flux_resolution.pack(pady=standard_pady, fill="x")

        self.category_visuals_label = customtkinter.CTkLabel(self.sidebar_frame, text="Visuals", font=customtkinter.CTkFont(weight="bold"), fg_color="#495057", corner_radius=20,)
        self.category_visuals_label.pack(pady=standard_pady)

        self.vector_size_slider = Slider_with_entry(
            self.sidebar_frame, 
            text_="Vector size", 
            from_=0.01, 
            to=1,
            number_of_steps_= 1/0.01, 
            def_val= 0.02, 
        )
        self.vector_size_slider.pack(fill="x", padx=standard_padx, pady=standard_pady)

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

        self.sonda_text = None
        self.sonda_point = None
        self.sonda_cid = None
        self.sonda_ax = None
        self.sonda_data_x = None
        self.sonda_data_y = None
        self.sonda_data_b = None

    def sonda_function(self, event):
        if event.inaxes != self.sonda_ax or self.sonda_data_b is None: 
            return 
            
        cx, cy = event.xdata, event.ydata
        if cx is None or cy is None: 
            return

        ix = (np.abs(self.sonda_data_x - cx)).argmin()
        iy = (np.abs(self.sonda_data_y - cy)).argmin()
        b_value = self.sonda_data_b[iy, ix]

        if self.sonda_text: 
            try: self.sonda_text.remove()
            except ValueError: pass
        if self.sonda_point: 
            try: self.sonda_point[0].remove()
            except ValueError: pass

        self.sonda_point = self.sonda_ax.plot(cx, cy, 'bo', markersize=6)
        
        text_color = "#000000"
        fg_color = "#ffffff"
        self.sonda_text = self.sonda_ax.annotate(
            f'|B|: {b_value:.2e} T\n(x: {cx:.2f}, y: {cy:.2f})', 
            (cx, cy), xytext=(10, 10), textcoords='offset points',
            bbox=dict(boxstyle="round,pad=0.5", fc=fg_color, alpha=0.9),
            color=text_color,
            arrowprops=dict(arrowstyle="->", connectionstyle="arc3", color=text_color)
        )

        self.data
        self.canvas.draw()

    def change_dipole_mode(self, chosen_mode):
            self.frame_magnets.pack_forget()
            self.frame_dipol.pack_forget()

            if chosen_mode == "Magnetized Volume":
                self.frame_magnets.pack(fill="both", expand=True)
                
            elif chosen_mode == "Independent Dipole":
                self.frame_dipol.pack(fill="both", expand=True)

    def generate_m_volumetric(self, lx, ly, lz, n, p_axis):
        
        Br = float(self.remanence_entry.get()) #Remanence
        M = Br/u0 #Magnetization
        dV = (lx*ly*lz)/(pow(n,3))

        m_mod = M*dV # m_mod is dipole moment for dV
        
        x = np.linspace(-lx/2, lx/2, n)
        y = np.linspace(-ly/2, ly/2, n)
        z = np.linspace(-lz/2, lz/2, n)
        X, Y, Z = np.meshgrid(x, y, z)
        
        pos_matrix = np.column_stack((X.flatten(), Y.flatten(), Z.flatten()))
        pos = pos_matrix.tolist()
        
        if   p_axis == 'x': m = [m_mod, 0,          0]
        elif p_axis == 'y': m = [0,     m_mod,      0]
        else:               m = [0,     0,      m_mod]
        
        m_arr = []
        for i in range(len(pos)):
            m_arr.append([pos[i][0], pos[i][1], pos[i][2], m[0], m[1], m[2]])

        if self.polar_cord.get():
            r = float(self.radius.get())
            count = int(self.mag_count.get())
            step = (2*np.pi)/count

            new_m_arr = []
            m_arr_element_handler = []
            x, y
            theta = 0
            while theta <= 2*np.pi:
                x = r*np.cos(theta)
                y = r*np.sin(theta)

                fi = 0 #angle of rotation
                if self.polar_swap.get() and theta > np.pi: fi = theta + np.pi
                else: fi = theta

                rotation_matrix = np.matrix([[np.cos(fi),-np.sin(fi), 0],[np.sin(fi), np.cos(fi), 0],[0, 0, 1]])

                for i in range(len(m_arr)):

                    pos_vec = np.array([m_arr[i][0], m_arr[i][1], m_arr[i][2]])
                    m_vec   = np.array([m_arr[i][3], m_arr[i][4], m_arr[i][5]])

                    new_pos_vec = np.dot(rotation_matrix, pos_vec)
                    new_m_vec = np.dot(rotation_matrix, m_vec)

                    m_arr_element_handler = [new_pos_vec[0, 0]+x, new_pos_vec[0, 1]+y, new_pos_vec[0, 2], new_m_vec[0, 0], new_m_vec[0, 1], new_m_vec[0, 2]]
                    new_m_arr.append(m_arr_element_handler)
                
                theta += step
            m_arr = new_m_arr


        return m_arr

    def compute_flux(self):

        if not hasattr(self, 'data') or self.data is None:
            return 0.0

        # FLUX = SS B*dS
        lx = float(self.flux_x.get())
        lz = float(self.flux_z.get())
        y_pos = float(self.flux_y_pos.get())
        n = int(self.flux_resolution.get())
        if n < 2: n = 2

        flux_x_arr = np.linspace(-lx/2, lx/2, n)
        flux_z_arr = np.linspace(-lz/2, lz/2, n)

        dx = lx / (n - 1)
        dz = lz / (n - 1)
        dS = dx * dz

        iy = (np.abs(self.data.y - y_pos)).argmin()
        ix_indices = np.abs(self.data.x[:, None] - flux_x_arr).argmin(axis=0)
        iz_indices = np.abs(self.data.z[:, None] - flux_z_arr).argmin(axis=0)

        IX, IZ = np.meshgrid(ix_indices, iz_indices)
        By_mapped = self.data.By_c[iy, IX, IZ]
        sum_of_flux = np.sum(By_mapped) * dS

        if hasattr(self, 'flux_result_label'):
            self.flux_result_label.configure(text=f"Flux: {sum_of_flux:.4e} Wb")
        else:
            print(f"{sum_of_flux:.4e} Wb")
        
        return sum_of_flux


    def generate_plots(self):
        gui_field_size = self.field_size_slider.get()
        gui_field_density = int(self.field_density_slider.get())
        gui_vector_size = self.vector_size_slider.get()
        gui_streamplot_Z = self.field_streamplot_Z_slider.get()

        if self.dipole_menu_button.get() == "Magnetized Volume":
            new_m_arr = self.generate_m_volumetric(float(self.size_x.get()), float(self.size_y.get()), float(self.size_z.get()), int(self.vol_resolution.get()), self.mag_axis_combobox.get()) 
        else:
            if int(self.dip_polar_setup.get()): new_m_arr = solver.generate_dipoles([0,0,0], (np.pi/12), [1,0,0], 0.1, 4)
            else: 
                dir = self.dip_axis_combobox.get()
                moment = float(self.dip_mag_moment.get())
                if dir == "x": new_m_arr = [[0,0,0,moment,0,0]]
                if dir == "y": new_m_arr = [[0,0,0,0,moment,0]]
                if dir == "z": new_m_arr = [[0,0,0,0,0,moment]]

        self.data = solver.solve(new_m_arr, gui_field_density, gui_vector_size, gui_field_size, gui_streamplot_Z)
        data = self.data

        B_mod = np.sqrt(np.square(data.Bx_c)+np.square(data.By_c)+np.square(data.Bz_c))
        B_flat = B_mod.flatten()
        norm = mcolors.Normalize(vmin=B_flat.min(), vmax=B_flat.max()/10)
        cmap = cm.RdPu
        try: vector_colors = cmap(norm(B_flat))
        except: vector_colors = cmap(norm(B_flat/10))

        self.fig.clf()

        self.sonda_text = None
        self.sonda_point = None
        ax1 = self.fig.add_subplot(121, projection='3d')

        ax1.quiver3D(data.X, data.Y, data.Z, data.Bx_c, data.By_c, data.Bz_c, length=gui_vector_size, normalize=True, colors=vector_colors)
        for i in range(len(data.m_arr)):
            ax1.quiver3D(data.m_arr[i][0], data.m_arr[i][1], data.m_arr[i][2], data.m_arr[i][3], data.m_arr[i][4], data.m_arr[i][5], length=gui_vector_size*2, normalize=True, color='red')

        z_level = gui_streamplot_Z
        size_x = float(self.flux_x.get())
        size_z = float(self.flux_z.get())
        poz_y = float(self.flux_y_pos.get())
        pos_3d = [
            [-size_x, poz_y, -size_z],
            [ size_x, poz_y, -size_z],
            [ size_x,  poz_y, size_z],
            [-size_x,  poz_y, size_z] 
        ]

        surf_3d = Poly3DCollection([pos_3d])
        surf_3d.set_facecolor((0.0, 1.0, 1.0, 0.2))
        surf_3d.set_edgecolor('black')
        ax1.add_collection3d(surf_3d)

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

        self.sonda_ax = ax2
        self.sonda_data_x = np.unique(data.x) 
        self.sonda_data_y = np.unique(data.y)
        self.sonda_data_b = B_mod_2d
        if self.sonda_cid:
            self.canvas.mpl_disconnect(self.sonda_cid)
        self.sonda_cid = self.canvas.mpl_connect('button_press_event', self.sonda_function)

        self.compute_flux()

        plt.tight_layout()
        self.canvas.draw()

    def update_button_callback(self):
        self.generate_plots()

    def destructor(self):
        plt.close('all') 
        self.destroy() 
        sys.exit(0)