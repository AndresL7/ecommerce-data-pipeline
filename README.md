# E-commerce Data Pipeline

## Overview

A data engineering project focused on building an end-to-end data pipeline using an e-commerce dataset.

The project currently focuses on data ingestion, schema validation, and data quality checks using Python and pandas.

## Current Features

- CSV ingestion using pandas
- Schema validation
- Primary key validation
- Data quality checks
- Referential integrity validation between tables

## Project Structure

```text
ecommerce-data-pipeline/
├── data/
│   └── raw/
├── src/
│   └── ingestion/
│       └── read_csv.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Technologies

- Python
- pandas
- MySQL

## Setup

Clone the repository:

```bash
git clone https://github.com/AndresL7/ecommerce-data-pipeline
cd ecommerce-data-pipeline
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the ingestion process

```bash
python3 src/ingestion/read_csv.py
```

The CSV files must be located in `data/raw/`.

## Project Status

Currently implementing the ingestion and data validation layer.

Next steps:

- Load validated data into MySQL
- Implement SQL transformations
- Develop analytical data models
- Integrate cloud storage and orchestration
