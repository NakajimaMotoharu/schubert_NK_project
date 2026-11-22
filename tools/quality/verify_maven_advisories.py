"""Check one verified local Maven SBOM against a pinned offline OSV database.

RD171 SCM-005 / SS352 §13 / PT-OPS-OSV-001..009.
"""

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path

from verify_maven_sbom import SHA256, unique_fields, verify_model_bom


def pinned_file(path, expected):
    if not SHA256.fullmatch(expected) or not path.is_file():
        raise ValueError("a regular file and its SHA-256 are required")
    with path.open("rb") as source:
        actual = hashlib.file_digest(source, "sha256").hexdigest()
    if actual != expected.lower():
        raise ValueError(f"SHA-256 mismatch for {path.name}")
    return path.resolve(strict=True)


def findings_from_report(report, scan_input, expected_refs):
    results = report["results"]
    if len(results) != 1 or results[0]["source"] != {
        "path": str(scan_input),
        "type": "sbom",
    }:
        raise ValueError("OSV report does not identify the selected SBOM")
    seen = set()
    findings = []
    for result in results[0]["packages"]:
        package = result["package"]
        ref = package["purl"]
        if package["ecosystem"] != "Maven" or ref not in expected_refs or ref in seen:
            raise ValueError("OSV report contains an unexpected or duplicate package")
        seen.add(ref)
        advisories = result.get("vulnerabilities", [])
        if not isinstance(advisories, list):
            raise ValueError("invalid OSV vulnerability list")
        for item in advisories:
            identifier = item["id"]
            if not isinstance(identifier, str) or not identifier or not all(
                ch.isascii() and (ch.isalnum() or ch == "-") for ch in identifier
            ):
                raise ValueError("invalid OSV vulnerability ID")
            findings.append((ref, identifier))
    if seen != expected_refs:
        raise ValueError("OSV report omits a package from the verified SBOM")
    return [{"purl": ref, "advisory": item} for ref, item in sorted(set(findings))]


def scan_bom(bom, repository, scanner, scanner_sha256, cache, database_sha256):
    scanner = pinned_file(scanner, scanner_sha256)
    cache = cache.resolve(strict=True)
    pinned_file(cache / "osv-scalibr" / "Maven" / "all.zip", database_sha256)
    contents = bom.read_bytes()
    document = json.loads(contents, object_pairs_hook=unique_fields)
    verify_model_bom(document, repository)
    expected_refs = {item["purl"] for item in document["components"]}
    if not expected_refs:
        raise ValueError("the verified SBOM contains no Maven JARs")

    with tempfile.TemporaryDirectory(prefix="nk-offline-advisories-") as directory:
        workspace = Path(directory)
        scan_input = workspace / "verified.cdx.json"
        scan_input.write_bytes(contents)
        config = workspace / "osv-scanner.toml"
        config.write_text("", encoding="utf-8")
        execution = subprocess.run(
            [
                str(scanner), "scan", "source", "--offline", "--all-packages",
                "--config", str(config), "--format", "json", "-L", str(scan_input),
            ],
            cwd=workspace,
            env={
                "PATH": os.defpath,
                "OSV_SCANNER_LOCAL_DB_CACHE_DIRECTORY": str(cache),
            },
            capture_output=True,
            check=False,
            timeout=120,
        )
        if execution.returncode not in (0, 1):
            raise ValueError(f"OSV scan did not complete, exit {execution.returncode}")
        report = json.loads(execution.stdout, object_pairs_hook=unique_fields)
        findings = findings_from_report(report, scan_input, expected_refs)
        if execution.returncode != int(bool(findings)):
            raise ValueError("OSV exit code and advisory report disagree")
    return {
        "bomSha256": hashlib.sha256(contents).hexdigest(),
        "scannerSha256": scanner_sha256.lower(),
        "databaseSha256": database_sha256.lower(),
        "scannedMavenPackages": len(expected_refs),
        "findings": findings,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bom", type=Path)
    parser.add_argument("repository", type=Path)
    parser.add_argument("scanner", type=Path)
    parser.add_argument("scanner_sha256")
    parser.add_argument("cache", type=Path)
    parser.add_argument("database_sha256")
    args = parser.parse_args()
    try:
        result = scan_bom(**vars(args))
    except (AttributeError, KeyError, OSError, RuntimeError, TypeError, ValueError,
            subprocess.TimeoutExpired) as failure:
        parser.exit(2, f"Maven dependency scan incomplete: {failure}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return int(bool(result["findings"]))


if __name__ == "__main__":
    raise SystemExit(main())
