"""The pipeline must really compute: partitions map to rainfall columns, lakes get their own
area, and water intake is deducted. Standard library only.

Run with:  python -m unittest discover -s tests -v
"""
import csv
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SAMPLE = ROOT / "data" / "sample"
sys.path.insert(0, str(ROOT))

import partition_map  # noqa: E402


def run_pipeline(work):
    return subprocess.run([sys.executable, str(ROOT / "comb0609.py"), str(work)],
                          capture_output=True, text=True, encoding="utf-8", errors="replace")


def stage(work, edit=None):
    for src in SAMPLE.glob("*.txt"):
        shutil.copy(src, work / src.name)
    if edit:
        edit(work)


def data_rows(path):
    """CSV rows after the leading '#' comment lines."""
    with open(path, encoding="utf-8", newline="") as handle:
        return list(csv.reader(line for line in handle if not line.startswith("#")))


def static_partitions():
    """[(stem, [lake, ...])] as the partition step names them, from static_PYLYSCS.txt."""
    found, number, code = [], None, None
    for line in (SAMPLE / "static_PYLYSCS.txt").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("分区") and "-名称:" in line:
            number, code = line[2:4], line.split(":", 1)[1].strip()
        elif number and "包含概湖的名称" in line:
            found.append(("%s_%s" % (number, code), [n.strip() for n in line.split(":", 1)[1].split(",") if n.strip()]))
    return found


class PartitionMapTest(unittest.TestCase):
    def test_every_partition_maps_to_a_rainfall_column(self):
        columns = (SAMPLE / "input_FQNNGXL.txt").read_text(encoding="utf-8").splitlines()[0].split("\t")
        partitions = static_partitions()
        self.assertEqual(len(partitions), 15)
        for stem, _ in partitions:
            self.assertIn(partition_map.column_for_stem(stem), columns, stem)

    def test_unknown_partition_is_an_error_not_a_zero(self):
        with self.assertRaises(partition_map.UnknownPartition):
            partition_map.column_for_stem("99_NOPE(none)")


class ComputedResultTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.work = Path(cls.tmp.name)

        def add_intake(work):
            # One synthetic hourly intake (not a measured value) for the first user on the first day.
            path = work / "input_YSH.txt"
            lines = path.read_text(encoding="utf-8").split("\n")
            cells = lines[1].split("\t")
            cls.user, cls.day = cells[0], cells[1]
            cells[2], cells[3] = "240", "10"
            lines[1] = "\t".join(cells)
            path.write_text("\n".join(lines), encoding="utf-8")

        stage(cls.work, add_intake)
        cls.run_result = run_pipeline(cls.work)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_run_succeeds(self):
        self.assertEqual(self.run_result.returncode, 0, self.run_result.stderr[-2000:])

    def test_lake_table_holds_lake_names_and_their_own_areas(self):
        rows = data_rows(self.work / "data/02area/gaihu.csv")
        self.assertEqual(rows[0], ["概湖名称", "面积(km2)"])
        names = [row[0] for row in rows[1:]]
        self.assertEqual(len(names), 225)
        self.assertTrue(all(name.startswith("G") for name in names), names[:5])
        self.assertEqual(dict(rows[1:])["G001"], "3.0777")  # first area listed for partition 02

    def test_rainfall_reaches_every_lake_of_every_partition(self):
        areas = dict(data_rows(self.work / "data/02area/fenqu.csv")[1:])
        seen = set()
        for stem, lakes in static_partitions():
            expected = 100 / 24 * 10000 / (float(areas[stem]) * 1_000_000) * 1000
            for lake in lakes:
                if lake in seen:  # a lake listed under two partitions keeps the first one
                    continue
                seen.add(lake)
                rows = data_rows(self.work / "data/03ggxs" / ("%s_ggxs.csv" % lake))
                self.assertAlmostEqual(float(rows[1][1]), expected, places=12, msg=lake)
                self.assertEqual(float(rows[25][1]), 0.0, lake)  # the next day has no rain in the sample
        self.assertEqual(len(seen), 225)

    def test_intake_is_computed_per_lake_and_deducted(self):
        lake = next(line.split("\t")[1].strip() for line in
                    (self.work / "input_YSH_GH.txt").read_text(encoding="utf-8").splitlines()[1:]
                    if line.split("\t")[0] == self.user)
        area_km2 = float(dict(data_rows(self.work / "data/02area/gaihu.csv")[1:])[lake])
        rows = data_rows(self.work / "data/03intake" / ("%s_intake.csv" % lake))
        column = rows[0].index(self.user)
        first_hour = next(row for row in rows[1:] if row[0].startswith(self.day + " 00:00"))
        expected = 10 / (area_km2 * 1_000_000) * 1000
        self.assertAlmostEqual(float(first_hour[column]), expected, places=12)
        deduct = data_rows(self.work / "data/04deduct" / ("%s_deduct.csv" % lake))
        header = deduct[0]
        row = next(r for r in deduct[1:] if r[0].startswith(self.day.replace("/", "-") + " 00:00"))
        self.assertAlmostEqual(float(row[header.index("total_demand")]),
                               float(row[header.index("ggxs_sum")]) + float(row[header.index("intake_total")]), places=12)
        self.assertAlmostEqual(float(row[header.index("intake_total")]), expected, places=12)


class MismatchedInputTest(unittest.TestCase):
    def test_rainfall_table_without_the_partition_columns_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)

            def rename_columns(work):
                path = work / "input_FQNNGXL.txt"
                lines = path.read_text(encoding="utf-8").split("\n")
                lines[0] = "\t".join(["日期"] + ["列%d" % i for i in range(len(lines[0].split("\t")) - 1)])
                path.write_text("\n".join(lines), encoding="utf-8")

            stage(work, rename_columns)
            result = run_pipeline(work)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((work / "data" / "final.csv").exists())


class ApiTest(unittest.TestCase):
    def test_api_runs_from_a_clean_checkout(self):
        try:
            import fastapi  # noqa: F401
        except ImportError:
            self.skipTest("fastapi is not installed")
        import io
        import zipfile
        import api
        self.assertEqual(api.health(), {"status": "ok"})
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            for src in SAMPLE.glob("*.txt"):
                archive.write(src, arcname=src.name)
        payload = api._run_rainfall_full(buffer.getvalue())
        self.assertTrue(payload["meta"]["finalPresent"])
        counts = {step["step"]: step["fileCount"] for step in payload["pipelineSteps"]}
        self.assertEqual(counts["ggxs"], 225)
        self.assertGreater(counts["intake"], 0)


if __name__ == "__main__":
    unittest.main()
