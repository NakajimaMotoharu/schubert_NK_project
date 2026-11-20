"""Qualify Checkstyle evidence for the exact current, non-held Test delta."""

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree


def git(*args):
    return subprocess.check_output(["git", *args])


def test_tree(revision):
    entries = git("ls-tree", "-rz", revision, "src").split(b"\0")
    result = {}
    for entry in filter(None, entries):
        metadata, raw_path = entry.split(b"\t", 1)
        path = raw_path.decode()
        if "/src/test/java/" in path and path.endswith(".java"):
            result[path] = metadata.decode().split()[-1]
    return result


def pin(path):
    return {"path": str(path), "sha256": hashlib.sha256(Path(path).read_bytes()).hexdigest()}


def verified(reference):
    path = Path(reference["path"])
    assert pin(path)["sha256"] == reference["sha256"], path
    return path


def read(path):
    return json.loads(path.read_bytes())


def report_rows(xml):
    root = ElementTree.parse(xml).getroot()
    assert root.tag == "checkstyle" and root.get("version") == "14.3.0"
    files = {str(Path(entry.attrib["name"]).resolve().relative_to(Path.cwd())):
             len(entry.findall("error")) for entry in root.findall("file")}
    assert len(root) == len(files)
    return files


def main():
    plan = next(Path("documents/400_PGPT/470_PMO").glob("601_*"))
    start = read(next(plan.glob("1158_*")))
    context = start["values"]
    manifest_paths = {p.parent.name.split("-")[0]: p
                      for p in map(verified, context["oracleReferences"]) if p.name == "manifest.json"}
    original = read(manifest_paths["PG40592"])
    independent = read(manifest_paths["PG40594"])
    data = read(verified(original["sourceEvidence"]))
    protection = verified(data["priorProtections"])
    held = set(read(protection)["protectedPathsMetadataOnly"])
    reference_tree = test_tree(independent["testSource"])
    current_tree = test_tree(context["source"])
    assert current_tree == test_tree(context["productionCoreMain"])
    stable = {path for path, blob in current_tree.items() if reference_tree.get(path) == blob}
    changed = set(current_tree) - stable
    assert len(held) == independent["heldMetadataOnly"] == 32
    assert held <= stable and len(stable - held) == 1107
    assert len(changed) == 6 and reference_tree.keys() <= current_tree.keys()

    java, checkstyle, rules, formatter = map(verified, original["toolInputs"])
    rules_path = str(rules.relative_to(Path.cwd()))
    assert git("rev-parse", f"{independent['testSource']}:{rules_path}") == git(
        "rev-parse", f"{context['source']}:{rules_path}")
    previous = [
        ("PG40616", "StorageFailureGraphTest.java", "testSource", None, "toolStyles", "newCheckstyle"),
        ("PG40640", "AlertThresholdsTest.java", "testedSource", None, None, "checkstyle"),
        ("PG40698", "ExpiryAuditJdbcFailureGraphTest.java", None, "test", "commandReceipts", None),
        ("PG40732", "ExpiryAuditPortTest.java", None, "newTest", "static", None),
        ("PG40742", "CleanupTerminalReferencesJdbcGraphTest.java", None, "test", "standaloneStatic", None),
    ]
    pinned_inputs = {}
    reused = {}
    for run, basename, source_key, test_key, command_group, xml_key in previous:
        path, = (path for path in changed if Path(path).name == basename)
        current = pin(path)
        assert git("show", f"{context['source']}:{path}") == Path(path).read_bytes()
        pinned_inputs[path] = current
        manifest = manifest_paths[run]
        prior = read(manifest)
        assert prior["actualExit"] == 0
        if source_key:
            old = prior[source_key]
            assert test_tree(old)[path] == current_tree[path]
            assert git("rev-parse", f"{old}:{rules_path}") == git(
                "rev-parse", f"{context['source']}:{rules_path}")
        else:
            assert prior[test_key] == current
        if command_group:
            entry = prior[command_group]["checkstyle"]
            args = entry["command"]
            assert entry["actualExit"] == 0 and args[0] == str(java) and str(checkstyle) in args
            assert Path(args[args.index("-c") + 1]).resolve() == rules and path in args
        xml = verified(prior[xml_key]) if xml_key else manifest.with_name("checkstyle.xml")
        assert report_rows(xml)[path] == 0
        reused[path] = {"source": current, "previous": pin(manifest), "xml": pin(xml)}

    pending = sorted(changed - reused.keys())
    assert [Path(path).name for path in pending] == ["ExpiryAuditValueOwnershipTest.java"]
    for path in pending:
        assert git("show", f"{context['source']}:{path}") == Path(path).read_bytes()
        pinned_inputs[path] = pin(path)
    out = Path("evidence/01_PT/018_NK-OPS-001/evidence") / context["run"]
    out.mkdir(exist_ok=True)
    assert not (out / "manifest.json").exists()
    commands = [
        ("checkstyle", [str(java), "-jar", str(checkstyle), "-c", str(rules), "-f", "xml",
                        "-o", str(out / "checkstyle.xml"), *pending]),
        ("format", [str(java), "-jar", str(formatter), "--skip-reflowing-long-strings",
                    "--dry-run", "--set-exit-if-changed", *pending]),
    ]
    observations = {}
    for name, args in commands:
        result = subprocess.run(args, capture_output=True, timeout=60)
        stdout, stderr = out / f"{name}.stdout", out / f"{name}.stderr"
        stdout.write_bytes(result.stdout)
        stderr.write_bytes(result.stderr)
        observations[name] = {"command": args, "actualExit": result.returncode,
                              "stdout": pin(stdout), "stderr": pin(stderr)}
    xml = out / "checkstyle.xml"
    fresh_clean = xml.exists() and report_rows(xml) == dict.fromkeys(pending, 0)
    success = fresh_clean and all(x["actualExit"] == 0 for x in observations.values())
    result = {
        "actualExit": 0 if success else 1,
        "startEvent": start["eventId"],
        "source": context["source"],
        "productionCore": context["productionCoreMain"],
        "toolInputs": original["toolInputs"],
        "runner": pin(Path(__file__).relative_to(Path.cwd())),
        "outsideScope": pin(protection),
        "testSourcesTotal": len(current_tree),
        "unchangedAndReused": len(stable - held),
        "exactPreviouslyCheckedDelta": reused,
        "newlyChecked": [pinned_inputs[path] for path in pending],
        "newCheckstyleXml": pin(xml) if xml.exists() else None,
        "newCheckstyleFindings": 0 if fresh_clean else None,
        "checkstyleConfirmed": len(stable - held) + len(reused) + (len(pending) if fresh_clean else 0),
        "heldMetadataOnly": len(held),
        "heldContentsRead": 0,
        "analyzers": observations,
        "productionTestsExecuted": 0,
        "productClassfilesRead": 0,
        "wholeF03": False,
        "formalDelta": 0,
        "terminalAtUTC": datetime.now(timezone.utc).isoformat(),
    }
    (out / "manifest.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(result["checkstyleConfirmed"], "/", len(current_tree), "fresh", len(pending), "exit", result["actualExit"])
    return result["actualExit"]


if __name__ == "__main__":
    raise SystemExit(main())

