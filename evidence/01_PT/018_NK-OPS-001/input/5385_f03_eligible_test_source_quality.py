"""Join the same Test sources and run the remaining ordinary Checkstyle inputs."""

from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
from xml.etree import ElementTree


BASE = Path(__file__).with_name("5129_f03_current_source_lint_join.py")
SCOPE = Path("documents/400_PGPT/470_PMO/601_WBS66短期実行_20261117")
OPS = Path("evidence/01_PT/018_NK-OPS-001/evidence")


def load_helpers():
    source = BASE.read_text()
    old_range = "38443 <= int(id_match[1]) <= 39300"
    assert source.count(old_range) == 1
    helpers = {"__name__": "source_quality_join", "__file__": str(BASE)}
    source = source.replace(old_range, "39314 <= int(id_match[1]) <= 40590")
    exec(compile(source, BASE, "exec"), helpers)
    return helpers


def main():
    h = load_helpers()
    read, tree, pin, verify = (h[key] for key in ("load", "tree", "ref", "verify"))
    start = read(next(SCOPE.glob("974_*")))["values"]
    receipts = [verify(ref) for ref in start["oracleReferences"]]
    _, previous_path, protection_path, schema_path, _ = receipts
    previous, security, schema = map(read, (previous_path, protection_path, schema_path))
    before = tree(previous["source"], "test")
    current = tree(start["source"], "test")
    tools = [verify(x) for x in previous["toolInputs"]]
    git = h["git"]
    rule = h["RULE"]
    assert git("rev-parse", f"{start['source']}:{rule}") == git("rev-parse", f"{previous['source']}:{rule}")
    hold = set(security["protectedPathsMetadataOnly"])
    assert len(hold) == previous["testCounts"]["baselineHeld"] == 32
    assert hold.issubset(before) and hold.issubset(current)
    assert before.keys() <= current.keys() and all(h["safe_source"](p) for p in current.keys() - hold)
    assert len(before) - len(hold) == previous["testCounts"]["confirmed"]
    unchanged = {p: blob for p, blob in current.items() if p not in hold and before.get(p) == blob}
    delta = {p: h["content_at"](start["source"], p) for p in current.keys() - hold - unchanged.keys()}
    prior, pending = h["scan_registered"](delta, tools)
    static_xml = schema_path.with_name("checkstyle.xml")
    css = schema["staticRuns"]["checkstyle"]
    candidate_ids = [p for p in delta if p.endswith("/SchemaHistoryAdmissionTest.java")]
    assert len(candidate_ids) == 1
    name = candidate_ids[0]
    if name in pending:
        files = ElementTree.parse(static_xml).getroot()
        assert not files.findall(".//error")
        result = [Path(file.get("name")) for file in files.findall("file")
                  if Path(file.get("name")).name == Path(name).name]
        assert len(result) == 1 and str(result[0]) in css["command"] and css["actualExit"] == 0
        assert css["command"][0] == str(tools[0]) and str(tools[1]) in css["command"] and str(tools[2]) in css["command"]
        assert current[name] == tree(schema["source"], "test")[name]
        verify(css["stdout"])
        verify(css["stderr"])
        prior[name] = dict(sourceSha256=pending.pop(name), receipt=pin(schema_path), checkstyleXml=pin(static_xml))
    assert set(unchanged) | set(prior) | set(pending) | hold == set(current)
    assert len(unchanged) + len(prior) + len(pending) + len(hold) == len(current)

    out = OPS / start["run"]
    out.mkdir()
    inputs = out / "eligible-delta.json"
    h["write"](inputs, dict(baseline=pin(previous_path), priorProtections=pin(protection_path),
                           hermeticSourceInputs=pin(BASE), unchangedGitBlobIds=unchanged,
                           priorExactDelta=prior, newInputs=pending, heldMetadataOnly=len(hold),
                           currentSource=start["source"], toolInputs=[pin(tool) for tool in tools]))
    executed = None
    blocked = set()
    if pending:
        files = sorted(pending)
        assert all(h["sha"](Path(p).read_bytes()) == pending[p] for p in files)
        xml = out / "checkstyle.xml"
        args = [str(tools[0]), "-Xmx768m", "-jar", str(tools[1]), "-c", str(tools[2]),
                "-f", "xml", "-o", str(xml), *files]
        command = subprocess.run(args, capture_output=True, timeout=60)
        stdout, stderr = out / "checkstyle.stdout", out / "checkstyle.stderr"
        stdout.write_bytes(command.stdout)
        stderr.write_bytes(command.stderr)
        ended = datetime.now(timezone.utc).isoformat()
        executed = dict(command=args, actualExit=command.returncode, stdout=pin(stdout),
                        stderr=pin(stderr), terminalAtUTC=ended)
        if xml.exists():
            root = ElementTree.parse(xml).getroot()
            assert root.tag == "checkstyle"
            names = {str(Path(row.get("name")).resolve().relative_to(Path.cwd())): row
                     for row in root.findall("file")}
            assert set(names) == set(files)
            blocked = {p for p, row in names.items() if row.findall("error")}
            executed["xml"] = pin(xml)
            assert bool(blocked) == bool(command.returncode)
        else:
            blocked = set(files)
    confirmed = set(current) - hold - blocked
    names_by_module = Counter(p.split("/", 2)[1] for p in confirmed)
    ending = datetime.now(timezone.utc).isoformat()
    manifest = out / "manifest.json"
    h["write"](manifest, dict(actualExit=int(bool(blocked)), currentSource=start["source"],
                              productionCore=start["productionCoreMain"], allTestSourceCount=len(current),
                              confirmedCheckstyleSourceCount=len(confirmed), unchanged=len(unchanged),
                              eligibleDelta=len(delta), priorExact=len(prior), freshInputs=len(pending),
                              freshClean=len(pending)-len(blocked), protectedMetadataOnly=len(hold),
                              unresolvedOrdinary=sorted(blocked), modules=dict(names_by_module),
                              toolInputs=[pin(p) for p in tools], sourceEvidence=pin(inputs),
                              currentExecution=executed, actualCompilerProcesses=0, productTests=0,
                              wholeF03Accepted=False, whole451Accepted=False, terminalAtUTC=ending))
    print(pin(manifest),len(current),len(confirmed),len(unchanged),len(prior),len(pending),len(blocked))
    return int(bool(blocked))


if __name__ == "__main__":
    raise SystemExit(main())
