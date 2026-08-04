from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class EndToEndTests(unittest.TestCase):
  def setUp(self) -> None:
    self.tempdir = tempfile.TemporaryDirectory()
    base = Path(self.tempdir.name)
    self.data_path = base / "valid" / "tasks.json"
    self.malformed_path = base / "malformed" / "tasks.json"

  def tearDown(self) -> None:
    self.tempdir.cleanup()

  def run_cli(
    self,
    data_path: Path,
    *arguments: str,
  ) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
      [
        sys.executable,
        "-m",
        "daymark",
        "--data",
        str(data_path),
        *arguments,
      ],
      cwd=ROOT,
      capture_output=True,
      text=True,
      check=False,
    )

  def assert_success(
    self,
    result: subprocess.CompletedProcess[str],
  ) -> None:
    self.assertEqual(result.returncode, 0, result.stderr)
    self.assertEqual(result.stderr, "")

  def assert_clean_error(
    self,
    result: subprocess.CompletedProcess[str],
    message: str,
  ) -> None:
    self.assertNotEqual(result.returncode, 0)
    self.assertIn(message, result.stderr)
    self.assertNotIn("Traceback", result.stderr)

  def add_task(self, title: str, *arguments: str) -> str:
    result = self.run_cli(self.data_path, "add", title, *arguments)
    self.assert_success(result)
    prefix, separator, task_id = result.stdout.partition(" ")
    self.assertEqual(prefix, "created")
    self.assertEqual(separator, " ")
    task_id = task_id.rstrip("\n")
    self.assertRegex(task_id, r"^[0-9a-f]{32}$")
    return task_id

  def test_complete_cli_workflow_and_isolated_malformed_read(self) -> None:
    overdue_id = self.add_task(
      "Prepare report",
      "--due-date",
      "2026-08-04",
      "--tag",
      "Work",
      "--tag",
      "focus",
      "--repeat",
      "daily",
    )
    future_id = self.add_task(
      "Plan meeting",
      "--due-date",
      "2026-08-06",
      "--tag",
      "work",
      "--repeat",
      "weekly",
    )
    due_today_id = self.add_task(
      "Review docs",
      "--due-date",
      "2026-08-05",
      "--tag",
      "docs",
    )

    first_list = self.run_cli(self.data_path, "list")
    second_list = self.run_cli(self.data_path, "list")
    self.assert_success(first_list)
    self.assertEqual(first_list.stdout, second_list.stdout)
    rows = first_list.stdout.splitlines()
    self.assertEqual(rows[0], "id\tstatus\tdue_date\ttags\ttitle\trepeat")
    listed_ids = [json.loads(row.split("\t", 1)[0]) for row in rows[1:]]
    self.assertEqual(listed_ids, sorted(listed_ids))
    self.assertEqual(
      set(listed_ids),
      {overdue_id, future_id, due_today_id},
    )

    overdue = self.run_cli(
      self.data_path,
      "list",
      "--reference-date",
      "2026-08-05",
      "--overdue",
      "--tag",
      "work",
      "--tag",
      "focus",
      "--tag-mode",
      "all",
      "--repeat",
      "daily",
    )
    self.assert_success(overdue)
    self.assertIn(overdue_id, overdue.stdout)
    self.assertIn("Prepare report", overdue.stdout)
    self.assertNotIn("Plan meeting", overdue.stdout)
    self.assertNotIn("Review docs", overdue.stdout)

    due_today = self.run_cli(
      self.data_path,
      "list",
      "--reference-date",
      "2026-08-05",
      "--due-on",
      "2026-08-05",
      "--tag",
      "docs",
    )
    self.assert_success(due_today)
    self.assertIn(due_today_id, due_today.stdout)
    self.assertNotIn("Prepare report", due_today.stdout)

    completed = self.run_cli(self.data_path, "done", overdue_id)
    self.assert_success(completed)
    completed_list = self.run_cli(
      self.data_path,
      "list",
      "--status",
      "completed",
    )
    self.assert_success(completed_list)
    self.assertIn(overdue_id, completed_list.stdout)
    self.assertIn('"completed"', completed_list.stdout)

    restored = self.run_cli(self.data_path, "restore", overdue_id)
    self.assert_success(restored)
    pending_list = self.run_cli(
      self.data_path,
      "list",
      "--status",
      "pending",
    )
    self.assert_success(pending_list)
    self.assertIn(overdue_id, pending_list.stdout)
    self.assertIn('"pending"', pending_list.stdout)

    persisted_before_failure = self.data_path.read_bytes()
    persisted_document = json.loads(persisted_before_failure)
    persisted_by_id = {
      task["id"]: task for task in persisted_document["tasks"]
    }
    self.assertEqual(persisted_by_id[overdue_id]["status"], "pending")
    self.assertEqual(persisted_by_id[future_id]["repeat"], "weekly")

    self.malformed_path.parent.mkdir(parents=True)
    self.malformed_path.write_text("{", encoding="utf-8")
    malformed = self.run_cli(self.malformed_path, "list")
    self.assert_clean_error(malformed, "ledger contains malformed JSON")
    self.assertEqual(self.data_path.read_bytes(), persisted_before_failure)

    valid_after_failure = self.run_cli(self.data_path, "list")
    self.assert_success(valid_after_failure)
    self.assertIn("Prepare report", valid_after_failure.stdout)


if __name__ == "__main__":
  unittest.main()
