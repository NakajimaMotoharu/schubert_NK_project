"""Verify the A02 ordered-session oracle from original offline PT and static evidence."""

from collections import Counter
import gzip
import hashlib
from pathlib import Path
import re
import runpy
import subprocess
from xml.etree import ElementTree as ET

HELPERS = runpy.run_path(str(Path(__file__).with_name("5255_p020_search_empty_independent.py")))
P, R, E = (HELPERS[name] for name in ("P", "R", "E"))
read, save, ref = (HELPERS[name] for name in ("read", "save", "ref"))
OLD = E / "PG40128-p020-path-contract-green206-v2"
OLD_POST = E / "PG40132-p020-path-contract-independent-v1"
RED = E / "PG40206-p020-a02-session-census-red208-v1"
UNIT = E / "PG40208-p020-a02-session-census-green208-v1"
STATIC = E / "PG40210-p020-a02-session-census-static-v1"
FIRST_POST = E / "PG40211-p020-a02-independent-initial-assertion-v1"
OUT = E / "PG40212-p020-a02-session-census-independent-v1"
CASES = {
    "PT-CHR-CMP-A02-001": "rejectsContradictoryActivityOfTheNewestSessionInBothReports",
    "PT-CHR-CMP-A02-002": "rejectsActivityReportsThatOmitBothNewerSessions",
}
TEST = "dev.codex.schubert.characterization.ArtifactComparatorTest"
CLASS = "dev/codex/schubert/characterization/ArtifactComparator"


def main():
    start = read(next(Path("documents/400_PGPT/470_PMO").glob("601_*/671_P020*")))
    plan = start["values"]
    assert all(ref(Path(row["path"])) == row for row in plan["oracleReferences"])
    red, green, static = (read(folder / "manifest.json") for folder in (RED, UNIT, STATIC))
    assert len({plan["characterizationBase"], red["source"], green["source"]}) == 3
    assert red["expected"] == 2 and green["expected"] == 208
    assert red["stages"]["unit"]["actualExit"] == 1
    assert green["source"] == static["source"] and static["allPhysicalUnchanged"]
    assert len(green["stages"]) == 6 and all(s["actualExit"] == 0 for s in green["stages"].values())
    assert red["actualBackendActions"] == green["actualBackendActions"] == 0
    red_xml = RED / "xml/TEST-junit-jupiter.xml"
    assert ref(red_xml)["sha256"] == red["xmlHashes"][red_xml.name]
    rejected = ET.parse(red_xml).getroot()
    assert {k: rejected.get(k) for k in ("tests", "failures", "errors", "skipped")} == {
        "tests": "2", "failures": "2", "errors": "0", "skipped": "0"
    }
    new_cases = {(TEST, method + "()") for method in CASES.values()}
    assert {(node.get("classname"), node.get("name")) for node in rejected.iter("testcase")} == new_cases
    assert all(node.find("failure").get("message") == "expected: <false> but was: <true>"
               for node in rejected.iter("testcase"))
    for name, digest in green["xmlHashes"].items():
        assert ref(UNIT / "xml" / name)["sha256"] == digest
    previous, current = P["all_cases"](OLD), P["all_cases"](UNIT)
    assert len(previous) == 206 and new_cases.isdisjoint(previous)
    assert current == previous | dict.fromkeys(new_cases, "PASS")
    assert len(current) == 208 and len({suite for suite, _ in current}) == 20
    assert set(current.values()) == {"PASS"}

    ui, ss, baseline = (Path(row["path"]) for row in plan["oracleReferences"][-3:])
    assert "最古sessionをrevoke" in R["git"]("show", f"{plan['canonicalDesignSource']}:{ui}").decode()
    assert "A02のCurrent 3 session継続はDIF-016、NKは最古revoke" in ss.read_text()
    current_expected = [True, True, True]
    nk_expected = [False, True, True]
    assert read(baseline)["sessionActiveOldestToNewest"] == current_expected
    assert not R["git"]("diff", "--name-only", "843de94", green["source"], "--",
                        str(R["B"] / "baseline/current"))
    assert not R["git"]("diff", "--name-only", plan["source"], green["source"], "--", "src")

    previous_post = read(OLD_POST / "manifest.json")
    pmd = HELPERS["decisions"](previous_post, static, STATIC)
    assert all(item["disposition"] == "NOT_APPLICABLE" for item in pmd), pmd
    init = Path(green["initLog"]["path"])
    assert ref(init) == green["initLog"]
    init_data = init.read_bytes()
    assert not re.search(
        rb"Initializing '(?:com/microsoft/playwright|dev/codex/schubert/nk/|dev/codex/schubert/characterization/(?:Native|CurrentCharacterizationTest)|org/postgresql)",
        init_data,
    )
    assert re.findall(r'^Session "([^"]+)":', (UNIT / "execinfo.log").read_text(), re.M) == [green["session"]]
    scope = Path(green["classesDir"])
    assert R["physical"](scope) == green["mainPhysical"] and len(green["mainPhysical"]) == 17
    assert set(green["mainPhysical"]) == set(red["mainPhysical"])
    record = CLASS + "$ComparisonResult"
    changed = {p for p, digest in green["mainPhysical"].items() if red["mainPhysical"][p] != digest}
    assert changed == {CLASS + ".class", record + ".class"}
    first_post_path = FIRST_POST / "manifest.json"
    first_post = read(first_post_path)
    assert first_post["actualExit"] == 1 and set(first_post["observedChangedPhysical"]) == changed
    javap = Path("../toolchain/jdk-25.0.4/bin/javap").resolve()
    assert ref(javap)["sha256"] == first_post["javapSha256"]
    command = [str(javap), "-p", "-c", "-s"]
    before, after = [subprocess.check_output([*command, "-cp", snapshot["classesDir"],
                                            record.replace("/", ".")], timeout=20)
                     for snapshot in (red, green)]
    assert before == after and hashlib.sha256(after).hexdigest() == first_post["nestedJavapWithoutDebugSha256"]
    OUT.mkdir()
    engine = read(next(E.glob("PG37324*/manifest.json")))
    result = P["unfiltered"](green, UNIT, scope, OUT, engine)
    assert result["missedMethods"] == previous_post["raw"]["missedMethods"]
    counters = Counter()
    for line in (OUT / "raw.tsv").read_text().splitlines():
        row = line.split("\t")
        if row[0] == "CLASS" and row[1] in (CLASS, CLASS + "$ComparisonResult"):
            assert row[3] == "true"
            for name, missed, hit in (c.split(":") for c in row[6:]):
                assert int(missed) == 0
                counters[name] += int(hit)
    assert counters["CLASS"] == 2

    log = OUT / "class-init.log.gz"
    log.write_bytes(gzip.compress(init_data, mtime=0))
    reviews = OUT / "pmd-per-site.json"
    save(reviews, pmd)
    proof = OUT / "manifest.json"
    save(proof, dict(actualExit=0, source=green["source"], productionCore=plan["productionCoreMain"],
                     red=dict(unit=ref(RED / "manifest.json"), xml=ref(red_xml),
                              exec=ref(RED / "jacoco.exec"), actualExit=1, tests=2, failures=2),
                     run=green["run"], unit=ref(UNIT / "manifest.json"), static=ref(STATIC / "manifest.json"),
                     firstIndependentFailure=ref(first_post_path), changedPhysical=sorted(changed),
                     nestedCodeAndDeclarationsEqual=True,
                     cases=CASES, expectedActivity=dict(current=current_expected, nk=nk_expected),
                     design="SS355 §8 / UI264 DIF-016", classInit=ref(log), raw=result,
                     comparatorCounters=dict(counters), pmdRaw=len(pmd), pmdReviews=ref(reviews),
                     pmdApplicable=0, pmdUnclassified=0, tests=208, suites=20, failed=0, skipped=0, notRun=0,
                     newDefinitions=2, baselineUnchanged=True, productTests=0, actualNkChr=False,
                     whole451Accepted=False, newAcceptance=0, terminalAtUTC=R["utc"](),
                     verifier=ref(Path(__file__))))
    print(ref(proof), dict(counters))


if __name__ == "__main__":
    main()
