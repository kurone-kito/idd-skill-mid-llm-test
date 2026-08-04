"""Pure query operations for Daymark task planning."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import date, datetime
import re
from typing import Any

from .model import Task, TaskValidationError, normalize_tags


_VALID_STATUSES = frozenset({"pending", "completed"})
_VALID_TAG_MODES = frozenset({"all", "any"})
_VALID_REPEATS = frozenset({"daily", "weekly"})
_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _parse_date(value: Any, field_name: str) -> date:
  if isinstance(value, date) and not isinstance(value, datetime):
    return value
  if isinstance(value, str) and _DATE_PATTERN.fullmatch(value):
    try:
      return date.fromisoformat(value)
    except ValueError as error:
      raise TaskValidationError(
        f"{field_name} must be YYYY-MM-DD"
      ) from error
  raise TaskValidationError(f"{field_name} must be YYYY-MM-DD")


def _validate_repeat(value: Any) -> str | None:
  if value is None:
    return None
  if not isinstance(value, str) or value not in _VALID_REPEATS:
    raise TaskValidationError("repeat must be null, daily, or weekly")
  return value


def _validate_status(value: Any) -> str | None:
  if value is None:
    return None
  if not isinstance(value, str) or value not in _VALID_STATUSES:
    raise TaskValidationError("status must be pending or completed")
  return value


def query_tasks(
  tasks: Iterable[Task],
  *,
  reference_date: date | str,
  due_on: date | str | None = None,
  due_by: date | str | None = None,
  overdue: bool = False,
  tags: Iterable[str] | None = None,
  tag_mode: str = "all",
  repeat: str | None = None,
  status: str | None = None,
) -> list[Task]:
  """Return matching tasks in the stable ID order used by ``list``.

  Repeat values are metadata filters. This function never expands recurring
  tasks or changes their stored due dates.
  """

  reference = _parse_date(reference_date, "reference_date")
  exact_due = (
    _parse_date(due_on, "due_on") if due_on is not None else None
  )
  upper_due = (
    _parse_date(due_by, "due_by") if due_by is not None else None
  )
  if tag_mode not in _VALID_TAG_MODES:
    raise TaskValidationError("tag_mode must be all or any")
  requested_tags = normalize_tags(tags)
  requested_repeat = _validate_repeat(repeat)
  requested_status = _validate_status(status)

  matches: list[Task] = []
  for task in tasks:
    task_due = date.fromisoformat(task.due_date) if task.due_date else None
    if requested_status is not None and task.status != requested_status:
      continue
    if exact_due is not None and task_due != exact_due:
      continue
    if upper_due is not None and (task_due is None or task_due > upper_due):
      continue
    if overdue and (
      task.status != "pending" or task_due is None or task_due >= reference
    ):
      continue
    if requested_tags:
      task_tags = set(task.tags)
      requested = set(requested_tags)
      if tag_mode == "all" and not requested <= task_tags:
        continue
      if tag_mode == "any" and not requested & task_tags:
        continue
    if requested_repeat is not None and task.repeat != requested_repeat:
      continue
    matches.append(task)
  return sorted(matches, key=lambda task: task.id)
