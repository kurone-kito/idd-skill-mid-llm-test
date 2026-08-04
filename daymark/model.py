"""Validated task domain objects used by Daymark."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import date
from typing import Any
import re


class TaskValidationError(ValueError):
  """Raised when a task cannot represent valid Daymark state."""


_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_VALID_STATUSES = frozenset({"pending", "completed"})
_VALID_REPEATS = frozenset({"daily", "weekly"})
_TASK_FIELDS = frozenset(
  {"id", "title", "due_date", "tags", "status", "repeat"}
)


def _validate_id(value: Any) -> str:
  if not isinstance(value, str) or not value or value != value.strip():
    raise TaskValidationError("task id must be a non-empty string")
  if any(character.isspace() for character in value):
    raise TaskValidationError("task id must not contain whitespace")
  return value


def _validate_title(value: Any) -> str:
  if not isinstance(value, str):
    raise TaskValidationError("task title must be a non-empty string")
  title = value.strip()
  if not title:
    raise TaskValidationError("task title must be a non-empty string")
  return title


def _validate_due_date(value: Any) -> str | None:
  if value is None:
    return None
  if not isinstance(value, str) or not _DATE_PATTERN.fullmatch(value):
    raise TaskValidationError("due_date must be YYYY-MM-DD or null")
  try:
    date.fromisoformat(value)
  except ValueError as error:
    raise TaskValidationError("due_date must be YYYY-MM-DD or null") from error
  return value


def normalize_tags(values: Iterable[str] | None) -> tuple[str, ...]:
  """Return lower-case, trimmed, unique, deterministic tags."""

  if values is None:
    return ()
  if isinstance(values, (str, bytes, Mapping)):
    raise TaskValidationError("tags must be a sequence of strings")
  try:
    raw_values = tuple(values)
  except TypeError as error:
    raise TaskValidationError("tags must be a sequence of strings") from error

  normalized: set[str] = set()
  for value in raw_values:
    if not isinstance(value, str):
      raise TaskValidationError("tags must be a sequence of strings")
    tag = value.strip().lower()
    if not tag:
      raise TaskValidationError("tag values must be non-empty strings")
    normalized.add(tag)
  return tuple(sorted(normalized))


def _validate_status(value: Any) -> str:
  if not isinstance(value, str) or value not in _VALID_STATUSES:
    raise TaskValidationError("status must be pending or completed")
  return value


def _validate_repeat(value: Any) -> str | None:
  if value is None:
    return None
  if not isinstance(value, str) or value not in _VALID_REPEATS:
    raise TaskValidationError("repeat must be null, daily, or weekly")
  return value


@dataclass(frozen=True)
class Task:
  """A validated task record with stable JSON representation."""

  id: str
  title: str
  due_date: str | None = None
  tags: tuple[str, ...] = ()
  status: str = "pending"
  repeat: str | None = None

  def __post_init__(self) -> None:
    object.__setattr__(self, "id", _validate_id(self.id))
    object.__setattr__(self, "title", _validate_title(self.title))
    object.__setattr__(self, "due_date", _validate_due_date(self.due_date))
    object.__setattr__(self, "tags", normalize_tags(self.tags))
    object.__setattr__(self, "status", _validate_status(self.status))
    object.__setattr__(self, "repeat", _validate_repeat(self.repeat))

  @classmethod
  def create(
    cls,
    task_id: str,
    title: str,
    *,
    due_date: str | None = None,
    tags: Iterable[str] | None = None,
    repeat: str | None = None,
  ) -> "Task":
    return cls(
      task_id,
      title,
      due_date,
      tags if tags is not None else (),
      "pending",
      repeat,
    )

  @classmethod
  def from_dict(cls, payload: Mapping[str, Any]) -> "Task":
    if not isinstance(payload, Mapping):
      raise TaskValidationError("task record must be an object")
    missing = {"id", "title"} - payload.keys()
    if missing:
      raise TaskValidationError("task record requires id and title")
    unknown = set(payload) - _TASK_FIELDS
    if unknown:
      raise TaskValidationError("task record contains unknown fields")
    return cls(
      payload["id"],
      payload["title"],
      payload.get("due_date"),
      payload.get("tags", ()),
      payload.get("status", "pending"),
      payload.get("repeat"),
    )

  def to_dict(self) -> dict[str, Any]:
    return {
      "id": self.id,
      "title": self.title,
      "due_date": self.due_date,
      "tags": list(self.tags),
      "status": self.status,
      "repeat": self.repeat,
    }

  def complete(self) -> "Task":
    return Task(
      self.id,
      self.title,
      self.due_date,
      self.tags,
      "completed",
      self.repeat,
    )

  def restore(self) -> "Task":
    return Task(
      self.id,
      self.title,
      self.due_date,
      self.tags,
      "pending",
      self.repeat,
    )
