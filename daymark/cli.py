"""Command-line boundary for the Daymark task ledger."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence

from .model import Task, TaskValidationError
from .store import Ledger, LedgerError


def _build_parser() -> argparse.ArgumentParser:
  parser = argparse.ArgumentParser(
    prog="python -m daymark",
    description="Manage an offline Daymark task ledger.",
  )
  parser.add_argument(
    "--data",
    required=True,
    type=Path,
    help="explicit JSON ledger path",
  )
  commands = parser.add_subparsers(dest="command", required=True)

  add = commands.add_parser("add", help="create a task")
  add.add_argument("title")
  add.add_argument("--due-date")
  add.add_argument("--tag", action="append", default=[])
  add.add_argument("--repeat", choices=("daily", "weekly"))

  list_tasks = commands.add_parser("list", help="list tasks")
  list_tasks.add_argument(
    "--status",
    choices=("pending", "completed", "all"),
    default="all",
  )

  for command, help_text in (
    ("done", "complete a task"),
    ("restore", "return a task to pending"),
  ):
    transition = commands.add_parser(command, help=help_text)
    transition.add_argument("task_id")

  return parser


def _render_task(task: Task) -> str:
  fields = (
    task.id,
    task.status,
    task.due_date or "-",
    ",".join(task.tags) or "-",
    task.title,
  )
  return "\t".join(json.dumps(field, ensure_ascii=False) for field in fields)


def _run_add(args: argparse.Namespace, ledger: Ledger) -> None:
  task = ledger.add(
    args.title,
    due_date=args.due_date,
    tags=args.tag,
    repeat=args.repeat,
  )
  print(f"created {task.id}")


def _run_list(args: argparse.Namespace, ledger: Ledger) -> None:
  tasks = ledger.load()
  if args.status != "all":
    tasks = [task for task in tasks if task.status == args.status]
  tasks.sort(key=lambda task: task.id)
  print("id\tstatus\tdue_date\ttags\ttitle")
  for task in tasks:
    print(_render_task(task))


def _find_task(ledger: Ledger, task_id: str) -> Task:
  for task in ledger.load():
    if task.id == task_id:
      return task
  raise LedgerError("task id was not found")


def _run_transition(args: argparse.Namespace, ledger: Ledger) -> None:
  task = _find_task(ledger, args.task_id)
  updated = task.complete() if args.command == "done" else task.restore()
  ledger.update(updated)
  print(f"updated {updated.id}")


def main(argv: Sequence[str] | None = None) -> int:
  args = _build_parser().parse_args(argv)
  ledger = Ledger(args.data)
  try:
    if args.command == "add":
      _run_add(args, ledger)
    elif args.command == "list":
      _run_list(args, ledger)
    else:
      _run_transition(args, ledger)
  except (LedgerError, TaskValidationError) as error:
    print(f"error: {error}", file=sys.stderr)
    return 2
  return 0
