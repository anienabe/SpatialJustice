# SpatialJustice

Our project for the course _Spatial Justice and Support Decision Systems_.

## Authors

Anke Nienaber, Lea Heming, Julia Ilchmann

## Motivation

Societies and cities are constantly changing and evolving due to factors such as migration, economic developments, and political decisions. While many working-age adults have the financial resources, mobility, and freedom to adapt to these changes by moving within a city or relocating elsewhere, not all population groups have the same opportunities.

Children and older people are particularly affected, as they often have a stronger dependence on their immediate surroundings and fewer possibilities to overcome spatial disadvantages on their own. Safe, accessible, and supportive environments are therefore essential for their participation, well-being, and quality of life.

As societies continue to age and the needs of younger generations shape the future of cities, ensuring spatial justice becomes increasingly important. Cities need to understand and address the different requirements of their residents to create fair living conditions across all districts.

## Justice Concept

Our support decision system is based on two Justice Concepts.

First, **John Rawls' Theory of Justice (1971)** [1] says that social and economic inequalities is only justified, if they bring the greatest benefit to the least advantaged people of our society A fair equality of opportunity is already ensured.

Also **Iris Marion Young in Justice and the Politics of Difference (1990)**[2] says that it is not good to think from justice only in a distributive kind of manner, so just asking who owns how much (number of daycares, care facilities per district). This does not show the structures and processes that create this distribution.

Our Composite Index shows where there is inequality in the infrastructure, not how it happened. The ranking is meant to help make decisions based on the idea that the most disadvantaged areas should be prioritised. This project does not look at the reasons for this.

## Project Idea and Goals

We want to design a decision support system for the city of Dortmund. Certain factors determine and contribute to inequalities in vulnerable groups. We analyse these factors to develop a support decision system where social stress might occur, giving the opportunity to recognize need for political decision actions in Dortmund's districts to reduce inequality and provide equal opportunities.
For a just city.

That's why we include socioeconomic factors from all 170 districts of Dortmund as well as the number of facilities (e.g. kindergartens, day care) in each district.
The following image shows our preliminary questions that will be analyzed with our Spatial Decision Support system which includes a spatial weight matrix.
For each question we plan to create a district ranking (e.g. top ten) to identify districts for the specific question and to find out if there are districts which seem to be inequal across multiple indicators.

## Project Overview

<img width="680" height="909" alt="Bildschirmfoto 2026-06-11 um 10 22 48" src="https://github.com/user-attachments/assets/4ace6b01-376d-4ee6-8af6-ebdfd7a52188" />

## Analytical Solution

## Data Sources

The social factors for Dortmund are taken from the

- [Statistikatlas Dortmund - 2018](https://www.dortmund.de/dortmund/projekte/rathaus/verwaltung/dortmunder-statistik/downloads/215_-_statistikatlas_-_2019.pdf)

- [Statistikatlas Dortmund - 2024](https://statistikportal.dortmund.de/#subpage_statistikatlas)

The Point data is from the [Open Data Portal Dortmund](https://open-data.dortmund.de/pages/start/)

The healthcare facilities are retrevied from OSM

## Project Structure

```
sj-explorer/
├── .venv
├── data
├── reports
├── preprocessing
|   └── output
├── src/sj
|   ├── __pycache__
|   ├── weights
|   |    ├── __init__.py
|   |    ├── contiguity.py
|   |    ├── distance.py
|   |    └── socioeconomic.py
|   ├── analysis.py
|   ├── composite.py
|   ├── io.py
|   ├── main.py
|   ├── points.py
|   ├── prediction.py
|   ├── report.py
|   ├── scoring.py
|   └── viz.py
├── pyproject.toml
├── requirements.md
└── README.md
```

## Quickstart

**Prerequisites:** [uv](https://docs.astral.sh/uv/) must be installed.

```bash
# Clone the repository
git clone https://github.com/anienabe/SpatialJustice

# Navigate to the frontend
cd sj-explorer

# Run the correlation app
uv run sj correlation

# Run with point data
# required: your_pointdata.geojson
# required: your_data_column
uv run sj correlation -v "your_pointdata_count" -s "your_data_column" -p "your_pointdata" -w "rook" -w "socio"

# What happens: by commanding -p "your_pointdata" the script in the back is running that counts the points per district. Result is a .geojson file which is called by -v "your_pointdata_count" as analysis variable.
# you can also use "your_pointdata_count" as socio index -s.

# Run the prediction app
# you can also use different flags.
uv run sj predict

## Run the scoring app
uv run sj score
```

## Flags and Methods

explanations and tables for each?

command main: what, why, flags as input, output

- for correlations between two factors
- LISA maps

command predict: what, why, flags as input, output

- we have two years, let's predict the next

command score: what, why, flags as input, output

- composite score to find out what does it mean for the whole city
- where is the biggest need to act (for policy makers)

## Our Results

Our questions
Our commands in console
Our outputs
Our discussion

## Our "Decision" resulting from our analysis

e.g. district A, B, C need action to make life more just for children.
e.g. district X, Y, Z need action to make life more just for older people.

### Data preprocessing (Section needs to be moved somewhere???)

As a first step, the geodata with the boundaries of each of Dortmund's Unterbezirke (sub-districts) needs to be downloaded and converted to a GeoJSON. All the needed statistical information of social factors have to be converted from plain text in a pdf (year 2018) to a csv format. This can then be joined with the boundaries into a larger file, which is subsequently converted into a GeoJSON format.

As a second step, the same data categories were collected, extracted and put in a csv. The data has to undergo some changes due to the aggregation of administrative districts over the period. After that, it was then joined with the administrative boundaries and converted into a GeoJSON format.

### Spatial Weight Matrix (Section needs to be moved/ integrated in flags and methods)

First we implemented the spatial weight types (rook, queen, knn, distance, social). After that we defined the Moran's I functionality, so now the global and local Moran's I can be computed.

In the main.py we defined with the help of typer the flags for "filename", "analysis_variable", "socio_index", "distance_threshold", "weights". So the users can define their own dataset to be used as well as the social indicators and weights used. The --help flag describes the possible options.

For the visualization of the Spatial Weight Matrix and the Moran's I the viz.py and report.py has the funcions.

Points extraction: To include infrastructural elements such as kindergartens or day care facilities, the point data was collected from Dortmund data portal and OSM. To use them in the spatial weight matrix a script was written to extract and count the points per districts. The counting is saved as geojson and can be used as flag in the console.

### Prediction (Section needs to be moved/ integrated in flags and methods)

For the prediction workflow, two GeoJSON files for different time points are loaded and merged, so that each district has values for both years available in one table. A spatial lag is then computed for each district using the spatial weight matrix, representing the weighted average of the indicator across all neighbouring districts.

A linear regression model is fitted with two predictors: ![formula](<https://latex.codecogs.com/svg.image?\color{white}\hat{y}_{t2}=\beta_0+\beta_1\cdot%20y_{t1}+\beta_2\cdot\text{lag}(y_{t1})>)

the district's own value at t1 and its spatial lag at t1. The target variable is the value at t2. This way the model captures how much of a district's development can be explained by its own starting point versus the influence of its surroundings. R², both coefficients, and the residuals per district are logged and saved to a CSV.

The trained model can be applied recursively for one or more steps into the future, using each projection as the input for the next step. In the main.py the predict command was defined with the help of typer with different flags. The --help flag describes the possible options.

For the visualization, maps are generated for each time point alongside a change map, saved to the reports folder.

### Composite Score and Ranking (Section needs to be moved/ integrated into flags, at least partly)

The score command combines a number of socioeconomic indicators into a single normalized need-for-action score per district, ranging from 0 (best situation) to 1 (highest need for action). Each indicator is min-max normalized across all districts and given a direction, higher_worse (e.g. child poverty rate) or lower_worse (e.g. living space per person), so that a higher score always means a worse situation regardless of the indicator's original scale. The final composite score is the weighted mean of all normalized indicators.

Point data layers (e.g. kindergartens, day care facilities) can be included via the --points flag and are automatically counted per district and treated as lower_worse indicators.

The --scope flag controls which time points are included in the score:

- current uses only the most recent dataset (e.g. 2024)
- historical combines past and current values, weighted by --weight-past and --weight-current
- full additionally includes a projected future year (e.g. 2030) via the spatial lag regression model from the predict workflow, weighted by --weight-future

For historical and full, all indicators are normalized across all included time points on a shared scale, so scores remain directly comparable across years. The final score is the weighted mean of the per-year composite scores, with weights normalized automatically so they don't need to sum to 1.

Districts that rank among the worst --flag-top-n for multiple indicators simultaneously are flagged as consistently disadvantaged — meaning their situation is not driven by a single outlier indicator but by structural, multidimensional deprivation.

Outputs saved to the reports folder include a ranked CSV table, a choropleth map with rank annotations, a bar chart of the worst districts, and a flagging table of consistently disadvantaged districts.

## Functional, Technical, and Non-Functional Requirements

See [Requirements](sj-explorer/requirements.md) for more details.

## License

This project is licensed under the [MIT License](LICENSE).

## References
[1] Rawls, J. (1971). A theory of justice (Rev. ed.). Harvard University Press.
[2] Young, I. M. (1990). Justice and the politics of difference. Princeton University Press.
