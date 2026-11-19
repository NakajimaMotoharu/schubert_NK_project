"""Independently qualify the two selected public YAML parser boundary results."""

from datetime import datetime, timezone
import gzip
import json
from pathlib import Path
import re
import runpy
import subprocess
import xml.etree.ElementTree as ET
from zipfile import ZipFile


OPS = Path("evidence/01_PT/018_NK-OPS-001")
RUN = OPS / "evidence/PG40296-public-config-yaml-utf8-limit-v1"
OUT = OPS / "evidence/PG40298-public-config-yaml-utf8-limit-independent-v1"
PREFIX = "dev/codex/schubert/nk/"
CLASSES = {PREFIX + "api/bootstrap/ApiNonSecretConfig", PREFIX + "web/bootstrap/WebNonSecretConfig"}
FIXTURE = PREFIX + "api/bootstrap/NonSecretYamlUtf8LimitTest"
TESTS = {"PT-OPS-APICFG008": "opsApiCfg008Utf8ByteLimit()",
         "PT-OPS-WEBCFG008": "opsWebCfg008Utf8ByteLimit()"}
PHYSICAL = runpy.run_path(str(OPS / "input/5257_p01810_broker_evidence_value_post.py"))
pin = PHYSICAL["pin"]


def main():
    unit = RUN / "manifest.json"
    m = json.loads(unit.read_bytes())
    assert m["actualExit"] == m["actualBackendActions"] == m["executedPreviouslyApprovedTests"] == 0
    assert m["selectedTests"] == len(TESTS) and m["scopes"] == ["bootstrap"]
    assert set(m["stages"]) == {"format", "compile", "pmd", "checkstyle", "unit", "coverage"}
    for name, stage in m["stages"].items():
        assert stage == json.loads((RUN / (name + "-exit.json")).read_bytes())
        assert stage["actualExit"] == 0
        assert all(pin(stage[key]["path"]) == stage[key] for key in ("stdout", "stderr"))
    for name in ("pmd", "checkstyle"):
        assert not any(n.tag.rsplit("}", 1)[-1] in {"violation", "suppressedviolation", "error"}
                       for n in ET.parse(RUN / (name + ".xml")).iter())
    text = subprocess.check_output(["git", "show", m["source"] + ":" + m["testFixture"]], timeout=25)
    assert PHYSICAL["hashlib"].sha256(text).hexdigest() == m["testSha256"]
    assert all(pin(item["path"]) == item for item in [m["jar"], *m["localDependencyPins"]])
    assert not subprocess.check_output(
        ["git", "diff", "--name-only", m["productionCore"], m["source"], "--",
         "src", ":(exclude)src/**/src/test/**"], timeout=25)

    xml = RUN / "xml/TEST-junit-jupiter.xml"
    suite = ET.parse(xml).getroot()
    assert [int(suite.get(k)) for k in ("tests", "failures", "errors", "skipped")] == [2, 0, 0, 0]
    test_cases = list(suite.iter("testcase"))
    assert sorted(c.get("name") for c in test_cases) == sorted(TESTS.values())
    assert all(c.get("classname") == FIXTURE.replace("/", ".") and
               not any(n.tag in {"failure", "error", "skipped"} for n in c) for c in test_cases)
    init = RUN / "class-init.log.gz"
    raw_log = gzip.decompress(init.read_bytes())
    initialized = {name.decode().split("$$Lambda", 1)[0] for name in re.findall(
        rb"Initializing '(dev/codex/schubert/nk/[^']+)'", raw_log)}
    assert initialized == CLASSES | {FIXTURE}

    exec_data = RUN / "jacoco.exec"
    decode = runpy.run_path("tools/quality/jacoco_readonly_exec_subset.py")["decode"]
    exec_meta = decode(exec_data.read_bytes(), CLASSES)
    assert [s["labelBytesHex"] for s in exec_meta["sessions"]] == [m["session"].encode().hex()]
    with ZipFile(m["jar"]["path"]) as jar:
        crc = {name: PHYSICAL["crc64"](jar.read(name + ".class")) for name in sorted(CLASSES)}
    assert {name: item["crc64"] for name, item in exec_meta["classes"].items()} == crc
    coverage = RUN / "coverage.xml"
    counters = {n.get("name"): {c.get("type"): {k: int(c.get(k)) for k in ("missed", "covered")}
                                for c in n.findall("counter")}
                for n in ET.parse(coverage).iter("class") if n.get("name") in CLASSES}
    core = b"nk.monitoring.mode: DEBUG\n# " + chr(0x1F642).encode("utf-8") * 4000
    sizes = [len(core + b"x" * fill + b"\n") for fill in (355, 356)]
    assert sizes == [16384, 16385]
    out = dict(source=m["source"], productionCore=m["productionCore"], actualExit=0,
               acceptedByteSize=sizes[0], rejectedByteSize=sizes[1], expectedAtLimit="DEBUG",
               tests=TESTS, passed=len(test_cases), failures=0, errors=0, skipped=0, notRun=0,
               physicalCrc=crc, scopedRawCounters=counters, productClassesInitialized=sorted(CLASSES),
               unit=pin(unit), junit=pin(xml), classInit=pin(init), exec=pin(exec_data), coverage=pin(coverage),
               whole451Accepted=False, newFormalAcceptance=0, actualBackendActions=0,
               terminalAtUTC=datetime.now(timezone.utc).isoformat())
    OUT.mkdir()
    with (OUT / "manifest.json").open("x") as stream:
        json.dump(out, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(pin(OUT / "manifest.json"))


if __name__ == "__main__":
    main()
