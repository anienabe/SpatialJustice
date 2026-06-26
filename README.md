# SpatialJustice

Our project for the course _Spatial Justice and Support Decision Systems_.

## Authors

Anke Nienaber, Lea Heming, Julia Ilchmann

## Project Overview

| Criteria                      | Weight  | Our Approach                                                                                                                                          |
| ----------------------------- | ------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| _Concept & Problem Relevance_ | 25 %    | Structural problems in supporting elderly people and children in Dortmund districts                                                                   |
| _Analytical Solution_         | 40 %    | Moran's I with spatial weight matrices (rook, queen, knn, distance band) to identify if neighbouring districts are spatially correlated + predictions |
| _Decision Support_            | 20 %    | Composite index per administrative district → ranking and justice system                                                                              |
| _Software Quality_            | 15 %    | Versioned on [GitHub](https://github.com/anienabe/SpatialJustice), inline comments and documentation                                                  |
| _Innovation_                  | Bonus % | Prediction models and additional spatial methods beyond course scope                                                                                  |

## Project Idea and Goals

We want to design a decision support system for the city of Dortmund. Certain factors determine and contribute to inequalities in vulnerable groups. We analyse these factors to develop a support decision system where social stress might occur, giving the opportunity to recognize need for political decision actions in Dortmund's districts to reduce inequality and provide equal opportunities.
For a just city.

That's why we include socioeconomic factors from all 170 districts of Dortmund as well as the number of facilities (e.g. kindergartens, day care) in each district.
The following image shows our preliminary questions that will be analyzed with our Spatial Decision Support system which includes a spatial weight matrix.
For each question we plan to create a district ranking (e.g. top ten) to identify districts for the specific question and to find out if there are districts which seem to be inequal across multiple indicators.

<img width="680" height="909" alt="Bildschirmfoto 2026-06-11 um 10 22 48" src="https://github.com/user-attachments/assets/4ace6b01-376d-4ee6-8af6-ebdfd7a52188" />

## Data Sources

The social factors for Dortmund are taken from the

- [Statistikatlas Dortmund - 2018](https://www.dortmund.de/dortmund/projekte/rathaus/verwaltung/dortmunder-statistik/downloads/215_-_statistikatlas_-_2019.pdf)

- [Statistikatlas Dortmund - 2024](https://statistikportal.dortmund.de/#subpage_statistikatlas)

The Point data is from the [Open Data Portal Dortmund](https://open-data.dortmund.de/pages/start/)

The healthcare facilities are retrevied from OSM

## Method

- spatial weight matrix ----> ranking
- values of 2018 ----> values of 2024 ----> prediction/ trend

### Data preprocessing

As a first step, the geodata with the boundaries of each of Dortmund's Unterbezirke (sub-districts) needs to be downloaded and converted to a GeoJSON. All the needed statistical information of social factors have to be converted from plain text in a pdf (year 2018) to a csv format. This can then be joined with the boundaries into a larger file, which is subsequently converted into a GeoJSON format.

As a second step, the same data categories were collected, extracted and put in a csv. The data has to undergo some changes due to the aggregation of administrative districts over the period. After that, it was then joined with the administrative boundaries and converted into a GeoJSON format.

To include infrastructural elements such as kindergartens or day care facilities, the point data was collected from Dortmund data portal and OSM. To use them in the spatial weight matrix a script was written to extract and count the points per districts. At the moment, the output is a data table in a csv-format and will probably converted to a GeoJSON format soon.

### Spatial Weight Matrix

First we implemented the spatial weight types (rook, queen, knn, distance, social). After that we defined the Moran's I functionality, so now the global and local Moran's I can be computed.

In the main.py we defined with the help of typer the flags for "filename", "analysis_variable", "socio_index", "distance_threshold", "weights". So the users can define their own dataset to be used as well as the social indicators and weights used. The --help flag describes the possible options.

For the visualization of the Spatial Weight Matrix and the Moran's I the viz.py and report.py has the funcions.

Points extraction
tbd

### Prediction

Spatial-lag-based prediction for socioeconomic indicators

tbd

## Project Structure

```
sj-explorer/
├── .venv
├── data
├── reports
├── preprocessing
|   ├── extract_point_data.py
|   └── output
├── src
|   ├── __pycache__
|   ├── weights
|   |    ├── __init__.py
|   |    ├── contiguity.py
|   |    ├── distance.py
|   |    └── socioeconomic.py
|   ├── analysis.py
|   ├── io.py
|   ├── viz.py
|   ├── points.py
|   ├── prediction.py
|   ├── report.py
|   └── main.py
├── pyproject.toml
├── requirements.py
└── README.md
```

## Quickstart

**Prerequisites:** [uv](https://docs.astral.sh/uv/) must be installed.

```bash
# Clone the repository
git clone https://github.com/anienabe/SpatialJustice

# Navigate to the frontend
cd sj-explorer

# Run the main app
uv run sj main

# Run the prediction app
uv run sj prediction
```

## Important Notes

## License

This project is licensed under the [MIT License](LICENSE).
