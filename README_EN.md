# hydro-rainfall

[中文](README.md) | **English**

Rainfall-runoff calculator for lake irrigation demand — processes 228 lakes across 15 partitions.

[![Live Demo](https://img.shields.io/badge/Live_Demo-hydro--rainfall.tianlizeng.cloud-blue?style=for-the-badge)](https://hydro-rainfall.tianlizeng.cloud)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-yellow?style=for-the-badge)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

---

### Try it now — no install needed

**https://hydro-rainfall.tianlizeng.cloud**

---

![hydro-rainfall demo](docs/screenshots/demo.png)

---

## What can hydro-rainfall do?

| Feature | Description |
|---------|-------------|
| **6-step pipeline** | partition → area → rainfall coefficient → intake → deduction → merge |
| **228 lakes / 15 partitions** | Pre-loaded spatial dataset, no manual upload needed |
| **Daily → hourly conversion** | Converts daily precipitation data into hourly time series |
| **Batch processing** | Upload multi-file ZIP for bulk computation |
| **Excel export** | Download results per lake with full breakdowns |

## Install

```bash
git clone https://github.com/zengtianli/hydro-rainfall.git
cd hydro-rainfall
pip install -r requirements.txt
```

With [uv](https://docs.astral.sh/uv/), run `uv sync` instead. It follows `.python-version` (3.13) by default; add `--python 3.10` to use the 3.10 / 3.11 you already have.

## Quick Start

```bash
python comb0609.py
```

Reads `static_PYLYSCS.txt` and `input_*.txt` from the current directory, runs the six steps, and writes `data/final.csv` and `output_GHJYL.txt`. If the input files live elsewhere, pass that directory: `python comb0609.py /path/to/dir`.

## Self-host

```bash
git clone https://github.com/zengtianli/hydro-rainfall.git
cd hydro-rainfall
pip install -r requirements.txt
python comb0609.py
```

Or use the hosted version: **https://hydro-rainfall.tianlizeng.cloud**

## Requirements

- Python 3.10 or newer (every commit is tested on 3.10, 3.11, 3.12 and 3.13)
- pandas 2.2 or newer

## License

MIT
