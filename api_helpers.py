"""Small response helpers for api.py. Standard library plus pandas only."""
from __future__ import annotations

import base64
import io
import json
import os
import zipfile
from pathlib import Path

import pandas as pd


def df_to_json_safe(df: pd.DataFrame, limit: int | None = None) -> dict:
    """DataFrame -> {columns, rows, totalRows}; NaN becomes null, dates become ISO strings.

    With ``limit`` only the first rows are included while ``totalRows`` keeps the real count.
    """
    total = len(df)
    sliced = df.head(limit) if limit is not None and total > limit else df
    parsed = json.loads(sliced.to_json(orient="split", date_format="iso", force_ascii=False))
    return {"columns": parsed["columns"], "rows": parsed["data"], "totalRows": total}


def cors_origins(web_port: int) -> list[str]:
    """Origins allowed to call the API from a browser.

    Local development origins by default; add your own, comma separated, in
    ``RAINFALL_CORS_ORIGINS`` (for example ``https://rainfall.example.com``).
    """
    extra = [o.strip() for o in os.environ.get("RAINFALL_CORS_ORIGINS", "").split(",") if o.strip()]
    return [f"http://localhost:{web_port}", f"http://127.0.0.1:{web_port}", *extra]


def build_json_response(
    preview: dict | None = None,
    meta: dict | None = None,
    results: dict | None = None,
    zip_bytes: bytes | None = None,
    extras: dict | None = None,
) -> dict:
    """Assemble the {preview, meta, results, zipBase64} payload; ``extras`` are merged on top."""
    out: dict = {"preview": preview or {}, "meta": dict(meta or {}), "results": results or {}}
    if zip_bytes is not None:
        out["zipBase64"] = base64.b64encode(zip_bytes).decode("ascii")
        out["meta"].setdefault("zipBytes", len(zip_bytes))
    out.update(extras or {})
    return out


def preview_zip_files(zip_bytes: bytes) -> dict:
    """List an uploaded ZIP as {fileCount, totalSize, groups: {input, static, other}}."""
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
        files = [{"name": i.filename, "size": i.file_size} for i in archive.infolist() if not i.is_dir()]
    groups: dict[str, list] = {"input": [], "static": [], "other": []}
    for item in files:
        base = Path(item["name"]).name
        key = "input" if base.startswith("input_") else "static" if base.startswith("static_") else "other"
        groups[key].append(item)
    return {"fileCount": len(files), "totalSize": sum(f["size"] for f in files), "groups": groups}
