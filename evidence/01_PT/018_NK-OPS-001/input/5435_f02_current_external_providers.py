"""Bind the four current artifacts' external reference names to their pinned SDK archives."""

from datetime import datetime, timezone
import gzip
from hashlib import sha256
import json
from pathlib import Path
import runpy
import subprocess


HERE = Path(__file__).resolve()
ROOT = HERE.parents[4]
PLAN = next((ROOT / "documents/400_PGPT/470_PMO").glob("601_*"))
OPS = ROOT / "evidence/01_PT/018_NK-OPS-001/evidence"
PRIOR = runpy.run_path(str(HERE.with_name("5190_f02_external_reference_delta.py")))


def pin(path):
    return {"path": str(path), "sha256": sha256(Path(path).read_bytes()).hexdigest()}


def data(ref):
    assert pin(ref["path"]) == ref
    return Path(ref["path"]).read_bytes()


def main():
    start = json.loads(next(PLAN.glob("1132_F02現四*")).read_bytes())
    v = start["values"]
    refs = v["oracleReferences"]
    data(refs[0])
    graph, prior, model = [json.loads(data(r)) for r in refs[1:]]
    core = v["productionCoreMain"]
    assert graph["productionCore"] == core and graph["actualExit"] == 0
    assert prior["actualExit"] == model["actualExit"] == 0
    assert model["matchedProductPomCount"] == 6
    assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip() == v["source"]
    assert not subprocess.check_output(
        ["git", "diff", "--name-only", prior["source"], core, "--", "pom.xml", "src/*/pom.xml"],
        cwd=ROOT,
    )
    old_ref = next(r for r in prior["evidence"] if r["path"].endswith("/external-origins.json"))
    old = json.loads(data(old_ref))
    raw = gzip.decompress(data(graph["raw"][0])).decode()
    rows = [line.split(None, 3) for line in raw.splitlines()
            if line.startswith(" ") and " -> " in line]
    current = {(origin, target) for origin, arrow, target, place in rows if place == "not found"}
    assert len(current) == graph["externalNotOnClasspath"] == 385
    assert current == {tuple(pair) for pair in old["all385"]}
    origin_run, checkpoint, pins, _ = PRIOR["origin_inputs"]()
    types = {target for _, target in current}
    providers = PRIOR["build_member_index"](pins, types)
    assert len(types) == 53 and all(len(items) == 1 for items in providers.values())
    unique = {name: entries[0] for name, entries in providers.items()}
    assert unique == old["classOrigins"]
    jar_count = len({record["archive"]["path"] for record in unique.values()})
    assert jar_count == prior["distinctProvidingJars"] == 10
    result = dict(
        actualExit=0, source=v["source"], productionCore=core, startEvent=start["eventId"],
        terminalAtUTC=datetime.now(timezone.utc).isoformat(), inputRefs=refs, runner=pin(HERE),
        classOriginProof=old_ref, fullArchiveRosterProofs=[pin(origin_run), pin(checkpoint)],
        sourcePomByteUnchangedAgainstPrior=True, exactCurrentOriginTargetPairs=385,
        distinctReferenceTypes=len(types), archivesChecked=len(pins), providingArchives=jar_count,
        unknownExternalOrigins=0, ambiguousExternalOrigins=0, newJdeps=0, newCompile=0,
        newProductTests=0, runtimeResolution=False, wholeF02=False, whole451=False,
        newFormalAcceptance=0,
    )
    out = OPS / v["run"]
    out.mkdir()
    (out / "manifest.json").write_text(json.dumps(result, indent=2) + "\n")
    print("385 exact pairs, 53 names, 10 unique provider archives, 47 archives rehashed")


if __name__ == "__main__":
    main()
