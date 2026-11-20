"""Determine which independently verified public release values transfer to current class bytes."""

import os
from pathlib import Path
import runpy
import subprocess
from tempfile import TemporaryDirectory
from zipfile import ZipFile


UPPER = runpy.run_path(str(Path(__file__).with_name("5326_f02_group_lookup_upper.py")))
STORE, PLAN, COMMON = (UPPER[key] for key in ("EVIDENCE", "PLAN", "COMMON"))
ROOT = "dev/codex/schubert/nk/bootstrap/"
SCHEMA = "dev/codex/schubert/nk/api/bootstrap/SchemaHistoryAdmission"


def main():
    read, pin, git, sha = (UPPER["read"], *(COMMON[key] for key in ("pin", "git", "sha")))
    begin = read(next(PLAN.glob("845_*")))
    values = begin["values"]
    refs = values["oracleReferences"]
    core, source = values["productionCoreMain"], values["source"]
    assert all(pin(Path(record["path"])) == record for record in refs)
    assert not git("diff", "--name-only", source, core, "--", "src", ":(exclude)src/**/src/test/**")
    jar, class_file, signature, inventory, approval = (read(ref["path"]) for ref in refs[1:6])
    assert jar["productionCore"] == core and jar["provenPhysical"] == 1102
    assert signature["selected"] == 10 and inventory["tests"] == 18 and approval["tests"] == 8
    assert all(row["actualExit"] == 0 for row in (jar, signature, inventory, approval))
    assert all(signature[key] == 0 for key in ("failed", "errors", "skipped", "notRun"))
    assert all(inventory[key] == 0 for key in ("failed", "errors", "skipped", "notRun"))
    table = class_file["classHashes"]["bootstrap"]
    prior_path = next(STORE.glob("PG37414-*/manifest.json"))
    prior = read(prior_path)
    approval_row, = [row for row in prior["rows"] if row["label"] == "APPROVAL8"]
    assert approval_row["originalProof"] == refs[5]
    assert all(sha(git("show", f"{source}:{approval_row[k+'Path']}")) == approval_row[k+"Sha256"]
               for k in ("main", "test"))
    assert all(table[name+".class"] == value for name, value in approval_row["physicalClassSha256"].items())
    signature_unit = read(signature["evidence"][0]["path"])
    assert pin(Path(signature_unit["compiled"]["path"])) == signature_unit["compiled"]
    source_sig = read(signature_unit["compiled"]["path"])["classHashes"]["bootstrap"]
    chosen = [n for n in sorted(table) if n.startswith(ROOT + "ReleaseSignatureVerifier")]
    assert len(chosen) == 3 and all(table[name] == source_sig[name] for name in chosen)
    test_path = signature_unit["testFixture"]
    assert git("show", f"{source}:{test_path}") == git("show", f"{signature['source']}:{test_path}")
    inventory_unit_path = next(STORE.glob("PG37438-*/manifest.json"))
    inventory_unit = read(inventory_unit_path)
    old = inventory["allPhysicalHashes"]
    assert all(table[name+".class"] == old[name+".class"] for name in inventory["targetClasses"])
    compare_inputs = {name: digest == sha(git("show", f"{source}:{name}"))
                      for name, digest in inventory_unit["inputHashes"].items()
                      if "ReleaseInventory" in name or "SchemaHistoryAdmission.java" in name}
    assert len(compare_inputs) == 4 and sum(compare_inputs.values()) == 3
    different_schema = [name for name in (SCHEMA, SCHEMA + "$Row") if table[name+".class"] != old[name+".class"]]
    assert len(different_schema) == 2

    artifact = jar["qualifiedLocalArtifacts"]["bootstrap"]["artifact"]
    archive = Path(artifact["path"])
    assert pin(archive) == artifact
    tool_config = read(next(STORE.glob("PG40212-*/manifest.json")))["raw"]
    assert pin(Path(tool_config["tool"]["path"])) == tool_config["tool"]
    stream = Path(signature["evidence"][-1]["path"])
    assert pin(stream) == signature["evidence"][-1]
    out = STORE / values["run"]
    out.mkdir()
    with ZipFile(archive) as current, TemporaryDirectory(dir="/dev/shm", prefix="pgpt-public-rfc-raw-") as name:
        root = Path(name)
        entries = []
        for entry in chosen:
            path = root / entry
            path.parent.mkdir(parents=True, exist_ok=True)
            data = current.read(entry)
            assert sha(data) == table[entry]
            path.write_bytes(data)
            entries.append(str(path))
        command = [*tool_config["command"][:5], str(stream), *entries]
        now = subprocess.run(command, capture_output=True, check=False, timeout=35,
                             env={"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8"})
    raw_path = out / "public-rfc-unfiltered.tsv"
    raw_path.write_bytes(now.stdout)
    assert now.returncode == 0 and now.stderr == b""
    counters = {}
    for row in (line.split("\t") for line in now.stdout.decode().splitlines()):
        if row[0] == "CLASS":
            counters[row[1]] = {item.split(":")[0]: dict(zip(("missed", "covered"),
                                  map(int, item.split(":")[1:]))) for item in row[6:]}
    assert set(counters) == {name.removesuffix(".class") for name in chosen}
    misses = {name: {k: v["missed"] for k, v in kinds.items() if v["missed"]}
              for name, kinds in counters.items() if any(v["missed"] for v in kinds.values())}
    outcome = dict(actualExit=0, source=source, productionCore=core, canonicalDesign=values["canonicalDesignSource"],
        scopedReferenceOnly=True, approval=dict(originalCount=8, matchingMain=True, matchingTest=True,
             rawCounters=approval_row["rawCounters"], proof=refs[5]),
        currentSignature=dict(originalCount=10, matchingThreePhysical=True, matchingTest=True,
             rawUnfiltered=counters, missing=misses, measurement=pin(raw_path), command=command,
             ownRawFour100=not misses, proof=refs[3]),
        inventory=dict(originalCount=18, ownerPhysicalsStillSame=3, matchingSources=compare_inputs,
             changedLiveComponentClasses=different_schema, currentWholeFixtureNotRequalified=True,
             originIndependent=refs[4], originUnit=pin(inventory_unit_path)),
        originalRunsCombined=False, newProductTests=0, actualNativeOrSigningActions=0,
        heldTwoOwners=["ReleasePayloadVerification", "StartupReleaseManifest"], formalDelta=0,
        whole451Accepted=False, wholeP01802Accepted=False,
        sourceEvidence=[*refs, pin(prior_path)], terminalAtUTC=COMMON["timestamp"]())
    COMMON["dump"](out / "manifest.json", outcome)
    print(pin(out / "manifest.json"), list(misses), different_schema)


if __name__ == "__main__":
    main()
