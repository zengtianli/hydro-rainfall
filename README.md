# Hydro Rainfall

降雨数据处理工具 -- 概湖灌溉需水计算程序。

处理流程：分区处理 -> 面积计算 -> 降雨系数(ggxs) -> 取水处理 -> 扣减计算 -> 合并输出。

## Usage

```bash
pip install -r requirements.txt

# 运行所有步骤
python comb0609.py

# 指定基础目录
python comb0609.py /path/to/data

# 运行指定步骤
python comb0609.py --steps partition area ggxs
```

## 输入文件

| 文件 | 说明 |
|------|------|
| `static_PYLYSCS.txt` | 分区静态数据（概湖名称、面积） |
| `input_FQNNGXL.txt` | 分区年内各旬降雨系数 |
| `input_GHJYL.txt` | 概湖径流量数据 |
| `input_YSH_GH.txt` | 取水户与概湖对应关系 |
| `input_YSH.txt` | 取水户取水量数据 |

## 输出

处理结果保存在 `data/` 目录下：

- `data/01csv/` -- 分区 CSV
- `data/02area/` -- 面积汇总
- `data/03ggxs/` -- 降雨系数
- `data/04deduct/` -- 扣减结果
- `data/final.csv` -- 最终合并结果
- `output_GHJYL.txt` -- 最终输出（TSV 格式）
