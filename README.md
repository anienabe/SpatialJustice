# SpatialJustice

Our project for the course *Spatial Justice and Support Decision Systems*.

## Authors

Anke Nienaber, Lea Heming, Julia Ilchmann

## Project Overview

| Criteria | Weight | Our Approach |
|---|---|---|
| *Concept & Problem Relevance* | 25 % | Structural problems in supporting elderly people and children in Dortmund districts |
| *Analytical Solution* | 40 % | Moran's I with spatial weight matrices (rook, queen, knn, distance band) to identify if neighbouring districts are spatially correlated + predictions |
| *Decision Support* | 20 % | Composite index per administrative district → ranking and justice system |
| *Software Quality* | 15 % | Versioned on [GitHub](https://github.com/anienabe/SpatialJustice), inline comments and documentation |
| *Innovation* | Bonus % | Prediction models and additional spatial methods beyond course scope |

## Project Idea and Goals

We want to design a decision support system for the city of Dortmund. Certain factors determine and contribute to inequalities in vulnerable groups. We analyse these factors to develop a support decision system where social stress might occur, giving the opportunity to recognize need for political decision actions in Dortmund's districts to reduce inequality and provide equal opportunities.
For a just city.

That's why we include socioeconomic factors from all 170 districts of Dortmund as well as the number of facilities (e.g. kindergartens, day care) in each district.
The following image shows our preliminary questions that will be analyzed with our Spatial Decision Support system which includes a spatial weight matrix.
For each question we plan to create a district ranking (e.g. top ten) to identify districts for the specific question and to find out if there are districts which seem to be inequal across multiple indicators.

<img width="680" height="909" alt="Bildschirmfoto 2026-06-11 um 10 22 48" src="https://github.com/user-attachments/assets/4ace6b01-376d-4ee6-8af6-ebdfd7a52188" />

## Data Sources

The social factors for Dortmund are taken from the Statistikatlas Dortmund (source: )

OpenStreetMap provides data for schools, kindergartens, elerly care facilities etc. 

## Method
- spatial weight matrix ----> ranking
- values of 2018 ----> values of 2024 ----> prediction/ trend

### Data preprocessing

As a first step, the geodata with the boundaries of each of Dortmund's Unterbezirke (sub-districts) needs to be downloaded and converted to a GeoJSON. All the needed statistical information of social factors have to be converted from plain text in a pdf (year 2018) to a csv format. This can then be joined with the boundaries into a larger file, which is subsequently converted into a GeoJSON format.
As a second step, the same data categories were collected, extracted and put in a csv. The data has to undergo some changes due to the aggregation of administrative districts over the period. After that, it was then joined with the administrative boundaries and converted into a GeoJSON format.
To include infrastructural elements such as kindergartens or day care facilities, the point data was collected from Dortmund data portal and OSM. To use them in the spatial weight matrix a script was written to extract and count the points per districts. At the moment, the output is a data table in a csv-format and will probably converted to a GeoJSON format soon. 

### Spatial Weight Matrix



## Project Structure

```
spatialjustice/
├── sj-frontend/  # Frontend application, tbd
├── .venv
├── data
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
|   └── main.py
├── pyproject.toml
└── README.md
```

## Quickstart

**Prerequisites:** [uv](https://docs.astral.sh/uv/) must be installed.

```bash
# Clone the repository
git clone https://github.com/anienabe/SpatialJustice

# Navigate to the frontend
cd sj-explorer

# Run the app
uv run sj
```

## Important Notes

## License

This project is licensed under the [MIT License](LICENSE).
