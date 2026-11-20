"""Independently classify the two findings in the fixed public Git interval."""

from datetime import datetime, timezone
import json
from pathlib import Path
import runpy
import subprocess
from tempfile import TemporaryDirectory


MAIN = runpy.run_path(str(Path(__file__).with_name("5356_g07_capacity_bom_delta.py")))
OPS, git, read, pin, digest = (MAIN[name] for name in ("OPS", "git", "read", "pin", "digest"))


def main():
    previous = next(OPS.glob("PG40426-*/manifest.json"))
    trial = read(previous)
    assert trial["actualExit"] == trial["scans"]["textPatch"]["actualExit"] == 1
    assert trial["scans"]["textPatch"]["rules"] == {"generic-api-key": 2}
    assert all(trial["scans"][kind]["actualExit"] == trial["scans"][kind]["count"] == 0
               for kind in ("projectedMixedMetadata", "gzipLogs"))
    paths = [next(OPS.glob(f"PG404{n:02d}-*/manifest.json")) for n in (2, 4)]
    old, new = (trial[key] for key in ("previousCursor", "source"))
    flags = {5880: str(paths[0]), 6456: str(paths[1])}
    original = {}
    for path in paths:
        blob = git("show", f"{new}:{path}")
        original[str(path)] = json.loads(blob)
        assert digest(blob) == pin(path)["sha256"]
    before, after = (original[str(p)] for p in paths)
    assert before["fixtureClassHashes"] == after["fixtureClassHashes"]
    assert len(before["fixtureClassHashes"]) == 36
    anchor = read(next(OPS.glob("PG40406-*/manifest.json")))
    assert anchor["identicalFixtureClassfiles"] == 36 and anchor["actualExit"] == 0
    assert all(ref in anchor["sourceEvidence"] for ref in map(pin, paths))
    all_paths = {}
    for line in git("diff", "--no-renames", "--numstat", "-z", old, new).split(b"\0"):
        if line:
            a, b, name = line.decode().split("\t", 2)
            all_paths[name] = (a, b)
    names = [n for n, v in sorted(all_paths.items()) if n not in trial["typedMetadata"]
             and v != ("-", "-") and not n.endswith(".exec")]
    scope = ["diff", "--no-ext-diff", "--no-textconv", "--no-renames", "--text", old, new, "--"]
    raw_original = git(*scope, *names)
    assert digest(raw_original) == trial["scans"]["textPatch"]["sha256"]
    key = "dev.codex.schubert.nk.api.KnownValue"
    for row, path in flags.items():
        line = raw_original.decode().splitlines()[row - 1]
        assert line.lstrip("+ ").rstrip(",") == json.dumps(key) + ": " + json.dumps(
            original[path]["fixtureClassHashes"][key])
        assert all_paths[path][1] == "0"
    project = MAIN["project"]
    for path in paths:
        obj = original[str(path)]
        obj["fixtureClassHashes"] = project(obj["fixtureClassHashes"])
    patched = git(*scope, *(n for n in names if n not in original))
    body = patched + b"\n".join(json.dumps(record, indent=2).encode() for record in original.values())
    gitleaks = Path(trial["scanner"]["path"])
    assert pin(gitleaks) == trial["scanner"]
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-remaining-metadata-") as temp:
        report = Path(temp) / "scanner.json"
        command = [str(gitleaks), "stdin", "--redact=100", "--no-banner", "--report-format=json",
                   "--report-path=" + str(report)]
        child = subprocess.run(command, input=body, capture_output=True, check=False, timeout=80)
        discoveries = read(report) if report.is_file() else []
    assert child.returncode == 0 and discoveries == []
    data = dict(actualExit=0, source=new, productionCore=trial["productionCore"], previousCursor=old,
                newCursor=new, textPaths=trial["verifiedTextPaths"]+len(trial["typedMetadata"]),
                gzipPaths=len(trial["gzipPaths"]), binaryMetadataOnly=len(trial["binaryMetadata"]),
                evaluatedCommits=trial["deltaCommits"], firstReportedSignals=2, firstResult=pin(previous),
                matchedMetadata=[dict(path=path, patchLine=line, className=key) for line, path in flags.items()],
                fixedInputMetadataClassCount=36, physicalScopeVerification=pin(next(OPS.glob("PG40406-*/manifest.json"))),
                firstGzipAndTypedStreamsReplayed=False, finalTextDigest=digest(body), secretFindings=0,
                scannerUnchanged=True, actualProductTests=0, wholeG07Accepted=False, whole451Accepted=False,
                terminalAtUTC=datetime.now(timezone.utc).isoformat())
    folder = OPS / "PG40428-g07-capacity-and-bom-delta-independent-v1"
    folder.mkdir()
    dest = folder / "manifest.json"
    with dest.open("x") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        file.write("\n")
    print(pin(dest))


if __name__ == "__main__":
    main()
