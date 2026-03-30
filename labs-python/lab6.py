import math
import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# -- Core formulas ------------------------------------------------------------

SPEED_OF_LIGHT = 2.998e8  # m/s


def wavelength(freq_hz):
    """lambda = c / f"""
    return SPEED_OF_LIGHT / freq_hz


def antenna_gain_circular(diameter_m, freq_hz, efficiency=0.55):
    """G = eta * (pi*D/lambda)^2"""
    lam = wavelength(freq_hz)
    return efficiency * (math.pi * diameter_m / lam) ** 2


def antenna_gain_db(diameter_m, freq_ghz, efficiency=0.55):
    """G[dB] = 20log(D) + 20log(f_GHz) + 20log(pi) + 10log(eta) ~ formula from lab sheet"""
    return (20 * math.log10(diameter_m)
            + 20 * math.log10(freq_ghz)
            + 20 * math.log10(math.pi)
            + 10 * math.log10(efficiency))


def received_power_free_space(Pt, Gt, Gr, freq_hz, d_m):
    """Pr = Pt * Gt * Gr * (lambda / 4*pi*d)^2"""
    lam = wavelength(freq_hz)
    return Pt * Gt * Gr * (lam / (4 * math.pi * d_m)) ** 2


def free_space_path_loss(freq_mhz, d_km):
    """Lf[dB] = 32.45 + 20*log10(f_MHz) + 20*log10(d_km)"""
    return 32.45 + 20 * math.log10(freq_mhz) + 20 * math.log10(d_km)


def doppler_shift_from_v(v_ms, freq_hz, theta_deg=0):
    """fd = v * cos(theta) / lambda"""
    lam = wavelength(freq_hz)
    return v_ms * math.cos(math.radians(theta_deg)) / lam


def max_doppler(v_ms, freq_hz):
    """fm = v / lambda"""
    lam = wavelength(freq_hz)
    return v_ms / lam


def level_crossing_rate(rho, fm):
    """N(Rs) = sqrt(2*pi) * fm * rho * exp(-rho^2)"""
    return math.sqrt(2 * math.pi) * fm * rho * math.exp(-(rho ** 2))


def fade_duration(rho, fm):
    """r(rho) = (exp(rho^2) - 1) / (rho * fm * sqrt(2*pi))"""
    return (math.exp(rho ** 2) - 1) / (rho * fm * math.sqrt(2 * math.pi))


def attenuation_coefficient(fm):
    """n(rho) = sqrt(pi/2) / fm  -- simplified; for rho=1: same formula"""
    # from lab: r_N = sqrt(2*pi) / fm  (duration formula variant)
    return math.sqrt(2 * math.pi) / fm


# -- Main App -----------------------------------------------------------------

class Lab6App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Lab 6 - Wave Propagation & Doppler Effect")
        self.geometry("1280x860")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_main()

    # -- Sidebar --------------------------------------------------------------

    def _build_sidebar(self):
        sb = ctk.CTkScrollableFrame(self, width=240, corner_radius=0)
        sb.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(sb, text="LAB 6", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(20, 4))
        ctk.CTkLabel(sb, text="Propagation & Doppler", font=ctk.CTkFont(size=13)).pack(pady=(0, 20))

        tasks = [
            ("Task 1 - Antenna gain + Pr",          self._show_task1),
            ("Task 2 - Free-space path loss",        self._show_task2),
            ("Task 3 - Received power (no gain)",    self._show_task3),
            ("Task 4 - Level crossing rate",         self._show_task4),
            ("Task 5 - Attenuation coefficient",     self._show_task5),
            ("Task 6 - Fade duration",               self._show_task6),
            ("Task 7 - Free space vs obstacles",     self._show_task7),
            ("Task 8 - Fast vs slow fading",         self._show_task8),
            ("Task 9 - NLOS reception",              self._show_task9),
            ("Task 10 - Doppler shift",              self._show_task10),
            ("Task 11 - Received frequency",         self._show_task11),
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
        # Given
        D_m    = 2.50          # diameter 250 cm = 2.50 m
        f_ghz  = 20.0          # 20 GHz
        f_hz   = f_ghz * 1e9
        Pt_w   = 30e-3         # 30 mW
        Gt_db  = 30.0          # 30 dB -> linear
        Gt     = 10 ** (Gt_db / 10)
        d_m    = 5000          # 5 km
        eta    = 0.55

        lam    = wavelength(f_hz)
        Gr     = antenna_gain_circular(D_m, f_hz, eta)
        Gr_db  = 10 * math.log10(Gr)
        Pr_w   = received_power_free_space(Pt_w, Gt, Gr, f_hz, d_m)
        Pr_mw  = Pr_w * 1e3
        Pr_dbm = 10 * math.log10(Pr_mw)

        text = (
            "TASK 1 - Antenna gain & received power\n"
            "===============================================\n\n"
            "Given:\n"
            f"  Antenna diameter  D  = {D_m*100:.0f} cm = {D_m} m\n"
            f"  Frequency         f  = {f_ghz} GHz\n"
            f"  Transmit power    Pt = {Pt_w*1e3:.0f} mW = {Pt_w} W\n"
            f"  TX antenna gain   Gt = {Gt_db} dB = {Gt:.2f} (linear)\n"
            f"  Distance          d  = {d_m/1000:.0f} km = {d_m} m\n"
            f"  Efficiency        eta= {eta}\n\n"
            "Step 1 - Wavelength:\n"
            f"  lambda = c / f = {SPEED_OF_LIGHT:.3e} / {f_hz:.3e}\n"
            f"         = {lam*100:.4f} cm = {lam:.6f} m\n\n"
            "Step 2 - RX antenna gain (circular):\n"
            f"  G = eta * (pi*D/lambda)^2\n"
            f"    = {eta} * (pi * {D_m} / {lam:.6f})^2\n"
            f"    = {Gr:.2f}  =  {Gr_db:.2f} dB\n\n"
            "Step 3 - Received power (free-space formula):\n"
            f"  Pr = Pt * Gt * Gr * (lambda / (4*pi*d))^2\n"
            f"     = {Pt_w} * {Gt:.2f} * {Gr:.2f} * ({lam:.6f} / (4*pi*{d_m}))^2\n"
            f"     = {Pr_w:.4e} W\n"
            f"     = {Pr_mw:.4e} mW\n"
            f"     = {Pr_dbm:.2f} dBm\n"
        )
        self._write(text)
        self._plot_pr_vs_distance(Pt_w, Gt, Gr, f_hz, marked_d=d_m)

    def _plot_pr_vs_distance(self, Pt, Gt, Gr, freq_hz, marked_d):
        distances = np.linspace(100, 20000, 500)
        pr_dbm = [10 * math.log10(
            received_power_free_space(Pt, Gt, Gr, freq_hz, d) * 1e3
        ) for d in distances]

        fig, ax = plt.subplots(figsize=(7, 3.5), facecolor="#1e1e1e")
        ax.set_facecolor("#1e1e1e")
        ax.plot(distances / 1000, pr_dbm, color="#3498db", lw=2)
        pr_mark = 10 * math.log10(
            received_power_free_space(Pt, Gt, Gr, freq_hz, marked_d) * 1e3)
        ax.axvline(marked_d / 1000, color="#e74c3c", lw=1.5, linestyle="--",
                   label=f"d={marked_d/1000:.0f} km -> {pr_mark:.1f} dBm")
        ax.set_xlabel("Distance [km]", color="gray")
        ax.set_ylabel("Received power [dBm]", color="gray")
        ax.set_title("Free-space received power vs distance", color="white")
        ax.tick_params(colors="gray")
        ax.legend(facecolor="#2b2b2b", labelcolor="white", fontsize=9)
        for spine in ax.spines.values():
            spine.set_edgecolor("#444")
        fig.tight_layout()
        self._embed_fig(fig)

    def _show_task2(self):
        # Given
        Pt_w   = 40.0          # W
        d_km   = 1.0
        f_mhz  = 900.0
        f_hz   = f_mhz * 1e6
        Gt_db  = 1.0
        Gr_db  = 1.0
        Gt     = 10 ** (Gt_db / 10)
        Gr     = 10 ** (Gr_db / 10)

        Lf_db  = free_space_path_loss(f_mhz, d_km)
        # Pr = Pt * Gt * Gr / Lf  -> in dB: Pr_dBW = Pt_dBW + Gt_dB + Gr_dB - Lf_dB
        Pt_dbw = 10 * math.log10(Pt_w)
        Pr_dbw = Pt_dbw + Gt_db + Gr_db - Lf_db
        Pr_w   = 10 ** (Pr_dbw / 10)
        Pr_mw  = Pr_w * 1e3

        # Cross-check with direct formula
        lam    = wavelength(f_hz)
        Pr_direct = received_power_free_space(Pt_w, Gt, Gr, f_hz, d_km * 1000)
        Pr_direct_dbm = 10 * math.log10(Pr_direct * 1e3)

        text = (
            "TASK 2 - Free-space path loss\n"
            "===============================================\n\n"
            "Given:\n"
            f"  Transmit power   Pt = {Pt_w} W  ({Pt_dbw:.2f} dBW)\n"
            f"  Distance          d = {d_km} km\n"
            f"  Carrier frequency f = {f_mhz} MHz\n"
            f"  TX antenna gain  Gt = {Gt_db} dB\n"
            f"  RX antenna gain  Gr = {Gr_db} dB\n\n"
            "Step 1 - Free-space path loss:\n"
            f"  Lf = 32.45 + 20*log10({f_mhz}) + 20*log10({d_km})\n"
            f"     = 32.45 + {20*math.log10(f_mhz):.2f} + {20*math.log10(d_km):.2f}\n"
            f"     = {Lf_db:.2f} dB\n\n"
            "Step 2 - Received power (dB domain):\n"
            f"  Pr[dBW] = Pt[dBW] + Gt[dB] + Gr[dB] - Lf[dB]\n"
            f"          = {Pt_dbw:.2f} + {Gt_db} + {Gr_db} - {Lf_db:.2f}\n"
            f"          = {Pr_dbw:.2f} dBW\n"
            f"          = {Pr_w:.4e} W  =  {Pr_mw:.4e} mW\n\n"
            "Verification (direct formula):\n"
            f"  Pr = {Pr_direct:.4e} W  =  {Pr_direct_dbm:.2f} dBm\n\n"
            f"ANSWER:\n"
            f"  Received power  = {Pr_mw:.4e} mW\n"
            f"  Path loss       = {Lf_db:.2f} dB\n"
        )
        self._write(text)
        self._plot_path_loss_vs_distance(f_mhz, marked_d=d_km)

    def _plot_path_loss_vs_distance(self, f_mhz, marked_d):
        distances = np.linspace(0.1, 20, 500)
        loss = [free_space_path_loss(f_mhz, d) for d in distances]

        fig, ax = plt.subplots(figsize=(7, 3.5), facecolor="#1e1e1e")
        ax.set_facecolor("#1e1e1e")
        ax.plot(distances, loss, color="#2ecc71", lw=2)
        ax.axvline(marked_d, color="#e74c3c", lw=1.5, linestyle="--",
                   label=f"d={marked_d} km -> {free_space_path_loss(f_mhz, marked_d):.1f} dB")
        ax.set_xlabel("Distance [km]", color="gray")
        ax.set_ylabel("Path loss [dB]", color="gray")
        ax.set_title(f"Free-space path loss @ {f_mhz} MHz", color="white")
        ax.tick_params(colors="gray")
        ax.legend(facecolor="#2b2b2b", labelcolor="white", fontsize=9)
        for spine in ax.spines.values():
            spine.set_edgecolor("#444")
        fig.tight_layout()
        self._embed_fig(fig)

    def _show_task3(self):
        Pt_w  = 5.0
        f_mhz = 900.0
        f_hz  = f_mhz * 1e6
        d_m   = 2000.0
        Gt    = 1.0
        Gr    = 1.0

        lam   = wavelength(f_hz)
        Pr_w  = received_power_free_space(Pt_w, Gt, Gr, f_hz, d_m)
        Pr_mw = Pr_w * 1e3
        Pr_dbm = 10 * math.log10(Pr_mw)
        Lf_db = free_space_path_loss(f_mhz, d_m / 1000)

        text = (
            "TASK 3 - Received power (unity gains)\n"
            "===============================================\n\n"
            "Given:\n"
            f"  Transmit power   Pt = {Pt_w} W\n"
            f"  Frequency         f = {f_mhz} MHz\n"
            f"  Distance          d = {d_m/1000:.0f} km = {d_m:.0f} m\n"
            f"  Gt = Gr = 1 (unity, isotropic antennas)\n\n"
            "Step 1 - Wavelength:\n"
            f"  lambda = c / f = {lam:.4f} m\n\n"
            "Step 2 - Free-space received power:\n"
            f"  Pr = Pt * (lambda / (4*pi*d))^2\n"
            f"     = {Pt_w} * ({lam:.4f} / (4*pi*{d_m:.0f}))^2\n"
            f"     = {Pr_w:.4e} W\n"
            f"     = {Pr_mw:.4e} mW\n"
            f"     = {Pr_dbm:.2f} dBm\n\n"
            "Cross-check via path loss:\n"
            f"  Lf = {Lf_db:.2f} dB\n"
            f"  Pr = {10*math.log10(Pt_w*1e3):.2f} dBm - {Lf_db:.2f} dB = {10*math.log10(Pt_w*1e3)-Lf_db:.2f} dBm\n\n"
            f"ANSWER:  Pr = {Pr_w:.4e} W  =  {Pr_dbm:.2f} dBm\n"
        )
        self._write(text)
        self._clear_plot()

    def _show_task4(self):
        # Multipath explanation + calculation
        Rs     = 1.0           # threshold amplitude
        sigma  = 1.02          # rms amplitude (given as sqrt(sigma^2) in problem)
        rho    = Rs / sigma    # rho = Rs / rms
        v_kmh  = 20.0
        v_ms   = v_kmh / 3.6
        f_hz   = 800e6         # 800 MHz
        fm     = max_doppler(v_ms, f_hz)
        N_lcr  = level_crossing_rate(rho, fm)

        lam = wavelength(f_hz)

        text = (
            "TASK 4 - Level Crossing Rate\n"
            "===============================================\n\n"
            "Multipath propagation explanation:\n"
            "  In a cellular network, the transmitted signal\n"
            "  reaches the receiver via multiple paths due to:\n"
            "    * Reflection  (from buildings, ground)\n"
            "    * Scattering  (from rough surfaces, foliage)\n"
            "    * Diffraction (bending around obstacles)\n\n"
            "  Each copy arrives with a different delay, phase,\n"
            "  and amplitude.  The copies add constructively or\n"
            "  destructively -> Rayleigh fading.\n\n"
            "Processing multipath signals:\n"
            "  * RAKE receiver (CDMA/WCDMA) - fingers align\n"
            "    and combine delayed copies coherently.\n"
            "  * Equaliser (GSM) - estimates channel impulse\n"
            "    response and inverts it.\n"
            "  * OFDM (LTE/5G) - cyclic prefix absorbs delay\n"
            "    spread; each sub-carrier sees flat fading.\n\n"
            "----------------------------------------------\n"
            "Level Crossing Rate  N(Rs) calculation:\n"
            "----------------------------------------------\n"
            "Given:\n"
            f"  Threshold RS    = {Rs}\n"
            f"  RMS amplitude   = {sigma}\n"
            f"  rho = RS/rms    = {Rs}/{sigma} = {rho:.4f}\n"
            f"  Speed           = {v_kmh} km/h = {v_ms:.4f} m/s\n"
            f"  Frequency       = {f_hz/1e6:.0f} MHz\n\n"
            "Step 1 - Wavelength:\n"
            f"  lambda = c/f = {lam:.4f} m\n\n"
            "Step 2 - Max Doppler frequency:\n"
            f"  fm = v/lambda = {v_ms:.4f}/{lam:.4f} = {fm:.4f} Hz\n\n"
            "Step 3 - Level crossing rate:\n"
            f"  N(RS) = sqrt(2*pi) * fm * rho * exp(-rho^2)\n"
            f"        = sqrt(2*pi) * {fm:.4f} * {rho:.4f} * exp(-{rho**2:.4f})\n"
            f"        = {N_lcr:.4f} crossings/second\n\n"
            f"ANSWER:  N(RS) = {N_lcr:.4f} crossings/s\n"
        )
        self._write(text)
        self._plot_lcr(sigma, fm)

    def _plot_lcr(self, sigma, fm):
        rhos = np.linspace(0.01, 3, 400)
        lcr  = [level_crossing_rate(r, fm) for r in rhos]

        fig, ax = plt.subplots(figsize=(7, 3.5), facecolor="#1e1e1e")
        ax.set_facecolor("#1e1e1e")
        ax.plot(rhos, lcr, color="#e67e22", lw=2)
        rho_mark = 1.0 / sigma
        ax.axvline(rho_mark, color="#e74c3c", lw=1.5, linestyle="--",
                   label=f"rho={rho_mark:.3f} -> N={level_crossing_rate(rho_mark, fm):.4f}")
        ax.set_xlabel("rho = RS / rms", color="gray")
        ax.set_ylabel("N(RS) [crossings/s]", color="gray")
        ax.set_title("Level Crossing Rate vs normalised threshold", color="white")
        ax.tick_params(colors="gray")
        ax.legend(facecolor="#2b2b2b", labelcolor="white", fontsize=9)
        for spine in ax.spines.values():
            spine.set_edgecolor("#444")
        fig.tight_layout()
        self._embed_fig(fig)

    def _show_task5(self):
        # Same data as task 4
        v_kmh = 20.0
        v_ms  = v_kmh / 3.6
        f_hz  = 800e6
        fm    = max_doppler(v_ms, f_hz)
        rho   = 1.0 / 1.02

        # Attenuation (fade) duration coefficient r_N
        # From lab: r_N(rho) = sqrt(2*pi) / fm  (at rho used in task 4)
        # More general: average fade duration t_f = r(rho) / N(rho)
        # t_f = (exp(rho^2)-1) / (rho * fm * sqrt(2*pi))
        t_f   = fade_duration(rho, fm)
        N_lcr = level_crossing_rate(rho, fm)
        lam   = wavelength(f_hz)

        text = (
            "TASK 5 - Attenuation (fade) coefficient\n"
            "===============================================\n\n"
            "Using data from Task 4:\n"
            f"  Speed     v  = {v_kmh} km/h = {v_ms:.4f} m/s\n"
            f"  Frequency f  = {f_hz/1e6:.0f} MHz\n"
            f"  lambda       = {lam:.4f} m\n"
            f"  fm           = {fm:.4f} Hz\n"
            f"  rho          = {rho:.4f}\n\n"
            "Fade attenuation coefficient:\n"
            "  The average fade duration (time signal stays\n"
            "  below threshold RS) is given by:\n\n"
            "  t_f = (exp(rho^2) - 1) / (rho * fm * sqrt(2*pi))\n\n"
            f"  exp(rho^2)  = exp({rho**2:.4f}) = {math.exp(rho**2):.6f}\n"
            f"  numerator   = {math.exp(rho**2)-1:.6f}\n"
            f"  denominator = {rho:.4f} * {fm:.4f} * sqrt(2*pi)\n"
            f"              = {rho * fm * math.sqrt(2*math.pi):.6f}\n\n"
            f"  t_f = {t_f:.6f} s\n\n"
            "Consistency check with LCR from Task 4:\n"
            f"  N(RS)       = {N_lcr:.6f} crossings/s\n"
            f"  t_f * N(RS) = {t_f * N_lcr:.6f}  (should equal exp(-rho^2) = {math.exp(-rho**2):.6f})\n\n"
            f"ANSWER:  Average fade duration = {t_f:.6f} s  =  {t_f*1000:.4f} ms\n"
        )
        self._write(text)
        self._clear_plot()

    def _show_task6(self):
        # Given: f = 5 MHz, rho = 0.1
        f_hz  = 5e6
        rho   = 0.1
        # We need fm.  The problem says "rho = 0.1" but no speed is given directly.
        # From the lab sheet formula: tau_s = (exp(rho^2)-1) / (rho*fm*sqrt(2*pi))
        # The problem asks to compute tau_s, so fm must come from somewhere.
        # Looking at lab: "Czas trwania tłumienia: tau_s = (exp(rho^2)-1)/(rho*fm*sqrt(2*pi))"
        # and earlier formula  tau_s = sqrt(pi/2) * (exp(rho^2)-1) / (rho * fm)
        # Without explicit speed, use the simplified version from the lab:
        # tau_s = sqrt(2*pi) / fm  when rho -> 0.
        # However the problem gives rho=0.1 so we use the full formula.
        # Since fm is not given in this task, interpret: use fm = v/lambda from previous tasks
        # OR note the lab lists two formula variants.  The simpler "tau_s = sqrt(2pi)/fm"
        # is the limit rho->0.  For rho=0.1 use the exact formula.
        # The problem gives only f and rho -- so we compute tau_s(rho) symbolically in terms
        # of fm, then also show a sample numerical result with a typical fm.

        lam = wavelength(f_hz)

        # Numerical example: assume v = 20 km/h from task 4 for illustration
        v_ms_example = 20 / 3.6
        fm_example   = max_doppler(v_ms_example, f_hz)
        tau_example  = fade_duration(rho, fm_example)

        text = (
            "TASK 6 - Fade duration\n"
            "===============================================\n\n"
            "Given:\n"
            f"  Carrier frequency  f   = {f_hz/1e6:.0f} MHz\n"
            f"  Normalised threshold rho = {rho}\n\n"
            "Formula:\n"
            "  tau_s = (exp(rho^2) - 1) / (rho * fm * sqrt(2*pi))\n\n"
            f"With rho = {rho}:\n"
            f"  exp(rho^2) = exp({rho**2:.4f}) = {math.exp(rho**2):.6f}\n"
            f"  exp(rho^2) - 1  = {math.exp(rho**2)-1:.6f}\n"
            f"  rho * sqrt(2*pi) = {rho * math.sqrt(2*math.pi):.6f}\n\n"
            f"  tau_s = {math.exp(rho**2)-1:.6f} / ({rho * math.sqrt(2*math.pi):.6f} * fm)\n"
            f"        = {(math.exp(rho**2)-1)/(rho*math.sqrt(2*math.pi)):.6f} / fm\n\n"
            "Numerical example (v = 20 km/h):\n"
            f"  lambda = c/f = {lam:.4f} m\n"
            f"  fm     = v/lambda = {v_ms_example:.4f}/{lam:.4f} = {fm_example:.4f} Hz\n"
            f"  tau_s  = {tau_example:.6f} s  =  {tau_example*1000:.4f} ms\n\n"
            f"ANSWER (rho={rho}, fm={fm_example:.4f} Hz):\n"
            f"  Fade duration tau_s = {tau_example*1000:.4f} ms\n"
        )
        self._write(text)
        self._plot_fade_duration(f_hz)

    def _plot_fade_duration(self, f_hz):
        v_ms = 20 / 3.6
        fm   = max_doppler(v_ms, f_hz)
        rhos = np.linspace(0.05, 3, 400)
        taus = [fade_duration(r, fm) * 1000 for r in rhos]  # ms

        fig, ax = plt.subplots(figsize=(7, 3.5), facecolor="#1e1e1e")
        ax.set_facecolor("#1e1e1e")
        ax.plot(rhos, taus, color="#9b59b6", lw=2)
        ax.axvline(0.1, color="#e74c3c", lw=1.5, linestyle="--",
                   label=f"rho=0.1 -> {fade_duration(0.1, fm)*1000:.4f} ms")
        ax.set_xlabel("rho = RS / rms", color="gray")
        ax.set_ylabel("Fade duration [ms]", color="gray")
        ax.set_title(f"Average fade duration @ f={f_hz/1e6:.0f} MHz, v=20 km/h", color="white")
        ax.tick_params(colors="gray")
        ax.legend(facecolor="#2b2b2b", labelcolor="white", fontsize=9)
        for spine in ax.spines.values():
            spine.set_edgecolor("#444")
        fig.tight_layout()
        self._embed_fig(fig)

    def _show_task7(self):
        self._clear_plot()
        text = (
            "TASK 7 - Free space vs propagation with obstacles\n"
            "===============================================\n\n"
            "FREE-SPACE PROPAGATION\n"
            "  * No objects between transmitter and receiver.\n"
            "  * Signal travels in a straight line (LOS).\n"
            "  * Only path loss: Lf ~ (4*pi*d/lambda)^2\n"
            "  * Predictable, well-modelled by Friis formula.\n"
            "  * Signal power decreases as 1/d^2 (20 dB/decade).\n\n"
            "PROPAGATION WITH OBSTACLES (indoor/urban)\n"
            "  * Multiple mechanisms alter the signal:\n\n"
            "  1. REFLECTION\n"
            "     Signal bounces off large smooth surfaces\n"
            "     (buildings, ground, walls).\n"
            "     Creates multipath -> Rayleigh/Rician fading.\n\n"
            "  2. DIFFRACTION\n"
            "     Signal bends around sharp edges (rooftops,\n"
            "     hilltops) -- allows NLOS coverage.\n"
            "     Modelled by knife-edge diffraction loss.\n\n"
            "  3. SCATTERING\n"
            "     Signal scattered by rough surfaces, foliage,\n"
            "     lamp posts, small objects.  Energy dispersed\n"
            "     in many directions.\n\n"
            "  4. ABSORPTION / PENETRATION LOSS\n"
            "     Walls, floors, terrain absorb signal energy.\n"
            "     Each wall may add 5-15 dB of loss.\n\n"
            "KEY DIFFERENCE:\n"
            "  Free space:   Lf ~ d^2  (path loss only)\n"
            "  With obstacles: L ~ d^n  where n = 2.7..5\n"
            "  (n depends on environment: urban, indoor, etc.)\n\n"
            "  Real-world models: Okumura-Hata, COST-231,\n"
            "  Indoor path-loss model, Two-ray ground model.\n"
        )
        self._write(text)

    def _show_task8(self):
        self._clear_plot()
        text = (
            "TASK 8 - Fast fading vs slow fading\n"
            "===============================================\n\n"
            "SLOW FADING  (large-scale / shadowing)\n"
            "  Caused by:\n"
            "    Large obstacles (hills, buildings) blocking\n"
            "    the signal -> shadowing.\n\n"
            "  Characteristics:\n"
            "    * Variations occur over hundreds of wavelengths.\n"
            "    * Signal level changes slowly as MS moves.\n"
            "    * Modelled by log-normal distribution (dB domain).\n"
            "    * Coherence distance >> wavelength.\n"
            "    * Represented by LS (slow-fading factor) in\n"
            "      the path-loss model  L = LP * LS * LF.\n\n"
            "FAST FADING  (small-scale / multipath fading)\n"
            "  Caused by:\n"
            "    Constructive/destructive interference of many\n"
            "    reflected, scattered, diffracted copies of the\n"
            "    signal arriving with different delays & phases.\n\n"
            "  Characteristics:\n"
            "    * Variations occur over fractions of a wavelength.\n"
            "    * Signal can change drastically in a few cm.\n"
            "    * Modelled by Rayleigh (NLOS) or Rician (LOS)\n"
            "      distributions.\n"
            "    * Coherence time ~ 1/fm  (Doppler-limited).\n"
            "    * Represented by LF (fast-fading factor).\n\n"
            "SUMMARY TABLE:\n"
            "  Property       | Slow fading      | Fast fading\n"
            "  --------------|------------------|------------------\n"
            "  Cause          | Shadowing         | Multipath\n"
            "  Scale          | >> lambda         | ~ lambda\n"
            "  Distribution   | Log-normal        | Rayleigh/Rician\n"
            "  Variation rate | Slow (seconds)    | Fast (ms)\n"
            "  Mitigation     | Power control,    | Diversity, RAKE,\n"
            "                 | link budget margin| equalisers, OFDM\n"
        )
        self._write(text)

    def _show_task9(self):
        self._clear_plot()
        text = (
            "TASK 9 - NLOS reception\n"
            "===============================================\n\n"
            "SITUATION:\n"
            "  The receiver is NOT in the line-of-sight (LOS)\n"
            "  of the base station.  A direct path is blocked\n"
            "  by buildings, terrain, or other obstacles.\n\n"
            "WHY CAN THE RECEIVER STILL RECEIVE THE SIGNAL?\n\n"
            "1. DIFFRACTION\n"
            "   Radio waves bend around the edges of obstacles\n"
            "   (e.g. rooftop edge, hilltop) -- this is called\n"
            "   knife-edge diffraction.  The signal 'reaches\n"
            "   around' the obstacle, though with additional loss.\n\n"
            "2. REFLECTION\n"
            "   The signal bounces off buildings, ground, or\n"
            "   other large surfaces and reaches the receiver\n"
            "   via an indirect path.\n\n"
            "3. SCATTERING\n"
            "   Rough surfaces and small objects scatter the\n"
            "   signal in all directions, sending some energy\n"
            "   toward the receiver.\n\n"
            "4. COMBINATION (multipath)\n"
            "   In urban environments, the receiver typically\n"
            "   collects many copies via all three mechanisms.\n"
            "   The Rayleigh fading model describes this scenario.\n\n"
            "PRACTICAL IMPLICATION:\n"
            "   Cellular networks are designed to provide\n"
            "   coverage in NLOS conditions.  The Hata/COST-231\n"
            "   propagation models already include NLOS losses.\n"
            "   The link budget allocates a 'shadow margin'\n"
            "   (typically 5-10 dB) to handle shadowing.\n"
        )
        self._write(text)

    def _show_task10(self):
        f_hz  = 900e6        # 900 MHz
        v_kmh = 40.0
        v_ms  = v_kmh / 3.6
        theta = 0.0          # theta not specified -> worst case (0 deg)
        lam   = wavelength(f_hz)
        fd    = doppler_shift_from_v(v_ms, f_hz, theta)

        text = (
            "TASK 10 - Doppler shift\n"
            "===============================================\n\n"
            "Given:\n"
            f"  Carrier frequency  fc = {f_hz/1e6:.0f} MHz\n"
            f"  Receiver speed      v = {v_kmh} km/h = {v_ms:.4f} m/s\n"
            f"  Angle theta             = not specified -> use 0 deg (max shift)\n\n"
            "Step 1 - Wavelength:\n"
            f"  lambda = c/f = {SPEED_OF_LIGHT:.3e} / {f_hz:.3e}\n"
            f"         = {lam:.6f} m\n\n"
            "  (Quick check: lambda[m] = 300 / f[MHz]\n"
            f"   = 300 / {f_hz/1e6:.0f} = {300/(f_hz/1e6):.6f} m  OK)\n\n"
            "Step 2 - Doppler shift:\n"
            f"  fd = v * cos(theta) / lambda\n"
            f"     = {v_ms:.4f} * cos({theta} deg) / {lam:.6f}\n"
            f"     = {fd:.4f} Hz\n\n"
            f"ANSWER:  Doppler shift fd = {fd:.4f} Hz  ~= {fd:.2f} Hz\n"
        )
        self._write(text)
        self._plot_doppler_vs_theta(v_ms, f_hz)

    def _plot_doppler_vs_theta(self, v_ms, f_hz):
        thetas = np.linspace(0, 180, 361)
        fd_vals = [doppler_shift_from_v(v_ms, f_hz, t) for t in thetas]

        fig, ax = plt.subplots(figsize=(7, 3.5), facecolor="#1e1e1e")
        ax.set_facecolor("#1e1e1e")
        ax.plot(thetas, fd_vals, color="#1abc9c", lw=2)
        ax.axhline(0, color="#555", lw=1)
        ax.set_xlabel("Angle theta [deg]", color="gray")
        ax.set_ylabel("Doppler shift fd [Hz]", color="gray")
        ax.set_title(f"Doppler shift vs angle  (f={f_hz/1e6:.0f} MHz, v={v_ms*3.6:.0f} km/h)",
                     color="white")
        ax.tick_params(colors="gray")
        for spine in ax.spines.values():
            spine.set_edgecolor("#444")
        fig.tight_layout()
        self._embed_fig(fig)

    def _show_task11(self):
        fc_hz  = 900e6       # 900 MHz
        v_kmh  = 50.0
        v_ms   = v_kmh / 3.6
        lam    = wavelength(fc_hz)
        fm     = max_doppler(v_ms, fc_hz)

        # a) moving toward BS: theta = 0 -> fd = +fm -> fr = fc + fd?
        #    Convention: moving toward -> positive Doppler -> fr = fc + fd
        # b) moving away:  theta = 180 -> fd = -fm -> fr = fc - fm
        # c) theta = 60 deg -> fd = fm * cos(60)

        fd_a = doppler_shift_from_v(v_ms, fc_hz, 0)    # toward -> theta=0
        fd_b = doppler_shift_from_v(v_ms, fc_hz, 180)  # away   -> theta=180
        fd_c = doppler_shift_from_v(v_ms, fc_hz, 60)   # 60 deg

        fr_a = fc_hz + fd_a
        fr_b = fc_hz + fd_b  # fd_b is negative
        fr_c = fc_hz + fd_c

        text = (
            "TASK 11 - Received frequency with Doppler\n"
            "===============================================\n\n"
            "Given:\n"
            f"  BS carrier frequency  fc = {fc_hz/1e6:.0f} MHz\n"
            f"  Receiver speed         v = {v_kmh} km/h = {v_ms:.4f} m/s\n\n"
            "Step 1 - Wavelength:\n"
            f"  lambda = 300/{fc_hz/1e6:.0f} MHz = {lam:.6f} m\n\n"
            "Step 2 - Max Doppler:\n"
            f"  fm = v/lambda = {v_ms:.4f}/{lam:.6f} = {fm:.4f} Hz\n\n"
            "Formula:  fr = fc + fd   where fd = fm * cos(theta)\n"
            "  (positive fd when moving toward source)\n\n"
            "--------------------------------------------\n"
            "a) Moving TOWARD the base station (theta = 0 deg):\n"
            f"   fd = fm * cos(0) = {fm:.4f} * 1 = +{fd_a:.4f} Hz\n"
            f"   fr = fc + fd = {fc_hz/1e6:.0f} MHz + {fd_a:.4f} Hz\n"
            f"      = {fr_a:.4f} Hz  =  {fr_a/1e6:.6f} MHz\n\n"
            "--------------------------------------------\n"
            "b) Moving AWAY from the base station (theta = 180 deg):\n"
            f"   fd = fm * cos(180) = {fm:.4f} * (-1) = {fd_b:.4f} Hz\n"
            f"   fr = fc + fd = {fc_hz/1e6:.0f} MHz + ({fd_b:.4f}) Hz\n"
            f"      = {fr_b:.4f} Hz  =  {fr_b/1e6:.6f} MHz\n\n"
            "--------------------------------------------\n"
            "c) Moving at angle 60 deg to the signal direction:\n"
            f"   fd = fm * cos(60) = {fm:.4f} * {math.cos(math.radians(60)):.4f} = {fd_c:.4f} Hz\n"
            f"   fr = fc + fd = {fc_hz/1e6:.0f} MHz + {fd_c:.4f} Hz\n"
            f"      = {fr_c:.4f} Hz  =  {fr_c/1e6:.6f} MHz\n"
        )
        self._write(text)
        self._plot_received_freq(fc_hz, fm)

    def _plot_received_freq(self, fc_hz, fm):
        thetas = np.linspace(0, 360, 720)
        fr_vals = [(fc_hz + fm * math.cos(math.radians(t))) / 1e6 for t in thetas]

        fig, ax = plt.subplots(figsize=(7, 3.5), facecolor="#1e1e1e")
        ax.set_facecolor("#1e1e1e")
        ax.plot(thetas, fr_vals, color="#e74c3c", lw=2)
        ax.axhline(fc_hz / 1e6, color="#aaa", lw=1, linestyle="--", label="fc")
        for angle, color, label in [(0, "#2ecc71", "a) toward"),
                                     (180, "#e67e22", "b) away"),
                                     (60, "#3498db", "c) 60 deg")]:
            fr_mark = (fc_hz + fm * math.cos(math.radians(angle))) / 1e6
            ax.plot(angle, fr_mark, "o", color=color, ms=8, label=f"{label}: {fr_mark:.6f} MHz")
        ax.set_xlabel("Angle theta [deg]", color="gray")
        ax.set_ylabel("Received frequency [MHz]", color="gray")
        ax.set_title(f"Received frequency vs angle  (fc={fc_hz/1e6:.0f} MHz)", color="white")
        ax.tick_params(colors="gray")
        ax.legend(facecolor="#2b2b2b", labelcolor="white", fontsize=8)
        for spine in ax.spines.values():
            spine.set_edgecolor("#444")
        fig.tight_layout()
        self._embed_fig(fig)


if __name__ == "__main__":
    app = Lab6App()
    app.mainloop()
