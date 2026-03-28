# 🌧️ Hydro Rainfall — Rainfall Runoff Calculator

[![GitHub stars](https://img.shields.io/github/stars/zengtianli/hydro-rainfall)](https://github.com/zengtianli/hydro-rainfall)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.36+-FF4B4B.svg)](https://streamlit.io)
[![Live Demo](https://img.shields.io/badge/Live%20Demo-hydro--rainfall.tianlizeng.cloud-brightgreen)](https://hydro-rainfall.tianlizeng.cloud)

Rainfall runoff calculator for lake irrigation demand — 6-step pipeline from partition processing to final output.

![screenshot](docs/screenshot.png)

## Features

- **6-step pipeline** — partition → area → rainfall coefficient → intake → deduction → merge
- **228 lakes across 15 partitions** — complete coverage of the study area
- **Hourly resolution** — convert daily data to hourly time series
- **Web + CLI** — Streamlit interface for interactive use, CLI for batch processing
- **Built-in sample data** — try it instantly with included example files

## Quick Start

```bash
git clone https://github.com/zengtianli/hydro-rainfall.git
cd hydro-rainfall
pip install -r requirements.txt
streamlit run app.py
```

## CLI Usage

```bash
# Run all steps
python comb0609.py

# Run specific steps
python comb0609.py --steps partition area ggxs merge_final
```

## Input Files

| File | Format | Description |
|------|--------|-------------|
| `static_PYLYSCS.txt` | Key-value | Partition and lake static configuration |
| `input_FQNNGXL.txt` | TSV | Daily rainfall coefficients (15 partitions) |
| `input_GHJYL.txt` | TSV | River runoff data (17 channels) |
| `input_YSH_GH.txt` | TSV | Water user to lake mapping |
| `input_YSH.txt` | TSV | Water intake volume per company |

## Output

- `data/final.csv` — hourly results for all 228 lakes
- `output_GHJYL.txt` — final output in TSV format

## Deploy (VPS)

```bash
git clone https://github.com/zengtianli/hydro-rainfall.git
cd hydro-rainfall
pip install -r requirements.txt
nohup streamlit run app.py --server.port 8518 --server.headless true &
```

## Hydro Toolkit Plugin

This project is a plugin for [Hydro Toolkit](https://github.com/zengtianli/hydro-toolkit) and can also run standalone. Install it in the Toolkit by pasting this repo URL in the Plugin Manager. You can also **[try it online](https://hydro-rainfall.tianlizeng.cloud)** — no install needed.

## License

MIT
