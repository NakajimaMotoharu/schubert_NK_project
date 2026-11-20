"""Scan the exact public interval and verify the five new standalone exec objects."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
import runpy
import subprocess
from tempfile import TemporaryDirectory


H = runpy.run_path(str(Path(__file__).with_name("5636_g07_public_range_jdbc_archive_scan.py")))
PMO, OPS, DOMAIN, BASELINE, git, pin = (H[n] for n in ("PMO", "OPS", "DOMAIN", "BASELINE", "git", "pin"))
EXEC_RUNS = {41246, 41248, 41250, 41256, 41260}
EXTRA_PUBLIC = {
    "documents/300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md",
    "program/characterization/src/main/java/dev/codex/schubert/characterization/ArtifactComparator.java",
    "program/characterization/tests/java/dev/codex/schubert/characterization/ArtifactComparatorTest.java",
}


def main():
    ctx = H["read"](next(PMO.glob("601_*/1691_*.json")))["values"]
    refs = [Path(row["path"]) for row in ctx["oracleReferences"]]
    assert [pin(path) for path in refs] == ctx["oracleReferences"]
    base = H["read"](refs[1])["headInclusive"]
    previous = H["read"](refs[2])
    assert previous["source"] == base and previous["wholeRangeClassified"]
    assert previous["confirmedSecrets"] == 0 and previous["unresolved"] == 0
    head = ctx["source"]
    assert git("rev-parse", "HEAD", "origin/dev-foundation").decode().splitlines() == [head] * 2
    assert git("merge-base", base, head).decode().strip() == base
    tree = git("rev-parse", f"{head}:{BASELINE}").decode().strip()
    assert tree == git("rev-parse", f"{base}:{BASELINE}").decode().strip()
    history = git("rev-list", "--reverse", f"{base}..{head}").decode().splitlines()
    text, archives, parts, fingerprints = {}, {}, [], []
    for commit in history:
        paths = git("diff", "--name-only", "-z", commit + "^", commit).decode().split("\0")[:-1]
        assert all((path.startswith(DOMAIN) or path in EXTRA_PUBLIC) and Path(path).suffix in H["SUFFIXES"]
                   and not path.endswith((".safe.json", ".raw.txt")) for path in paths)
        delta = []
        for path in paths:
            if Path(path).suffix == ".exec":
                assert path not in archives
                archives[path] = commit
                continue
            patch = git("diff", "--no-renames", "--no-ext-diff", "--unified=0", commit + "^", commit, "--", path)
            assert not any(line.startswith((b"Binary files ", b"GIT binary patch")) for line in patch.splitlines())
            delta.append(patch)
            text.setdefault(path, []).append(patch)
        data = b"\n".join(delta)
        parts.append(data)
        fingerprints.append(dict(commit=commit, paths=len(paths), patchSha256=sha256(data).hexdigest()))
    assert len(archives) == len(EXEC_RUNS)
    decode = runpy.run_path("tools/quality/jacoco_readonly_exec_subset.py")["decode"]
    binary = []
    seen = set()
    for path, commit in sorted(archives.items()):
        run = Path(path).parent.name
        number = int(run.split("-", 1)[0][2:])
        assert number in EXEC_RUNS and number not in seen
        seen.add(number)
        content = git("show", f"{commit}:{path}")
        assert content == git("show", f"{head}:{path}")
        manifest = Path(path).with_name("manifest.json")
        witness = json.loads(git("show", f"{head}:{manifest}"))
        refs = witness.get("original") or witness.get("originals") or witness["originalArtifacts"]
        item, = [row for row in refs if Path(row["path"]).name == Path(path).name]
        assert sha256(content).hexdigest() == item["sha256"]
        parsed = decode(content, set())
        assert len(parsed["sessions"]) == 1 and parsed["sessions"][0]["labelBytesHex"] == run.encode().hex()
        assert parsed["totalClassRecords"] > 0
        printable = b"\n".join(re.findall(rb"[ -~]{8,}", content))
        text[path] = [printable]
        binary.append(dict(path=path, sha256=item["sha256"], records=parsed["totalClassRecords"],
                           manifest=pin(manifest), printableSha256=sha256(printable).hexdigest()))
    assert seen == EXEC_RUNS

    objects = {}

    def classify(rule, line):
        found = H["RESOLVED_COMMIT"].match(line)
        if rule != "sourcegraph-access-token" or not found:
            return None
        object_id = found[2].decode()
        if object_id not in objects:
            result = subprocess.run(["git", "cat-file", "-t", object_id], capture_output=True, timeout=10)
            objects[object_id] = result.stdout.strip()
        if objects[object_id] == b"commit":
            return "existing Git commit"
        if objects[object_id] == b"tree" and object_id == tree:
            return "exact protected Current baseline tree"
        return None

    unresolved = []
    paths = []
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-g07-media-comparison-") as temp:
        scratch = Path(temp)
        combined, by_interval = H["report_result"](b"\n".join(parts), scratch / "aggregate.json", classify)
        unresolved.extend(dict(scope="aggregate", **item) for item in by_interval if not item["meaning"])
        for idx, (path, seq) in enumerate(text.items()):
            _, results = H["report_result"](b"\n".join(seq), scratch / f"path-{idx}.json", classify)
            paths.extend(dict(file=path, **item) for item in results)
            unresolved.extend(dict(file=path, **item) for item in results if not item["meaning"])
    out = OPS / ctx["run"]
    out.mkdir()
    result = dict(actualExit=int(bool(unresolved)), baseExclusive=base, headInclusive=head,
                  productionCore=ctx["productionCoreMain"], baselineTree=tree, commits=len(history),
                  commitFingerprints=fingerprints, uniquePaths=len(text), verifiedSyntheticExec=binary,
                  aggregateExit=combined, aggregateCandidates=by_interval, pathCandidates=paths,
                  unresolved=unresolved, confirmedSecrets=None if unresolved else 0,
                  scannerRulesChanged=False, actualProductTests=0, wholeG07=False, whole451=False,
                  formalDelta=0, terminalAtUTC=datetime.now(timezone.utc).isoformat())
    with (out / "manifest.json").open("x") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(len(history), len(text), len(binary), len(by_interval), len(paths), len(unresolved))


if __name__ == "__main__":
    main()
