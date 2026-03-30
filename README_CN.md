        # hydro-rainfall

        [English](README.md) | **中文**

        湖泊灌区降雨径流计算工具——覆盖 15 个分区、228 个湖泊的径流推算。

        [![在线演示](https://img.shields.io/badge/在线演示-hydro--rainfall.tianlizeng.cloud-blue?style=for-the-badge)](https://hydro-rainfall.tianlizeng.cloud)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-yellow?style=for-the-badge)](https://python.org)
        [![License: MIT](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

        ---

        ---

### 无需安装，立即体验

**https://hydro-rainfall.tianlizeng.cloud**

---

![hydro-rainfall demo](docs/screenshots/demo.svg)

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

        ## 快速开始

        ```bash
        streamlit run app.py
        ```

        ## 自托管

```bash
git clone https://github.com/zengtianli/hydro-rainfall.git
cd hydro-rainfall
pip install -r requirements.txt
streamlit run app.py
```

或直接使用托管版本：**https://hydro-rainfall.tianlizeng.cloud**

## 环境要求

        - Python 3.9+
        - Streamlit 1.36+

        ## License

        MIT
