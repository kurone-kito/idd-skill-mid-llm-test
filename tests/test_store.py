from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from daymark import Ledger, LedgerError, Task, TaskValidationError


class StoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.path = Path(self.tempdir.name) / "tasks.json"

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_task_normalizes_values_and_serializes(self) -> None:
        task = Task(
            "task-1",
            "  Write tests  ",
            "2026-08-05",
            (" Work ", "work", "Tier-A"),
            repeat="daily",
        )

        self.assertEqual(task.title, "Write tests")
        self.assertEqual(task.tags, ("tier-a", "work"))
        self.assertEqual(task.to_dict()["tags"], ["tier-a", "work"])

    def test_invalid_task_data_has_stable_validation_errors(self) -> None:
        with self.assertRaisesRegex(
            TaskValidationError, "task id must be a non-empty string"
        ):
            Task("", "title")

        with self.assertRaisesRegex(
            TaskValidationError, "task id must not contain whitespace"
        ):
            Task("task 1", "title")

        with self.assertRaisesRegex(
            TaskValidationError, "task title must be a non-empty string"
        ):
            Task("id", "  ")

        for value in ("2026-8-5", "2026-02-30"):
            with self.subTest(due_date=value):
                with self.assertRaisesRegex(
                    TaskValidationError, "due_date must be YYYY-MM-DD or null"
                ):
                    Task("id", "title", due_date=value)

        with self.assertRaisesRegex(
            TaskValidationError, "status must be pending or completed"
        ):
            Task("id", "title", status="bad")

        with self.assertRaisesRegex(
            TaskValidationError, "repeat must be null, daily, or weekly"
        ):
            Task("id", "title", repeat="monthly")

        with self.assertRaisesRegex(
            TaskValidationError, "tags must be a sequence of strings"
        ):
            Task("id", "title", tags="work")

        with self.assertRaisesRegex(
            TaskValidationError, "tags must be a sequence of strings"
        ):
            Task.create("id", "title", tags="work")

    def test_add_round_trip_and_injected_id(self) -> None:
        ledger = Ledger(self.path, id_factory=lambda: "task-1")
        created = ledger.add("Write tests", tags=["work"])

        self.assertEqual(created.id, "task-1")
        self.assertEqual(ledger.load(), [created])
        document = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertEqual(document["schema_version"], 1)

    def test_missing_file_is_an_empty_ledger(self) -> None:
        self.assertEqual(Ledger(self.path).load(), [])

    def test_malformed_file_is_a_stable_ledger_error(self) -> None:
        self.path.write_text("{", encoding="utf-8")

        with self.assertRaisesRegex(LedgerError, "ledger contains malformed JSON"):
            Ledger(self.path).load()

    def test_unsupported_schema_and_duplicate_ids_are_rejected(self) -> None:
        self.path.write_text(
            json.dumps({"schema_version": 99, "tasks": []}), encoding="utf-8"
        )
        with self.assertRaisesRegex(LedgerError, "schema version is unsupported"):
            Ledger(self.path).load()

        ledger = Ledger(self.path)
        with self.assertRaisesRegex(LedgerError, "duplicate task ids"):
            ledger.save([Task("same", "one"), Task("same", "two")])

    def test_serialization_failure_preserves_existing_file(self) -> None:
        ledger = Ledger(self.path)
        ledger.save([Task("task-1", "Original")])
        original = self.path.read_bytes()

        class BrokenTask:
            def to_dict(self) -> dict[str, str]:
                raise RuntimeError("test serializer failure")

        with self.assertRaisesRegex(LedgerError, "could not serialize ledger"):
            ledger.save([BrokenTask()])

        self.assertEqual(self.path.read_bytes(), original)

    def test_replace_failure_preserves_existing_file(self) -> None:
        ledger = Ledger(self.path)
        ledger.save([Task("task-1", "Original")])
        original = self.path.read_bytes()

        with patch("daymark.store.os.replace", side_effect=OSError("replace failed")):
            with self.assertRaisesRegex(LedgerError, "could not write ledger"):
                ledger.save([Task("task-1", "Updated")])

        self.assertEqual(self.path.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
