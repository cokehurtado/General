"""Modelo de costos de internación y transporte a Panamá + costo de capital.

Todos los parámetros son configurables. Los valores por defecto asumen el
escenario 'importar para uso propio' (conservador). Para reexportación vía
Zona Libre de Colón el arancel/impuesto puede acercarse a 0 — cambiar el config.

IMPORTANTE: las tasas aduaneras y de impuesto son ESTIMADAS; confirmar con un
corredor de aduanas antes de operar con dinero real.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ImportCostConfig:
    # Transporte
    shipping_flat_usd: float = 120.0     # courier asegurado puerta a puerta
    insurance_rate: float = 0.006        # % del valor asegurado
    # Internación (sobre CIF = valor + flete + seguro)
    duty_rate: float = 0.05              # arancel de importación (estimado)
    itbms_rate: float = 0.07             # ITBMS Panamá (estimado)
    broker_flat_usd: float = 60.0        # corredor/handling
    # Capital
    capital_annual_rate: float = 0.12    # costo de oportunidad anual del capital

    # Escenario reexportación ZLC (arancel/ITBMS ~0). Úsalo si operas sin nacionalizar.
    @staticmethod
    def zlc_reexport() -> "ImportCostConfig":
        return ImportCostConfig(duty_rate=0.0, itbms_rate=0.0)


def landed_cost(
    buy_price: float,
    value_for_customs: float,
    hold_days: int,
    cfg: ImportCostConfig,
) -> dict:
    """Costo total de poner la pieza en Panamá y mantenerla hasta venderla.

    `value_for_customs` normalmente es el precio de compra (o el declarado);
    lo dejamos separado por si la aduana valúa distinto.
    Devuelve un breakdown; 'total' es la suma de sobrecostos (SIN el precio de compra).
    """
    insurance = value_for_customs * cfg.insurance_rate
    shipping = cfg.shipping_flat_usd
    cif = value_for_customs + shipping + insurance
    duty = cif * cfg.duty_rate
    itbms = cif * cfg.itbms_rate
    broker = cfg.broker_flat_usd
    capital = buy_price * (hold_days / 365.0) * cfg.capital_annual_rate

    total = shipping + insurance + duty + itbms + broker + capital
    return {
        "shipping": round(shipping, 2),
        "insurance": round(insurance, 2),
        "duty": round(duty, 2),
        "itbms": round(itbms, 2),
        "broker": round(broker, 2),
        "capital_cost": round(capital, 2),
        "total": round(total, 2),
    }
