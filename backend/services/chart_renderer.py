"""
Rendu de graphiques via matplotlib (headless).
Génère des PNG à partir des données brutes.
"""
from pathlib import Path
from collections import Counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


COLORS = ["#0f3460", "#e94560", "#16213e", "#533483", "#0a1931", "#185adb", "#ffc93c"]


def _detect_numeric_columns(data: list[dict]) -> list[str]:
    """Identifie les colonnes numériques dans les données."""
    if not data:
        return []
    numeric = []
    for key in data[0]:
        try:
            float(data[0][key])
            numeric.append(key)
        except (ValueError, TypeError):
            pass
    return numeric


def _detect_categorical_columns(data: list[dict]) -> list[str]:
    """Identifie les colonnes catégorielles."""
    if not data:
        return []
    categorical = []
    for key in data[0]:
        try:
            float(data[0][key])
        except (ValueError, TypeError):
            categorical.append(key)
    return categorical


def _render_bar(data: list[dict], output_path: Path) -> Path:
    """Génère un graphique en barres."""
    numeric_cols = _detect_numeric_columns(data)
    cat_cols = _detect_categorical_columns(data)

    if not numeric_cols:
        return _render_placeholder(output_path, "bar")

    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor("#fafafa")

    y_col = numeric_cols[0]
    values = [float(row.get(y_col, 0)) for row in data[:20]]
    labels = [str(row.get(cat_cols[0], i)) if cat_cols else str(i) for i, row in enumerate(data[:20])]

    bars = ax.bar(range(len(values)), values, color=COLORS[:len(values)], edgecolor="white", linewidth=0.5)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=9)
    ax.set_ylabel(y_col, fontsize=11, fontweight="bold")
    ax.set_title(f"{y_col}", fontsize=14, fontweight="bold", color="#16213e")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()
    plt.savefig(str(output_path), dpi=150, bbox_inches="tight")
    plt.close()
    return output_path


def _render_pie(data: list[dict], output_path: Path) -> Path:
    """Génère un graphique circulaire."""
    cat_cols = _detect_categorical_columns(data)

    if not cat_cols:
        return _render_placeholder(output_path, "pie")

    col = cat_cols[0]
    counts = Counter(row.get(col, "N/A") for row in data)
    top = dict(counts.most_common(7))

    fig, ax = plt.subplots(figsize=(8, 8))
    fig.patch.set_facecolor("#fafafa")

    wedges, texts, autotexts = ax.pie(
        top.values(),
        labels=top.keys(),
        colors=COLORS[:len(top)],
        autopct="%1.1f%%",
        startangle=140,
        pctdistance=0.8,
    )
    for t in autotexts:
        t.set_fontsize(10)
        t.set_fontweight("bold")

    ax.set_title(f"Distribution: {col}", fontsize=14, fontweight="bold", color="#16213e")

    plt.tight_layout()
    plt.savefig(str(output_path), dpi=150, bbox_inches="tight")
    plt.close()
    return output_path


def _render_line(data: list[dict], output_path: Path) -> Path:
    """Génère un graphique linéaire."""
    numeric_cols = _detect_numeric_columns(data)
    if not numeric_cols:
        return _render_placeholder(output_path, "line")

    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor("#fafafa")

    for i, col in enumerate(numeric_cols[:3]):
        values = [float(row.get(col, 0)) for row in data[:30]]
        ax.plot(values, color=COLORS[i % len(COLORS)], linewidth=2, label=col, marker="o", markersize=4)

    ax.legend(fontsize=10)
    ax.set_title("Tendances", fontsize=14, fontweight="bold", color="#16213e")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(str(output_path), dpi=150, bbox_inches="tight")
    plt.close()
    return output_path


def _render_placeholder(output_path: Path, chart_type: str) -> Path:
    """Placeholder quand les données ne permettent pas le type demandé."""
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.text(0.5, 0.5, f"Données insuffisantes pour {chart_type}",
            ha="center", va="center", fontsize=14, color="#888")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    plt.savefig(str(output_path), dpi=100)
    plt.close()
    return output_path


RENDERERS = {
    "bar": _render_bar,
    "pie": _render_pie,
    "line": _render_line,
}


async def render_charts(data: list[dict], chart_types: list[str],
                        output_dir: Path) -> list[Path]:
    """Génère tous les graphiques demandés."""
    charts = []
    for i, chart_type in enumerate(chart_types):
        output_path = output_dir / f"chart_{i}.png"
        renderer = RENDERERS.get(chart_type, _render_bar)
        renderer(data, output_path)
        charts.append(output_path)
    return charts
