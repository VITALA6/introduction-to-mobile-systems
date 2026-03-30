# Lab 06 – Propagacja fal i Efekt Dopplera

## Co zostało zrealizowane

Laboratorium dotyczyło propagacji fal radiowych, bilansu łącza oraz efektu Dopplera.

**Zadanie 1 – Parametry łącza radiowego:**
Obliczono zysk anteny odbiornika i moc odbieraną (równanie Friisa). Dane: D = 2,5 m, f = 20 GHz, Pt = 30 mW, Gt = 30 dB, d = 5 km, η = 0,55.

```
G[dB] = 20log(D) + 20log(f[GHz]) + 10log(η) + 20.4
G = 20log(2.5) + 20log(20) + 10log(0.55) + 20.4 ≈ 51.79 dB
```

**Zadanie 2 – Straty w wolnej przestrzeni:**
Dane: Pt = 40 W, d = 1 km, f = 900 MHz, Gt = Gr = 1 dB.

```
Lf[dB] = 32.45 + 20log(f[MHz]) + 20log(d[km])
Lf = 32.45 + 20log(900) + 20log(1) = 32.45 + 59.08 + 0 = 91.53 dB
Pr[dBW] = Pt[dBW] + Gt[dB] + Gr[dB] - Lf[dB]
```

**Zadanie 4 – Wielodrogowość i przekraczanie progu:**
Sygnały wielodrogowe modelowane modelem Rayleigha/Rice'a. Dane: R = 1, σ² = 1,02, v = 20 km/h (5,56 m/s), f = 800 MHz.

```
λ = c / f = 3×10⁸ / 8×10⁸ = 0.375 m
fm = v / λ = 5.56 / 0.375 ≈ 14.83 Hz

ρ = R / σ = 1 / √1.02 ≈ 0.99
N(R) = fm × ρ × √(2π) × exp(-ρ²) ≈ 13.6 s⁻¹
```

**Zadanie 8 – Fading szybki vs wolny:**
- **Fast Fading:** spowodowany wielodrogowością; zmienia się na dystansach rzędu λ/2
- **Slow Fading (Shadowing):** spowodowany przesłonięciem przez duże obiekty; zmiany na znacznie większych dystansach

**Zadanie 9 – Propagacja poza NLOS:**
Odbiór bez bezpośredniej widoczności możliwy dzięki:
1. **Odbicie (Reflection)** – od płaskich powierzchni budynków
2. **Dyfrakcja (Diffraction)** – uginanie fali na krawędziach przeszkód (zasada Huygensa)
3. **Rozproszenie (Scattering)** – od małych obiektów i nierównych powierzchni

**Zadanie 10 i 11 – Przesunięcie Dopplera:**
Dane: f = 900 MHz (λ = 0,333 m), v = 50 km/h (13,89 m/s). Wzór: fd = (v / λ) × cos(θ)

```
a) θ = 0°  (w stronę BS):   fd = +41.7 Hz  → fr = 900.0000417 MHz
b) θ = 180° (od BS):        fd = -41.7 Hz  → fr = 899.9999583 MHz
c) θ = 60°:                 fd = +20.85 Hz → fr = 900.00002085 MHz
