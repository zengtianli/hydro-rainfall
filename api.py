"""FastAPI wrapper for hydro-rainfall — unchanged Python core, no Streamlit.

Run:
    uv run uvicorn api:app --host 127.0.0.1 --port 8618 --reload

Requires python-multipart for file upload:
    uv add python-multipart
"""
from __future__ import annotations

import base64
import io
import json
import sys
import tempfile
import time
import zipfile
from pathlib import Path
from urllib.parse import quote

import pandas as pd
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

# Project root on sys.path so `from comb0609 import Config, Processor` resolves
# exactly like the original Streamlit entrypoint does.
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from comb0609 import Config, Processor  # noqa: E402

app = FastAPI(title="hydro-rainfall-api", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3118",
        "http://127.0.0.1:3118",
        "https://hydro-rainfall.tianlizeng.cloud",
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

SAMPLE_DIR = PROJECT_ROOT / "data" / "sample"
REQUIRED_INPUTS = {
    "static_PYLYSCS.txt",
    "input_FQNNGXL.txt",
    "input_GHJYL.txt",
    "input_YSH_GH.txt",
    "input_YSH.txt",
}


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/meta")
def meta_info() -> dict:
    return {
        "name": "rainfall",
        "title": "降雨径流计算",
        "icon": "🌧️",
        "description": "概湖灌溉需水量计算（分区→面积→降雨系数→取水→扣减→合并）",
        "version": "1.0.0",
    }


def _extract_inputs(zip_bytes: bytes, workdir: Path) -> list[str]:
    """Extract zip into workdir flat (txt files only, strip any subpath).

    Returns sorted list of extracted file names.
    """
    extracted: list[str] = []
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
        for name in z.namelist():
            if name.endswith("/") or name.startswith("__MACOSX"):
                continue
            base = Path(name).name
            if not base or not base.lower().endswith(".txt"):
                continue
            with z.open(name) as src:
                (workdir / base).write_bytes(src.read())
            extracted.append(base)
    return sorted(extracted)


def _package_outputs(workdir: Path) -> bytes:
    """Pack final.csv + all intermediate dirs (data/01csv..04deduct) into a zip."""
    data_dir = workdir / "data"
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        if data_dir.exists():
            for p in data_dir.rglob("*"):
                if p.is_file():
                    # Skip log files and keep the structure relative to data/
                    rel = p.relative_to(data_dir)
                    if rel.parts and rel.parts[0] == "logs":
                        continue
                    z.write(p, arcname=str(Path("data") / rel))
        # Also include output_GHJYL.txt written back to BASE_DIR
        out_txt = workdir / "output_GHJYL.txt"
        if out_txt.exists():
            z.write(out_txt, arcname="output_GHJYL.txt")
    return buf.getvalue()


def _run_rainfall(zip_bytes: bytes) -> tuple[bytes, int, bool]:
    """Run the 6-step comb0609 pipeline in a temp workdir.

    Returns (zip_bytes, final_row_count, final_csv_present).
    """
    with tempfile.TemporaryDirectory() as tmpdir_raw:
        workdir = Path(tmpdir_raw)

        extracted = _extract_inputs(zip_bytes, workdir)
        if not extracted:
            raise HTTPException(400, "ZIP 内未找到任何 .txt 输入文件")

        present = set(extracted)
        # If user omitted static file but it exists in sample, auto-fill it.
        if "static_PYLYSCS.txt" not in present and SAMPLE_DIR.exists():
            static_src = SAMPLE_DIR / "static_PYLYSCS.txt"
            if static_src.exists():
                (workdir / "static_PYLYSCS.txt").write_bytes(static_src.read_bytes())
                present.add("static_PYLYSCS.txt")

        missing = REQUIRED_INPUTS - present
        if missing:
            raise HTTPException(
                400,
                f"缺少必需的输入文件: {', '.join(sorted(missing))}",
            )

        # Run pipeline
        config = Config(str(workdir))
        processor = Processor(config)
        processor.partition_process()
        processor.area_process()
        processor.ggxs_process()
        processor.intake_process()
        processor.deduct_process()
        processor.merge_final_process()

        final_csv = workdir / "data" / "final.csv"
        final_present = final_csv.exists()
        row_count = 0
        if final_present:
            # Rough row count (exclude header).
            with final_csv.open("r", encoding="utf-8") as f:
                row_count = max(0, sum(1 for _ in f) - 1)

        zip_out = _package_outputs(workdir)
        return zip_out, row_count, final_present


def _df_to_json_safe(df: pd.DataFrame, limit: int | None = None) -> dict:
    """DataFrame → {columns, rows, totalRows}. Handles NaN / datetime / numpy types."""
    total = len(df)
    sliced = df.head(limit) if limit is not None and total > limit else df
    parsed = json.loads(sliced.to_json(orient="split", date_format="iso", force_ascii=False))
    return {"columns": parsed["columns"], "rows": parsed["data"], "totalRows": total}


def _list_input_files(zip_bytes: bytes) -> tuple[list[dict], int]:
    """List .txt file manifest from the uploaded ZIP (name, size, category)."""
    entries: list[dict] = []
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
        for info in z.infolist():
            if info.is_dir() or info.filename.startswith("__MACOSX"):
                continue
            base = Path(info.filename).name
            if not base or not base.lower().endswith(".txt"):
                continue
            if base.startswith("static_"):
                category = "static"
            elif base.startswith("input_"):
                category = "input"
            else:
                category = "other"
            entries.append({"name": base, "size": info.file_size, "category": category})
    entries.sort(key=lambda e: (e["category"], e["name"]))
    return entries, len(entries)


def _read_csv_safe(path: Path, comment: str | None = None) -> pd.DataFrame:
    try:
        if comment:
            return pd.read_csv(path, comment=comment)
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def _read_tsv_safe(path: Path) -> pd.DataFrame:
    try:
        return pd.read_csv(path, sep="\t")
    except Exception:
        return pd.DataFrame()


PIPELINE_STEPS = [
    ("partition", "分区划定", "data/01csv"),
    ("area", "面积权重", "data/02area"),
    ("ggxs", "降雨系数", "data/03ggxs"),
    ("intake", "取水", "data/03intake"),
    ("deduct", "扣减", "data/04deduct"),
    ("merge_final", "合并", "data"),
]


def _collect_pipeline_steps(workdir: Path) -> list[dict]:
    """Walk known output dirs and count produced files per step."""
    data_dir = workdir / "data"
    steps: list[dict] = []
    for key, label, rel in PIPELINE_STEPS:
        dir_path = workdir / rel if rel == "data" else data_dir / rel.split("/", 1)[1]
        files: list[dict] = []
        if dir_path.exists() and dir_path.is_dir():
            for p in sorted(dir_path.iterdir()):
                if not p.is_file():
                    continue
                if key == "merge_final":
                    # 只收 final.csv / merge_all.csv，排除子目录和中间文件
                    if p.name not in {"final.csv", "merge_all.csv"}:
                        continue
                files.append({"name": p.name, "size": p.stat().st_size})
        # merge_final 额外含 output_GHJYL.txt
        if key == "merge_final":
            out_txt = workdir / "output_GHJYL.txt"
            if out_txt.exists():
                files.append({"name": out_txt.name, "size": out_txt.stat().st_size})
        steps.append(
            {
                "step": key,
                "label": label,
                "outputDir": rel,
                "files": files,
                "fileCount": len(files),
                "status": "completed" if files else "empty",
            }
        )
    return steps


def _run_rainfall_full(zip_bytes: bytes) -> dict:
    """Rich pipeline: preview + per-step outputs + result tables + zip base64."""
    started = time.perf_counter()

    input_manifest, input_count = _list_input_files(zip_bytes)

    with tempfile.TemporaryDirectory() as tmpdir_raw:
        workdir = Path(tmpdir_raw)

        extracted = _extract_inputs(zip_bytes, workdir)
        if not extracted:
            raise HTTPException(400, "ZIP 内未找到任何 .txt 输入文件")

        present = set(extracted)
        if "static_PYLYSCS.txt" not in present and SAMPLE_DIR.exists():
            static_src = SAMPLE_DIR / "static_PYLYSCS.txt"
            if static_src.exists():
                (workdir / "static_PYLYSCS.txt").write_bytes(static_src.read_bytes())
                present.add("static_PYLYSCS.txt")

        missing = REQUIRED_INPUTS - present
        if missing:
            raise HTTPException(
                400,
                f"缺少必需的输入文件: {', '.join(sorted(missing))}",
            )

        config = Config(str(workdir))
        processor = Processor(config)
        processor.partition_process()
        processor.area_process()
        processor.ggxs_process()
        processor.intake_process()
        processor.deduct_process()
        processor.merge_final_process()

        pipeline_steps = _collect_pipeline_steps(workdir)

        data_dir = workdir / "data"
        final_csv = data_dir / "final.csv"
        merge_all_csv = data_dir / "merge_all.csv"
        output_ghjyl = workdir / "output_GHJYL.txt"

        final_present = final_csv.exists()
        row_count = 0
        if final_present:
            with final_csv.open("r", encoding="utf-8") as f:
                row_count = max(0, sum(1 for _ in f) - 1)

        DISPLAY_LIMIT = 500
        results_payload: dict[str, dict] = {}
        if final_csv.exists():
            results_payload["final.csv"] = _df_to_json_safe(_read_csv_safe(final_csv), limit=DISPLAY_LIMIT)
        if merge_all_csv.exists():
            results_payload["merge_all.csv"] = _df_to_json_safe(_read_csv_safe(merge_all_csv), limit=DISPLAY_LIMIT)
        if output_ghjyl.exists():
            results_payload["output_GHJYL.txt"] = _df_to_json_safe(_read_tsv_safe(output_ghjyl), limit=DISPLAY_LIMIT)

        zip_out = _package_outputs(workdir)

        elapsed_ms = int((time.perf_counter() - started) * 1000)

        return {
            "preview": {
                "inputFiles": input_manifest,
                "fileCount": input_count,
            },
            "meta": {
                "finalRows": row_count,
                "finalPresent": final_present,
                "pipeline": [k for k, _, _ in PIPELINE_STEPS],
                "elapsedMs": elapsed_ms,
                "zipBytes": len(zip_out),
            },
            "results": results_payload,
            "pipelineSteps": pipeline_steps,
            "zipBase64": base64.b64encode(zip_out).decode("ascii"),
        }


@app.post("/api/compute")
async def compute(
    file: UploadFile = File(..., description="ZIP 含 static_PYLYSCS.txt + input_*.txt"),
    format: str = Form("zip", description="zip (binary) | json (preview+pipelineSteps+results+base64)"),
) -> Response:
    content = await file.read()
    if not content:
        raise HTTPException(400, "上传文件为空")
    try:
        if format == "json":
            payload = _run_rainfall_full(content)
            return JSONResponse(content=payload)
        zip_bytes, row_count, final_present = _run_rainfall(content)
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        raise HTTPException(
            500,
            f"计算失败: {type(e).__name__}: {e}\n{traceback.format_exc()[-800:]}",
        )
    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={
            "Content-Disposition": 'attachment; filename="rainfall_result.zip"',
            "X-Final-Rows": str(row_count),
            "X-Final-Present": "1" if final_present else "0",
            "X-Pipeline": quote("分区→面积→降雨系数→取水→扣减→合并"),
            "Access-Control-Expose-Headers": "X-Final-Rows, X-Final-Present, X-Pipeline, Content-Disposition",
        },
    )


@app.get("/api/sample")
def sample_zip() -> Response:
    """Return a zip of the bundled sample inputs for one-click demo."""
    if not SAMPLE_DIR.exists():
        raise HTTPException(404, "示例输入目录不存在")
    buf = io.BytesIO()
    count = 0
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(SAMPLE_DIR.glob("*.txt")):
            z.write(p, arcname=p.name)
            count += 1
    if count == 0:
        raise HTTPException(404, "示例输入文件为空")
    return Response(
        content=buf.getvalue(),
        media_type="application/zip",
        headers={"Content-Disposition": 'attachment; filename="sample_input.zip"'},
    )
