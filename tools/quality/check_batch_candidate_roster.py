"""Check independently pinned Batch expectations against a finished run's exact JUnit outputs.

WBS-G08 / SS354 / 451 / BUG-3605 / PT-OPS-G08-RST001..008.
"""

import argparse
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from verify_maven_sbom import SHA256, unique_fields


SOURCE = re.compile(r"[0-9a-f]{40}")
RUN = re.compile(r"PT-WEB-[A-Za-z0-9-]+")
CLASS = re.compile(r"[A-Za-z_$][A-Za-z0-9_$]*(?:\.[A-Za-z_$][A-Za-z0-9_$]*)*")
EXPECTED_FIELDS = {"schema", "targetCommit", "suites"}
RECEIPT_FIELDS = {"schema", "runId", "targetCommit", "exitCode", "reports"}


def pinned_bytes(path, expected):
    if not SHA256.fullmatch(expected) or path.is_symlink() or not path.is_file():
        raise ValueError("a regular file and its fixed SHA-256 are required")
    contents = path.read_bytes()
    if hashlib.sha256(contents).hexdigest() != expected.lower():
        raise ValueError("SHA-256 mismatch in candidate inputs")
    return contents


def record(path, expected, fields, schema):
    value = json.loads(pinned_bytes(path, expected), object_pairs_hook=unique_fields)
    if not isinstance(value, dict) or value.keys() != fields or value["schema"] != schema:
        raise ValueError("invalid candidate record schema")
    if not isinstance(value["targetCommit"], str) or not SOURCE.fullmatch(value["targetCommit"]):
        raise ValueError("invalid candidate source")
    return value


def valid_case(owner, name):
    return (isinstance(owner, str) and CLASS.fullmatch(owner)
            and isinstance(name, str) and bool(name.strip()) and name.isprintable())


def expected_suites(suites):
    if not isinstance(suites, dict) or not suites:
        raise ValueError("Batch suite expectations are required")
    expected = {}
    for name, cases in suites.items():
        if not CLASS.fullmatch(name) or not isinstance(cases, list) or not cases:
            raise ValueError("invalid or empty Batch suite expectation")
        members = set()
        for case in cases:
            if not isinstance(case, list) or len(case) != 2 or not valid_case(*case):
                raise ValueError("invalid Batch test case expectation")
            key = tuple(case)
            if key in members:
                raise ValueError("duplicate Batch test case expectation")
            members.add(key)
        expected[f"TEST-{name}.xml"] = (name, members)
    return expected


def verify_report(contents, name, expected):
    suite = ET.fromstring(contents)
    cases = suite.findall("testcase")
    if (suite.tag != "testsuite" or suite.get("name") != name
            or suite.get("tests") != str(len(cases))
            or any(suite.get(field) != "0" for field in ("failures", "errors", "skipped"))
            or any(node.tag not in ("testcase", "properties", "system-out", "system-err")
                   for node in suite)):
        raise ValueError("inconsistent or nonpassing Batch report")
    checked = set()
    for case in cases:
        member = (case.get("classname"), case.get("name"))
        if (not valid_case(*member) or member in checked
                or any(node.tag not in ("system-out", "system-err") for node in case)):
            raise ValueError("invalid, duplicate, or nonpassing Batch test case")
        checked.add(member)
    if checked != expected:
        raise ValueError("Batch case IDs differ from approved expectations")


def verify_roster(profile, profile_sha256, receipt, receipt_sha256, report_directory):
    plan = record(profile, profile_sha256, EXPECTED_FIELDS, "pgpt-batch-roster-v1")
    execution = record(receipt, receipt_sha256, RECEIPT_FIELDS, "pgpt-batch-junit-receipt-v1")
    if (plan["targetCommit"] != execution["targetCommit"]
            or not isinstance(execution["runId"], str) or not RUN.fullmatch(execution["runId"])
            or type(execution["exitCode"]) is not int or execution["exitCode"] != 0):
        raise ValueError("Batch receipt must be a successful run of the planned source")
    expected = expected_suites(plan["suites"])
    reports = execution["reports"]
    if (not isinstance(reports, dict) or reports.keys() != expected.keys()
            or {entry.name for entry in report_directory.glob("TEST-*.xml")} != expected.keys()):
        raise ValueError("Batch report inventory differs from approved expectations")
    for filename, (name, cases) in expected.items():
        verify_report(pinned_bytes(report_directory / filename, reports[filename]), name, cases)
    return {
        "runId": execution["runId"],
        "targetCommit": plan["targetCommit"],
        "suites": len(expected),
        "testCases": sum(len(cases) for _, cases in expected.values()),
        "profileSha256": profile_sha256.lower(),
        "receiptSha256": receipt_sha256.lower(),
        "result": "BATCH_ROSTER_MATCH",
        "formalAcceptance": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profile", type=Path)
    parser.add_argument("profile_sha256")
    parser.add_argument("receipt", type=Path)
    parser.add_argument("receipt_sha256")
    parser.add_argument("report_directory", type=Path)
    try:
        result = verify_roster(**vars(parser.parse_args()))
    except (ET.ParseError, OSError, TypeError, ValueError) as error:
        parser.exit(1, f"Batch candidate roster did not match: {error}\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
