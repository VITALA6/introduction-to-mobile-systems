import customtkinter as ctk
import random
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import messagebox

# UI Style Configuration
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class ModernBaseStationSim(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Mobile Systems Simulator (M/M/S/S) - Mirosław Szaban Model")
        self.geometry("1300x850")

        # --- Simulation State Variables ---
        self.running = False
        self.current_time = 0
        self.channels = []       # Tracks time remaining for each channel
        self.queue = []          # Stores call durations of waiting calls
        self.stats = {'rho': [], 'Q': []} # Historical data for plotting

        self.setup_ui()

    def setup_ui(self):
        """Initializes the graphical user interface components."""
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Sidebar (Configuration Panel) ---
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(self.sidebar, text="STATION PARAMETERS",
                     font=ctk.CTkFont(size=18, weight="bold")).pack(pady=20)

        self.entries = {}
        # Parameter list: (Display Label, Internal Key, Default Value)
        params = [
            ("Channels (S)", "S", "10"),
            ("Queue Length (K)", "K", "10"),
            ("Arrival Rate (λ)", "lambda", "1.5"),
            ("Mean Duration (N)", "N", "20"),
            ("Std Deviation (σ)", "sigma", "5"),
            ("Sim Time (sec)", "time", "120")
        ]

        for label, key, default in params:
            lbl = ctk.CTkLabel(self.sidebar, text=label, font=ctk.CTkFont(size=13))
            lbl.pack(pady=(10, 0), padx=25, anchor="w")
            ent = ctk.CTkEntry(self.sidebar, placeholder_text=default)
            ent.insert(0, default)
            ent.pack(pady=(0, 5), padx=25, fill="x")
            self.entries[key] = ent

        self.start_btn = ctk.CTkButton(self.sidebar, text="START SIMULATION",
                                      command=self.start_simulation,
                                      fg_color="#2ecc71", hover_color="#27ae60",
                                      font=ctk.CTkFont(weight="bold"))
        self.start_btn.pack(pady=40, padx=25, fill="x")

        # --- Main Viewport ---
        self.main_content = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_content.grid_columnconfigure(0, weight=1)

        # Channel Status Monitor
        self.chan_frame = ctk.CTkScrollableFrame(self.main_content, label_text="Base Station Channels (Live)", height=220)
        self.chan_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        self.chan_indicators = []

        # Real-time Graphs Frame
        self.graph_frame = ctk.CTkFrame(self.main_content)
        self.graph_frame.grid(row=1, column=0, sticky="nsew")
        self.setup_graphs()

        # Bottom Status Bar
        self.info_frame = ctk.CTkFrame(self.main_content, height=80)
        self.info_frame.grid(row=2, column=0, sticky="ew", pady=(20, 0))

        self.lbl_rho = ctk.CTkLabel(self.info_frame, text="Load (ρ): 0.00", font=ctk.CTkFont(size=15, weight="bold"))
        self.lbl_rho.pack(side="left", padx=40)

        self.lbl_queue = ctk.CTkLabel(self.info_frame, text="Queue (Q): 0", font=ctk.CTkFont(size=15))
        self.lbl_queue.pack(side="left", padx=40)

        self.lbl_time = ctk.CTkLabel(self.info_frame, text="Time: 0 / 0s", font=ctk.CTkFont(size=15))
        self.lbl_time.pack(side="right", padx=40)

    def setup_graphs(self):
        """Configures the Matplotlib charts for real-time data visualization."""
        plt.style.use('dark_background')
        # Create subplots for ρ (Load) and Q (Queue Size)
        self.fig, (self.ax_rho, self.ax_q) = plt.subplots(1, 2, figsize=(11, 4))
        self.fig.patch.set_facecolor('#2b2b2b')
        for ax in [self.ax_rho, self.ax_q]:
            ax.set_facecolor('#1e1e1e')
            ax.tick_params(colors='gray')

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def start_simulation(self):
        """Initializes simulation parameters and starts the main loop."""
        if self.running: return

        try:
            num_s = int(self.entries['S'].get())
            self.max_time = int(self.entries['time'].get())
        except ValueError:
            messagebox.showerror("Input Error", "Please verify all numerical parameters!")
            return

        # Initialize Simulation State
        self.current_time = 0
        self.stats = {'rho': [], 'Q': []}
        self.channels = [0] * num_s
        self.queue = []

        # Cleanup and Rebuild UI Indicators
        for widget in self.chan_indicators: widget.destroy()
        self.chan_indicators = []

        for i in range(num_s):
            ind = ctk.CTkButton(self.chan_frame, text=f"CH {i+1}", width=90, height=45,
                               fg_color="#34495e", state="disabled", text_color="white")
            ind.grid(row=i//6, column=i%6, padx=8, pady=8)
            self.chan_indicators.append(ind)

        self.running = True
        self.run_step()

    def run_step(self):
        """Performs one iteration (1 second) of the simulation."""
        if not self.running or self.current_time >= self.max_time:
            self.running = False
            self.start_btn.configure(state="normal", text="START SIMULATION")
            return

        # 1. Update Channels (Process ongoing calls)
        for i in range(len(self.channels)):
            if self.channels[i] > 0:
                self.channels[i] -= 1
                if self.channels[i] == 0:
                    # Mark channel as idle (Green/Gray)
                    self.chan_indicators[i].configure(fg_color="#34495e")

        # 2. Process Queue (Assign waiting calls to newly idle channels)
        for i in range(len(self.channels)):
            if self.channels[i] == 0 and self.queue:
                duration = self.queue.pop(0)
                self.channels[i] = duration
                self.chan_indicators[i].configure(fg_color="#e74c3c")

        # 3. New Arrivals (Poisson Distribution with parameter λ)
        lam = float(self.entries['lambda'].get())
        new_calls = np.random.poisson(lam)

        for _ in range(new_calls):
            # Calculate call duration (Gaussian Distribution with parameters N, σ)
            n_mean = float(self.entries['N'].get())
            s_dev = float(self.entries['sigma'].get())
            dur = int(random.gauss(n_mean, s_dev))
            dur = max(2, dur) # Ensure call lasts at least 2 seconds

            # Attempt to allocate channel
            placed = False
            for i in range(len(self.channels)):
                if self.channels[i] == 0:
                    self.channels[i] = dur
                    self.chan_indicators[i].configure(fg_color="#e74c3c") # Mark as busy (Red)
                    placed = True
                    break

            # If all channels busy, attempt to enter queue
            if not placed and len(self.queue) < int(self.entries['K'].get()):
                self.queue.append(dur)

        # 4. Statistical Calculations and UI Updates
        busy_count = sum(1 for c in self.channels if c > 0)
        rho_val = busy_count / len(self.channels)
        self.stats['rho'].append(rho_val)
        self.stats['Q'].append(len(self.queue))

        self.lbl_rho.configure(text=f"Load (ρ): {rho_val:.2f}")
        self.lbl_queue.configure(text=f"Queue (Q): {len(self.queue)}")
        self.lbl_time.configure(text=f"Time: {self.current_time} / {self.max_time}s")

        self.update_graphs()
        self.current_time += 1

        # Schedule next step (100ms interval for smoother visual feedback)
        self.after(100, self.run_step)

    def update_graphs(self):
        """Refreshes the data on the charts."""
        self.ax_rho.clear()
        self.ax_rho.plot(self.stats['rho'], color='#2ecc71', linewidth=2)
        self.ax_rho.set_title("Traffic Intensity (ρ)", color="white")
        self.ax_rho.set_ylim(0, 1.1)

        self.ax_q.clear()
        self.ax_q.plot(self.stats['Q'], color='#3498db', linewidth=2)
        self.ax_q.set_title("Queue Length (Q)", color="white")

        self.canvas.draw()

if __name__ == "__main__":
    app = ModernBaseStationSim()
    app.mainloop()
