"""Atomic, versioned JSON persistence for Daymark tasks."""

from __future__ import annotations

from collections.abc import Callable, Iterable
import json
import os
from pathlib import Path
import tempfile
from typing import Any
import uuid

from .model import Task, TaskValidationError


class LedgerError(Exception):
    """Raised for stable, user-facing ledger failures."""


class Ledger:
    """Read and write a version-1 task ledger without partial replacement."""

    SCHEMA_VERSION = 1

    def __init__(
        self,
        path: str | os.PathLike[str],
        *,
        id_factory: Callable[[], str] | None = None,
    ) -> None:
        self.path = Path(path)
        self._id_factory = id_factory or (lambda: uuid.uuid4().hex)

    def load(self) -> list[Task]:
        if not self.path.exists():
            return []
        try:
            text = self.path.read_text(encoding="utf-8")
            document = json.loads(text)
        except (OSError, UnicodeError) as error:
            raise LedgerError("could not read ledger") from error
        except json.JSONDecodeError as error:
            raise LedgerError("ledger contains malformed JSON") from error

        if not isinstance(document, dict):
            raise LedgerError("ledger document must be an object")
        if document.get("schema_version") != self.SCHEMA_VERSION:
            raise LedgerError("ledger schema version is unsupported")
        records = document.get("tasks")
        if not isinstance(records, list):
            raise LedgerError("ledger tasks must be an array")

        tasks: list[Task] = []
        try:
            for record in records:
                tasks.append(Task.from_dict(record))
        except TaskValidationError as error:
            raise LedgerError(f"invalid task record: {error}") from error
        self._ensure_unique_ids(tasks)
        return tasks

    def save(self, tasks: Iterable[Task]) -> None:
        """Serialize all tasks, then atomically replace the destination."""

        try:
            records = [task.to_dict() for task in tasks]
            self._ensure_unique_record_ids(records)
            records.sort(key=lambda record: record["id"])
            document = {"schema_version": self.SCHEMA_VERSION, "tasks": records}
            serialized = json.dumps(
                document,
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            ) + "\n"
        except LedgerError:
            raise
        except Exception as error:
            raise LedgerError("could not serialize ledger") from error

        temporary_path: str | None = None
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            descriptor, temporary_path = tempfile.mkstemp(
                prefix=f".{self.path.name}.",
                suffix=".tmp",
                dir=self.path.parent,
            )
            with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(serialized)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary_path, self.path)
            temporary_path = None
        except OSError as error:
            raise LedgerError("could not write ledger") from error
        finally:
            if temporary_path is not None:
                try:
                    os.unlink(temporary_path)
                except OSError:
                    pass

    def add(
        self,
        title: str,
        *,
        due_date: str | None = None,
        tags: Iterable[str] | None = None,
        repeat: str | None = None,
    ) -> Task:
        tasks = self.load()
        task = Task.create(
            self._id_factory(),
            title,
            due_date=due_date,
            tags=tags,
            repeat=repeat,
        )
        if any(existing.id == task.id for existing in tasks):
            raise LedgerError("generated task id already exists")
        self.save([*tasks, task])
        return task

    def update(self, task: Task) -> Task:
        tasks = self.load()
        if not any(existing.id == task.id for existing in tasks):
            raise LedgerError("task id was not found")
        self.save([task if existing.id == task.id else existing for existing in tasks])
        return task

    @staticmethod
    def _ensure_unique_ids(tasks: Iterable[Task]) -> None:
        ids = [task.id for task in tasks]
        if len(ids) != len(set(ids)):
            raise LedgerError("ledger contains duplicate task ids")

    @staticmethod
    def _ensure_unique_record_ids(records: list[dict[str, Any]]) -> None:
        ids = [record.get("id") for record in records]
        if len(ids) != len(set(ids)):
            raise LedgerError("ledger contains duplicate task ids")
