"""Validate the completed stage journal of an explicitly selected local PT run (SS354)."""

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path


def _file(directory, name):
    path = directory / name
    if not path.is_file() or path.resolve() != path:
        raise ValueError(f"missing or noncanonical stage artifact: {name}")
    return path


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate stage record field")
        result[key] = value
    return result


def _record(directory, label, role):
    path = _file(directory, f"{label}-{role}.safe.json")
    record = json.loads(path.read_bytes(), object_pairs_hook=_unique_object)
    if not isinstance(record, dict):
        raise ValueError(f"{label}: malformed stage record")
    return record


def _instant(value):
    if not isinstance(value, str):
        raise ValueError("stage timestamp required")
    observed = datetime.fromisoformat(value)
    if observed.tzinfo is None:
        raise ValueError("stage timestamp requires an offset")
    return observed


def verify_completed_stages(directory, *, cwd, commands, accepted_exits):
    """Return bound numeric stage outcomes. A caller supplies the fixed stage roster and scope."""
    directory = Path(directory)
    if not directory.is_dir() or directory.resolve() != directory:
        raise ValueError("canonical stage directory required")
    if not commands or commands.keys() != accepted_exits.keys() or any(
        not isinstance(label, str) or not re.fullmatch(r"[a-z][a-z0-9-]*", label)
        for label in commands
    ):
        raise ValueError("unique declared stage roster required")
    for label, command in commands.items():
        exits = accepted_exits[label]
        if (
            not isinstance(command, list)
            or not command
            or not all(isinstance(part, str) for part in command)
            or not isinstance(exits, (tuple, set, frozenset))
            or not exits
            or not all(type(code) is int for code in exits)
        ):
            raise ValueError(f"{label}: exact command and numeric outcome policy required")
    cwd = Path(cwd)
    if not cwd.is_dir() or cwd.resolve() != cwd:
        raise ValueError("canonical stage working directory required")

    for role in ("begin", "process", "exit"):
        suffix = f"-{role}.safe.json"
        observed = {p.name.removesuffix(suffix) for p in directory.glob(f"*{suffix}")}
        if observed != commands.keys():
            raise ValueError(f"incomplete or unexpected {role} stage roster")

    results = {}
    run_owner = None
    for label, command in commands.items():
        began = _record(directory, label, "begin")
        process = _record(directory, label, "process")
        terminal = _record(directory, label, "exit")
        start = began.get("startUTC")
        for record in (began, process, terminal):
            if (record.get("command"), record.get("cwd"), record.get("startUTC")) != (
                command,
                str(cwd),
                start,
            ):
                raise ValueError(f"{label}: stage context differs from expected invocation")
        pid, owner = process.get("pid"), process.get("ownerPid")
        if type(pid) is not int or type(owner) is not int or min(pid, owner) < 1 or pid == owner:
            raise ValueError(f"{label}: missing process ownership record")
        if run_owner is None:
            run_owner = owner
        elif owner != run_owner:
            raise ValueError(f"{label}: stage belongs to a different process owner")
        ended = terminal.get("endUTC")
        if _instant(ended) < _instant(start):
            raise ValueError(f"{label}: terminal precedes start")
        code = terminal.get("actualExit")
        if (
            type(code) is not int
            or code not in accepted_exits[label]
            or terminal.get("timedOut") is not False
        ):
            raise ValueError(f"{label}: unacceptable or unknown stage outcome")
        for stream in ("stdout", "stderr"):
            with _file(directory, f"{label}.{stream}").open("rb") as source:
                observed = hashlib.file_digest(source, "sha256").hexdigest()
            if observed != terminal.get(f"{stream}Sha256"):
                raise ValueError(f"{label}: {stream} differs from recorded bytes")
        results[label] = {"actualExit": code, "startUTC": start, "endUTC": ended}
    return results
