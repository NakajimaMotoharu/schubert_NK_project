"""Measure ExpiryAudit's exact packaged class family within the admitted static scope."""

from collections import Counter
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import runpy
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET
from zipfile import ZipFile


HERE = Path(__file__)
CONTRACT = runpy.run_path(str(HERE.with_name("5417_f02_expiry_audit_jdbc_pt.py")))
OPS, PLAN, TARGET, JSPECIFY, JAVA = (CONTRACT[k] for k in ("E", "PLAN", "TARGET", "JSPECIFY", "JAVA"))
pin, run, git = (CONTRACT[k] for k in ("proof", "run", "git"))


def read(path):
    return json.loads(Path(path).read_bytes())


def pmd_sites(path, name):
    root = ET.parse(path).getroot()
    ns = {"p": root.tag.partition("}")[0].lstrip("{")}
    assert root.tag.endswith("}pmd")
    assert not any(root.find(f".//p:{tag}", ns) is not None
                   for tag in ("error", "configerror", "suppressedviolation"))
    fields = ("rule", "beginline", "begincolumn", "endline", "endcolumn", "class", "method")
    return Counter(tuple(report.attrib.get(key) for key in fields)
                   for file in root.findall("p:file", ns) if file.get("name").endswith(name)
                   for report in file.findall("p:violation", ns))


def main():
    start = read(next(PLAN.glob("1074_F03*")))
    v = start["values"]
    assert all(pin(row["path"]) == row for row in v["oracleReferences"])
    packaged, unit, baseline_pmd, decisions, spot = (read(ref["path"]) for ref in v["oracleReferences"][1:])
    core = packaged["candidateProductionSource"]
    assert packaged["verify"]["focusedPhysicalByteEqual"] and unit["actualExit"] == 0
    assert not git("diff", "--name-only", core, v["source"], "--", "pom.xml", "src")
    assert pin(TARGET) == unit["candidateSource"]
    prior_tests = read(next(OPS.glob("PG40696-*-after/manifest.json")))
    expected = prior_tests["physical"]
    javasource = git("show", f"{core}:{TARGET}")
    assert javasource == TARGET.read_bytes()
    out = (OPS / v["run"]).resolve()
    out.mkdir()
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-f03-expiry-typed-") as scratch:
        work = Path(scratch)
        source = work / TARGET.name
        source.write_bytes(javasource)
        allowed_jar = work / "expiry.jar"
        batch = packaged["privateJars"]["batch"]["artifact"]
        assert pin(batch["path"]) == batch
        with ZipFile(batch["path"]) as product, ZipFile(allowed_jar, "x") as allowed:
            for member in expected:
                data = product.read(member)
                staged = work / Path(member).name
                staged.write_bytes(data)
                assert pin(staged)["sha256"] == expected[member]
                allowed.writestr(member, data)
        dependencies = CONTRACT["make_classpath"](packaged["privateJars"], work / "allowed-deps")
        assert dependencies == prior_tests["pinnedAllowedDependencies"]
        aux = work / "aux-list.txt"
        aux.write_text(f"{work / 'allowed-deps'}\n{JSPECIFY}\n")
        spot_args = spot["terminal"]["command"]
        stop = spot_args.index("-auxclasspathFromFile") + 1
        assert spot_args[0] == str(JAVA) and "-effort:max" in spot_args[:stop] and "-low" in spot_args[:stop]
        sb = out / "spotbugs.xml"
        stages = {"spotbugs": run("spotbugs", [*spot_args[:stop], aux, "-output", sb, allowed_jar], out, work)}
        pmd_args = read(baseline_pmd["terminal"]["path"])["command"]
        rules = Path.cwd() / "tools/quality/static/pmd.xml"
        assert pin(rules)["sha256"] == baseline_pmd["rules"]["sha256"]
        pmd = out / "pmd.xml"
        stages["pmd"] = run("pmd", [*pmd_args[:5], "-d", source, "--rulesets", rules, "--use-version",
                                   "java-25", "--aux-classpath",
                                   os.pathsep.join(map(str, (work / "allowed-deps", allowed_jar, JSPECIFY,
                                                             JAVA.parent.parent / "lib/jrt-fs.jar"))),
                                   "--no-cache", "--format", "xml", "--report-file", pmd], out, work)
    assert pin(baseline_pmd["raw"]["path"]) == baseline_pmd["raw"]
    old_raw, new_raw = (pmd_sites(path, TARGET.name) for path in (Path(baseline_pmd["raw"]["path"]), pmd))
    view = ET.parse(sb).getroot()
    classes = [row.attrib["class"] for row in view.iter("ClassStats")]
    expected_binary = {Path(name).with_suffix("").as_posix().replace("/", ".") for name in expected}
    reports = {key: len(list(view.iter(key))) for key in ("BugInstance", "Error", "MissingClass")}
    spot_complete = set(classes) == expected_binary and len(classes) == len(expected)
    actual_success = (stages["spotbugs"]["actualExit"] == 0 and not any(reports.values())
                      and spot_complete and stages["pmd"]["actualExit"] == 4 and old_raw == new_raw)
    result = dict(
        actualExit=0 if actual_success else 1, source=v["source"], candidateProductionCore=core,
        startEvent=start["eventId"], classCensus=sorted(classes), expectedPhysical=len(expected),
        physicalHashes=expected, spotCounts=reports, spotComplete=spot_complete, rawPmdOld=old_raw.total(),
        rawPmdCurrent=new_raw.total(), rawPmdExactMultiset=old_raw == new_raw,
        newPmdDelta=[dict(site=key, count=count) for key, count in (new_raw - old_raw).items()],
        oldPmdMissing=[dict(site=key, count=count) for key, count in (old_raw - new_raw).items()],
        preservedBatchClassification=decisions["assignedHere"], classpaths=dependencies,
        staticReports=[pin(sb), pin(pmd)], stages=stages, productTests=0, heldOperationsExecuted=0,
        wholeF03=False, whole451=False, formalDelta=0, terminalAtUTC=datetime.now(timezone.utc).isoformat(),
    )
    (out / "manifest.json").write_text(json.dumps(result, indent=2) + "\n")
    print(dict(spotExit=stages["spotbugs"]["actualExit"], pmdExit=stages["pmd"]["actualExit"],
               classStats=len(classes), spotCounts=reports, oldRaw=old_raw.total(), newRaw=new_raw.total(),
               same=old_raw == new_raw))
    return result["actualExit"]


if __name__ == "__main__":
    raise SystemExit(main())
