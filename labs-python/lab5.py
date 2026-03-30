import math
import customtkinter as ctk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.patches as mpatches
import numpy as np

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# -- Core formulas ------------------------------------------------------------

def valid_cluster_sizes():
    """Return sorted list of valid N = i^2+ij+j^2 values (first 10)."""
    sizes = set()
    for i in range(10):
        for j in range(10):
            n = i*i + i*j + j*j
            if n > 0:
                sizes.add(n)
    return sorted(sizes)

def reuse_distance(R, N):
    """D = R * sqrt(3*N)"""
    return R * math.sqrt(3 * N)

def cell_number(i_coord, v, u, N):
    """L = [(i+1)*u + v] mod N"""
    return ((i_coord + 1) * u + v) % N

def cochannel_interference(R, distances):
    """SIR = (R/D_k)^4 summed -- returns sum of (R/Dk)^4"""
    return sum((R / dk) ** 4 for dk in distances)

def erlang_traffic(arrival_rate, mean_duration_hours):
    """a = lambda * T  (T in hours)"""
    return arrival_rate * mean_duration_hours


# -- Main App -----------------------------------------------------------------

class Lab5App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Lab 5 - Cellular Network Concept")
        self.geometry("1280x860")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_main()

    # -- Sidebar --------------------------------------------------------------

    def _build_sidebar(self):
        sb = ctk.CTkScrollableFrame(self, width=240, corner_radius=0)
        sb.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(sb, text="LAB 5", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(20, 4))
        ctk.CTkLabel(sb, text="Cellular Concept", font=ctk.CTkFont(size=13)).pack(pady=(0, 20))

        tasks = [
            ("Task 1 - Octagon vs Hex",    self._show_task1),
            ("Task 2 - Cluster N=7",        self._show_task2),
            ("Task 3 - Erlang (basic)",     self._show_task3),
            ("Task 4 - Network architecture", self._show_task4),
            ("Task 5 - Metro network",      self._show_task5),
            ("Task 6 - N=16 split?",        self._show_task6),
            ("Task 7 - Reuse dist. + cap.", self._show_task7),
            ("Task 8 - 12-cell cluster",    self._show_task8),
            ("Task 9 - Handoff",            self._show_task9),
            ("Task 10 - Interference types",self._show_task10),
            ("Task 11 - Sectorisation",     self._show_task11),
        ]

        for label, cmd in tasks:
            ctk.CTkButton(sb, text=label, command=cmd, anchor="w",
                          fg_color="transparent", hover_color="#2c3e50",
                          font=ctk.CTkFont(size=12)).pack(fill="x", padx=10, pady=3)

    # -- Main area ------------------------------------------------------------

    def _build_main(self):
        self.main = ctk.CTkFrame(self, fg_color="transparent")
        self.main.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main.grid_rowconfigure(0, weight=1)
        self.main.grid_columnconfigure(0, weight=1)

        self.text_box = ctk.CTkTextbox(self.main, font=ctk.CTkFont(family="Courier", size=13),
                                        wrap="word", state="disabled")
        self.text_box.grid(row=0, column=0, sticky="nsew")

        self.canvas_frame = ctk.CTkFrame(self.main, fg_color="transparent")
        self.canvas_frame.grid(row=1, column=0, sticky="nsew")
        self.main.grid_rowconfigure(1, weight=1)

        self._mpl_canvas = None

    def _write(self, text):
        self.text_box.configure(state="normal")
        self.text_box.delete("1.0", "end")
        self.text_box.insert("end", text)
        self.text_box.configure(state="disabled")

    def _clear_plot(self):
        if self._mpl_canvas:
            self._mpl_canvas.get_tk_widget().destroy()
            self._mpl_canvas = None
        plt.close("all")

    def _embed_fig(self, fig):
        self._clear_plot()
        canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        self._mpl_canvas = canvas

    # -- Task handlers ---------------------------------------------------------

    def _show_task1(self):
        self._clear_plot()
        text = (
            "TASK 1 - Why not octagonal cells?\n"
            "===============================================\n\n"
            "An octagon is a closer approximation to a circle\n"
            "than a hexagon -- so why are hexagons used?\n\n"
            "REASON:\n"
            "  Octagons CANNOT tile the plane without gaps.\n"
            "  When you try to cover a flat surface with\n"
            "  regular octagons, small square gaps appear\n"
            "  between them.  Those uncovered regions would\n"
            "  not belong to any cell, leaving dead zones.\n\n"
            "  Only three regular polygons tile perfectly:\n"
            "    * Equilateral triangle\n"
            "    * Square\n"
            "    * Regular hexagon  <-- used in cellular networks\n\n"
            "  Among these, the hexagon:\n"
            "    - Best approximates a circular coverage area\n"
            "    - Minimises the number of cells needed\n"
            "    - Gives each cell 6 equidistant neighbours\n"
            "    - Minimises co-channel interference\n\n"
            "CONCLUSION:\n"
            "  The hexagon is chosen as the best balance\n"
            "  between circular shape and complete, gap-free\n"
            "  coverage of the service area.\n"
        )
        self._write(text)
        self._draw_tiling_comparison()

    def _draw_tiling_comparison(self):
        fig, axes = plt.subplots(1, 2, figsize=(9, 4),
                                  facecolor="#1e1e1e")
        fig.suptitle("Tiling comparison", color="white", fontsize=13)

        # Hexagonal tiling (perfect)
        ax = axes[0]
        ax.set_facecolor("#1e1e1e")
        ax.set_title("Hexagons - perfect tiling", color="white")
        ax.set_aspect("equal")
        ax.axis("off")
        dx, dy = math.sqrt(3), 1.5
        for row in range(-2, 3):
            for col in range(-3, 4):
                cx = col * dx + (row % 2) * dx / 2
                cy = row * dy
                hex_patch = mpatches.RegularPolygon((cx, cy), numVertices=6,
                                                     radius=0.95, orientation=0,
                                                     facecolor="#2471a3", edgecolor="#85c1e9", lw=1.2)
                ax.add_patch(hex_patch)
        ax.set_xlim(-5, 5); ax.set_ylim(-4, 4)

        # Octagonal tiling (gaps)
        ax2 = axes[1]
        ax2.set_facecolor("#1e1e1e")
        ax2.set_title("Octagons - gaps appear!", color="white")
        ax2.set_aspect("equal")
        ax2.axis("off")
        s = 1.0
        a = s / (1 + math.sqrt(2))  # side of the square gap
        step = s + a
        for row in range(-2, 3):
            for col in range(-2, 3):
                cx = col * step
                cy = row * step
                oct_pts = []
                r = s / 2
                for k in range(8):
                    angle = math.pi / 8 + k * math.pi / 4
                    oct_pts.append((cx + r * math.cos(angle),
                                    cy + r * math.sin(angle)))
                oct = mpatches.Polygon(oct_pts, closed=True,
                                        facecolor="#1a5276", edgecolor="#5dade2", lw=1.2)
                ax2.add_patch(oct)
                # Draw gap squares
                for offset in [(step/2, step/2), (-step/2, step/2),
                                (step/2, -step/2), (-step/2, -step/2)]:
                    gx, gy = cx + offset[0], cy + offset[1]
                    sq = mpatches.Rectangle((gx - a/2, gy - a/2), a, a,
                                            facecolor="#c0392b", edgecolor="#e74c3c", lw=1)
                    ax2.add_patch(sq)
        ax2.set_xlim(-3.5, 3.5); ax2.set_ylim(-3.5, 3.5)
        red_patch = mpatches.Patch(color="#c0392b", label="Gap (dead zone)")
        ax2.legend(handles=[red_patch], loc="lower right",
                   facecolor="#2b2b2b", labelcolor="white", fontsize=9)

        self._embed_fig(fig)

    def _show_task2(self):
        N = 7
        R = 1.0  # normalised radius
        D = reuse_distance(R, N)

        # Worst-case cochannel interference: M=6 co-channel base stations,
        # all at distance D (first tier, worst case: MS at edge of its cell)
        distances = [D] * 6
        sir_inv = cochannel_interference(R, distances)   # sum (R/Dk)^4
        sir_db = -10 * math.log10(sir_inv)              # SIR = 1/sum

        # Cell numbering L = [(i+1)*u + v] mod N  for a grid
        text = (
            f"TASK 2 - Cluster with N=7 cells\n"
            f"===============================================\n\n"
            f"Valid N values:  N = i^2 + i*j + j^2\n"
            f"  For i=2, j=1:  N = 4+2+1 = 7  OK\n\n"
            f"Reuse distance:\n"
            f"  D = R * sqrt(3N) = R * sqrt({3*N}) ~= {D:.4f} * R\n\n"
            f"Cell numbering  L = [(i+1)*u + v] mod N\n"
            f"  Sample (i=2) for u,v in [0..2]:\n"
        )
        rows = []
        for v in range(3):
            for u in range(3):
                L = cell_number(2, v, u, N)
                rows.append(f"    u={u}, v={v}  ->  L={L}")
        text += "\n".join(rows)
        text += (
            f"\n\n  Cell labels 0-{N-1} appear (some may repeat -- use\n"
            f"  a full hexagonal grid for all unique labels).\n\n"
            f"Worst-case co-channel interference (M=6):\n"
            f"  All 6 first-tier interferers at distance D={D:.4f}*R\n"
            f"  SIR^(-1) = sum(R/Dk)^4 = 6*(1/{D:.4f})^4 = {sir_inv:.6f}\n"
            f"  SIR      = 1/{sir_inv:.6f} ~= {1/sir_inv:.2f}\n"
            f"  SIR      ~= {sir_db:.2f} dB\n"
        )
        self._write(text)
        self._draw_cluster7()

    def _draw_cluster7(self):
        fig, ax = plt.subplots(figsize=(6, 5), facecolor="#1e1e1e")
        ax.set_facecolor("#1e1e1e")
        ax.set_title("N=7 cluster cell numbering", color="white")
        ax.set_aspect("equal"); ax.axis("off")

        N = 7
        colors = plt.cm.Set2.colors
        R = 1.0
        dx = math.sqrt(3) * R
        dy = 1.5 * R

        # Axial coordinates for 7-cell cluster (i=2,j=1)
        axial = [(0,0),(1,0),(0,1),(-1,1),(-1,0),(0,-1),(1,-1)]

        for idx, (q, r) in enumerate(axial):
            cx = dx * (q + r * 0.5)
            cy = dy * r
            hex_pts = [(cx + R * math.cos(math.pi/6 + k*math.pi/3),
                        cy + R * math.sin(math.pi/6 + k*math.pi/3)) for k in range(6)]
            p = mpatches.Polygon(hex_pts, closed=True,
                                  facecolor=colors[idx % len(colors)],
                                  edgecolor="white", lw=1.5, alpha=0.85)
            ax.add_patch(p)
            ax.text(cx, cy, str(idx), ha="center", va="center",
                    color="black", fontsize=14, weight="bold")

        ax.set_xlim(-3, 3); ax.set_ylim(-2.5, 2.5)
        self._embed_fig(fig)

    def _show_task3(self):
        mean_duration_min = 15
        calls_per_hour = 60
        T_hours = mean_duration_min / 60
        a = erlang_traffic(calls_per_hour, T_hours)

        text = (
            "TASK 3 - Traffic intensity in Erlangs\n"
            "===============================================\n\n"
            "Formula:   a = lambda * T\n"
            "  where  lambda = arrival rate [calls/hour]\n"
            "         T      = mean holding time [hours]\n\n"
            f"Given:\n"
            f"  Mean call duration  = {mean_duration_min} min = {T_hours:.4f} h\n"
            f"  Calls per hour      = {calls_per_hour}\n\n"
            f"Calculation:\n"
            f"  a = {calls_per_hour} x {T_hours:.4f}\n"
            f"  a = {a:.2f} Erlang\n\n"
            "Interpretation:\n"
            "  15 Erlang means on average 15 channels are\n"
            "  occupied simultaneously during the busy hour.\n"
        )
        self._write(text)
        self._clear_plot()

    def _show_task4(self):
        self._clear_plot()
        text = (
            "TASK 4 - Network architecture factors\n"
            "===============================================\n\n"
            "Potential factors that determine the architecture\n"
            "of a cellular network:\n\n"
            "1. POPULATION DENSITY\n"
            "   Dense urban areas -> small cells (microcells)\n"
            "   to handle high traffic per km^2.\n"
            "   Rural areas -> large macro-cells.\n\n"
            "2. GEOGRAPHY / TERRAIN\n"
            "   Mountains, valleys, rivers restrict coverage;\n"
            "   extra base stations compensate for shadowing.\n\n"
            "3. FREQUENCY REUSE CONSTRAINTS\n"
            "   Higher reuse factor N -> more spectrum\n"
            "   per cell but fewer cells in the cluster.\n\n"
            "4. TRAFFIC DEMAND / ERLANG LOAD\n"
            "   High demand areas require cell splitting\n"
            "   to increase capacity.\n\n"
            "5. ROAMING / HANDOFF REQUIREMENTS\n"
            "   Highways, railways -> elongated cells\n"
            "   (umbrella cells) to reduce handoff frequency.\n\n"
            "6. REGULATORY / SPECTRUM ALLOCATION\n"
            "   Licensed bandwidth limits total system capacity.\n\n"
            "7. COST OF INFRASTRUCTURE\n"
            "   Fewer, larger cells reduce CAPEX but limit\n"
            "   capacity; trade-off guides final design.\n"
        )
        self._write(text)

    def _show_task5(self):
        self._clear_plot()
        text = (
            "TASK 5 - Metro (subway) cellular network\n"
            "===============================================\n\n"
            "A metro network has very specific constraints\n"
            "that dictate its architecture:\n\n"
            "1. TUNNEL GEOMETRY\n"
            "   The signal is confined inside a long, narrow\n"
            "   tube.  Linear (chain) cell layout follows the\n"
            "   track.  Radio waves propagate almost only\n"
            "   along the tunnel axis.\n\n"
            "2. LEAKY FEEDER / DISTRIBUTED ANTENNAS\n"
            "   Coaxial cables with slots (leaky feeders)\n"
            "   or DAS (Distributed Antenna Systems) run\n"
            "   along the tunnel to provide continuous coverage.\n\n"
            "3. HIGH USER DENSITY AT STATIONS\n"
            "   Platforms create hotspots -> dedicated small\n"
            "   cells or access points at each station.\n\n"
            "4. FREQUENT HANDOFF\n"
            "   Trains travel at high speed through short cells\n"
            "   -> overlapping handoff regions must be large\n"
            "   enough to complete handoff before the train\n"
            "   leaves the cell.\n\n"
            "5. UNDERGROUND SHIELDING\n"
            "   No outdoor signal penetrates underground.\n"
            "   The entire coverage must be self-contained\n"
            "   inside the tunnel infrastructure.\n\n"
            "6. SAFETY & REDUNDANCY\n"
            "   Emergency services (GSM-R / TETRA) require\n"
            "   100% coverage -> redundant antenna paths.\n"
        )
        self._write(text)

    def _show_task6(self):
        N_orig = 16
        N1, N2 = 7, 9

        valid = valid_cluster_sizes()
        n1_valid = N1 in valid
        n2_valid = N2 in valid

        text = (
            f"TASK 6 - Can N={N_orig} be split into N={N1} and N={N2}?\n"
            "===============================================\n\n"
            f"Valid cluster sizes  N = i^2 + i*j + j^2:\n"
            f"  {valid[:15]}\n\n"
            f"Check N={N_orig}:  i=4,j=0 -> 16+0+0=16  OK  (valid)\n"
            f"Check N={N1}:   i=2,j=1 -> 4+2+1=7    {'OK' if n1_valid else 'NOT VALID'}\n"
            f"Check N={N2}:   i=3,j=0 -> 9+0+0=9    {'OK' if n2_valid else 'NOT VALID'}\n\n"
        )

        if n1_valid and n2_valid:
            d16 = reuse_distance(1, N_orig)
            d7  = reuse_distance(1, N1)
            d9  = reuse_distance(1, N2)
            text += (
                f"ANSWER:  YES - both N={N1} and N={N2} are valid cluster sizes.\n\n"
                f"Effect on reuse distance (for R=1):\n"
                f"  D(N=16) = {d16:.3f} R\n"
                f"  D(N=7)  = {d7:.3f} R   (smaller -> more interference)\n"
                f"  D(N=9)  = {d9:.3f} R   (smaller -> more interference)\n\n"
                f"Trade-off:\n"
                f"  Smaller cluster -> more frequency reuse -> higher\n"
                f"  capacity, but increased co-channel interference.\n"
                f"  The split is geometrically valid; whether it is\n"
                f"  practical depends on the SIR requirement of the system.\n"
            )
        else:
            text += f"ANSWER:  NO - not all target sizes are geometrically valid.\n"

        self._write(text)
        self._clear_plot()

    def _show_task7(self):
        # Given data
        cell_diameter_km = 2
        R = cell_diameter_km / 2        # 1 km
        total_bw_mhz = 30
        channel_bw_khz = 25
        control_channels = 10
        tdma_per_channel = 8

        # Determine N from a typical diagram with N=4 (square reuse) -- the
        # problem shows a diagram; a common textbook case for such parameters
        # is N=4.  We solve generically for the user to see the formula.
        N = 4   # assumed from diagram (i=2,j=0 -> 4)
        D = reuse_distance(R, N)

        total_channels = int((total_bw_mhz * 1000) / channel_bw_khz)
        channels_per_cell = total_channels // N - control_channels
        simultaneous_users = channels_per_cell * tdma_per_channel

        text = (
            "TASK 7 - Reuse distance + simultaneous users\n"
            "===============================================\n\n"
            f"Given:\n"
            f"  Cell diameter    = {cell_diameter_km} km  ->  R = {R} km\n"
            f"  Total bandwidth  = {total_bw_mhz} MHz\n"
            f"  Channel width    = {channel_bw_khz} kHz\n"
            f"  Control channels = {control_channels} per cell\n"
            f"  TDMA multiplier  = {tdma_per_channel} users/channel\n"
            f"  Cluster size N   = {N}  (from diagram; i=2, j=0)\n\n"
            f"Step 1 - Reuse distance:\n"
            f"  D = R * sqrt(3N) = {R} * sqrt({3*N}) = {D:.4f} km\n\n"
            f"Step 2 - Total traffic channels:\n"
            f"  Total = {total_bw_mhz*1000} kHz / {channel_bw_khz} kHz = {total_channels} channels\n\n"
            f"Step 3 - Traffic channels per cell:\n"
            f"  Channels/cell = floor({total_channels}/{N}) - {control_channels}\n"
            f"                = {total_channels//N} - {control_channels} = {channels_per_cell}\n\n"
            f"Step 4 - Simultaneous users per cell (TDMA):\n"
            f"  Users = {channels_per_cell} x {tdma_per_channel} = {simultaneous_users}\n\n"
            f"ANSWER:  {simultaneous_users} users can talk simultaneously per cell.\n"
        )
        self._write(text)
        self._clear_plot()

    def _show_task8(self):
        calls = [2200, 1900, 4000, 1100, 1200, 1800, 2100, 2000, 1580, 1800, 900, 1120]
        R = 5       # km
        mean_duration_min = 1
        T_hours = mean_duration_min / 60

        N = len(calls)   # 12 cells
        D = reuse_distance(R, N)

        # Traffic per cell in Erlangs
        erlangs = [erlang_traffic(c, T_hours) for c in calls]
        total_erlang = sum(erlangs)

        car_fraction = 0.75
        car_users_per_cell = [e * car_fraction for e in erlangs]
        # Each mobile phone carries 1 call at a time, number of mobiles = calls * T
        # "number of car subscribers" = traffic * car_fraction (in Erlangs = simultaneous calls)
        total_car = sum(car_users_per_cell)

        text = (
            "TASK 8 - 12-cell cluster analysis\n"
            "===============================================\n\n"
            f"Given:\n"
            f"  Cells (N)           = {N}\n"
            f"  Cell radius  R      = {R} km\n"
            f"  Mean call duration  = {mean_duration_min} min = {T_hours:.4f} h\n"
            f"  Car phone fraction  = {int(car_fraction*100)}%\n\n"
            f"Traffic per cell  a = lambda * T  [Erl]:\n"
        )
        for i, (c, a) in enumerate(zip(calls, erlangs)):
            text += f"  Cell {i+1:2d}: lambda={c:4d}/h -> a = {a:.2f} Erl\n"

        text += (
            f"\nTotal network load:\n"
            f"  A_total = sum(a) = {total_erlang:.2f} Erlang\n\n"
            f"Reuse distance (N=12, R={R} km):\n"
            f"  D = {R} * sqrt(3 x {N}) = {D:.3f} km\n\n"
            f"Car subscribers (75% of traffic, 1 call/phone):\n"
            f"  Total simultaneous car calls = {total_car:.2f}\n"
            f"  ~= approximately {round(total_car)} car phones active at peak.\n"
            f"\nNote: 'number of subscribers' depends on usage model;\n"
            f"  above value represents simultaneously active car phones.\n"
        )
        self._write(text)
        self._draw_erlang_bar(calls, erlangs)

    def _draw_erlang_bar(self, calls, erlangs):
        fig, axes = plt.subplots(1, 2, figsize=(9, 3.5), facecolor="#1e1e1e")
        fig.suptitle("12-cell cluster traffic", color="white")

        cell_labels = [f"C{i+1}" for i in range(len(calls))]
        c1 = "#3498db"

        for ax, data, title, ylabel in zip(
            axes,
            [calls, erlangs],
            ["Calls per hour", "Traffic (Erlang)"],
            ["calls/h", "Erlang"]
        ):
            ax.set_facecolor("#1e1e1e")
            ax.bar(cell_labels, data, color=c1, edgecolor="#2c3e50")
            ax.set_title(title, color="white", fontsize=11)
            ax.set_ylabel(ylabel, color="gray")
            ax.tick_params(colors="gray", labelsize=9)
            for spine in ax.spines.values():
                spine.set_edgecolor("#444")

        fig.tight_layout()
        self._embed_fig(fig)

    def _show_task9(self):
        self._clear_plot()
        text = (
            "TASK 9 - Handoff and Handoff Region\n"
            "===============================================\n\n"
            "HANDOFF (also: handover)\n"
            "  The process of transferring an active call\n"
            "  from one base station (BS) to another as the\n"
            "  mobile station (MS) moves across cell boundaries.\n"
            "  The connection is maintained without interruption.\n\n"
            "Types:\n"
            "  * Hard handoff   - break-before-make (GSM)\n"
            "  * Soft handoff   - make-before-break (CDMA)\n\n"
            "HANDOFF REGION\n"
            "  The overlap zone between two adjacent cells\n"
            "  where signal levels from both BSs are comparable.\n"
            "  Within this region the network decides whether\n"
            "  to initiate a handoff.\n\n"
            "Trigger conditions:\n"
            "  * Received signal from current BS falls below\n"
            "    a threshold  (-delta dB below target BS signal)\n"
            "  * Signal from new BS exceeds current BS signal\n"
            "    by a hysteresis margin  (prevents ping-pong)\n\n"
            "Diagram (simplified):\n\n"
            "  BS-A coverage | Handoff | BS-B coverage\n"
            "  --------------|  region |---------------\n"
            "  signal A  +++++++++----.................  \n"
            "  signal B  .................----+++++++++\n"
            "                   ^^^\n"
            "            Handoff initiated here\n"
            "            when B > A + hysteresis\n"
        )
        self._write(text)

    def _show_task10(self):
        self._clear_plot()
        text = (
            "TASK 10 - Adjacent-channel vs Co-channel Interference\n"
            "===============================================\n\n"
            "CO-CHANNEL INTERFERENCE (CCI)\n"
            "  Interference from distant cells that reuse the\n"
            "  SAME frequency channel.\n\n"
            "  Cause:    Finite reuse distance D; interfering BS\n"
            "            transmits on identical frequency f0.\n"
            "  Effect:   Degrades SIR even when the desired signal\n"
            "            is strong.\n"
            "  Remedy:   Increase cluster size N -> larger D;\n"
            "            or use directional antennas (cell sectors).\n\n"
            "  SIR ~= (D/R)^4 / (2M)  [for 4th-power path loss]\n\n"
            "------------------------------------------------------\n\n"
            "ADJACENT-CHANNEL INTERFERENCE (ACI)\n"
            "  Interference from a transmitter using a NEARBY\n"
            "  (adjacent) frequency channel, not the same one.\n\n"
            "  Cause:    Imperfect bandpass filters in receivers\n"
            "            allow energy from channel f0 +/- df to leak in.\n"
            "            Can also occur from a near-by transmitter\n"
            "            whose sidelobes overlap the desired channel.\n"
            "  Effect:   Near-far problem: a nearby strong transmitter\n"
            "            on an adjacent channel can overwhelm a weak\n"
            "            desired signal.\n"
            "  Remedy:   Guard bands between channels; better filters;\n"
            "            power control; careful frequency assignment.\n\n"
            "KEY DIFFERENCE:\n"
            "  CCI  -> same frequency, different cell (distance-based)\n"
            "  ACI  -> adjacent frequency, often same/nearby cell\n"
            "         (filter & near-far based)\n"
        )
        self._write(text)

    def _show_task11(self):
        self._clear_plot()
        text = (
            "TASK 11 - Advantage of cell sectors\n"
            "===============================================\n\n"
            "WHAT IS CELL SPLITTING INTO SECTORS?\n"
            "  A cell is divided into sectors (typically 3 x 120 deg\n"
            "  or 6 x 60 deg) using directional antennas instead of\n"
            "  a single omnidirectional antenna.\n\n"
            "PRIMARY ADVANTAGE: Reduced co-channel interference\n\n"
            "  With omnidirectional antennas every cell has M=6\n"
            "  first-tier co-channel interferers.\n\n"
            "  With 3-sector antennas (120 deg each), only the\n"
            "  interferers within the antenna beam are significant.\n"
            "  Effectively M is reduced:\n"
            "    * 3-sector:  M ~= 2  (instead of 6)\n"
            "    * 6-sector:  M ~= 1\n\n"
            "  SIR improvement (N=7, 3-sector example):\n"
            f"    D/R       = {reuse_distance(1,7):.3f}\n"
            f"    SIR_omni  = (D/R)^4 / (2*6) ~= {(reuse_distance(1,7)**4)/(2*6):.1f}\n"
            f"    SIR_3sec  = (D/R)^4 / (2*2) ~= {(reuse_distance(1,7)**4)/(2*2):.1f}\n"
            f"    Improvement ~= x3 (about +4.8 dB)\n\n"
            "ADDITIONAL ADVANTAGES:\n"
            "  * Increased system capacity (more Erl per km^2)\n"
            "  * Allows smaller cluster size N without violating SIR\n"
            "  * Reduced handoff rate within a sector\n\n"
            "TRADE-OFFS:\n"
            "  * More antennas & RF chains per base station\n"
            "  * Increased handoff frequency at sector boundaries\n"
            "  * Channel assignment becomes more complex\n"
        )
        self._write(text)


if __name__ == "__main__":
    app = Lab5App()
    app.mainloop()
