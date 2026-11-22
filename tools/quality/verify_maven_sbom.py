"""Verify the local Maven model BOM produced for SCM-005 / RD171 / SS352 §13."""

import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import parse_qsl


PART = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_.+-]*")
SHA256 = re.compile(r"[0-9a-fA-F]{64}")


def unique_fields(pairs):
    fields = {}
    for key, value in pairs:
        if key in fields:
            raise ValueError("duplicate JSON field")
        fields[key] = value
    return fields


def maven_jar(component, repository):
    group, name, version = (component[key] for key in ("group", "name", "version"))
    if not all(
        isinstance(value, str) and PART.fullmatch(value) for value in (group, name, version)
    ) or not all(map(PART.fullmatch, group.split("."))):
        raise ValueError("invalid Maven coordinates")
    ref = component["bom-ref"]
    expected = f"pkg:maven/{group}/{name}@{version}"
    identifier, separator, query = ref.partition("?")
    qualifiers = parse_qsl(query, strict_parsing=True, keep_blank_values=True)
    attributes = unique_fields(qualifiers)
    if (
        not separator
        or identifier != expected
        or ref != component["purl"]
        or set(attributes) - {"type", "classifier"}
        or attributes.get("type") != "jar"
    ):
        raise ValueError("BOM reference does not match the Maven JAR")
    classifier = attributes.get("classifier")
    if classifier is not None and not PART.fullmatch(classifier):
        raise ValueError("invalid Maven classifier")
    filename = f"{name}-{version}" + (f"-{classifier}" if classifier else "") + ".jar"
    artifact = repository.joinpath(*group.split("."), name, version, filename).resolve(strict=True)
    if not artifact.is_relative_to(repository) or not artifact.is_file():
        raise ValueError("artifact is outside the selected Maven repository or is not a file")
    return artifact


def valid_license_record(record):
    def nonempty(value):
        return isinstance(value, str) and bool(value.strip())

    if not isinstance(record, dict):
        return False
    if "expression" in record:
        return "license" not in record and nonempty(record["expression"])
    license_info = record.get("license")
    return isinstance(license_info, dict) and any(
        nonempty(license_info.get(key)) for key in ("id", "name")
    )


def verify_graph(dependencies, known, root):
    graph = {}
    for entry in dependencies:
        ref, targets = entry["ref"], entry["dependsOn"]
        if ref in graph or ref not in known or not isinstance(targets, list):
            raise ValueError("duplicate, unknown or malformed dependency row")
        target_set = set(targets)
        if len(target_set) != len(targets) or target_set - known:
            raise ValueError("duplicate or unknown dependency target")
        graph[ref] = target_set
    if graph.keys() != known:
        raise ValueError("missing component dependency row")
    seen = set()
    pending = [root]
    while pending:
        ref = pending.pop()
        if ref not in seen:
            seen.add(ref)
            pending.extend(graph[ref] - seen)
    if seen != known:
        raise ValueError("component is unreachable from the BOM root")
    return len(graph)


def verify_model_bom(document, repository):
    if document["bomFormat"] != "CycloneDX" or document["specVersion"] != "1.6":
        raise ValueError("expected CycloneDX 1.6")
    root = document["metadata"]["component"]["bom-ref"]
    if not isinstance(root, str) or not root:
        raise ValueError("BOM root is required")
    components = document["components"]
    dependencies = document["dependencies"]
    if not isinstance(components, list) or not isinstance(dependencies, list):
        raise ValueError("BOM components and dependency rows must be arrays")
    repository = repository.resolve(strict=True)
    known = {root}
    missing_license = []
    for component in components:
        ref = component["bom-ref"]
        if ref in known:
            raise ValueError("duplicate BOM reference")
        artifact = maven_jar(component, repository)
        known.add(ref)
        declared = [item["content"] for item in component["hashes"] if item["alg"] == "SHA-256"]
        if len(declared) != 1 or not isinstance(declared[0], str) or not SHA256.fullmatch(declared[0]):
            raise ValueError(f"expected one SHA-256 for {ref}")
        with artifact.open("rb") as jar:
            actual = hashlib.file_digest(jar, "sha256").hexdigest()
        if actual != declared[0].lower():
            raise ValueError(f"JAR SHA-256 mismatch for {ref}")
        licenses = component.get("licenses", [])
        if not isinstance(licenses, list) or not all(map(valid_license_record, licenses)):
            raise ValueError(f"malformed license records for {ref}")
        if not licenses:
            missing_license.append(ref)
    return {
        "rootRef": root,
        "verifiedJarHashes": len(components),
        "dependencyRows": verify_graph(dependencies, known, root),
        "missingLicenseMetadata": sorted(missing_license),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bom", type=Path)
    parser.add_argument("repository", type=Path)
    options = parser.parse_args()
    try:
        with options.bom.open(encoding="utf-8") as source:
            document = json.load(source, object_pairs_hook=unique_fields)
        result = verify_model_bom(document, options.repository)
    except (AttributeError, KeyError, OSError, RuntimeError, TypeError, ValueError) as failure:
        parser.exit(1, f"BOM verification failed: {failure}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
