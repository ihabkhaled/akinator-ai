# reportly

A small CLI that reads a CSV of usage events and prints a summary report.

## Usage

```bash
python src/report.py events.csv
```

The CSV needs a `team` column and a `kind` column, one row per event.

## Development

```bash
python -m pytest tests -q
```
