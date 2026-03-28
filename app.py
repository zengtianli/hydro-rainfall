#!/usr/bin/env python3
"""降雨径流计算 — Streamlit Web 界面"""

import sys
import shutil
import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

# Self-path resolution for both standalone and toolkit plugin modes
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.common.st_utils import page_config, footer

page_config("降雨径流计算 - Hydro Toolkit", "🌧️")

REPO_DIR = Path(__file__).resolve().parent
SAMPLE_DIR = REPO_DIR / "data" / "sample"

# Input file definitions
INPUT_FILES = {
    "static_PYLYSCS.txt": "分区与概湖静态配置",
    "input_FQNNGXL.txt": "逐日降雨系数数据（TSV）",
    "input_GHJYL.txt": "河道径流数据（TSV）",
    "input_YSH_GH.txt": "取水户-概湖映射（TSV）",
    "input_YSH.txt": "取水户取水量数据（TSV）",
}

STEPS = [
    ("partition", "分区处理"),
    ("area", "面积汇总"),
    ("ggxs", "降雨系数计算"),
    ("intake", "取水处理"),
    ("deduct", "扣减计算"),
    ("merge_final", "合并输出"),
]

st.title("🌧️ 降雨径流计算")
st.caption("概湖灌溉需水量计算 — 分区→面积→降雨系数→取水→扣减→合并")

# ── Sidebar ──
with st.sidebar:
    st.header("使用说明")
    st.markdown("""
    1. 选择数据来源（示例数据或上传）
    2. 选择要运行的处理步骤
    3. 点击"开始计算"
    4. 查看结果并下载
    """)
    st.markdown("---")
    st.markdown("**输入文件说明**")
    for fname, desc in INPUT_FILES.items():
        st.markdown(f"- `{fname}`: {desc}")

# ── Step 1: Data Source ──
st.header("① 数据来源")
source = st.radio("选择数据来源", ["示例数据", "上传数据"], horizontal=True)

uploaded_files = {}
if source == "上传数据":
    cols = st.columns(2)
    for i, (fname, desc) in enumerate(INPUT_FILES.items()):
        with cols[i % 2]:
            f = st.file_uploader(f"{desc}", key=fname, type=["txt"])
            if f:
                uploaded_files[fname] = f
else:
    # Check sample data exists
    if SAMPLE_DIR.exists():
        st.success(f"使用内置示例数据（{len(list(SAMPLE_DIR.glob('*.txt')))} 个文件）")
    else:
        st.error("示例数据目录不存在")

# ── Step 2: Processing Steps ──
st.header("② 处理步骤")
step_cols = st.columns(3)
selected_steps = []
for i, (step_key, step_name) in enumerate(STEPS):
    with step_cols[i % 3]:
        if st.checkbox(step_name, value=True, key=f"step_{step_key}"):
            selected_steps.append(step_key)

# ── Step 3: Run ──
st.header("③ 运行计算")

if st.button("🚀 开始计算", type="primary", use_container_width=True):
    if source == "上传数据" and len(uploaded_files) < 4:
        st.error("请至少上传 4 个输入文件（静态配置可选）")
    elif not selected_steps:
        st.error("请至少选择一个处理步骤")
    else:
        # Create temp working directory
        work_dir = Path(tempfile.mkdtemp(prefix="hydro_rainfall_"))

        try:
            # Copy input files to work_dir
            if source == "示例数据":
                for f in SAMPLE_DIR.glob("*"):
                    shutil.copy2(f, work_dir / f.name)
            else:
                # Copy static file from sample if not uploaded
                if "static_PYLYSCS.txt" not in uploaded_files and SAMPLE_DIR.exists():
                    static_src = SAMPLE_DIR / "static_PYLYSCS.txt"
                    if static_src.exists():
                        shutil.copy2(static_src, work_dir / "static_PYLYSCS.txt")
                # Write uploaded files
                for fname, fobj in uploaded_files.items():
                    (work_dir / fname).write_bytes(fobj.getvalue())

            # Import and run processor
            from comb0609 import Config, Processor

            config = Config(str(work_dir))
            processor = Processor(config)

            progress = st.progress(0, text="准备中...")
            total = len(selected_steps)

            step_methods = {
                "partition": processor.partition_process,
                "area": processor.area_process,
                "ggxs": processor.ggxs_process,
                "intake": processor.intake_process,
                "deduct": processor.deduct_process,
                "merge_final": processor.merge_final_process,
            }

            for i, step_key in enumerate(selected_steps):
                step_name = dict(STEPS)[step_key]
                progress.progress((i) / total, text=f"正在运行: {step_name}...")
                try:
                    step_methods[step_key]()
                except Exception as e:
                    st.warning(f"步骤 {step_name} 出错: {e}")

            progress.progress(1.0, text="计算完成！")

            # ── Step 4: Results ──
            st.header("④ 计算结果")

            # Final result
            final_csv = work_dir / "data" / "final.csv"
            output_txt = work_dir / "output_GHJYL.txt"

            if final_csv.exists():
                df_final = pd.read_csv(final_csv)
                st.subheader("最终结果预览")
                st.dataframe(df_final.head(50), use_container_width=True)
                st.caption(f"共 {len(df_final)} 行 × {len(df_final.columns)} 列")

                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        "📥 下载 final.csv",
                        final_csv.read_text(encoding="utf-8"),
                        file_name="final.csv",
                        mime="text/csv",
                    )
                with col2:
                    if output_txt.exists():
                        st.download_button(
                            "📥 下载 output_GHJYL.txt",
                            output_txt.read_text(encoding="utf-8"),
                            file_name="output_GHJYL.txt",
                            mime="text/plain",
                        )
            else:
                st.warning("未生成最终结果文件。请确认已选择'合并输出'步骤。")

            # Intermediate results
            with st.expander("📁 中间结果"):
                data_dir = work_dir / "data"
                for subdir in ["01csv", "02area", "03ggxs", "03intake", "04deduct"]:
                    sub_path = data_dir / subdir
                    if sub_path.exists():
                        files = list(sub_path.glob("*.csv"))
                        st.markdown(f"**{subdir}/** — {len(files)} 个文件")
                        if files and len(files) <= 20:
                            for f in sorted(files)[:5]:
                                try:
                                    df = pd.read_csv(f, comment="#")
                                    st.markdown(f"`{f.name}`")
                                    st.dataframe(df.head(10), use_container_width=True)
                                except Exception:
                                    pass

        except Exception as e:
            st.error(f"处理出错: {e}")
            import traceback
            st.code(traceback.format_exc())

        finally:
            # Store work_dir in session state for potential cleanup
            st.session_state["work_dir"] = str(work_dir)

# ── Footer ──
footer("降雨径流计算", repo_url="https://github.com/zengtianli/hydro-rainfall")
