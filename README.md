# hydro-rainfall

**中文** | [English](README_EN.md)

湖泊灌区降雨径流计算工具——覆盖 15 个分区、228 个湖泊的径流推算。

[![在线演示](https://img.shields.io/badge/在线演示-hydro--rainfall.tianlizeng.cloud-blue?style=for-the-badge)](https://hydro-rainfall.tianlizeng.cloud)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-yellow?style=for-the-badge)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

---

### 无需安装，立即体验

**https://hydro-rainfall.tianlizeng.cloud**

---

![hydro-rainfall demo](docs/screenshots/demo.png)

---

## 功能一览

| 功能 | 说明 |
|------|------|
| **6 步处理流程** | 分区 → 面积 → 径流系数 → 引水量 → 扣损 → 合并 |
| **228 个湖泊 / 15 个分区** | 内置空间数据集，无需手动上传 |
| **日→时转换** | 将日降水数据转换为逐小时时序 |
| **批量处理** | 上传 ZIP 压缩包批量计算 |
| **Excel 导出** | 按湖泊下载含完整明细的计算结果 |

## 安装

```bash
git clone https://github.com/zengtianli/hydro-rainfall.git
cd hydro-rainfall
pip install -r requirements.txt
```

使用 [uv](https://docs.astral.sh/uv/) 时运行 `uv sync` 即可；它默认按 `.python-version` 选用 3.13，想用本机的 3.10 / 3.11 请加 `--python 3.10`。

## 快速开始

```bash
python comb0609.py
```

读取当前目录的 `static_PYLYSCS.txt` 和 `input_*.txt`，依次执行六步流程，结果写入 `data/final.csv` 与 `output_GHJYL.txt`。输入文件放在别处时把目录作为参数：`python comb0609.py /path/to/dir`。

## 自托管

```bash
git clone https://github.com/zengtianli/hydro-rainfall.git
cd hydro-rainfall
pip install -r requirements.txt
python comb0609.py
```

或直接使用托管版本：**https://hydro-rainfall.tianlizeng.cloud**

## 环境要求

- Python 3.10 及以上（每次提交在 3.10、3.11、3.12、3.13 上自动测试）
- pandas 2.2 及以上

## License

MIT
