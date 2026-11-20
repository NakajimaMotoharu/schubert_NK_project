"""Bind the current fixed wire layout and changed sources to their actual run."""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess


OPS = Path("evidence/01_PT/018_NK-OPS-001/evidence")
PMO = Path("documents/400_PGPT/470_PMO/601_WBS66短期実行_20261117")
MODULE = Path("src/schubert-nk-protocol")
PREFIX = MODULE / "src/main/java"
OWNED = {
    "FieldCodecRules.java": "FieldCodec.java",
    "LargeResultDigest.java": "LargeResultRecordCodec.java",
    "MediaDescriptorValidatorRules.java": "MediaDescriptorValidator.java",
    "PayloadSemanticValidatorRules.java": "PayloadSemanticValidator.java",
}
TEST_LAYOUTS = {
    "LogSearchWireUnicodeTest": {"LGSREQ01"},
    "QuestionNotificationWireTest": {"QSSREQ01", "NTSREQ01"},
    "UserCommandWireUnicodeTest": {"UCRREQ01", "UPWREQ01"},
    "UserListReplyWireTest": {"USRRSP01"},
}


def read(path):
    return json.loads(path.read_bytes())


def sha(data):
    return hashlib.sha256(data).hexdigest()


def pin(path):
    return dict(path=str(path), sha256=sha(path.read_bytes()))


def git(*args):
    return subprocess.check_output(["git", *args], timeout=40)


def at(source, path):
    return git("show", f"{source}:{path}")


def publish(path, data):
    with path.open("x") as fp:
        json.dump(data, fp, ensure_ascii=False, indent=2)
        fp.write("\n")


def main():
    start = read(next(PMO.glob("986_*")))["values"]
    refs = [Path(row["path"]) for row in start["oracleReferences"]]
    assert [pin(p) for p in refs] == start["oracleReferences"]
    original, scoped_acceptance, static, run = map(read, refs[1:5])
    candidate = start["productionCoreMain"]
    assert static["productionCoreMain"] != "" and run["productionCore"] == candidate
    assert run["unfilteredCurrentRawFour100"] and run["tests"] == 170
    assert original["sourceMain165"] == 165 and original["layout64"] == 64
    assert scoped_acceptance["scopeAcceptance"].startswith("WBS-G13.01 ")
    design = read(refs[1].with_name("design-current-pins.json"))
    prior_layouts = read(refs[1].with_name("layout64-fields389-types69.json"))
    previous_sources = read(refs[1].with_name("source-class-owner-requirement-cases.json"))
    baseline = original["sourceCore"]
    use_source = run["source"]
    canonical = start["canonicalDesignSource"]
    verified_fixtures = {}
    for ref in design["fixtures"]:
        assert sha(at(candidate, ref["path"])) == ref["sha256"]
        verified_fixtures[Path(ref["path"]).name] = ref["sha256"]
    layout_path = MODULE / "src/test/resources/protocol/layouts-ui233.tsv"
    field_path = MODULE / "src/test/resources/protocol/fields-ui234-236.tsv"
    layout_lines = at(candidate, layout_path).decode().splitlines()
    rows = [line.split("\t") for line in layout_lines if line and not line.startswith("#")]
    layout_ids = {row[0] for row in rows}
    known = {row["layout"]: row for row in prior_layouts}
    assert len(rows) == len(layout_ids) == 64 and layout_ids == set(known)
    fields = [line for line in at(candidate, field_path).decode().splitlines() if line and not line.startswith("#")]
    assert len(fields) == 389
    canonical_links = {}
    for path in design["documents"]:
        if Path(path).name.startswith(("233_", "323_")):
            text = at(canonical, path)
            assert all(id.encode() in text for id in layout_ids)
            canonical_links[path] = sha(text)
    assert len(canonical_links) == 2

    existing = {Path(row["sourcePath"]): row for row in previous_sources}
    all_source = {Path(line) for line in git("ls-tree", "-r", "--name-only", candidate, "--", str(PREFIX))
                  .decode().splitlines() if line.endswith(".java")}
    assert len(existing) == 165 and len(all_source) == 169
    more_or_updated = {Path(line) for line in git("diff", "--name-only", baseline, candidate, "--", str(PREFIX))
                       .decode().splitlines()}
    assert len(more_or_updated) == 11 and len(all_source - existing.keys()) == 4
    assert {path.name for path in all_source - existing.keys()} == set(OWNED)
    physical = read(refs[4].with_name("jvm-crc.json"))["classes"]
    assert len(physical) == 176
    differences = {}
    for path in sorted(more_or_updated):
        owner_path = path.with_name(OWNED.get(path.name, path.name))
        suffix = path.relative_to(PREFIX).with_suffix("").as_posix()
        class_ids = {name: value for name, value in physical.items() if name == suffix or name.startswith(suffix + "$")}
        assert class_ids
        owner = existing[owner_path]
        differences[str(path)] = dict(sha256=sha(at(candidate, path)), canonicalOwner=owner["canonicalOwner"],
                                      ownerPath=str(owner_path), designSections=owner["ssFromOwner"],
                                      currentClassCrc=class_ids)

    current_tests = read(refs[4].with_name("testcases.json"))
    result_rows = [case for case in current_tests if case["className"].rpartition(".")[2] in TEST_LAYOUTS]
    assert len(result_rows) == 14 and all(case["outcome"] == "PASS" for case in result_rows)
    known_results = {}
    for name, layouts in TEST_LAYOUTS.items():
        java = MODULE / "src/test/java/dev/codex/schubert/nk/protocol/codec" / (name + ".java")
        body = at(use_source, java)
        tagged = {literal.decode() for literal in re.findall(rb'new LayoutId\("([A-Z0-9]+)"\)', body)}
        assert tagged == layouts and layouts <= layout_ids
        the_cases = [case["method"] for case in result_rows if case["className"].endswith("." + name)]
        declared = {item.decode() for item in re.findall(rb"@Test\s+(?:public\s+)?void\s+(\w+)\(", body)}
        assert set(the_cases) == declared
        known_results[name] = dict(source=dict(path=str(java), sha256=sha(body)),
                                   layouts={value: known[value]["traceId"] for value in sorted(layouts)},
                                   cases=sorted(the_cases))

    output = OPS / start["run"]
    output.mkdir()
    matrix = output / "changed-sources-and-wire-tests.json"
    publish(matrix, dict(existingScope=pin(refs[2]), fixedFixtures=verified_fixtures,
                         canonicalWireDesign=canonical_links, changedMain=differences, currentWireCases=known_results))
    result = output / "manifest.json"
    publish(result, dict(actualExit=0, productionCore=candidate, testExecutionSource=use_source, trace=pin(matrix),
                         currentRun=pin(refs[4]), priorLayoutScope=pin(refs[1]), layouts=64, fields=389,
                         currentMain=169, addedMain=4, changedExistingMain=7, testDefinitionsJoined=14,
                         observedFixtureLayouts=6, noNewTestExecutions=True, newOriginalAcceptance=0,
                         wholeG13ParentAccepted=False, whole451Accepted=False,
                         terminalAtUTC=datetime.now(timezone.utc).isoformat()))
    print(pin(result))


if __name__ == "__main__":
    main()
