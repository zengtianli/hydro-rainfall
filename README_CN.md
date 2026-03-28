# 🌧️ 降雨径流计算

[English](README.md) | **中文**

[![GitHub stars](https://img.shields.io/github/stars/zengtianli/hydro-rainfall)](https://github.com/zengtianli/hydro-rainfall)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.36+-FF4B4B.svg)](https://streamlit.io)
[![在线演示](https://img.shields.io/badge/%E5%9C%A8%E7%BA%BF%E6%BC%94%E7%A4%BA-hydro--rainfall.tianlizeng.cloud-brightgreen)](https://hydro-rainfall.tianlizeng.cloud)

概湖灌溉需水量计算工具 — 6 步管线，从分区处理到最终输出。

![screenshot](docs/screenshot.png)

## 功能特点

- **6 步管线** — 分区→面积→降雨系数→取水→扣减→合并
- **228 个概湖，15 个分区** — 完整覆盖研究区
- **逐时精度** — 将逐日数据转为逐时序列
- **Web + CLI** — Streamlit 交互界面 + 命令行批量处理
- **内置示例数据** — 打开即用，零门槛体验

## 快速开始

```bash
git clone https://github.com/zengtianli/hydro-rainfall.git
cd hydro-rainfall
pip install -r requirements.txt
streamlit run app.py
```

## 命令行用法

```bash
# 运行所有步骤
python comb0609.py

# 运行指定步骤
python comb0609.py --steps partition area ggxs merge_final
```

## 输入文件

| 文件 | 格式 | 说明 |
|------|------|------|
| `static_PYLYSCS.txt` | 键值对 | 分区与概湖静态配置 |
| `input_FQNNGXL.txt` | TSV | 逐日降雨系数（15 分区） |
| `input_GHJYL.txt` | TSV | 河道径流数据（17 通道） |
| `input_YSH_GH.txt` | TSV | 取水户-概湖映射 |
| `input_YSH.txt` | TSV | 取水户取水量 |

## 输出

- `data/final.csv` — 全部 228 个概湖逐时结果
- `output_GHJYL.txt` — 最终输出（TSV 格式）

## 部署（VPS）

```bash
git clone https://github.com/zengtianli/hydro-rainfall.git
cd hydro-rainfall
pip install -r requirements.txt
nohup streamlit run app.py --server.port 8518 --server.headless true &
```

## Hydro Toolkit 插件

本项目是 [Hydro Toolkit](https://github.com/zengtianli/hydro-toolkit) 的插件，也可独立运行。在 Toolkit 的插件管理页面粘贴本仓库 URL 即可安装。也可以直接**[在线体验](https://hydro-rainfall.tianlizeng.cloud)**，无需安装。

## 许可证

MIT
