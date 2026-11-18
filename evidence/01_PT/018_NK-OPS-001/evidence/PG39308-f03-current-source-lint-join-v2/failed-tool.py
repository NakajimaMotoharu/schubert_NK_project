"""Reconcile current source-only quality inputs with immutable public receipts."""

from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess
from xml.etree import ElementTree as XML

ROOT = Path.cwd()
B = Path("evidence/01_PT/018_NK-OPS-001/evidence")
OUT = B / "PG39308-f03-current-source-lint-join-v2"
START = Path("documents/400_PGPT/470_PMO/601_WBS66短期実行_20261117/423_F03現候補Main差分書式開始.json")
RULE = "tools/quality/static/checkstyle.xml"
MAIN = ":(glob)src/*/src/main/java/**/*.java"
TEST = ":(glob)src/*/src/test/java/**/*.java"
HOLD = {
    "TemporaryInfrastructureException", "FingerprintKeyRing", "ResponseSnapshotCodec", "WebStartupException",
    "RootFailedStartRecoveryTest", "RootFailedStartPairRecoveryTest", "SnapshotKeyCloseWitness",
    "pg9892_snapshot_key_close_witness",
}
OLD = B / "PG38442-f03-current-six-main-source-lint-v1/manifest.json"
STORAGE = B / "PG38502-f03-storage-current-full-static-v1/manifest.json"
OLD_TEST = B / "PG39102-f03-six-test-source-checkstyle-delta-v1/manifest.json"
TEST_FIVE = B / "PG39104-f03-five-current-test-source-checkstyle-v1/manifest.json"
LEGACY = B / "PG39168-p01810-guarded-jms-value-independent-v1/legacy-checkstyle-manifest.json"
ALLOWED_MODULES = {"api", "batch", "bootstrap", "protocol", "storage", "web"}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def ref(path):
    p = Path(path)
    return dict(path=str(p), sha256=sha(p.read_bytes()))


def load(path):
    return json.loads(Path(path).read_bytes())


def verify(value):
    path = Path(value["path"])
    assert ref(path) == value
    return path


def git(*args):
    return subprocess.check_output(["git", *args], timeout=60)


def tree(revision, kind):
    data = git("ls-tree", "-r", "-z", revision, "--", "src")
    pattern = re.compile(r"src/schubert-nk-(api|batch|bootstrap|protocol|storage|web)/src/" + kind + r"/java/.+\.java")
    matches = {}
    for line in data.decode().split("\0"):
        cols = line.split("\t", 1)
        if len(cols) != 2 or not pattern.fullmatch(cols[1]):
            continue
        mode, typ, oid = cols[0].split()
        assert mode in {"100644", "100755"} and typ == "blob"
        matches[cols[1]] = oid
    return matches


def safe_source(path):
    p = Path(path)
    return not p.is_absolute() and ".." not in p.parts and p.stem not in HOLD


def content_at(revision, path):
    assert safe_source(path)
    return sha(git("show", f"{revision}:{path}"))


def xml_names(xml_path, workdir=ROOT):
    xml = XML.parse(xml_path).getroot()
    assert xml.tag == "checkstyle" and not xml.findall(".//error")
    return {
        str((workdir / Path(x.get("name"))).resolve().relative_to(workdir))
        for x in xml.findall("file")
    }


def safe_xml(path, cwd):
    try:
        return xml_names(path, cwd)
    except (AssertionError, ValueError, OSError, XML.ParseError):
        return set()


def check_old():
    m = load(OLD)
    b = load(verify(m["physicalSourceProof"]))
    tool = [verify(x) for x in b["toolArtifacts"]]
    baseline = tree(m["source"], "main")
    assert m["actualExit"] == 0 and m["checkstyleFindings"] == 0 and m["sourceCount"] == len(baseline)
    assert set(m["modules"]) == ALLOWED_MODULES
    assert set(b["sourceIds"]) == set(baseline)
    assert xml_names(verify(m["checkstyleXml"])) == set(baseline)
    for key in ("checkstyleTerminal", "formatTerminal"):
        exit_info = load(verify(m[key]))
        assert exit_info["actualExit"] == 0
    return m, baseline, tool


def check_storage(core, wanted):
    m = load(STORAGE)
    begin = load(verify(m["staticBegin"]))
    term = load(verify(m["staticTerminals"]))
    assert m["actualExit"] == 0 and m["checkstyleFindings"] == 0 and m["formatExit"] == 0
    assert term["checkstyle"]["actualExit"] == term["format"]["actualExit"] == 0
    root = begin["commands"]["checkstyle"][begin["commands"]["checkstyle"].index("-c") + 1]
    assert str(root).endswith("/" + RULE)
    old = tree(m["source"], "main")
    current = tree(core, "main")
    return {p: dict(source=m["source"], sameTrackedBlob=current[p], receipt=ref(STORAGE))
        for p in wanted if p.startswith("src/schubert-nk-storage/") and
        p in begin["sourcePaths"] and current[p] == old.get(p)}


def verify_stream(path, metadata):
    for i in ("stdout", "stderr"):
        plain = path.with_name(path.name + "." + i)
        packed = plain.with_name(plain.name + ".gz")
        try:
            value = gzip.decompress(packed.read_bytes()) if packed.is_file() else plain.read_bytes()
        except (FileNotFoundError, gzip.BadGzipFile, EOFError):
            return False
        if sha(value) != metadata[i + "Sha256"]:
            return False
    return True


def scan_registered(changed, tool):
    remaining = dict(changed)
    output = {}
    rule_sha = sha(tool[2].read_bytes())
    for row in reversed(git("ls-files", "--", str(B)).decode().splitlines()):
        p = Path(row)
        id_match = re.match(r"PG(\d+)-.*static", p.parent.name)
        if p.name != "manifest.json" or not id_match or not 38443 <= int(id_match[1]) <= 39300:
            continue
        m = load(p)
        hashes = m.get("inputHashes", {})
        if RULE not in hashes or hashes[RULE] != rule_sha:
            continue
        eligible = {k for k, v in remaining.items() if hashes.get(k) == v}
        if not eligible:
            continue
        stages = m.get("stages", {})
        cs = stages.get("checkstyle", {})
        fm = stages.get("format", {})
        if (m.get("actualExit") != 0 or m.get("checkstyleFindings") != 0
                or cs.get("actualExit") != 0 or fm.get("actualExit") != 0
                or cs.get("timedOut") is not False or fm.get("timedOut") is not False):
            continue
        cmd = cs["command"]
        assert cmd[0] == str(tool[0]) and cmd[cmd.index("-jar") + 1] == str(tool[1])
        assert cmd[cmd.index("-c") + 1] == str(tool[2])
        assert fm["command"][0] == str(tool[0]) and str(tool[3]) in fm["command"]
        assert all("--" + flag in fm["command"] for flag in ("skip-reflowing-long-strings","dry-run","set-exit-if-changed"))
        if (not verify_stream(p.parent / "checkstyle", cs)
                or not verify_stream(p.parent / "format", fm)):
            continue
        xml = p.parent / "checkstyle.xml"
        seen = safe_xml(xml, ROOT)
        formatted = {str(Path(arg).relative_to(ROOT)) for arg in fm["command"]
                     if arg.startswith(str(ROOT)+"/src/")}
        for k in eligible & seen & formatted:
            output[k] = dict(sourceSha256=remaining.pop(k), receipt=ref(p), checkstyleXml=ref(xml))
        if not remaining:
            break
    return output, remaining


def run_source_checks(wanted, tool, output):
    if not wanted:
        return None
    assert all(safe_source(p) and (ROOT/p).resolve() == ROOT/p for p in wanted)
    for path, digest in wanted.items():
        assert sha(Path(path).read_bytes()) == digest
    out = output / "as-needed"
    out.mkdir()
    files = [str(ROOT / p) for p in sorted(wanted)]
    sources = out / "sources.txt"
    sources.write_text("".join(path + "\n" for path in files))
    xml = out / "checkstyle.xml"
    commands = {
        "checkstyle": [str(tool[0]), "-Xmx768m", "-jar", str(tool[1]), "-c", str(tool[2]),
                          "-f", "xml", "-o", str(ROOT / xml), "@" + str(ROOT / sources)],
        "format": [str(tool[0]), "-Xmx768m", "-jar", str(tool[3]), "--skip-reflowing-long-strings",
                   "--dry-run", "--set-exit-if-changed", *files],
    }
    stages = {}
    for stage, cmd in commands.items():
        p = subprocess.run(cmd, capture_output=True, timeout=60)
        stdout = out / (stage + ".stdout")
        stderr = out / (stage + ".stderr")
        stdout.write_bytes(p.stdout)
        stderr.write_bytes(p.stderr)
        stages[stage] = dict(command=cmd, actualExit=p.returncode, stdout=ref(stdout), stderr=ref(stderr),
            terminalAtUTC=datetime.now(timezone.utc).isoformat())
    assert xml_names(xml) == set(wanted)
    assert all(row["actualExit"] == 0 for row in stages.values())
    return dict(actualExit=0, stages=stages, xml=ref(xml), ownSourceHashes=wanted)


def write(path, value):
    with path.open("x") as f:
        f.write(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def main():
    OUT.mkdir()
    start = load(START)
    core, head = start["baseCore"], start["values"]["source"]
    latest=git("rev-parse","HEAD").decode().strip()
    assert not git("diff","--name-only",head,latest,"--",MAIN,TEST,RULE)
    m, baseline, tools = check_old()
    assert git("rev-parse", m["source"] + ":" + RULE) == git("rev-parse", core + ":" + RULE)
    now = tree(core, "main")
    assert now == tree(head,"main")
    main_held = {p: oid for p, oid in now.items() if not safe_source(p)}
    exact = {p: oid for p, oid in now.items() if safe_source(p) and baseline.get(p) == oid}
    delta = {p: content_at(core, p) for p, oid in now.items() if safe_source(p) and baseline.get(p) != oid}
    assert len(now) == 1027 and len(main_held) == 4 and len(delta) == 31
    assert all(baseline.get(p) == v for p,v in main_held.items())
    storage = check_storage(core, delta)
    for s in storage: delta.pop(s)
    main_proof, missing_main = scan_registered(delta, tools)
    old_test = load(OLD_TEST)
    t0 = tree(old_test["source"], "test")
    t1 = tree(head, "test")
    assert len(t0) == old_test["currentFiles"] and len(t1) == len(t0) + 1
    test_supplement = load(TEST_FIVE)
    assert test_supplement["actualExit"] == 0
    assert xml_names(verify(test_supplement["checkstyleXml"])) == set(test_supplement["inputHashes"])
    assert set(old_test["missingEligible"]) == set(test_supplement["inputHashes"])
    for name, digest in test_supplement["inputHashes"].items():
        assert content_at(old_test["source"], name) == digest
    count_before = old_test["confirmedCheckstyleFiles"] + len(test_supplement["inputHashes"])
    candidate_tests = {p for p in t1 if t1[p] != t0.get(p)}
    assert len(candidate_tests) == 16 and all(safe_source(p) for p in candidate_tests)
    legacy = load(LEGACY)
    legacy_names = xml_names(verify(legacy["xml"])) & candidate_tests
    assert len(legacy_names) == 1 and legacy["actualExit"] == 0
    assert all(t1[p] == tree(legacy["source"],"test")[p] for p in legacy_names)
    assert all(str(x) in legacy["command"] for x in tools[:3])
    test_delta = {p: content_at(head, p) for p in candidate_tests - legacy_names}
    test_proof, missing_test = scan_registered(test_delta, tools)
    first = dict(baseMain=ref(OLD), baseTest=ref(OLD_TEST), baseTestCompletedSupplement=ref(TEST_FIVE),
         oldMainSameGitBlobCount=len(exact), mainHoldNameMetadata=sorted(main_held),
         oldMainSameGitBlobs=exact, storageExact=storage, existingMain=main_proof,
         legacyTestCheckstyleOnly=dict(artifacts=sorted(legacy_names),proof=ref(LEGACY)),
         existingTest=test_proof, missingMain=missing_main, missingTest=missing_test)
    first["failedEarlierMetadataTool"] = ref(B / "PG39306-f03-current-source-lint-join-v1/attempt-1.json")
    first["streamOracle"] = ref(Path(__file__).with_name("5130_f03_stage_stream_receipt_checks.py"))
    write(OUT / "evidence-join-before.json", first)
    needed = {**missing_main, **missing_test}
    actual = run_source_checks(needed, tools, OUT)
    assert len(exact)+len(storage)+len(main_proof)+len(missing_main)+len(main_held)==len(now)
    assert len(test_proof)+len(missing_test)+len(legacy_names)==len(candidate_tests)
    complete_test = count_before + len(t1)-len(t0)
    result = dict(actualExit=0, productionCoreMain=core, source=head, newAcceptance=0,
        wholeF03Accepted=False, whole451Accepted=False, productTests=0, compiledClasses=0,
        mainCounts=dict(total=len(now),sameEligible=len(exact),storedIndependentStorageDelta=len(storage),
            existingIndividual=len(main_proof),newRequired=len(missing_main),qa056Hold=len(main_held),
            currentEligibleConfirmed=len(now)-len(main_held)),
        testCounts=dict(total=len(t1),confirmed=complete_test,baselineHeld=len(t1)-complete_test,
            revisedInputs=len(candidate_tests),existingIndividual=len(test_proof),legacySourceOnly=len(legacy_names),
            newRequired=len(missing_test)), oldResultsRerun=0,
        baseline=ref(OUT / "evidence-join-before.json"), newSourceOnlyCheck=actual,
        toolInputs=[ref(p) for p in tools], terminalAtUTC=datetime.now(timezone.utc).isoformat())
    write(OUT / "manifest.json", result)
    print(result["mainCounts"], result["testCounts"])


if __name__ == "__main__":
    main()
