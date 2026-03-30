        # hydro-rainfall

        **English** | [中文](README_CN.md)

        Rainfall-runoff calculator for lake irrigation demand — processes 228 lakes across 15 partitions.

        [![Live Demo](https://img.shields.io/badge/Live_Demo-hydro--rainfall.tianlizeng.cloud-blue?style=for-the-badge)](https://hydro-rainfall.tianlizeng.cloud)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-yellow?style=for-the-badge)](https://python.org)
        [![License: MIT](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

        ---

        ---

### Try it now — no install needed

**https://hydro-rainfall.tianlizeng.cloud**

---

![hydro-rainfall demo](docs/screenshots/demo.svg)

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

        ## Quick Start

        ```bash
        streamlit run app.py
        ```

        ## Self-host

```bash
git clone https://github.com/zengtianli/hydro-rainfall.git
cd hydro-rainfall
pip install -r requirements.txt
streamlit run app.py
```

Or use the hosted version: **https://hydro-rainfall.tianlizeng.cloud**

## Requirements

        - Python 3.9+
        - Streamlit 1.36+

        ## License

        MIT
