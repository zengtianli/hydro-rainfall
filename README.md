# hydro-rainfall

**中文** | [English](README_EN.md)

平原河网概湖的逐小时序列计算：把分区日值按面积折算到 225 个概湖（15 个分区），算出各概湖的取水量，再从概湖序列里扣减。命令行脚本，另带一个可选的 HTTP 接口。

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-yellow?style=for-the-badge)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

## 安装

```bash
git clone https://github.com/zengtianli/hydro-rainfall.git
cd hydro-rainfall
pip install -r requirements.txt
```

使用 [uv](https://docs.astral.sh/uv/) 时运行 `uv sync` 即可；它默认按 `.python-version` 选用 3.13，想用本机的 3.10 / 3.11 请加 `--python 3.10`。

## 运行

```bash
python comb0609.py
```

读取当前目录的 `static_PYLYSCS.txt` 和 `input_*.txt`，依次执行六步，结果写入 `data/final.csv` 与 `output_GHJYL.txt`。输入文件放在别处时把目录作为参数：`python comb0609.py /path/to/dir`；只跑其中几步用 `--steps partition area`。

## 输入文件

| 文件 | 内容 |
|------|------|
| `static_PYLYSCS.txt` | 15 个分区各自包含的概湖名称与面积 |
| `input_FQNNGXL.txt` | 各分区的逐日数值，列名是分区的中文名 |
| `input_YSH.txt` | 各取水户的逐日、逐小时取水量 |
| `input_YSH_GH.txt` | 取水户属于哪个概湖 |
| `input_GHJYL.txt` | 各概湖的逐小时序列，最后一步从它里面扣减 |

## 六步流程

| 步骤 | 做什么 | 结果 |
|------|--------|------|
| 1 分区 | 把 `static_PYLYSCS.txt` 拆成每个分区一个文件 | `data/01csv/` |
| 2 面积 | 汇总每个概湖的面积和每个分区的总面积 | `data/02area/` |
| 3 降雨系数 | 分区日值平均到 24 小时，按分区面积折算成毫米，写到该分区的每个概湖 | `data/03ggxs/` |
| 4 取水 | 取水户的小时取水量按所属概湖的面积折算成毫米 | `data/03intake/` |
| 5 扣减 | 每个概湖逐小时：第 3 步的值 + 第 4 步的取水合计 | `data/04deduct/` |
| 6 合并 | `input_GHJYL.txt` 减去第 3 步的值，得到最终序列 | `data/final.csv`、`output_GHJYL.txt` |

`final.csv` 目前只扣第 3 步的结果；第 4、5 步算出的取水量与合计保存在 `data/04deduct/`，没有并入 `final.csv`。

分区文件名（如 `01_NSPYQ(南沙)`）与 `input_FQNNGXL.txt` 的列名（如 `南沙平原区`）由 `partition_map.py` 对应。两边对不上时程序报错退出，不会用 0 代替。

## 自带样例

仓库根目录和 `data/sample/` 里的输入用于演示格式和流程：`input_FQNNGXL.txt` 只有 2025/05/14 这一行给每个分区填了 100，这是示例值，不是实测资料；其余输入全部是 0。`data/` 下已提交的结果就是用这份样例跑出来的。

## HTTP 接口（可选）

```bash
uvicorn api:app --host 127.0.0.1 --port 8618
```

- `GET /api/sample` 下载样例输入的 ZIP
- `POST /api/compute` 上传含五个输入文件的 ZIP，返回结果 ZIP；表单字段 `format=json` 时返回各步产物清单和结果表

浏览器跨域默认只放行本机地址，其他来源写进环境变量 `RAINFALL_CORS_ORIGINS`（逗号分隔）。

## 测试

```bash
python -m unittest discover -s tests -v
```

## 环境要求

- Python 3.10 及以上（每次提交在 3.10、3.11、3.12、3.13 上自动测试）
- pandas 2.2 及以上

## License

MIT
