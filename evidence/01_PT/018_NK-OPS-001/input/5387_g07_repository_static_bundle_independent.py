"""Verify reported checksum signals, then scan the rest of the public interval."""

from collections import Counter
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import re
import runpy
import subprocess
from tempfile import TemporaryDirectory


INPUT = Path(__file__).parent
history = runpy.run_path(str(INPUT / "5365_g07_public_history_utc42.py"))
repository = runpy.run_path(str(INPUT / "5384_f02_repository_type_dependencies.py"))
V, R, C, H = (repository[key] for key in ("V", "R", "C", "H"))
OPS = history["OPS"]
COUNTS = {40568: 8, 40572: 1, 40574: 8, 40584: 3, 40586: 10, 40592: 34}


def reproduction(root, number):
    def anchors(name):
        return [C["write_fixture"](root, H["P"] + m + "." + name, C["MARKER"]) for m in H["MODULES"]]

    if number == 40568:
        return C["inputs"](root) + R["additional_sources"](root)
    if number == 40572:
        return anchors("Marker") + V["fixture_sources"](root)
    if number == 40584:
        return anchors("Anchor") + repository["fixture"](root)
    prior = C["inputs"](root) + R["additional_sources"](root) + V["fixture_sources"](root)
    return prior + repository["fixture"](root) if number == 40586 else prior


def current_signals(source_log, manifest, target):
    pin, git, read, digest = (history[key] for key in ("pin", "git", "read", "digest"))
    anomalies = {item["start"] for item in source_log["scans"]["textCommitDiffs"]["signalLocations"]}
    assert len(anomalies) == 64
    assert source_log["scans"]["textCommitDiffs"]["rules"] == {"generic-api-key": 64}
    scanner = Path(source_log["tool"]["path"])
    assert pin(scanner) == source_log["tool"]
    new_stream, original_stream = io.BytesIO(), io.BytesIO()
    counts, evidence = Counter(), []
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-g07-isolated-checksums-") as workspace:
        root = Path(workspace)
        for commit in source_log["commits"]:
            parent = git("rev-parse", commit + "^").decode().strip()
            for row in git("diff", "--no-renames", "--numstat", "-z", parent, commit).split(b"\0"):
                if not row:
                    continue
                add, delete, filename = row.decode().split("\t", 2)
                assert (add, delete) != ("-", "-")
                diff = git("diff", "--no-ext-diff", "--no-textconv", "--text", "--no-renames",
                           "--unified=0", parent, commit, "--", filename)
                first = original_stream.getvalue().count(b"\n") + 1
                header = f"\n{filename} {commit}\n".encode()
                original_stream.write(header + diff + b"\n")
                new_stream.write(header)
                signal_indices = [line - first - 2 for line in sorted(anomalies)
                                  if first + 2 <= line < first + 2 + len(diff.split(b"\n"))]
                if not signal_indices:
                    new_stream.write(diff + b"\n")
                    continue
                path = Path(filename)
                code = int(re.match(r"PG(\d+)-", path.parent.name)[1])
                assert code in COUNTS and delete == "0"
                archived = git("show", f"{commit}:{filename}")
                old = json.loads(archived)
                if code == 40592:
                    assert path.name == "eligible-delta.json"
                    candidates = old["unchangedGitBlobIds"]
                else:
                    assert path.name == "manifest.json" and old["productTests"] == old["productJars"] == 0
                    candidates = old["inputPhysical"]
                    assert code not in counts
                    receipts = old["receipts"]
                    compiler = receipts.get("compile-fixture", receipts.get("fixture"))
                    assert compiler["actualExit"] == 0
                    target_dir = root / str(code)
                    sources = reproduction(target_dir / "sources", code)
                    out = target_dir / "classes"
                    result = subprocess.run(
                        [H["JAVA"].with_name("javac"), "--release", "25", "-Xlint:all", "-Werror", "-proc:none",
                         "-d", out, *sources],
                        capture_output=True, timeout=60,
                    )
                    assert result.returncode == 0 and not result.stdout and not result.stderr
                    physical = {p.relative_to(out).as_posix().removesuffix(".class").replace("/", "."):
                                digest(p.read_bytes()) for p in out.rglob("*.class")}
                    assert all(physical.get(name) == value for name, value in candidates.items())
                lines = diff.split(b"\n")
                for index in signal_indices:
                    matched = re.fullmatch(rb'\+\s*"([^"]+)": "([0-9a-f]+)",?', lines[index])
                    assert matched
                    key, value = [part.decode() for part in matched.groups()]
                    assert candidates[key] == value
                    if code == 40592:
                        assert len(value) == 40
                        assert git("rev-parse", f"{old['currentSource']}:{key}").decode().strip() == value
                    else:
                        assert len(value) == 64
                    lines[index] = lines[index].replace(matched[2], b"VERIFIED_CHECKSUM")
                new_stream.write(b"\n".join(lines) + b"\n")
                counts[code] = len(signal_indices)
                evidence.append(dict(path=filename, commit=commit, sha256=digest(archived),
                                     checksumSignals=len(signal_indices)))
    assert counts == COUNTS
    assert digest(original_stream.getvalue()) == source_log["scans"]["textCommitDiffs"]["sha256"]
    checks = history["scan"](scanner, {"checksumVerifiedText": new_stream})["checksumVerifiedText"]
    assert checks["actualExit"] == 0 and not checks["signalLocations"]
    assert source_log["scans"]["gzipPublicStreams"]["actualExit"] == 0
    target.parent.mkdir()
    with target.open("x") as fp:
        json.dump(dict(actualExit=0, source=source_log["source"], productionCore=source_log["productionCore"],
                       previousCursor=source_log["previousCursor"], newCursor=source_log["source"],
                       first=pin(manifest), tool=pin(scanner), secretFindings=0, rawSecretsStored=0,
                       gitBlobSignals=34, syntheticClassShaSignals=30, syntheticCompileOnly=5,
                       verificationEvidence=evidence, projectedTextCheck=checks,
                       gzipVersions=len(source_log["gzipVersions"]), textPathVersions=len(source_log["textPathVersions"]),
                       gitCommitCount=len(source_log["commits"]), privateArchivesRead=0,
                       productTestExecutions=0, wholeG07=False, whole451=False,
                       terminalAtUTC=datetime.now(timezone.utc).isoformat()), fp, ensure_ascii=False, indent=2)
        fp.write("\n")
    print(pin(target))


if __name__ == "__main__":
    raw = next(OPS.glob("PG40596-*/manifest.json"))
    current_signals(history["read"](raw), raw, OPS / "PG40598-g07-repository-static-bundle-independent-v1/manifest.json")
