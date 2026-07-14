"""Libro personal: posiciones, P&L, señales de salida y calibración por velocidad.

Registra compras y ventas (SQLite stdlib), calcula P&L no realizado contra el
fair value actual, días en inventario y una **señal de salida** basada en la
velocidad esperada (doc velocity). Cada venta registrada:
  - se convierte en un cierre propio (calidad 1.0) que calibra el pricing, y
  - aporta un días-a-venta realizado que calibra la estimación de tiempo.

Es el loop del moat: operar → registrar → el modelo mejora con TUS datos.
"""

from __future__ import annotations

import os
import sqlite3
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Callable, Optional

from . import velocity
from .comparables import Sale
from .models import Condition, LiquidityTier


@dataclass
class Position:
    id: int
    ref: str
    buy_price: float
    buy_date: str          # ISO date
    target_price: Optional[float]
    status: str            # open | closed
    sale_price: Optional[float] = None
    sale_date: Optional[str] = None


@dataclass
class PositionView:
    pos: Position
    fair_value: float
    unrealized_pnl: float
    pnl_pct: float
    days_held: int
    expected_days: int
    signal: str            # SELL | HOLD | REVIEW
    reason: str


def _today() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def _days_between(a: str, b: Optional[str] = None) -> int:
    d0 = date.fromisoformat(a)
    d1 = date.fromisoformat(b) if b else datetime.now(timezone.utc).date()
    return max(0, (d1 - d0).days)


class Portfolio:
    def __init__(self, path: str = ":memory:"):
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute(
            """CREATE TABLE IF NOT EXISTS positions(
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 ref TEXT NOT NULL, buy_price REAL NOT NULL, buy_date TEXT NOT NULL,
                 target_price REAL, status TEXT NOT NULL DEFAULT 'open',
                 sale_price REAL, sale_date TEXT)"""
        )
        self.conn.commit()

    # --- registro ---
    def record_buy(self, ref: str, price: float, buy_date: Optional[str] = None,
                   target: Optional[float] = None) -> int:
        cur = self.conn.execute(
            "INSERT INTO positions(ref,buy_price,buy_date,target_price) VALUES(?,?,?,?)",
            (ref, float(price), buy_date or _today(), target),
        )
        self.conn.commit()
        return cur.lastrowid

    def record_sale(self, position_id: int, price: float,
                    sale_date: Optional[str] = None) -> None:
        self.conn.execute(
            "UPDATE positions SET status='closed', sale_price=?, sale_date=? WHERE id=?",
            (float(price), sale_date or _today(), position_id),
        )
        self.conn.commit()

    # --- lecturas ---
    def _rows(self, status: Optional[str] = None):
        q = "SELECT * FROM positions"
        params: tuple = ()
        if status:
            q += " WHERE status=?"; params = (status,)
        return [Position(**dict(r)) for r in self.conn.execute(q, params)]

    def open_positions(self) -> list[Position]:
        return self._rows("open")

    def closed_positions(self) -> list[Position]:
        return self._rows("closed")

    def view(self, fair_value_fn: Callable[[str], Optional[float]],
             tier_fn: Optional[Callable[[str], LiquidityTier]] = None) -> list[PositionView]:
        """Vista de posiciones abiertas con P&L y señal de salida.

        `fair_value_fn(ref)` -> fair value actual (EXCELLENT full set).
        `tier_fn(ref)` -> tier de liquidez (para la velocidad esperada).
        """
        out: list[PositionView] = []
        for p in self.open_positions():
            fv = fair_value_fn(p.ref) or p.buy_price
            pnl = fv - p.buy_price
            days = _days_between(p.buy_date)
            tier = tier_fn(p.ref) if tier_fn else LiquidityTier.A
            exp, _ = velocity.expected_days_to_sell(tier, Condition.EXCELLENT)
            signal, reason = self._signal(p, fv, days, exp)
            out.append(PositionView(
                pos=p, fair_value=round(fv, 2), unrealized_pnl=round(pnl, 2),
                pnl_pct=round(pnl / p.buy_price * 100, 1) if p.buy_price else 0.0,
                days_held=days, expected_days=exp, signal=signal, reason=reason,
            ))
        return out

    @staticmethod
    def _signal(p: Position, fv: float, days: int, expected: int) -> tuple[str, str]:
        if p.target_price and fv >= p.target_price:
            return "SELL", "Fair value alcanzó tu objetivo."
        if days > expected * 1.5:
            return "REVIEW", f"{days}d en inventario (esperado ~{expected}d): rota lento."
        return "HOLD", "Dentro de la ventana esperada."

    def summary(self, fair_value_fn) -> dict:
        views = self.view(fair_value_fn)
        deployed = sum(v.pos.buy_price for v in views)
        value = sum(v.fair_value for v in views)
        return {
            "deployed": round(deployed, 2),
            "current_value": round(value, 2),
            "unrealized_pnl": round(value - deployed, 2),
            "return_pct": round((value - deployed) / deployed * 100, 1) if deployed else 0.0,
            "open_positions": len(views),
        }

    # --- calibración: las ventas cerradas mejoran el modelo ---
    def realized_sales_as_comparables(self) -> list[Sale]:
        """Cada venta propia es un cierre de calidad 1.0 para calibrar el pricing."""
        out = []
        for p in self.closed_positions():
            if p.sale_price is None:
                continue
            age = _days_between(p.sale_date) if p.sale_date else 0
            # asume EXCELLENT full set (baseline) para la venta propia registrada
            out.append(Sale(ref=p.ref, baseline_price=float(p.sale_price),
                            quality=1.0, age_days=age))
        return out

    def realized_days_to_sell(self) -> list[int]:
        return [_days_between(p.buy_date, p.sale_date)
                for p in self.closed_positions() if p.sale_date]

    def close(self) -> None:
        self.conn.close()


def seed_demo(pf: Portfolio) -> None:
    """Posiciones de ejemplo (las del terminal) para que la CLI muestre algo.

    Fechas relativas a hoy para que los días-en-inventario y las señales
    (SELL / HOLD / REVIEW) sean realistas independientemente de la fecha.
    """
    def days_ago(n):
        return (datetime.now(timezone.utc).date() - timedelta(days=n)).isoformat()
    pf.record_buy("126610LN", 11200, days_ago(88), target=14000)    # fv 14000 → SELL
    pf.record_buy("310.30.42", 5400, days_ago(41), target=7000)     # dentro de ventana → HOLD
    pf.record_buy("126710BLNR", 17500, days_ago(132), target=19500) # 132d → REVIEW


def _cli() -> int:
    from .universe import UNIVERSE
    pf = Portfolio(":memory:")
    seed_demo(pf)
    fv = lambda ref: UNIVERSE[ref].base_fair_value_usd if ref in UNIVERSE else None
    print("\nThe Cote Solo · libro personal\n" + "=" * 72)
    print(f"{'MODELO':<26}{'COMPRA':>9}{'FAIR VAL':>10}{'P&L':>9}{'DÍAS':>6}  SEÑAL")
    print("-" * 72)
    for v in pf.view(fv):
        inst = UNIVERSE.get(v.pos.ref)
        name = (inst.brand + " " + inst.name)[:25] if inst else v.pos.ref
        print(f"{name:<26}{('$'+format(v.pos.buy_price,',.0f')):>9}"
              f"{('$'+format(v.fair_value,',.0f')):>10}"
              f"{(('+' if v.unrealized_pnl>=0 else '')+format(v.unrealized_pnl,',.0f')):>9}"
              f"{str(v.days_held)+'d':>6}  {v.signal} · {v.reason}")
    s = pf.summary(fv)
    print("-" * 72)
    print(f"Desplegado ${s['deployed']:,.0f} · Valor ${s['current_value']:,.0f} · "
          f"P&L ${s['unrealized_pnl']:+,.0f} ({s['return_pct']:+.1f}%)\n")
    pf.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())
