"""Bind the reactor's original JUnit bytes to its successful terminal record."""

import argparse
import hashlib
import json
from pathlib import Path
import re
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


def _digest(content):
    return hashlib.sha256(content).hexdigest()


def _file_digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def _run_path(directory, run, suffix):
    if not re.fullmatch(r"PT-(WEB|ADM|MED|SCN)-[A-Za-z0-9-]+", run):
        raise ValueError("invalid reactor run ID")
    return directory / (run + suffix)


def _report(content):
    suite = ET.fromstring(content)
    cases = suite.findall("testcase")
    if (
        suite.tag != "testsuite"
        or not cases
        or suite.get("tests") != str(len(cases))
        or any(suite.get(field) != "0" for field in ("failures", "errors", "skipped"))
        or any(
            child.tag not in ("properties", "testcase", "system-out", "system-err")
            for child in suite
        )
        or any(
            not case.get("classname")
            or not case.get("name")
            or any(child.tag not in ("system-out", "system-err") for child in case)
            for case in cases
        )
    ):
        raise ValueError("empty, inconsistent or nonpassing reactor JUnit report")
    return {"sha256": _digest(content), "tests": len(cases)}


def _snapshot(repo, run, commit, directory):
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("invalid reactor commit")
    observed = _run_path(directory, run, ".commit").read_text().strip()
    if commit != observed:
        raise ValueError("reactor commit does not match")
    reports = {}
    repo = repo.resolve()
    for module, path in MODULE_DIRECTORIES:
        folder = repo / path / "target/surefire-reports"
        files = sorted(folder.glob("TEST-*.xml"))
        if not files:
            raise ValueError("missing original reactor JUnit reports for " + module)
        for file in files:
            if not file.is_file() or file != file.resolve():
                raise ValueError("reactor report must be a local regular file")
            reports[file.relative_to(repo).as_posix()] = _report(file.read_bytes())
    return {
        "schema": "pgpt-reactor-junit-v1",
        "runId": run,
        "targetCommit": commit,
        "startedAt": _run_path(directory, run, ".started").read_text().strip(),
        "completedAt": _run_path(directory, run, ".completed").read_text().strip(),
        "buildLogSha256": _file_digest(_run_path(directory, run, ".log")),
        "reports": reports,
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
    if _run_path(directory, run, ".exit").read_text().strip() != "0":
        raise ValueError("reactor execution is not successful")
    manifest = _run_path(directory, run, ".junit.json")
    content = manifest.read_bytes()
    if _serialize(_snapshot(repo, run, commit, directory)) != content:
        raise ValueError("reactor JUnit differs from the successful terminal record")
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
