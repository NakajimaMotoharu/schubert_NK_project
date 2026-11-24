"""Reconcile JaCoCo counters with the reported executable method detail."""

from collections import Counter
import re

from classfile_code_metadata import decode as decode_classfile


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
    if not methods and add_covered([cls], counters)["LINE"]:
        raise ValueError("JaCoCo class without code reports covered lines")
    return methods


def validated_class_rows(cls):
    counters = {cls: coverage_rows(cls)}
    counters.update((method, coverage_rows(method)) for method in cls.findall("method"))
    validate_class_detail(cls, counters)
    return counters[cls]


def validate_selected_class_coverage(report, subject, *, require_branch):
    classes = [element for element in report.iter("class") if element.get("name") == subject]
    if len(classes) != 1:
        raise ValueError("missing or duplicated JaCoCo class for selected scope")
    rows = validated_class_rows(classes[0])
    required = {"INSTRUCTION", "LINE", "METHOD", "CLASS"}
    if require_branch:
        required.add("BRANCH")
    if not required <= rows.keys() or any(rows[metric]["covered"] == 0 for metric in required):
        raise ValueError("selected JaCoCo class coverage is incomplete")
    return rows


def validate_class_family_coverage(report, subject):
    """Check an inspected owner and its nested types, including natural no-Code rows."""
    result = {}
    for cls in report.iter("class"):
        name = cls.get("name", "")
        if name != subject and not name.startswith(subject + "$"):
            continue
        if name in result:
            raise ValueError("duplicate JaCoCo class in selected family")
        result[name] = validated_class_rows(cls)
    if subject not in result:
        raise ValueError("selected JaCoCo family has no outer class")
    return result


def coverage_class_names(physical_classes):
    """Return the XML class roster; package-info has no executable methods."""
    names = set()
    for binary_name, path in physical_classes.items():
        name = binary_name.replace(".", "/")
        if name.rsplit("/", 1)[-1] != "package-info":
            names.add(name)
            continue
        metadata = decode_classfile(path.read_bytes(), name + ".class")
        if any(method["hasCode"] for method in metadata["methods"]):
            raise ValueError("package-info unexpectedly contains executable code")
    return names


def validate_module_coverage(report, expected_classes):
    """Require complete module coverage with the actual compile roster and detail."""
    counters = {element: coverage_rows(element) for element in report.iter()}
    root = counters[report]
    packages = report.findall("package")
    names = [package.get("name") for package in packages]
    if (
        report.tag != "report"
        or not packages
        or None in names
        or len(names) != len(set(names))
        or not REQUIRED_COVERAGE <= root.keys()
        or any(root[metric]["covered"] == 0 for metric in REQUIRED_COVERAGE)
        or any(values["missed"] for values in root.values())
    ):
        raise ValueError("incomplete or nonpassing module JaCoCo report")
    aggregate_nodes = {report, *packages}
    if any(row["missed"] for node in packages for row in counters[node].values()):
        raise ValueError("JaCoCo report contains missed package counters")
    if add_covered([report], counters) != add_covered(packages, counters):
        raise ValueError("module JaCoCo counters disagree with package totals")
    if any(row["missed"] for element, rows in counters.items() if element not in aggregate_nodes
           for row in rows.values()):
        raise ValueError("JaCoCo report contains missed detail counters")
    classes = {}
    source_files = set()
    source_lines = set()
    for package in packages:
        package_name = package.attrib["name"]
        members = package.findall("class")
        for cls in members:
            name = cls.get("name", "")
            if not name or name.rpartition("/")[0] != package_name or name in classes:
                raise ValueError("missing, misplaced or duplicated JaCoCo class name")
            classes[name] = cls
        files = package.findall("sourcefile")
        file_names = [file.get("name") for file in files]
        if not all(file_names) or len(file_names) != len(set(file_names)):
            raise ValueError("missing or duplicated JaCoCo source file name")
        source_files.update(files)
        for file in files:
            lines = file.findall("line")
            numbers = set()
            for line in lines:
                number = line.get("nr", "")
                if (not re.fullmatch(r"[1-9][0-9]*", number) or number in numbers
                        or (line.get("mi"), line.get("mb")) != ("0", "0")
                        or not re.fullmatch(r"[1-9][0-9]*", line.get("ci", ""))
                        or not re.fullmatch(r"[0-9]+", line.get("cb", ""))):
                    raise ValueError("JaCoCo report contains incomplete or missed line detail")
                numbers.add(number)
            if add_covered([file], counters)["LINE"] != len(lines):
                raise ValueError("source file JaCoCo line count disagrees with detail")
            source_lines.update(lines)
        # Several classes can share a source line. Only sourcefile lines are additive here.
        expected = add_covered(members, counters, omitted=("LINE",))
        expected["LINE"] = add_covered(files, counters)["LINE"]
        if add_covered([package], counters) != expected:
            raise ValueError("package JaCoCo counters disagree with class or source detail")
    if (not expected_classes or classes.keys() != expected_classes
            or set(report.iter("class")) != set(classes.values())
            or set(report.iter("sourcefile")) != source_files
            or set(report.iter("line")) != source_lines):
        raise ValueError("JaCoCo class roster or source placement differs from measured scope")

    reported_methods = set()
    for cls in classes.values():
        reported_methods.update(validate_class_detail(cls, counters))
    if set(report.iter("method")) != reported_methods:
        raise ValueError("misplaced JaCoCo method detail")
    return root
