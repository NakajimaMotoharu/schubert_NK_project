"""Qualify the new G07 interval with exact regular-build and archived probe receipts."""
from gzip import decompress
from pathlib import Path
import json
import re
import runpy
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve()
TOOLS = runpy.run_path(str(HERE.with_name("5216_g07_scope_build_delta.py")))
START = next(Path("documents/400_PGPT/470_PMO/601_WBS66短期実行_20261117").glob("519_G07*"))
EVIDENCE = HERE.parent.parent / "evidence"
VALUE = json.loads(START.read_bytes())["values"]
OUT = EVIDENCE / VALUE["run"] / "scan"
WORK = Path(VALUE["volatileStaging"])
RETAIN = Path.cwd().parent / "pgpt-runs/PG379" / VALUE["run"].lower()
BUILD = EVIDENCE / "PG39862-service-db-state-lock-four-main-v1" / "manifest.json"
UNIT = EVIDENCE / "PG39866-service-db-state-lock-unit-v1"
POST = EVIDENCE / "PG39868-p00405-service-db-state-lock-independent-v1" / "manifest.json"
PRIOR = EVIDENCE / "PG39840-g07-cleanup-static-and-characterization-delta-v1/scan/manifest.json"


def configure(module):
    module.OUT = OUT
    module.START = START
    module.TEMP = WORK
    module.RETAIN = RETAIN
    return module


def classify():
    p = TOOLS["load"]("g07_lock_classifier", "5182_g07_jdbc_metrics_cached_classification.py")
    configure(p.t.WRAPPER)
    p.OUT = p.t.OUT = p.B.OUT = OUT
    p.WORK = p.t.WORK = p.B.WORK = WORK
    p.t.PREPARE_RUNS = ()
    p.t.ORDINARY_BUILD_RUNS = ()
    B = p.B
    index = {}
    current = B.load(BUILD)
    directory = Path(current["cwd"])
    assert directory.parent == RETAIN.parent and directory.resolve() == directory
    assert current["actualExit"] == 0 and current["inputHashesReverified"]
    denied = B.HELD | {"RootFailedStartRecovery", "NativeNkA01Capture", "NativeNkL01Capture"}
    for module, classes in current["physicalClassHashes"].items():
        assert module in {"batch", "bootstrap", "protocol", "storage"}
        root = directory / f"src/schubert-nk-{module}/target/classes"
        for name, digest in classes.items():
            relative = Path(name)
            if relative.stem.split("$")[0] in denied:
                continue
            assert not relative.is_absolute() and ".." not in relative.parts
            index[digest.encode()] = (root / relative, name, module)
    old_contents = p.proven_content

    def history():
        old = B.load(PRIOR)
        assert old["qualifiedRangeOnly"] and old["unresolvedCandidates"] == old["confirmedSecrets"] == 0
        keys = set()
        for name in ("classified-findings.json", "pinned-sdk-origin.json"):
            original = old["exactPrivateProofFiles"][name]
            path = Path(original["path"])
            assert path.is_relative_to(RETAIN.parent) and B.ref(path) == original
            for row in B.load(path):
                if row["ground"] is not None:
                    keys.add((row["rule"], row["lineSha256"], row["startColumn"], row["endColumn"]))
        return keys, B.ref(PRIOR)

    def content(line, start, end, digests, reachable):
        previous = old_contents(line, start, end, digests, reachable)
        if previous:
            return previous
        tokens = [match.group(1) for match in p.TOKEN.finditer(line)
                  if max(0, min(match.end(1), end+1)-max(match.start(1), start-2)) >= len(match.group(1))-1]
        if len(tokens) != 1 or tokens[0] not in index:
            return None
        path, name, module = index[tokens[0]]
        assert path.resolve() == path and B.ref(path)["sha256"] == tokens[0].decode()
        return dict(kind="Exact current normal-build physical class digest", path=name, module=module, owner=B.ref(BUILD))

    def binary(rows, by_key, unused_scan):
        matches = []
        for row in rows:
            path = Path(row["path"])
            if row.get("actualExit") == 0 or path != UNIT.relative_to(Path.cwd()) / "jacoco.exec":
                continue
            meta = by_key[row["path"], row["blob"]]
            copy = WORK / meta["relativeProjection"]
            main = B.load(UNIT / "manifest.json")
            prior = B.load(UNIT / "begin.json")
            result = B.load(UNIT / "execinfo-exit.json")
            post = B.load(POST)
            assert main["source"] == prior["source"] == post["source"] == VALUE["productionCoreMain"]
            assert main["unitSource"] == prior["unitSource"] == post["unitSource"]
            assert main["actualExits"] == {"unit": 0, "execinfo": 0} and result["actualExit"] == post["actualExit"] == 0
            assert main["casesExpected"] == post["oldTests"] + post["newTests"] == 32
            xml = Path(post["actualWholeCases"]["path"])
            assert B.ref(xml) == post["actualWholeCases"]
            tree = ET.parse(xml)
            assert len(list(tree.iter("testcase"))) == 32 and not any(
                node.tag in {"failure", "error", "skipped"} for node in tree.iter())
            assert B.ref(copy)["sha256"] == B.ref(path)["sha256"] == main["files"]["jacoco.exec"] == meta["blobSha256"]
            assert B.ref(path) == post["singleExec"]
            assert Path(result["command"][-1]) == path.absolute() and result["command"][-2] == "execinfo"
            replies = {}
            for stream in ("stdout", "stderr"):
                receipt = result[stream]
                archive = UNIT / f"execinfo.{stream}.gz"
                assert str(archive) == receipt["archive"]["path"]
                assert B.ref(archive)["sha256"] == receipt["archive"]["sha256"]
                assert receipt["archive"]["sha256"] == main["files"][archive.name]
                plain = decompress(archive.read_bytes())
                assert len(plain) == receipt["size"] and B.sha(plain) == receipt["exactSha256"]
                replies[stream] = plain
            assert not replies["stderr"]
            decoded = replies["stdout"].decode()
            assert re.findall(r'^Session "([^"]+)":', decoded, re.M) == [prior["session"]]
            targets = re.findall(r"^([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(\S+)$", decoded, re.M)
            for name in ("ServiceDatabaseSource", "ServiceDatabaseAdmission"):
                assert any(label == f"dev/codex/schubert/nk/api/bootstrap/{name}" and int(hit) > 0
                           for _, hit, _, label in targets)
            assert not any(label.startswith(("org/postgresql/", "com/microsoft/playwright/")) for _, _, _, label in targets)
            matches.append(dict(row, actualExit=0, originalUnitExit=0, ordinaryProbeDataOnly=True,
                                commandReplayed=False, session=prior["session"], rowCount=len(targets),
                                exactArchivedDecoder=B.ref(UNIT / "execinfo-exit.json"), independentlyBoundPreviousPost=B.ref(POST)))
        return matches

    p.exact_previous = history
    p.proven_content = content
    p.t.extra_binary = binary
    p.main()


def retain():
    p = TOOLS["load"]("g07_lock_compactor", "5184_g07_jdbc_metrics_retain_compact.py")
    configure(p.w)
    initial = p.p.load(OUT / "qualified-cached-initial.json")
    assert initial["unresolvedCandidates"] == 1 and initial["unqualifiedBinary"] == 0
    [uncertain] = p.p.load(OUT / "remaining-origins.json")
    assert Path(uncertain["path"]).resolve() == BUILD and uncertain["rule"] == "generic-api-key"
    [meta] = [r for r in p.p.load(WORK / "projection.json")
              if (r["path"], r["blobOid"]) == (uncertain["path"], uncertain["blob"])]
    copy = WORK / meta["relativeProjection"]
    assert copy.read_bytes() == BUILD.read_bytes()
    line = copy.read_bytes().splitlines()[uncertain["line"] - 1]
    assert p.p.sha(line) == uncertain["lineSha256"]
    [(class_name, claimed)] = json.loads(b"{" + line.strip().rstrip(b",") + b"}").items()
    assert class_name == "dev/codex/schubert/nk/api/file/ServiceCredentialException.class"
    at = line.index(claimed.encode())
    assert uncertain["startColumn"] - 1 < at <= uncertain["endColumn"] < at + len(claimed)
    owner = p.p.load(BUILD)
    folder = Path(owner["cwd"])
    assert folder.parent == RETAIN.parent and folder.resolve() == folder
    physical = folder / "src/schubert-nk-bootstrap/target/classes" / class_name
    assert physical.resolve() == physical
    assert p.p.ref(physical)["sha256"] == owner["physicalClassHashes"]["bootstrap"][class_name] == claimed
    extra = OUT / "additional-build-origins.json"
    p.p.write(extra, [dict(uncertain, ground=dict(kind="Exact manifest key and current physical SHA at the split scanner span",
                                                owner=p.p.ref(BUILD), classPath=class_name))])
    categories = dict(initial["categories"])
    categories["Exact manifest key and current physical SHA at the split scanner span"] = 1
    p.p.write(OUT / "qualified-final-private-detail.json", dict(initial, verifier=p.p.ref(HERE),
        setupPreScannerExit=1, classifierPreconditionExits=[1, 1], scannerExecutions=1,
        unresolvedCandidates=0, confirmedSecrets=0, resultQualifiedForRange=True,
        categories=categories, exactAdditionalOrigin=p.p.ref(extra), sameRangeScannerRepeated=False))
    p.DETAILS = ("scan-terminal.json", "qualified-cached-initial.json", "qualified-final-private-detail.json",
                 "classified-findings.json", "remaining-origins.json", "binary-qualification.json",
                 "additional-build-origins.json")
    p.main()


if __name__ == "__main__":
    import sys
    action, = sys.argv[1:]
    {"classify": classify, "retain": retain}[action]()
