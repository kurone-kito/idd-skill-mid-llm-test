from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class CliTests(unittest.TestCase):
  def setUp(self) -> None:
    self.tempdir = tempfile.TemporaryDirectory()
    self.data_path = Path(self.tempdir.name) / "nested" / "tasks.json"

  def tearDown(self) -> None:
    self.tempdir.cleanup()

  def run_cli(self, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
      [
        sys.executable,
        "-m",
        "daymark",
        "--data",
        str(self.data_path),
        *arguments,
      ],
      cwd=ROOT,
      capture_output=True,
      text=True,
      check=False,
    )

  def assert_clean_error(self, result: subprocess.CompletedProcess[str]) -> None:
    self.assertNotEqual(result.returncode, 0)
    self.assertNotIn("Traceback", result.stderr)
    self.assertRegex(result.stderr, r"(?:error:|usage:)")

  def test_add_list_done_restore_flow_is_deterministic(self) -> None:
    added = self.run_cli(
      "add",
      "Write tests",
      "--due-date",
      "2026-08-05",
      "--tag",
      "Work",
      "--tag",
      "work",
    )
    self.assertEqual(added.returncode, 0, added.stderr)
    task_id = added.stdout.strip().split(" ", 1)[1]
    self.assertRegex(task_id, r"^[0-9a-f]{32}$")
    self.assertTrue(self.data_path.exists())

    first_list = self.run_cli("list", "--status", "pending")
    second_list = self.run_cli("list", "--status", "pending")
    self.assertEqual(first_list.returncode, 0, first_list.stderr)
    self.assertEqual(first_list.stdout, second_list.stdout)
    self.assertIn(
      f'"{task_id}"\t"pending"\t"2026-08-05"\t["work"]\t"Write tests"',
      first_list.stdout,
    )

    done = self.run_cli("done", task_id)
    self.assertEqual(done.returncode, 0, done.stderr)
    completed = self.run_cli("list", "--status", "completed")
    self.assertIn(f'"{task_id}"\t"completed"', completed.stdout)

    restored = self.run_cli("restore", task_id)
    self.assertEqual(restored.returncode, 0, restored.stderr)
    pending = self.run_cli("list", "--status", "pending")
    self.assertIn(f'"{task_id}"\t"pending"', pending.stdout)

  def test_list_all_is_sorted_and_uses_explicit_placeholders(self) -> None:
    first = self.run_cli("add", "Zulu")
    second = self.run_cli("add", "Alpha", "--tag", "one")
    self.assertEqual(first.returncode, 0, first.stderr)
    self.assertEqual(second.returncode, 0, second.stderr)
    comma_tag = self.run_cli("add", "Comma tag", "--tag", "a,b", "--tag", "-")
    self.assertEqual(comma_tag.returncode, 0, comma_tag.stderr)

    listed = self.run_cli("list")
    self.assertEqual(listed.returncode, 0, listed.stderr)
    rows = listed.stdout.splitlines()
    self.assertEqual(rows[0], "id\tstatus\tdue_date\ttags\ttitle")
    data_rows = rows[1:]
    self.assertEqual(
      [row.split("\t", 1)[0] for row in data_rows],
      sorted(row.split("\t", 1)[0] for row in data_rows),
    )
    alpha_row = next(row for row in data_rows if row.endswith('"Alpha"'))
    zulu_row = next(row for row in data_rows if row.endswith('"Zulu"'))
    comma_row = next(row for row in data_rows if row.endswith('"Comma tag"'))
    self.assertIn('"-"\t["one"]', alpha_row)
    self.assertIn('"-"\t[]', zulu_row)
    self.assertIn('\t["-","a,b"]\t"Comma tag"', comma_row)

  def test_invalid_fields_and_ids_are_clean_errors(self) -> None:
    for arguments in (
      ("add", "Task", "--due-date", "2026-02-30"),
      ("done", "missing"),
      ("restore", "missing"),
    ):
      with self.subTest(arguments=arguments):
        self.assert_clean_error(self.run_cli(*arguments))

  def test_parser_failures_are_clean_errors(self) -> None:
    for arguments in (("unknown",), ("add",), ("list", "--status", "bad")):
      with self.subTest(arguments=arguments):
        self.assert_clean_error(self.run_cli(*arguments))

  def test_data_path_is_required_and_never_falls_back(self) -> None:
    result = subprocess.run(
      [sys.executable, "-m", "daymark", "list"],
      cwd=ROOT,
      capture_output=True,
      text=True,
      check=False,
    )
    self.assert_clean_error(result)
    self.assertFalse((ROOT / "tasks.json").exists())

  def test_list_reports_clean_error_on_unrepresentable_stdout(self) -> None:
    added = self.run_cli("add", "日本語のタスク")
    self.assertEqual(added.returncode, 0, added.stderr)
    result = subprocess.run(
      [
        sys.executable,
        "-m",
        "daymark",
        "--data",
        str(self.data_path),
        "list",
      ],
      cwd=ROOT,
      capture_output=True,
      text=True,
      env={**os.environ, "PYTHONIOENCODING": "ascii"},
      check=False,
    )
    self.assert_clean_error(result)


if __name__ == "__main__":
  unittest.main()
