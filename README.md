# SpatialJustice

Our project for the course *Spatial Justice and Support Decision Systems*.

## Authors

Anke Nienaber, Lea Heming, Julia Ilchmann

## Project Idea and Goals

We want to design a decision support system for the city of Dortmund. Certain factors determine and contribute to inequalities in vulnerable groups. We analyse these factors to develop a support decision system where social stress might occur, giving the opportunity to recognize need for action in Dortmund's districts.

Social stress factors include, but are not limited to:
- elderly people
    - poverty
    - opportunities

- children and their access to...
    - schools, secondary schools
    - leisure activities



## Data Sources

The social factors for Dortmund are taken from the Statistikatlas Dortmund (source: )

OpenStreetMap provides data for schools, kindergartens, elerly care facilities etc. 

## Method

tbd

### Data preprocessing

As a first step, the geodata with the boundaries of each of Dortmund's Unterbezirke (sub-districts) needs to be downloaded and converted to a GeoJSON. All the needed statistical information of social factors have to be converted from plain text in a pdf (year 2018) to a csv format. This can then be joined with the boundaries into a larger file, which is subsequently converted into a GeoJSON format.

## Project Structure

```
spatialjustice/
├── sj-frontend/  # Frontend application, tbd
├── .venv
├── data
├── src
|   ├── __pycache__
|   └── weights
├── .env.example  # Example environment 
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