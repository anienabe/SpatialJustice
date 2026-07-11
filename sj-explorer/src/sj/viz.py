import esda
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
from splot.esda import lisa_cluster

def add_caption(fig, text: str):
    """
    Adds a short explanation at the bottom of a figure.
    Kept as one helper so every plot explains itself the same way.
    """
    fig.text(
        0.5, 0.02, text,
        ha="center", va="bottom",
        fontsize=9, style="italic", color="dimgrey", wrap=True,
    )
    fig.subplots_adjust(bottom=0.12)

def plot_lisa(gdf, lisa: esda.Moran_Local, title: str):
    """
    Plots a LISA cluster map from a precomputed Moran_Local object.

    Args:
        gdf:   GeoDataFrame with geometry.
        lisa:  A precomputed esda.Moran_Local object from analysis.py.
        title: Title for the map.

    Returns:
        A matplotlib Figure object.
    """
    fig, ax = lisa_cluster(lisa, gdf, p=0.05)
    ax.set_title(title, fontsize=14)

    add_caption(
        fig,
        "Colored areas are statistically significant spatial clusters (p < 0.05):\n"
        "High-High = a high-value area surrounded by high-value neighbors, "
        "Low-Low = a low-value area surrounded by low-value neighbors.\n"
        "High-Low / Low-High mark outliers that differ from their neighbors. Grey = not significant.",
    )
    return fig

def plot_swm_weighted(gdf, w, title: str):
    """
    Visualizes a weighted W object — line thickness encodes edge weight.
    Use this for the socioeconomic W to show varying connection strength.
    """
    fig, ax = plt.subplots(figsize=(8, 8))
    gdf.plot(ax=ax, color="lightgrey", edgecolor="white", linewidth=0.5)

    centroids = gdf.geometry.centroid
    cx = centroids.x.values
    cy = centroids.y.values

    # collect all weights to normalize line thickness across the full range
    all_weights = [weight for weights in w.weights.values() for weight in weights]
    max_weight = max(all_weights)
    min_weight = min(all_weights)
    weight_range = max_weight - min_weight if max_weight != min_weight else 1.0

    for i, neighbors in w.neighbors.items():
        for j, weight in zip(neighbors, w.weights[i]):
            # normalize weight to [0, 1] relative to the actual range in this W
            normalized = (weight - min_weight) / weight_range
            contrast = normalized ** 2
            # I tweeked the contrast, and linewidth on purpuse
            ax.plot(
                [cx[i], cx[j]],
                [cy[i], cy[j]],
                color="steelblue",
                linewidth=0.3 + contrast * 12,
                alpha=0.15 + contrast * 0.85,
            )

    ax.scatter(cx, cy, color="steelblue", s=15, zorder=3)
    ax.set_title(title)
    ax.set_axis_off()

    add_caption(
        fig,
        "Each dot is a district. Lines show which districts are connected as 'neighbors'.\n"
        "Thicker, darker lines mean a stronger connection between those two districts.",
    )
    return fig

def plot_prediction_maps(gdf, table, indicator: str, year_t1: int, year_t2: int, steps: int = 1, year_step: int = None, cmap: str = "viridis"):
    """
    Plots t1, t2 and every projected future step side by side, sharing one
    colour scale across all panels so the change over time is directly
    comparable at a glance.
    Args:
        gdf:       GeoDataFrame with geometry, same index as `table`
                   (e.g. the result of merge_two_years).
        table:     DataFrame from build_prediction_table. Must contain
                   f"{indicator}_t1", f"{indicator}_t2" and
                   f"{indicator}_projection_step1" .. f"{indicator}_projection_step{steps}".
        indicator: Name of the indicator column being plotted.
        year_t1:   Year label for t1 (e.g. 2018).
        year_t2:   Year label for t2 (e.g. 2024).
        steps:     How many projection steps to show after t2.
        year_step: Year gap per projection step. Defaults to year_t2 - year_t1.
        cmap:      Matplotlib colormap name.
    Returns:
        A matplotlib Figure object.
    """
    if year_step is None:
        year_step = year_t2 - year_t1
 
    cols = [f"{indicator}_t1", f"{indicator}_t2"] + [
        f"{indicator}_projection_step{i}" for i in range(1, steps + 1)
    ]
    years = [year_t1, year_t2] + [year_t2 + i * year_step for i in range(1, steps + 1)]
 
    plot_gdf = gdf[["geometry"]].join(table[cols])

    vmin, vmax = plot_gdf[cols].min().min(), plot_gdf[cols].max().max()
    norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
 
    n = len(cols)
    fig, axes = plt.subplots(1, n, figsize=(5.5 * n, 6))
    axes = axes if n > 1 else [axes]
 
    for ax, col, year in zip(axes, cols, years):
        plot_gdf.plot(
            column=col,
            cmap=cmap,
            norm=norm,
            ax=ax,
            edgecolor="white",
            linewidth=0.3,
        )
        label = "\n(Prediction)" if year > year_t2 else ""
        ax.set_title(f"{year}{label}", fontsize=14)
        ax.set_axis_off()
 
    sm = cm.ScalarMappable(norm=norm, cmap=cmap)
    fig.colorbar(sm, ax=axes, shrink=0.7, label=indicator)
    fig.suptitle(f"{indicator} — Prediction", fontsize=16)

    return fig

def plot_change_map(gdf, table, indicator: str, year_t1: int, year_t2: int, relative: bool = False, cmap: str = "RdBu_r"):
    """
    Plots the actual change in `indicator` between t1 and t2 as a single
    choropleth map. Uses a diverging colormap centered at zero so increases
    and decreases are visually distinguishable on the same scale.
    Args:
        gdf:       GeoDataFrame with geometry, same index as `table`.
        table:     DataFrame from build_prediction_table. Must contain
                   f"{indicator}_t1" and f"{indicator}_t2".
        indicator: Name of the indicator column.
        year_t1:   Year label for t1 (e.g. 2018).
        year_t2:   Year label for t2 (e.g. 2024).
        relative:  If True, shows percentage change instead of absolute
                   difference.
        cmap:      Diverging matplotlib colormap name.
    Returns:
        A matplotlib Figure object.
    """
    col_t1, col_t2 = f"{indicator}_t1", f"{indicator}_t2"
    plot_gdf = gdf[["geometry"]].join(table[[col_t1, col_t2]])
 
    if relative:
        change_col = f"{indicator}_pct_change"
        plot_gdf[change_col] = (plot_gdf[col_t2] - plot_gdf[col_t1]) / plot_gdf[col_t1] * 100
        legend_label = f"{indicator} — Change (%)"
    else:
        change_col = f"{indicator}_change"
        plot_gdf[change_col] = plot_gdf[col_t2] - plot_gdf[col_t1]
        legend_label = f"{indicator} — Change (absolute)"
 
    # diverging colormap centered at zero, so growth and shrinkage are symmetric around the same midpoint, regardless of which direction has the larger swing
    max_abs = plot_gdf[change_col].abs().max()
    norm = mcolors.TwoSlopeNorm(vmin=-max_abs, vcenter=0, vmax=max_abs)
 
    fig, ax = plt.subplots(figsize=(8, 8))
    plot_gdf.plot(
        column=change_col,
        cmap=cmap,
        norm=norm,
        ax=ax,
        edgecolor="white",
        linewidth=0.3,
        legend=True,
        legend_kwds={"label": legend_label, "shrink": 0.7},
    )
    ax.set_title(f"Change {indicator}: {year_t1} → {year_t2}", fontsize=14)
    ax.set_axis_off()

    explain = "shows the percentage change" if relative else "shows the absolute change"
    add_caption(
        fig,
        f"This map {explain} in '{indicator}' between {year_t1} and {year_t2}.\n"
        "Blue = increase, red = decrease (white = little to no change).",
    )
    return fig

    return fig


def plot_composite_map(gdf, table, id_col: str, title: str, cmap: str = "Reds"):
    """
    Choropleth map of the final composite score, with the rank number
    annotated at each district's centroid.

    Args:
        gdf:    GeoDataFrame with geometry and id_col (e.g. the t2 polygons).
        table:  DataFrame from build_multi_year_score. Must contain
                "final_score" and "rank", indexed by the same values as id_col.
        id_col: Column name of the district ID in gdf.
        title:  Map title.
        cmap:   Matplotlib colormap name.
    Returns:
        A matplotlib Figure object.
    """
    plot_gdf = gdf.set_index(id_col)[["geometry"]].join(table[["final_score", "rank"]], how="inner")

    fig, ax = plt.subplots(figsize=(8, 8))
    plot_gdf.plot(
        column="final_score",
        cmap=cmap,
        ax=ax,
        edgecolor="white",
        linewidth=0.3,
        legend=True,
        legend_kwds={"label": "Composite Score (1 = highest need for action)", "shrink": 0.7},
    )

    for _, row in plot_gdf.iterrows():
        if row.geometry is not None:
            c = row.geometry.centroid
            ax.annotate(str(int(row["rank"])), (c.x, c.y), ha="center", va="center", fontsize=7, color="black")

    ax.set_title(title, fontsize=14)
    ax.set_axis_off()
    return fig


def plot_ranking_bar(table, top_n: int = 10, title: str = "Ranking — highest need for action"):
    """
    Horizontal bar chart of the top_n districts with the highest (worst)
    final_score, worst district at the top.

    Args:
        table: DataFrame from build_multi_year_score, sorted descending by
               final_score, with a "name" column.
        top_n: How many districts to show.
        title: Chart title.
    Returns:
        A matplotlib Figure object.
    """
    subset = table.head(top_n).iloc[::-1]

    fig, ax = plt.subplots(figsize=(8, max(4, 0.4 * len(subset))))
    ax.barh(subset["name"], subset["final_score"], color="firebrick")
    ax.set_xlabel("Composite Score (1 = highest need for action)")
    ax.set_title(title, fontsize=14)
    fig.tight_layout()
    return fig

