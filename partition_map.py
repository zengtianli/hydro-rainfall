"""Joins partition file names to rainfall-table columns.

The partition step names its files after static_PYLYSCS.txt ("分区01-名称:NSPYQ(南沙)" gives
the stem "01_NSPYQ(南沙)"), while input_FQNNGXL.txt is keyed by the full Chinese partition
name ("南沙平原区"). This table is the only place the two are matched; the 15 entries follow
partitions 01-15 of static_PYLYSCS.txt. The two river-channel columns of input_FQNNGXL.txt
(曹娥江江道, 姚江江道) belong to no partition and are deliberately absent.

An unknown code raises UnknownPartition. It is never skipped: a skipped partition would
leave its lakes without rainfall while the run still looks successful.
"""

from __future__ import annotations

__all__ = ["COLUMN_BY_CODE", "UnknownPartition", "code_of_stem", "column_for_stem"]

# 分区代号（static_PYLYSCS.txt「分区NN-名称:」冒号后、括号前的拼音缩写）
# → input_FQNNGXL.txt 的列名。键序即分区 01–15 序。
COLUMN_BY_CODE: dict[str, str] = {
    "NSPYQ": "南沙平原区",
    "SSPYQ": "蜀山平原区",
    "SYPYQ": "绍虞平原区",
    "YBPYSHQ": "虞北平原上河区",
    "YBPYZHQ": "虞北平原中河区",
    "FHPYQ": "丰惠平原区",
    "YYPYSHQ": "余姚平原上河区",
    "YYPYXHQ": "余姚平原下河区",
    "YYPYMZZHQ": "余姚平原马渚中河区",
    "YYPYYJSYQ": "余姚平原姚江上游区",
    "YYPYYJXYQ": "余姚平原姚江下游区",
    "CXPYXHQ": "慈溪平原西河区",
    "CXPYZHQ": "慈溪平原中河区",
    "CXPYDHQ": "慈溪平原东河区",
    "JBZHPYQ": "江北镇海平原区",
}


class UnknownPartition(KeyError):
    """分区代号不在对照表里 —— 表与 static_PYLYSCS.txt 漂移了，先补表再跑。"""


def code_of_stem(stem: str) -> str:
    """「01_NSPYQ(南沙)」→「NSPYQ」。容忍无序号前缀与全/半角括号。"""
    body = stem.split("_", 1)[1] if "_" in stem else stem
    return body.split("(")[0].split("（")[0].strip()


def column_for_stem(stem: str) -> str:
    """stem → input_FQNNGXL.txt 列名。查不到 raise，不返回 None、不静默。"""
    code = code_of_stem(stem)
    try:
        return COLUMN_BY_CODE[code]
    except KeyError:
        raise UnknownPartition(
            f"分区代号 {code!r}（来自文件名 {stem!r}）不在对照表里"
            f"（现有 {len(COLUMN_BY_CODE)} 项：{sorted(COLUMN_BY_CODE)}）。"
            "static_PYLYSCS.txt 新增了分区时，先在 partition_map.COLUMN_BY_CODE 补上对应的列名。"
        ) from None
