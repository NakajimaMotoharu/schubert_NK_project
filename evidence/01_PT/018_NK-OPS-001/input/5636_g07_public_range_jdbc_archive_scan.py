"""Scan the frozen public text interval and validate its six synthetic JaCoCo blobs."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
import runpy
import subprocess
from tempfile import TemporaryDirectory


p = runpy.run_path(str(Path(__file__).with_name("5613_g07_public_view_tests_scan.py")))
PMO, OPS, SCAN, DOMAIN, BASELINE, git, pin = (
    p[key] for key in ("PMO", "OPS", "SCAN", "DOMAIN", "BASELINE", "fetch_git", "pin")
)
SUFFIXES = p["SUFFIXES"] | {".stdout", ".stderr", ".exec"}
ALLOWED_EXEC_RUNS = {41202, 41204, 41210, 41214, 41226, 41230}
KNOWN_CLASS_DIGEST = re.compile(rb'^\+\s*"HttpByteRangeUnitTokenTest\.class": "([0-9a-f]{64})"')
RESOLVED_COMMIT = p["GIT_ID_FIELD"]


def read(path):
    return json.loads(path.read_bytes())


def report_result(binary, report, classify):
    used = subprocess.run([str(SCAN), "stdin", "--redact=100", "--no-banner", "--report-format", "json",
                          "--report-path", report], input=binary, capture_output=True, timeout=35)
    assert used.returncode in (0,1) and report.is_file()
    candidates = json.loads(report.read_bytes()) or []
    rows = binary.splitlines()
    output = []
    for result in candidates:
        index, rule = result["StartLine"], result["RuleID"]
        source = rows[index-1] if 0 < index <= len(rows) else b""
        reason = classify(rule, source)
        output.append(dict(rule=rule, streamLine=index, meaning=reason))
    return used.returncode, output


def main():
    start, = PMO.glob("601_*/1658_*.json")
    context = read(start)["values"]
    for ref in context["oracleReferences"]:
        assert pin(Path(ref["path"])) == ref
    original_path = Path(context["oracleReferences"][1]["path"])
    head = context["source"]
    base = read(original_path)["headInclusive"]
    assert git("rev-parse","HEAD","origin/dev-foundation").decode().splitlines() == [head,head]
    assert git("merge-base",base,head).decode().strip() == base
    baseline = git("rev-parse",f"{head}:{BASELINE}").decode().strip()
    assert git("rev-parse",f"{base}:{BASELINE}").decode().strip() == baseline
    history = git("rev-list","--reverse",f"{base}..{head}").decode().splitlines()
    assert history
    detector_git_ids = {}
    known, = OPS.glob("PG41206-*/redacted-scan-review.json")
    proof = read(known)
    class_digest = read(known.parent/"manifest.json")["typedPhysicalHashes"][proof["exactClass"]]
    assert proof["independentRecompileMatch"] and proof["confirmedSecretFindings"] == 0
    paths, commits, execs, text = {}, [], {}, []
    for commit in history:
        changed = git("diff","--name-only","-z",commit+"^",commit).decode().split("\0")[:-1]
        assert all(n.startswith(DOMAIN) and Path(n).suffix in SUFFIXES and
                   not n.endswith((".safe.json",".raw.txt")) for n in changed)
        deltas = []
        for path in changed:
            if path.endswith(".exec"):
                assert path not in execs
                execs[path] = commit
                continue
            diff = git("diff","--no-renames","--no-ext-diff","--unified=0",commit+"^",commit,"--",path)
            assert not any(line.startswith((b"Binary files ", b"GIT binary patch")) for line in diff.splitlines())
            deltas.append(diff)
            paths.setdefault(path,[]).append(diff)
        delta = b"\n".join(deltas)
        text.append(delta)
        commits.append(dict(commit=commit, affected=len(changed), textPatchSha256=sha256(delta).hexdigest()))
    assert len(execs) == 6
    decoder = runpy.run_path("tools/quality/jacoco_readonly_exec_subset.py")["decode"]
    checked_binary = []
    for path, commit in sorted(execs.items()):
        run = int(Path(path).parent.name.split("-",1)[0].removeprefix("PG"))
        assert run in ALLOWED_EXEC_RUNS
        body = git("show",f"{commit}:{path}")
        assert git("show",f"{head}:{path}") == body
        manifest = Path(path).with_name("manifest.json")
        witness = json.loads(git("show",f"{head}:{manifest}"))
        references = witness.get("originals") or witness.get("originalArtifacts")
        entry, = [r for r in references if r["path"].endswith("/unit.exec")]
        assert sha256(body).hexdigest() == entry["sha256"]
        parsed = decoder(body,set())
        assert len(parsed["sessions"]) == 1 and parsed["totalClassRecords"] > 0
        assert parsed["sessions"][0]["labelBytesHex"] == Path(path).parent.name.encode().hex()
        printable = b"\n".join(re.findall(rb"[ -~]{8,}", body))
        checked_binary.append(dict(path=path,sha256=entry["sha256"],inlineBinaryRecords=parsed["totalClassRecords"],
            printableExtractSha256=sha256(printable).hexdigest(), archiveManifest=pin(manifest)))
        paths[path] = [printable]
    assert len({item["sha256"] for item in checked_binary}) == len(execs)

    def classify(rule, line):
        match = RESOLVED_COMMIT.match(line)
        if rule == "sourcegraph-access-token" and match:
            oid = match[2].decode()
            if oid not in detector_git_ids:
                result = subprocess.run(["git","cat-file","-t",oid],capture_output=True,timeout=10)
                detector_git_ids[oid] = result.stdout == b"commit\n"
            if detector_git_ids[oid]:
                return "existing Git commit object"
        digest = KNOWN_CLASS_DIGEST.match(line)
        if rule == "generic-api-key" and digest and digest[1].decode() == class_digest:
            return "previously independently verified synthetic Java class SHA-256"
        return None

    aggregate = b"\n".join(text)
    unresolved = []
    by_path = []
    with TemporaryDirectory(dir="/dev/shm",prefix="pgpt-g07-range-jdbc-") as scratch:
        target = Path(scratch)
        combined_exit, combined = report_result(aggregate,target/"aggregate.json",classify)
        unresolved.extend(dict(inScope="combined",**result) for result in combined if not result["meaning"])
        for index, (path, content) in enumerate(paths.items()):
            _, findings = report_result(b"\n".join(content),target/f"file-{index}.json",classify)
            by_path.extend(dict(path=path,**finding) for finding in findings)
            unresolved.extend(dict(inScope=path,**result) for result in findings if not result["meaning"])
    out = OPS/context["run"]
    out.mkdir()
    result = out/"manifest.json"
    data = dict(actualExit=int(bool(unresolved)),terminalAtUTC=datetime.now(timezone.utc).isoformat(),
                source=head,core=context["productionCoreMain"],baseExclusive=base,headInclusive=head,
                previousScan=pin(original_path),baselineTree=baseline,commits=len(commits),commitTrace=commits,
                uniquePaths=len(paths),verifiedSyntheticExec=checked_binary,combinedExit=combined_exit,
                combinedReport=combined,perPathReports=by_path,unresolved=unresolved,
                secretFindings=0 if not unresolved else None,detectorRulesChanged=False,
                independentlyVerifiedEarlierDigest=pin(known),privateRawRead=0,actualProductTests=0,
                wholeG07=False,whole451=False,formalDelta=0)
    with result.open("x") as file:
        json.dump(data,file,ensure_ascii=False,indent=2)
        file.write("\n")
    print(pin(result),len(commits),len(paths),len(combined),len(by_path),unresolved)
    return data["actualExit"]


if __name__ == "__main__":
    raise SystemExit(main())
