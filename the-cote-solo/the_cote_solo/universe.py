"""Universo curado (seed) de referencias líquidas — top marcas deportivas.

NÚMEROS ILUSTRATIVOS: retail y base_fair_value son valores semilla de referencia,
NO cotizaciones en vivo. El valor de v0 es el método; la ingesta real reemplaza
estos números. base_fair_value = fair value del secundario en EXCELLENT + full set.
comparables_per_qtr aproxima la densidad de datos (gobierna el tier de liquidez).
"""

from __future__ import annotations

from .models import Instrument

_SEED: list[Instrument] = [
    # --- Rolex deportivos ---
    Instrument("124060", "Rolex", "Submariner", "Submariner No-Date", 9100, 11500, 40),
    Instrument("126610LN", "Rolex", "Submariner", "Submariner Date", 10400, 14000, 45),
    Instrument("126710BLRO", "Rolex", "GMT-Master II", "GMT-Master II Pepsi", 11200, 19500, 35),
    Instrument("126710BLNR", "Rolex", "GMT-Master II", "GMT-Master II Batman", 11200, 18000, 35),
    Instrument("116500LN", "Rolex", "Daytona", "Cosmograph Daytona (cerámico)", 15100, 29000, 30),
    Instrument("124270", "Rolex", "Explorer", "Explorer 36", 7000, 8200, 22),
    Instrument("126234", "Rolex", "Datejust", "Datejust 36", 8200, 9600, 25),
    Instrument("126600", "Rolex", "Sea-Dweller", "Sea-Dweller 43", 13000, 14500, 15),
    Instrument("126622", "Rolex", "Yacht-Master", "Yacht-Master 40", 12300, 13800, 14),
    # --- Omega ---
    Instrument("310.30.42", "Omega", "Speedmaster", "Speedmaster Moonwatch Professional", 7000, 6600, 28),
    Instrument("210.30.42", "Omega", "Seamaster", "Seamaster Diver 300M", 5600, 5200, 24),
    # --- Audemars Piguet ---
    Instrument("15500ST", "Audemars Piguet", "Royal Oak", "Royal Oak 41 Selfwinding", 23900, 42000, 12),
    Instrument("15400ST", "Audemars Piguet", "Royal Oak", "Royal Oak 41 (descat.)", None, 45000, 8),
    # --- Patek Philippe ---
    Instrument("5711/1A", "Patek Philippe", "Nautilus", "Nautilus (descat.)", None, 95000, 6),
    Instrument("5167A", "Patek Philippe", "Aquanaut", "Aquanaut 5167A", 24500, 55000, 5),
    # --- Tudor ---
    Instrument("79030N", "Tudor", "Black Bay", "Black Bay Fifty-Eight", 4100, 3600, 26),
    Instrument("25600TN", "Tudor", "Pelagos", "Pelagos 42", 5000, 4200, 12),
    # --- Cartier (deportivo) ---
    Instrument("WSSA0009", "Cartier", "Santos", "Santos de Cartier Large", 7400, 6900, 14),
]

UNIVERSE: dict[str, Instrument] = {i.ref: i for i in _SEED}


def get(ref: str) -> Instrument | None:
    return UNIVERSE.get(ref)
