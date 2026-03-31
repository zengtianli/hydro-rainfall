# hydro-rainfall — 228 湖/15 分区湖泊降雨径流计算器

## Quick Reference

| 项目 | 路径/值 |
|------|---------|
| 入口 | `app.py` (Streamlit) |
| 批处理脚本 | `comb0609.py` |
| 线上地址 | https://hydro-rainfall.tianlizeng.cloud |
| VPS 部署路径 | `/var/www/hydro-rainfall/` |
| 静态湖泊数据 | `static_PYLYSCS.txt` |
| 分区参数文件 | `input_YSH.txt`、`input_YSH_GH.txt`、`input_FQNNGXL.txt`、`input_GHJYL.txt` |
| 数据流水线目录 | `data/01csv → 02area → 03ggxs → 04deduct → final/merge` |
| Python | `/Users/tianli/miniforge3/bin/python3` |

## 常用命令

```bash
# 本地启动
cd /Users/tianli/Dev/hydro-rainfall
streamlit run app.py

# 运行批处理流水线（日降雨 → 逐小时 → 合并）
python3 comb0609.py

# 安装依赖
pip install -r requirements.txt
```

## 项目结构

```
hydro-rainfall/
├── app.py              # Streamlit 主入口，六步流水线 UI
├── comb0609.py         # 批处理脚本（全流水线自动化）
├── src/common/         # 公共计算模块
├── data/
│   ├── 01csv/          # 原始日降雨 CSV（上传 ZIP 或预置）
│   ├── 02area/         # 面积权重
│   ├── 03ggxs/         # 降雨系数
│   ├── 04deduct/       # 扣损结果
│   ├── final.csv       # 单次运行输出
│   └── merge_all.csv   # 批量合并输出
├── input_*.txt         # 各分区参数文件（修改分区配置用）
├── static_PYLYSCS.txt  # 湖泊空间静态数据集（228 湖）
└── .streamlit/config.toml
```

## 六步流水线

1. **分区划定** — 将湖泊映射到 15 个分区
2. **面积权重** — 计算各湖面积比例
3. **降雨系数** — 读取 `input_*.txt` 分区参数
4. **需水量** — 日降雨 → 逐小时时间序列转换
5. **扣损** — 计算净径流
6. **合并** — 输出每湖 Excel + `merge_all.csv`

## 开发注意

- 无外部 API，无需凭证，`~/.personal_env` 不涉及
- 新增计算模块放 `src/common/`，在 `app.py` 中按步骤注册
- 修改分区参数编辑对应 `input_*.txt`，格式见文件头注释
- Streamlit 端口配置在 `.streamlit/config.toml`
