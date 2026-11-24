"""Reconcile JaCoCo counters with the reported executable method detail."""

from collections import Counter
import re


REQUIRED_COVERAGE = frozenset(("LINE", "METHOD", "CLASS", "BRANCH"))
JACOCO_COUNTERS = REQUIRED_COVERAGE | {"INSTRUCTION", "COMPLEXITY"}


def coverage_rows(element):
    counters = {}
    for counter in element.findall("counter"):
        metric = counter.get("type")
        missed = counter.get("missed", "")
        covered = counter.get("covered", "")
        if (
            metric not in JACOCO_COUNTERS
            or metric in counters
            or not re.fullmatch(r"[0-9]+", missed)
            or not re.fullmatch(r"[0-9]+", covered)
        ):
            raise ValueError("invalid or duplicated JaCoCo counter")
        counters[metric] = {"missed": int(missed), "covered": int(covered)}
    return counters


def add_covered(nodes, counters, omitted=()):
    totals = Counter()
    for node in nodes:
        totals.update({metric: row["covered"] for metric, row in counters[node].items()
                       if metric not in omitted})
    return totals


def validate_class_detail(cls, counters):
    methods = cls.findall("method")
    signatures = [(method.get("name"), method.get("desc")) for method in methods]
    if (any(not all(signature) for signature in signatures)
            or len(signatures) != len(set(signatures))):
        raise ValueError("missing or duplicated JaCoCo method signature")
    if set(cls.iter("method")) != set(methods):
        raise ValueError("misplaced JaCoCo method detail")
    if any(row["missed"] for node in [cls, *methods] for row in counters[node].values()):
        raise ValueError("JaCoCo report contains missed class or method counters")
    for method in methods:
        values = add_covered([method], counters)
        if values["METHOD"] != 1 or not values["INSTRUCTION"]:
            raise ValueError("missing executable JaCoCo method counters")
    expected = add_covered(methods, counters, omitted=("LINE",))
    expected["CLASS"] = int(bool(methods))
    if add_covered([cls], counters, omitted=("LINE",)) != expected:
        raise ValueError("class JaCoCo counters disagree with method detail")
    return methods


def validate_selected_class_coverage(report, subject, *, require_branch):
    classes = [element for element in report.iter("class") if element.get("name") == subject]
    if len(classes) != 1:
        raise ValueError("missing or duplicated JaCoCo class for selected scope")
    cls = classes[0]
    counters = {cls: coverage_rows(cls)}
    counters.update((method, coverage_rows(method)) for method in cls.findall("method"))
    validate_class_detail(cls, counters)
    required = {"INSTRUCTION", "LINE", "METHOD", "CLASS"}
    if require_branch:
        required.add("BRANCH")
    rows = counters[cls]
    if not required <= rows.keys() or any(rows[metric]["covered"] == 0 for metric in required):
        raise ValueError("selected JaCoCo class coverage is incomplete")
    return rows
