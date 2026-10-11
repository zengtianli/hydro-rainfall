"""Guards the supported Python range (issue #1).

Run with:  python -m unittest discover -s tests -v

Standard library only, so it runs on the lowest supported Python without extra
test dependencies (``tomllib`` is deliberately not used: it needs Python 3.11).
"""
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SAMPLE_INPUTS = sorted((ROOT / "data" / "sample").glob("*.txt"))


def declared_floor():
    """Lowest Python from pyproject.toml, e.g. ``(3, 10)``. The single source."""
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'^requires-python\s*=\s*">=\s*(\d+)\.(\d+)"', text, re.M)
    assert match, "pyproject.toml must declare requires-python as >=X.Y"
    return int(match.group(1)), int(match.group(2))


def normalized(path):
    """File content with platform line endings folded, for a stable comparison."""
    return path.read_bytes().replace(b"\r\n", b"\n")


class DeclaredRangeTest(unittest.TestCase):
    def test_running_interpreter_is_supported(self):
        self.assertGreaterEqual(sys.version_info[:2], declared_floor())

    def test_readmes_state_the_same_floor(self):
        floor = "%d.%d" % declared_floor()
        for name in ("README.md", "README_EN.md"):
            text = (ROOT / name).read_text(encoding="utf-8")
            stated = set(re.findall(r"Python[ -](\d+\.\d+)\+", text))
            stated |= set(re.findall(r"Python (\d+\.\d+) (?:及以上|or newer)", text))
            self.assertEqual(stated, {floor}, "%s states Python %s" % (name, sorted(stated)))

    def test_ci_matrix_starts_at_the_floor(self):
        workflow = (ROOT / ".github" / "workflows" / "test.yml").read_text(encoding="utf-8")
        line = re.search(r"^\s*python-version:\s*\[(.+)\]\s*$", workflow, re.M)
        self.assertIsNotNone(line, "CI matrix line python-version: [...] not found")
        versions = [tuple(int(n) for n in v.strip(" \"'").split(".")) for v in line.group(1).split(",")]
        self.assertEqual(min(versions), declared_floor())


class PipelineResultTest(unittest.TestCase):
    """The bundled sample must give the committed result on every supported Python."""

    def test_sample_run_matches_committed_result(self):
        self.assertEqual(len(SAMPLE_INPUTS), 5, "data/sample should hold the five input files")
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            for src in SAMPLE_INPUTS:
                shutil.copy(src, work / src.name)
            run = subprocess.run(
                [sys.executable, str(ROOT / "comb0609.py"), str(work)],
                capture_output=True, text=True, encoding="utf-8", errors="replace",
            )
            self.assertEqual(run.returncode, 0, run.stderr[-2000:])
            for name in ("final.csv", "merge_all.csv"):
                self.assertEqual(
                    normalized(work / "data" / name),
                    normalized(ROOT / "data" / name),
                    "data/%s differs from the committed result" % name,
                )
            self.assertTrue((work / "output_GHJYL.txt").is_file())


if __name__ == "__main__":
    unittest.main()
