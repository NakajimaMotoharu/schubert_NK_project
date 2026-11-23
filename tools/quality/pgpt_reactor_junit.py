"""Bind the original reactor quality artifacts to its successful terminal record."""

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET


MODULE_DIRECTORIES = (
    ("characterization", "program/characterization"),
    ("protocol", "src/schubert-nk-protocol"),
    ("storage", "src/schubert-nk-storage"),
    ("bootstrap", "src/schubert-nk-bootstrap"),
    ("api", "src/schubert-nk-api"),
    ("web", "src/schubert-nk-web"),
    ("batch", "src/schubert-nk-batch"),
)
TERMINAL_TIMESTAMP = re.compile(
    r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}"
    r"(?:\.[0-9]{1,6})?(?:Z|[+-](?:[01][0-9]|2[0-3]):[0-5][0-9])"
)


def _digest(content):
    return hashlib.sha256(content).hexdigest()


def _file_digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def _run_path(directory, run, suffix):
    if not re.fullmatch(r"PT-(WEB|ADM|MED|SCN)-[A-Za-z0-9-]+", run):
        raise ValueError("invalid reactor run ID")
    return directory / (run + suffix)


def reactor_run_record(directory, run, suffix):
    """Locate an existing regular record under its own run path."""
    path = _run_path(directory, run, suffix)
    if not path.exists() and not path.is_symlink():
        raise FileNotFoundError(path)
    if not path.is_file() or path.absolute() != path.resolve():
        raise ValueError("reactor run record must be a local regular file")
    return path


def _report(content, module_cases):
    suite = ET.fromstring(content)
    cases = suite.findall("testcase")
    if (
        suite.tag != "testsuite"
        or not (suite.get("name") or "").strip()
        or not cases
        or suite.get("tests") != str(len(cases))
        or any(suite.get(field) != "0" for field in ("failures", "errors", "skipped"))
        or any(
            child.tag not in ("properties", "testcase", "system-out", "system-err")
            for child in suite
        )
        or any(
            not (case.get("classname") or "").strip()
            or not (case.get("name") or "").strip()
            or any(child.tag not in ("system-out", "system-err") for child in case)
            for case in cases
        )
    ):
        raise ValueError("empty, inconsistent or nonpassing reactor JUnit report")
    case_ids = {(case.get("classname"), case.get("name")) for case in cases}
    if len(case_ids) != len(cases) or module_cases & case_ids:
        raise ValueError("duplicate reactor JUnit case")
    module_cases.update(case_ids)
    return {"sha256": _digest(content), "tests": len(cases)}


def compiled_class_paths(directory):
    if not directory.is_dir() or directory.absolute() != directory.resolve():
        raise ValueError("missing or redirected compiled Main directory")
    classes = {}
    for path in directory.rglob("*"):
        if path.is_symlink():
            raise ValueError("redirected compiled Main input")
        if path.is_file() and path.suffix == ".class":
            name = path.relative_to(directory).with_suffix("").as_posix().replace("/", ".")
            if name in classes:
                raise ValueError("duplicate compiled Main class name")
            classes[name] = path
    return classes


def quality_artifact_hashes(target, module):
    coverage = ("jacoco.exec", "site/jacoco/jacoco.xml", "site/jacoco/jacoco.csv")
    reports = [target / path for path in coverage]
    if module != "characterization":
        reports.append(target / "spotbugsXml.xml")
    classes = compiled_class_paths(target / "classes")
    if not classes:
        raise ValueError("missing compiled Main classes for " + module)
    hashes = {}
    for path in [*reports, *classes.values()]:
        if not path.is_file() or path.absolute() != path.resolve() or path.stat().st_size == 0:
            raise ValueError("missing, empty or redirected reactor quality artifact for " + module)
        hashes[path.relative_to(target).as_posix()] = _file_digest(path)
    return hashes


def _terminal_instant(value):
    if not TERMINAL_TIMESTAMP.fullmatch(value):
        raise ValueError("invalid reactor timestamp")
    try:
        return datetime.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("invalid reactor timestamp") from exc


def _snapshot(repo, run, commit, directory):
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("invalid reactor commit")
    observed = reactor_run_record(directory, run, ".commit").read_text().strip()
    if commit != observed:
        raise ValueError("reactor commit does not match")
    branch = subprocess.check_output(["git", "branch", "--show-current"], cwd=repo,
                                     text=True).strip()
    if not branch or branch != reactor_run_record(directory, run, ".branch").read_text().strip():
        raise ValueError("reactor branch does not match")
    started = reactor_run_record(directory, run, ".started").read_text().strip()
    completed = reactor_run_record(directory, run, ".completed").read_text().strip()
    if _terminal_instant(started) > _terminal_instant(completed):
        raise ValueError("reactor completion precedes start")
    reports = {}
    quality = {}
    repo = repo.resolve()
    for module, path in MODULE_DIRECTORIES:
        target = repo / path / "target"
        folder = target / "surefire-reports"
        files = sorted(folder.glob("TEST-*.xml"))
        if not files:
            raise ValueError("missing original reactor JUnit reports for " + module)
        module_cases = set()
        for file in files:
            if not file.is_file() or file != file.resolve():
                raise ValueError("reactor report must be a local regular file")
            reports[file.relative_to(repo).as_posix()] = _report(file.read_bytes(), module_cases)
        for relative, sha256 in quality_artifact_hashes(target, module).items():
            quality[(target.relative_to(repo) / relative).as_posix()] = sha256
    return {
        "schema": "pgpt-reactor-junit-v3",
        "runId": run,
        "targetCommit": commit,
        "branch": branch,
        "startedAt": started,
        "completedAt": completed,
        "buildLogSha256": _file_digest(reactor_run_record(directory, run, ".log")),
        "reports": reports,
        "qualityArtifacts": quality,
    }


def _serialize(snapshot):
    return (json.dumps(snapshot, sort_keys=True, indent=2) + "\n").encode()


def capture_reactor_junit(repo, run, commit, directory=Path("/tmp")):
    """Called only on a successful build, before publishing its terminal exit marker."""
    manifest = _run_path(directory, run, ".junit.json")
    content = _serialize(_snapshot(repo, run, commit, directory))
    with manifest.open("xb") as stream:
        stream.write(content)
    return _digest(content)


def verify_reactor_junit(repo, run, commit, directory=Path("/tmp")):
    """Refuse a missing success marker or any difference from the terminal bytes."""
    if reactor_run_record(directory, run, ".exit").read_text().strip() != "0":
        raise ValueError("reactor execution is not successful")
    manifest = reactor_run_record(directory, run, ".junit.json")
    content = manifest.read_bytes()
    if _serialize(_snapshot(repo, run, commit, directory)) != content:
        raise ValueError("reactor quality input differs from the successful terminal record")
    return content


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_id")
    parser.add_argument("commit")
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[2]
    print(capture_reactor_junit(repo, args.run_id, args.commit))


if __name__ == "__main__":
    main()
