from __future__ import annotations

from datetime import date, datetime
import unittest

from daymark import Task, TaskValidationError, query_tasks


REFERENCE_DATE = date(2026, 8, 5)


def sample_tasks() -> list[Task]:
  return [
    Task(
      "task-c",
      "Future weekly",
      "2026-08-06",
      ("home", "work"),
      repeat="weekly",
    ),
    Task(
      "task-a",
      "Past daily",
      "2026-08-04",
      ("urgent", "work"),
      repeat="daily",
    ),
    Task(
      "task-b",
      "Today completed",
      "2026-08-05",
      ("work",),
      status="completed",
    ),
    Task("task-d", "No due date", tags=("home",)),
  ]


class QueryTests(unittest.TestCase):
  def test_date_boundaries_and_overdue_are_reference_date_based(self) -> None:
    tasks = sample_tasks()

    self.assertEqual(
      [task.id for task in query_tasks(
        tasks,
        reference_date=REFERENCE_DATE,
        due_on="2026-08-05",
      )],
      ["task-b"],
    )
    self.assertEqual(
      [task.id for task in query_tasks(
        tasks,
        reference_date=REFERENCE_DATE,
        due_by="2026-08-05",
      )],
      ["task-a", "task-b"],
    )
    self.assertEqual(
      [task.id for task in query_tasks(
        tasks,
        reference_date="2026-08-05",
        overdue=True,
      )],
      ["task-a"],
    )

  def test_tags_support_all_any_and_empty_filters(self) -> None:
    tasks = sample_tasks()

    self.assertEqual(
      [task.id for task in query_tasks(
        tasks,
        reference_date=REFERENCE_DATE,
        tags=("WORK", "urgent"),
        tag_mode="all",
      )],
      ["task-a"],
    )
    self.assertEqual(
      [task.id for task in query_tasks(
        tasks,
        reference_date=REFERENCE_DATE,
        tags=("urgent", "missing"),
        tag_mode="any",
      )],
      ["task-a"],
    )
    self.assertEqual(
      [task.id for task in query_tasks(
        tasks,
        reference_date=REFERENCE_DATE,
        tags=(),
        tag_mode="any",
      )],
      ["task-a", "task-b", "task-c", "task-d"],
    )

  def test_repeat_filter_is_metadata_only_and_results_are_sorted(self) -> None:
    tasks = sample_tasks()
    before = list(tasks)

    daily = query_tasks(
      tasks,
      reference_date=REFERENCE_DATE,
      repeat="daily",
    )
    weekly = query_tasks(
      tasks,
      reference_date=REFERENCE_DATE,
      due_by="2026-08-06",
      repeat="weekly",
    )

    self.assertEqual([task.id for task in daily], ["task-a"])
    self.assertEqual([task.id for task in weekly], ["task-c"])
    self.assertEqual(tasks, before)
    self.assertEqual(daily[0].repeat, "daily")
    self.assertEqual(weekly[0].due_date, "2026-08-06")

  def test_invalid_query_inputs_are_rejected(self) -> None:
    for kwargs, message in (
      ({"reference_date": "2026-02-30"}, "reference_date"),
      ({"reference_date": datetime(2026, 8, 5)}, "reference_date"),
      ({"reference_date": REFERENCE_DATE, "due_on": "2026-8-5"}, "due_on"),
      ({"reference_date": REFERENCE_DATE, "due_on": "20260805"}, "due_on"),
      ({"reference_date": REFERENCE_DATE, "tag_mode": "missing"}, "tag_mode"),
      ({"reference_date": REFERENCE_DATE, "overdue": "false"}, "overdue"),
      ({"reference_date": REFERENCE_DATE, "repeat": "monthly"}, "repeat"),
      ({"reference_date": REFERENCE_DATE, "status": "missing"}, "status"),
    ):
      with self.subTest(kwargs=kwargs):
        with self.assertRaisesRegex(TaskValidationError, message):
          query_tasks(sample_tasks(), **kwargs)


if __name__ == "__main__":
  unittest.main()
