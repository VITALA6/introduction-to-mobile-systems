# Lab 05 – Koncepcja komórki i inżynieria ruchu

## Co zostało zrealizowane

Laboratorium dotyczyło geometrii sieci komórkowych oraz podstawowych obliczeń z zakresu inżynierii ruchu.

**Zadanie 1 – Geometria komórek:**
Uzasadnienie stosowania sześciokąta zamiast ośmiokąta: sześciokąt jest jedyną figurą zapewniającą teselację płaszczyzny bez luk, minimalizując przy tym liczbę stacji bazowych przy zasięgu zbliżonym do kołowego.

**Zadanie 2 – Analiza klastra N=7:**
Obliczono odległość ponownego użycia częstotliwości oraz współczynnik S/I dla najgorszego przypadku:

```
D = R × √(3N) = R × √21 ≈ 4,58R
S/I = (1/6) × (D/R)^4 = (1/6) × (4,58)^4 ≈ 73,5  (18,66 dB)
```

**Zadanie 3 – Natężenie ruchu:**
Dla λ = 60 rozmów/h i T = 15 min:

```
A = λ × T = 60 × 0,25 = 15 [Erl]
```

**Zadanie 6 – Skalowalność klastra:**
Analiza podziału klastra N=16 na N=7 i N=9 w kontekście cell splittingu przy rosnącym natężeniu ruchu.

**Zadanie 7 – Pojemność systemu TDMA:**
Przy paśmie 30 MHz, kanałach 25 kHz, N=7 i TDMA×8:

```
1200 kanałów łącznie → 171 na komórkę → 161 użytkowych → 1288 połączeń/komórkę
```

**Zadanie 8 – Analiza obciążenia sieci:**
Dla 12 komórek, 21720 rozmów/h, T = 1 min:

```
Obciążenie = 21720 × (1/60) = 362 [Erl]
Abonenci mobilni (75%): 16290
```

**Zadanie 10 – Rodzaje interferencji:**
- **Współkanałowa (Cochannel):** zakłócenia od stacji na tej samej częstotliwości; redukowana przez zwiększenie D
- **Sąsiedniokanałowa (Adjacent):** zakłócenia od bliskich częstotliwości; redukowana przez separację widmową i filtry

**Zadanie 11 – Zalety sektoryzacji:**
Sektoryzacja poprawia S/I bez zmiany D, co umożliwia stosowanie mniejszych klastrów (mniejsze N) i zwiększenie pojemności systemu bez dodatkowego pasma.
