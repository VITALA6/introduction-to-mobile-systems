# Lab 03 – Mobile Systems Simulator (M/M/S/S Queue Model)

## Co zostało zrealizowane
Zaimplementowano symulator stacji bazowej oparty na modelu kolejkowym M/M/S/S (model Mirosława Szabana). Aplikacja posiada graficzny interfejs użytkownika (customtkinter) umożliwiający konfigurację parametrów: liczby kanałów, długości kolejki, intensywności zgłoszeń (λ), czasu trwania połączenia (N, σ) oraz czasu symulacji. Wyniki prezentowane są w czasie rzeczywistym jako wykresy obciążenia (ρ) i długości kolejki (Q).

## Uruchomienie
```bash
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt
python lab3.py
```
