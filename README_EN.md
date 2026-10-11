# hydro-rainfall

[中文](README.md) | **English**

Hourly series for lake units in a plain river network: per-partition daily values are spread by area over 225 lake units in 15 partitions, water intake is computed per lake unit, and the result is deducted from the lake series. A command-line script with an optional HTTP API.

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-yellow?style=for-the-badge)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

## Install

```bash
git clone https://github.com/zengtianli/hydro-rainfall.git
cd hydro-rainfall
pip install -r requirements.txt
```

With [uv](https://docs.astral.sh/uv/), run `uv sync` instead. It follows `.python-version` (3.13) by default; add `--python 3.10` to use the 3.10 / 3.11 you already have.

## Run

```bash
python comb0609.py
```

Reads `static_PYLYSCS.txt` and `input_*.txt` from the current directory, runs the six steps, and writes `data/final.csv` and `output_GHJYL.txt`. If the input files live elsewhere, pass that directory: `python comb0609.py /path/to/dir`. Use `--steps partition area` to run only some steps.

## Input files

| File | Content |
|------|---------|
| `static_PYLYSCS.txt` | The lake units of each of the 15 partitions, with their areas |
| `input_FQNNGXL.txt` | Daily values per partition; columns are the Chinese partition names |
| `input_YSH.txt` | Daily and hourly intake per water user |
| `input_YSH_GH.txt` | Which lake unit each water user belongs to |
| `input_GHJYL.txt` | Hourly series per lake unit; the last step deducts from it |

## The six steps

| Step | What it does | Output |
|------|--------------|--------|
| 1 partition | Splits `static_PYLYSCS.txt` into one file per partition | `data/01csv/` |
| 2 area | Collects each lake unit's area and each partition's total area | `data/02area/` |
| 3 rainfall coefficient | Spreads the daily partition value over 24 hours, converts it to millimetres by partition area, and writes it for every lake unit of that partition | `data/03ggxs/` |
| 4 intake | Converts each user's hourly intake to millimetres by the area of its lake unit | `data/03intake/` |
| 5 deduction | Per lake unit and hour: the step 3 value plus the step 4 intake total | `data/04deduct/` |
| 6 merge | `input_GHJYL.txt` minus the step 3 value gives the final series | `data/final.csv`, `output_GHJYL.txt` |

`final.csv` currently deducts the step 3 result only. The intake and the totals from steps 4 and 5 are kept in `data/04deduct/` and are not merged into `final.csv`.

Partition file names (such as `01_NSPYQ(南沙)`) and the columns of `input_FQNNGXL.txt` (such as `南沙平原区`) are joined by `partition_map.py`. If they do not line up the program stops with an error; it does not substitute zeros.

## Bundled sample

The inputs in the repository root and in `data/sample/` demonstrate the format and the flow: `input_FQNNGXL.txt` has 100 for every partition on the single row 2025/05/14, which is an example value, not measured data; all other inputs are zero. The results committed under `data/` come from this sample.

## HTTP API (optional)

```bash
uvicorn api:app --host 127.0.0.1 --port 8618
```

- `GET /api/sample` downloads the sample inputs as a ZIP
- `POST /api/compute` takes a ZIP with the five input files and returns a result ZIP; with the form field `format=json` it returns the per-step file lists and the result tables

Browser cross-origin access is limited to local addresses by default; list other origins, comma separated, in `RAINFALL_CORS_ORIGINS`.

## Tests

```bash
python -m unittest discover -s tests -v
```

## Requirements

- Python 3.10 or newer (every commit is tested on 3.10, 3.11, 3.12 and 3.13)
- pandas 2.2 or newer

## License

MIT
