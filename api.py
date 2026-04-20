"""FastAPI wrapper for hydro-rainfall — unchanged Python core, no Streamlit.

Run:
    uv run uvicorn api:app --host 127.0.0.1 --port 8618 --reload

Requires python-multipart for file upload:
    uv add python-multipart
"""
from __future__ import annotations

import io
import sys
import tempfile
import zipfile
from pathlib import Path
from urllib.parse import quote

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

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


@app.post("/api/compute")
async def compute(file: UploadFile = File(..., description="ZIP 含 static_PYLYSCS.txt + input_*.txt")) -> Response:
    content = await file.read()
    if not content:
        raise HTTPException(400, "上传文件为空")
    try:
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
