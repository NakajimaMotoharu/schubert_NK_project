"""Reconcile the original SSC-461 caller roster against the current production commit."""

from collections import Counter
from pathlib import Path
import runpy
import subprocess


RUN = runpy.run_path(str(Path(__file__).with_name("5326_f02_group_lookup_upper.py")))
STORE, PLAN, COMMON = (RUN[name] for name in ("EVIDENCE", "PLAN", "COMMON"))
LEGACY = "StorageIoException.preserveFatal("
ADAPTER = "JdbcFailureGraph.preserveFatal("
SOURCE_SCOPE = "src/**/src/main/**/*.java"


def sites(commit, token):
    command = ["git", "grep", "-n", "-F", "-z", token, commit, "--", SOURCE_SCOPE]
    result = subprocess.run(command, capture_output=True, check=False, timeout=35)
    assert result.returncode in (0, 1)
    found = {}
    for line in result.stdout.splitlines():
        reference, number, contents = line.decode().split("\0", 2)
        revision, _, path = reference.partition(":")
        assert revision == commit and token in contents
        anchors = found.setdefault(path, [])
        anchors.extend([int(number)] * contents.count(token))
    return found


def module(path):
    return path.split("/")[1]


def main():
    pin, dump, git = (COMMON[k] for k in ("pin", "dump", "git"))
    read = RUN["read"]
    start = read(next(PLAN.glob("860_*")))
    work = start["values"]
    refs = work["oracleReferences"]
    assert all(pin(Path(item["path"])) == item for item in refs)
    original, file_calls, checkpoint, package, physical = (read(ref["path"]) for ref in refs[1:6])
    core, source = work["productionCoreMain"], work["source"]
    assert package["productionCore"] == checkpoint["productionCore"] == core
    assert file_calls["fullF02Accepted"] is False
    assert physical["violations"] == [
        {"origin": "dev.codex.schubert.nk.storage.StorageIoException",
         "target": "java.sql.SQLException", "artifact": "java.sql"}]
    historical = sites(original["source"], LEGACY)
    assert {row["path"] for row in original["sourceFiles"]} == historical.keys()
    assert Counter({key: sum(len(rows) for path, rows in historical.items() if module(path) == key)
                    for key in original["moduleCallerSites"]}) == Counter(original["moduleCallerSites"])
    before, after = sites(core, LEGACY), sites(core, ADAPTER)
    bridge, = [path for path in before if path.endswith("/JdbcFailureGraph.java")]
    assert len(before.pop(bridge)) == 1 and bridge not in historical and bridge not in after
    assert set(before) | set(after) == historical.keys()
    assert all(len(before.get(path, [])) + len(after.get(path, [])) == len(lines)
               for path, lines in historical.items())
    assert not sites(core, "::preserveFatal")
    counts = {}
    records = []
    for path in sorted(historical):
        category = module(path)
        low_level = category == "schubert-nk-storage"
        previous = len(historical[path])
        old = before.get(path, [])
        new = after.get(path, [])
        counter = counts.setdefault(category, Counter())
        counter.update(originalSites=previous, currentLegacySites=len(old), migratedAdapterSites=len(new))
        records.append(dict(path=path, module=category, originalCount=previous,
                            migratedCurrentLines=new, legacyCurrentLines=old,
                            scope="OWNED_FILE_OPERATION_CONVERSION" if low_level else
                            "UPPER_CALLER_NEEDS_ITS_OWN_QA_AND_EXACT_PT_REVIEW"))
    low = counts["schubert-nk-storage"]
    assert low == {"originalSites": 3, "currentLegacySites": 3, "migratedAdapterSites": 0}
    upper = [entry for name, entry in counts.items() if name != "schubert-nk-storage"]
    assert [sum(row[field] for row in upper) for field in ("originalSites", "migratedAdapterSites", "currentLegacySites")] == [104, 48, 56]
    original_note = git("show", f"{work['canonicalDesignSource']}:{refs[-1]['path']}").decode()
    assert "旧入口とSQL次辺は、既利用側とFileOperation全件の変更・再試験が終わるまで互換維持する" in original_note
    output = STORE / work["run"]
    output.mkdir()
    report = dict(actualExit=0, source=source, productionCore=core, originalAuditSource=original["source"],
                  originalNamedMainSources=len(historical), originalUpper=104, confirmedMigratedUpper=48,
                  confirmedRemainingUpper=56, storageOwnedSites=3, bridgeCount=1,
                  moduleCounts=counts, exactAnchors=records, sourceProofOnly=True, staleGroupCountsExcluded=True,
                  noSharedArtifactOrRuntimeMoved=True,
                  remainingRequirements=["Original compatible Storage entry remains for all FileOperation callbacks.",
                                         "No currently held classes, runtime DB, native or release action inferred.",
                                         "Actual current six JARs, all F03 and 451 still require qualifying evidence."],
                  sourceEvidence=refs, rerunProductTests=0, actualBackendActions=0,
                  newFormalAcceptance=0, terminalAtUTC=COMMON["timestamp"]())
    dump(output / "manifest.json", report)
    print(pin(output / "manifest.json"), counts)


if __name__ == "__main__":
    main()
