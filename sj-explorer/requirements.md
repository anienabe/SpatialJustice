# Requirements Document – SpatialJustice

Goal: A spatial decision support system  built for Dortmund's sub-districts (2018 & 2024)

## 1. Functional Requirements (FR)

### FR-1 — Data Preprocessing (generalized)
| ID | Requirement |
|----|-------------|
| FR-1.1 | Read district/region boundaries for a given city and convert them to GeoJSON |
| FR-1.2 | Extract/read socioeconomic data for a given year and source format (PDF for 2018, portal export for 2024, etc.) and convert it to CSV |
| FR-1.3 | Join socioeconomic CSV data with boundaries (handling administrative reclassifications between years) and export as GeoJSON |
| FR-1.4 | Read point data (e.g. kindergartens, day care) from open data portals / OSM for a given city, count/aggregate points per district, and export as CSV/GeoJSON |
| FR-1.5 | Generalize all of the above so city and year are parameters rather than hard-coded values (Dortmund 2018/2024 remain the default/example dataset) |

### FR-2 — Spatial Weight Matrices
| ID | Requirement |
|----|-------------|
| FR-2.1 | Compute contiguity-based weight matrices: **Rook** and **Queen** |
| FR-2.2 | Compute distance-based weight matrices: **k-nearest neighbours (knn)** and **distance band**, with configurable k / threshold |
| FR-2.3 | Compute a **socioeconomic** weight matrix based on social indicators |

### FR-3 — Spatial Autocorrelation Analysis
| ID | Requirement |
|----|-------------|
| FR-3.1 | Compute **Global** and **Local Moran's I (LISA)** for a chosen indicator and weight matrix |
| FR-3.2 | Run significance tests (permutation/p-values) and classify cluster types (High-High, Low-Low, High-Low, Low-High / hot spots, cold spots, outliers) |

### FR-4 — Composite Index & Ranking
| ID | Requirement |
|----|-------------|
| FR-4.1 | Combine multiple socioeconomic indicators into a composite index per district |
| FR-4.2 | Rank districts per individual indicator and per composite index (e.g. top 10 most affected) |
| FR-4.3 | Identify districts that are consistently disadvantaged across multiple indicators |

### FR-5 — Trend & Prediction Analysis
| ID | Requirement |
|----|-------------|
| FR-5.1 | Compare two datasets/years per district (delta/change) |
| FR-5.2 | Derive a trend/prediction for future development per indicator and district |
| FR-5.3 | Expose this as its own `predict` command, defaulting to Dortmund 2018 vs. 2024, but accepting any two arbitrary datasets/years/cities as input |

### FR-6 — CLI (`main.py`, Typer)
| ID | Requirement |
|----|-------------|
| FR-6.1 | Analysis command with its flags: `filename`, `analysis_variable`, `socio_index`, `distance_threshold`, `weights` (`--help` documents all options) |
| FR-6.2 | Flag to `main` to support the generalized (city/year-agnostic) workflow from FR-1.5 |
| FR-6.3 | Separate `predict` command/subcommand implementing FR-5.3 (own parameters for the two datasets/years/cities to compare, with Dortmund 2018/2024 as defaults) |

### FR-7 — Visualization & Reporting
| ID | Requirement |
|----|-------------|
| FR-7.1 | Render choropleth maps, weight-matrix/connectivity visualizations, Moran scatterplots, and LISA cluster maps |
| FR-7.2 | Generate an automated report (PDF/HTML) summarizing the results of a run, including prediction results from FR-5 |

---

## 2. Technical Requirements (TR)

| Functional area | Implementation |
|---|---|
| Project setup | Python 3.x, `pyproject.toml`, package manager **uv** |
| CLI (incl. flag & `predict` command) | **typer** — `main.py` as a multi-command app (`@app.command()` for the analysis command and the  `predict` command); shared options factored out so both commands can take city/year parameters |
| Geodata & tabular data | **geopandas**, **pandas**, **numpy** |
| Point data acquisition | **geopandas**, **pandas**; `preprocessing/extract_point_data.py`, generalized to accept city/source parameters |
| Spatial weight matrices | **libpysal** (`Rook`, `Queen`, `KNN`, `DistanceBand`); custom socioeconomic weighting in `src/weights/socioeconomic.py` |
| Moran's I (global/local) | **esda** (`esda.Moran`, `esda.Moran_Local`) in `src/analysis.py` |
| Composite index & ranking | custom logic (e.g. normalized weighted sum) in `src/analysis.py` |
| Trend/prediction (`predict` command) | **scikit-linear** for trend extrapolation between two arbitrary datasets; logic in `src/analysis.py`, exposed via the CLI command |
| Visualization & reporting | **matplotlib** in `src/viz.py`; **pathlib** in `src/report.py` |
| Testing & versioning | Git/GitHub |

---

## 3. Non-Functional Requirements
- **Reproducibility:** same parameters → same result
- **Extensibility:** new weighting types, indicators, cities, or years should be addable with minimal code changes 
- **Documentation:** README kept up to date
- **Performance:** acceptable runtime, even across all 170 Dortmund districts