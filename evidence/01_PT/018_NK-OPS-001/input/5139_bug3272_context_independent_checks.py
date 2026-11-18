"""Attest the bounded fixture assertions and exact original PG39374 unit evidence."""
from pathlib import Path
from xml.etree import ElementTree
import datetime
import gzip
import hashlib
import json
import re
import subprocess

B = Path("evidence/01_PT/018_NK-OPS-001")
E = B / "evidence"
OUT = E / "PG39382-f03-api-context-finite-independent-v1"
METHODS = re.compile(r"^  void (apimctx\d{3})[^\n]*\n(.*?)(?=^  @Test|^\})", re.M | re.S)
TOKEN = re.compile(r'"(?:\\.|[^"\\])*"|[A-Za-z_$][A-Za-z_0-9$]*|\d+(?:\.\d+)?|[^\s]')


def load(p):
    return json.loads(p.read_bytes())


def ref(path):
    path = Path(path)
    return dict(path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def git(*a):
    return subprocess.check_output(["git", *a], text=True)


def write(path, value):
    with path.open("x") as f:
        f.write(json.dumps(value, indent=2) + "\n")


def assertion_calls(method):
    """Select balanced named assertion expressions without depending on formatting."""
    tokens = TOKEN.findall(method)
    out = []
    for i, token in enumerate(tokens[:-1]):
        if not token.startswith("assert") or tokens[i + 1] != "(":
            continue
        balance = 0
        for j in range(i + 1, len(tokens)):
            balance += (tokens[j] == "(") - (tokens[j] == ")")
            if balance == 0:
                out.append(tuple(tokens[i : j + 1]))
                break
        else:
            raise ValueError("unbalanced fixture assertion")
    return out


def verify_test_inputs(c):
    start = next(Path("documents/400_PGPT/470_PMO/601_WBS66短期実行_20261117").glob("434_*"))
    old = load(start)["values"]["source"]
    path = c["testSources"][0]["path"]
    before = dict(METHODS.findall(git("show", f"{old}:{path}")))
    after = dict(METHODS.findall(Path(path).read_text()))
    assert len(before) == len(after) == 33 and before.keys() == after.keys()
    diff = {n for n in before if before[n] != after[n]}
    assert diff == {f"apimctx{x}" for x in ("004", "021", "023", "024", "033")}
    count = 0
    for name in sorted(diff - {"apimctx004"}):
        calls = assertion_calls(before[name])
        assert assertion_calls(after[name]) == calls
        count += len(calls)
        assert "awaitTermination(30, TimeUnit.SECONDS)" in after[name]
        assert "try (var executor" not in after[name] and "try (var worker" not in after[name]
    assert 'List.of("unknown", "DEBTf", "STANDAQc")' in after["apimctx004"]
    expected = "new ApiMetricContext<String>(mode, registry -> FIXTURE_BINDING)"
    assert expected in after["apimctx004"] and '"CONFIG_INVALID"' in after["apimctx004"]
    return sorted(diff), count


def archive_streams(c):
    result = []
    for folder in map(Path,c["slots"].values()):
        for f in folder.glob("*.stdout"):
            data = f.read_bytes()
            if not (b"\r" in data or any(row.endswith((b" ",b"\t")) for row in data.split(b"\n"))
                    or data.endswith(b"\n\n")):
                continue
            g = f.with_name(f.name + ".gz")
            with g.open("xb") as stream:
                with gzip.GzipFile(filename="", mode="wb", fileobj=stream, mtime=0) as comp:
                    comp.write(data)
            assert gzip.decompress(g.read_bytes()) == data
            result.append(dict(original=ref(f), archive=ref(g)))
    return result


def main():
    c = load(B / "input/5137_bug3272_api_context_profile.json")
    proofs = {k: ref(Path(v) / "manifest.json") for k, v in c["slots"].items()}
    m = {k: load(Path(v["path"])) for k, v in proofs.items()}
    assert m["unit"]["actualExit"] == m["post"]["actualExit"] == 0
    assert m["unit"]["tests"] == m["post"]["tests"] == 33
    assert all(m["unit"][k] == 0 for k in ("failures","errors","skipped"))
    xml = Path(c["slots"]["post"]) / "original-TEST-junit-jupiter.xml"
    assert len(list(ElementTree.parse(xml).getroot().iter("testcase"))) == 33
    assert m["preflight"]["staticApplicable"] == 0 and len(m["static"]["rawFindings"]) == 25
    source = m["post"]["source"]
    assert not git("diff", "--name-only", source, "HEAD", "--", "src")
    assert not git("diff", "--name-only", c["productionCoreMain"], source, "--", ":(glob)src/*/src/main/java/**/*.java")
    diff, witness_count = verify_test_inputs(c)
    command = load(E / "PG39282-f03-api-recorder-unfiltered-with-generated-v1/raw-command.json")[:5]
    classes = (Path("../pgpt-runs/PG379") / c["privateDirs"]["prepare"] / "component").resolve()
    command.extend([str(Path(c["slots"]["post"]) / "jacoco.exec"), *[str(classes / f) for f in c["physicalClasses"]]])
    recovery = OUT / "second-verifier-failure.json"
    old_step = load(recovery)
    assert old_step["rawMeasurementAlreadySucceeded"] and old_step["source"] == source
    assert old_step["originalVerifier"] == ref(Path(old_step["originalVerifier"]["path"]))
    for name, receipt in old_step["priorEvidence"].items():
        assert receipt == ref(OUT / name)
    assert command == load(OUT / "raw-command.json")
    unfiltered = OUT / "unfiltered.tsv"
    raw = {}
    deficits = []
    for line in unfiltered.read_text().splitlines():
        a = line.split("\t")
        if a[0] not in ("CLASS","DEFICIT"):
            continue
        offset = 6 if a[0] == "CLASS" else 5
        counts = {k: dict(missed=int(x), covered=int(y)) for k, x, y in [v.split(":") for v in a[offset:]]}
        if a[0] == "CLASS":
            raw[a[1]] = counts
        else:
            deficits.append(dict(type=a[1], method=a[2], line=int(a[4]), counters=counts))
    target = next(v for k, v in raw.items() if k.endswith("/ApiMetricContext"))
    old = E / "PG39350-bug3269-api-standard-source-prepare-v1/manifest.json"
    previous = load(old)["physicalClassHashes"]
    assert len(previous) == 6 and all(m["prepare"]["physicalClassHashes"][k] == v for k, v in previous.items())
    retention = OUT / "retention.json"
    for item in load(retention):
        original = Path(item["original"]["path"])
        archive = Path(item["archive"]["path"])
        assert original.parent in set(map(Path, c["slots"].values()))
        assert ref(original) == item["original"] and ref(archive) == item["archive"]
        assert gzip.decompress(archive.read_bytes()) == original.read_bytes()
    result = dict(actualExit=0, source=source, productionCoreMain=c["productionCoreMain"], run=c["id"],
        tests=33, failures=0, errors=0, skipped=0, notRun=0, firstProductRunSuccess=True,
        firstIndependentPostSuccess=True, newTestDefinitions=0, changedExistingTests=diff,
        addedIndependentInvalidInputs=2, originalFiniteFixtureAssertionsByTokens=witness_count,
        productionMainDiff=0, physicalClasses=27, positiveMainCrc=19, sdkArtifactCount=len(c["sdkJars"]),
        staticApplicable=0, staticRawPmd=25, firstEvidenceCheckerFailure=ref(OUT / "first-verifier-failure.json"),
        secondEvidenceCheckerFailure=ref(recovery), priorRawEvidenceRecoveredWithoutReplay=True,
        preliminaryStyleFailure=ref(E / "PG39366-bug3272-api-context-prestyle-v1/manifest.json"),
        priorHelperPhysicalExact=6, priorHelperEvidence=ref(old), unfilteredTarget=target, unfilteredClassCounters=raw,
        unfilteredDeficits=deficits, standardScope=m["post"]["coverage"], oldExecUnion=0, noManualExclusions=True,
        whole451Accepted=False, newAcceptance=0, formalUpdated=False,
        terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(), proofs=proofs,
        raw=ref(unfiltered), rawCommand=ref(OUT / "raw-command.json"), archive=ref(retention), verifier=ref(__file__))
    write(OUT / "manifest.json", result)
    print(ref(OUT / "manifest.json")["sha256"], result["terminalAtUTC"])
    print(target, len(deficits), witness_count,
          [(a["method"], a["line"]) for a in deficits if a["type"].endswith("/ApiMetricContext")])


if __name__ == "__main__":
    main()
