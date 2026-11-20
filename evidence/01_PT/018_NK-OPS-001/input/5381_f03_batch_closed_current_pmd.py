"""Get raw PMD results on the already admitted Batch type closure."""

from collections import Counter, defaultdict
from datetime import datetime, timezone
import json
from pathlib import Path
import runpy
from tempfile import TemporaryDirectory
from xml.etree import ElementTree
from zipfile import ZipFile

TOOLS = runpy.run_path(str(Path(__file__).with_name("5370_f03_batch_admitted_spotbugs.py")))
OPS, PLAN, UPPER, COMMON, archive_classes = (
    TOOLS[key] for key in ("OPS", "PLAN", "UPPER", "COMMON", "archive_classes")
)
BATCH = "src/schubert-nk-batch/src/main/java/"
SCHEMA = "dev/codex/schubert/nk/api/bootstrap/SchemaHistoryAdmission.class"


def main():
    pin, sha, dump, git = (COMMON[key] for key in ("pin", "sha", "dump", "git"))
    read = UPPER["read"]
    begin = next(PLAN.glob("917_*"))
    start = read(begin)["values"]
    references = start["oracleReferences"]
    assert all(pin(Path(ref["path"])) == ref for ref in references)
    previous, package, peers, pmd_template, _ = (read(ref["path"]) for ref in references[1:])
    core = start["productionCoreMain"]
    assert core == package["productionCore"] == peers["productionCore"]
    assert previous["actualExit"] == previous["protectedClassBytesRead"] == 0
    graph = previous["evidence"]["graph"]
    assert pin(Path(graph["path"])) == graph
    closure = read(graph["path"])
    closed = set(closure["checkedSet"])
    held = set(closure["explicitPhysicalHoldMetadataOnly"])
    outside = set(closure["deferredTransitive"])
    assert len(closed) == 277 and len(held) == 53 and len(outside) == 316
    assert sum(map(len, (closed, held, outside))) == len(closed | held | outside) == 646
    edges = TOOLS["G"]["G"]["dependency_rows"](previous["stages"]["typed"])
    schema = SCHEMA.removesuffix(".class").replace("/", ".")
    assert all(schema not in edges.get(name.removesuffix(".class").replace("/", "."), ())
               for name in closed)

    batches = package["packagedBuild"]["batch"]["artifact"]
    assert pin(Path(batches["path"])) == batches
    with ZipFile(batches["path"]) as zipped:
        physical = {name for name in zipped.namelist() if name.endswith(".class")}
        assert physical == closed | held | outside
        approved = {name: zipped.read(name) for name in sorted(closed)}
    hashes = {name: sha(body) for name, body in approved.items()}
    assert sha(json.dumps(hashes, sort_keys=True).encode()) == previous["candidatePhysicalMapSha256"]

    sources = git("ls-tree", "-r", "--name-only", core, "--", BATCH).decode().splitlines()
    by_source = defaultdict(set)
    for name in physical:
        stem, _, _ = name.removesuffix(".class").partition("$")
        by_source[BATCH + stem + ".java"].add(name)
    assert len(sources) == 200 and all(name in by_source for name in sources)
    selected = {name for name in sources if by_source[name] <= closed}
    assert 0 < len(selected) < len(sources)
    source_hashes = {}
    pm = pmd_template["stages"]["pmd"]["command"]
    old_aux = pm[pm.index("--aux-classpath") + 1].split(":")
    allowed_sdk = [name for name in old_aux if "/toolchain/" in name]
    assert len(old_aux) - len(allowed_sdk) == 3
    reference_sdk = dict(read(next(OPS.glob("PG39810-*/begin.json")))["sdkJars"])
    for ref in (read(next(OPS.glob("PG39812-*/manifest.json")))["onlyAdditionalAux"],
                read(next(OPS.glob("PG40370-*/manifest.json")))["explicitMetricsSdk"]):
        reference_sdk[ref["path"]] = ref["sha256"]
    for name in allowed_sdk[1:]:
        assert pin(Path(name))["sha256"] == reference_sdk[name]
    rules = Path("tools/quality/static/pmd.xml")
    assert rules.read_bytes() == git("show", f"{core}:{rules}")
    assert rules.read_bytes() == git("show", f"{previous['productionCore']}:{rules}")

    output = (OPS / start["run"]).resolve()
    output.mkdir()
    xml = output / "pmd.xml"
    environment = {"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8"}
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-f03-closed-batch-pmd-") as folder:
        scratch = Path(folder)
        batch = scratch / "admitted-batch.jar"
        archive_classes(batch, approved)
        input_jars = [str(batch)]
        for name, qualified in peers["artifacts"].items():
            current = package["packagedBuild"][name]["artifact"]
            assert current == qualified["jar"] and pin(Path(current["path"])) == current
            input_jars.append(current["path"])
        for name in sorted(selected):
            data = git("show", f"{core}:{name}")
            assert data == git("show", f"{previous['productionCore']}:{name}")
            point = scratch / name
            point.parent.mkdir(parents=True, exist_ok=True)
            point.write_bytes(data)
            source_hashes[name] = sha(data)
        listing = scratch / "sources.txt"
        listing.write_text("".join(str(scratch / name) + "\n" for name in sorted(selected)))
        input_ref = output / "admitted-inputs.json"
        dump(input_ref, dict(sources=source_hashes, selectedBatchTypes=hashes))
        execution = UPPER["run"](output, "pmd", [
            *pm[:pm.index("check") + 1], "--file-list", listing, "--rulesets", rules.resolve(),
            "--use-version", "java-25", "--aux-classpath", ":".join([*allowed_sdk, *input_jars]),
            "--no-cache", "--format", "xml", "--report-file", xml,
        ], scratch, environment)
    dump(output / "pmd-terminal.json", execution)
    findings = Counter()
    errors = []
    if xml.is_file():
        for entry in ElementTree.parse(xml).getroot():
            if entry.tag.endswith("}file"):
                path = Path(entry.get("name")).relative_to(scratch).as_posix()
                assert path in selected
                findings.update(node.get("rule") for node in entry.findall("{*}violation"))
            elif entry.tag.endswith(("}error", "}configerror")):
                errors.append(entry.attrib)
    ok = xml.is_file() and not errors and execution["actualExit"] in (0, 4)
    record = dict(actualExit=0 if ok else 1, source=start["source"], productionCore=core,
                  terminal=pin(output / "pmd-terminal.json"), pmdExit=execution["actualExit"],
                  sourceCount=len(selected), sourceExcluded=len(sources) - len(selected),
                  batchTypedInput=len(approved), explicitHeldTypeBytesOpened=0,
                  deferredTransitiveBytesOpened=0, priorClosure=pin(Path(graph["path"])),
                  priorCandidatePhysicalMapSha256=previous["candidatePhysicalMapSha256"],
                  raw=pin(xml) if xml.is_file() else None, inputs=pin(input_ref),
                  rawFindings=sum(findings.values()), rawRules=dict(findings), processingErrors=errors,
                  rules=pin(rules), removedRules=0, productTests=0,
                  wholeBatchAccepted=False, wholeF03Accepted=False, whole451Accepted=False,
                  terminalAtUTC=datetime.now(timezone.utc).isoformat())
    dump(output / "manifest.json", record)
    print(pin(output / "manifest.json"), record["pmdExit"], len(selected), record["rawFindings"], len(errors))
    return record["actualExit"]


if __name__ == "__main__":
    raise SystemExit(main())
