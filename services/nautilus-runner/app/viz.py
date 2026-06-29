"""Lightweight HTML backtest report (tearsheet).

Pure Python — no plotting deps. Renders a summary table plus an inline SVG
cumulative-PnL (equity) curve from the realized position PnLs. Self-contained
HTML, written next to the CSV reports. Backtest/simulation only.
"""

from __future__ import annotations

import html
from datetime import datetime, timezone


def _equity_svg(pnls: list[float], width: int = 720, height: int = 220, pad: int = 30) -> str:
    """Inline SVG cumulative-PnL curve from per-trade realized PnLs."""
    if not pnls:
        return '<p>No closed trades to plot.</p>'
    equity = []
    running = 0.0
    for p in pnls:
        running += p
        equity.append(running)
    lo, hi = min(equity + [0.0]), max(equity + [0.0])
    span = (hi - lo) or 1.0
    n = len(equity)
    dx = (width - 2 * pad) / max(n - 1, 1)

    def x(i: int) -> float:
        return pad + i * dx

    def y(v: float) -> float:
        return height - pad - (v - lo) / span * (height - 2 * pad)

    pts = " ".join(f"{x(i):.1f},{y(v):.1f}" for i, v in enumerate(equity))
    zero_y = y(0.0)
    color = "#2e7d32" if equity[-1] >= 0 else "#c62828"
    return (
        f'<svg viewBox="0 0 {width} {height}" width="100%" style="background:#fafafa;border:1px solid #ddd">'
        f'<line x1="{pad}" y1="{zero_y:.1f}" x2="{width - pad}" y2="{zero_y:.1f}" stroke="#bbb" stroke-dasharray="4"/>'
        f'<polyline fill="none" stroke="{color}" stroke-width="2" points="{pts}"/>'
        f'<text x="{pad}" y="{pad - 8}" font-size="12" fill="#555">Cumulative PnL (USD)</text>'
        f'</svg>'
    )


def render_html(summary: dict, realized_pnls: list[float]) -> str:
    stats = summary.get("stats_pnls_usd", {})
    rows = "".join(
        f"<tr><td>{html.escape(str(k))}</td><td>{html.escape(str(v))}</td></tr>"
        for k, v in {
            "Strategy": summary.get("strategy"),
            "Market": summary.get("market"),
            "Dataset": summary.get("dataset"),
            "Data provenance": summary.get("data_provenance"),
            "Engine API": summary.get("engine_api"),
            "Bars": summary.get("bars"),
            "Orders": summary.get("total_orders"),
            "Positions": summary.get("total_positions"),
            "Live": summary.get("live"),
            **stats,
        }.items()
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Backtest {html.escape(str(summary.get('backtest_id')))}</title>
<style>body{{font-family:system-ui,Arial;margin:24px;color:#222}}table{{border-collapse:collapse}}
td{{border:1px solid #ddd;padding:4px 10px;font-size:14px}}td:first-child{{color:#555}}
.tag{{background:#e8f5e9;color:#2e7d32;padding:2px 8px;border-radius:4px;font-size:12px}}</style></head>
<body>
<h2>Trading Demo — Backtest report <span class="tag">BACKTEST ONLY · live=false</span></h2>
<p><b>{html.escape(str(summary.get('backtest_id')))}</b> — generated {datetime.now(timezone.utc):%Y-%m-%d %H:%M UTC}</p>
{_equity_svg(realized_pnls)}
<h3>Metrics</h3>
<table>{rows}</table>
<p style="color:#888;font-size:12px">No real orders, no broker. NautilusTrader backtest/simulation.</p>
</body></html>"""
