"""Reconcile exact source-inventory regression output and targeted static findings."""

from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import runpy
import subprocess
import xml.etree.ElementTree as ET

H = runpy.run_path(str(Path(__file__).with_name("5589_p020_typed_inventory.py")))
OPS, WORK, CORE, TEST, MODULE, PACKAGE = (H[key] for key in ("OPS","WORK","CORE","TEST","MODULE","PACKAGE"))
pin, dump, raw_physical = (H[key] for key in ("pin","dump","physical"))


def locate(prefix):
    found, = OPS.glob(prefix+"-*/manifest.json")
    return found, json.loads(found.read_bytes())


def main():
    red_path, red = locate("PG41116")
    green_path, green = locate("PG41122")
    old_path, old = locate("PG41030")
    assert red["observedTestCounts"] == dict(tests=1, failures=1, errors=0, skipped=0)
    assert green["observedTestCounts"] == dict(tests=214, failures=0, errors=0, skipped=0)
    assert all(pin(Path(row["path"])) == row for label in (red,green)
               for row in [label["junit"], label["execData"]])
    assert pin(Path(green["raw"]["path"])) == green["raw"]
    green_work = WORK/green["run"]
    snap = green_work/"snapshot"
    classes = snap/MODULE/"target/classes"
    assert raw_physical(classes) == green["physical"]
    changed_types = {name for name, digest in green["physical"].items() if red["physical"][name] != digest}
    assert {Path(name).stem for name in changed_types} == {
        "GateCli", "GateCli$BaselineNumbers", "GateCli$TreeStats"}
    older_work = WORK/json.loads(Path(green["prior"]["path"]).read_bytes())["run"]
    out = OPS/"PG41124-p020-source-count-static-independent-v1"
    out.mkdir()
    terminals = {}
    rules = {}
    for step in old["steps"]:
        name = step["name"]
        if name not in ("checkstyle","pmd-GateCli","spotbugs"):
            continue
        old_command = step["command"]
        command = [arg.replace(str(older_work),str(green_work)) for arg in old_command]
        report = out/(name+".xml")
        if name == "checkstyle":
            command = command[:7] + [str(snap/CORE), str(snap/TEST)]
        else:
            option = "-output" if name == "spotbugs" else "--report-file"
            command[command.index(option)+1] = str(report)
            if name == "spotbugs":
                command = command[:command.index(option)+2] + [
                    str(classes/path) for path in green["physical"]
                    if Path(path).stem.split("$",1)[0] == "GateCli"]
        completed = subprocess.run(command, capture_output=True, timeout=100, check=False)
        if name == "checkstyle":
            report.write_bytes(completed.stdout)
        terminals[name] = dict(actualExit=completed.returncode, report=pin(report), argv=command)
        root = ET.parse(report).getroot()
        if name == "checkstyle":
            assert completed.returncode == 0 and len(root.findall("file")) == 2
            assert not root.findall("file/error")
        elif name == "spotbugs":
            assert completed.returncode == 0
            assert not root.findall(".//BugInstance") + root.findall(".//MissingClass") + root.findall(".//Error")
        else:
            ns = {"p": "http://pmd.sourceforge.net/report/2.0.0"}
            assert completed.returncode in (0, 4) and not root.findall("p:error",ns)
            line_map = (snap/CORE).read_text().splitlines()
            for violation in root.findall("p:file/p:violation", ns):
                index = int(violation.attrib["beginline"])
                key = (violation.attrib["rule"], violation.attrib.get("method", ""),
                       line_map[index-1].strip())
                rules[key] = rules.get(key, 0) + 1
    previous = old_path.with_name("GateCli-pmd.xml")
    earlier = (older_work/"snapshot"/CORE).read_text().splitlines()
    prior_rules = Counter((row.attrib["rule"], row.attrib.get("method", ""),
                          earlier[int(row.attrib["beginline"])-1].strip())
                         for row in ET.parse(previous).getroot().findall("p:file/p:violation",
                             {"p":"http://pmd.sourceforge.net/report/2.0.0"}))
    novel = Counter(rules) - prior_rules
    raw = [line.split("\t") for line in Path(green["raw"]["path"]).read_text().splitlines()
           if line.startswith("METHOD\t") and "\tcompare\t" in line]
    row, = [item for item in raw if item[1] == "dev/codex/schubert/characterization/GateCli"]
    assert all(int(item.split(":")[1]) == 0 for item in row[5:])
    output = out/"manifest.json"
    dump(output, dict(actualExit=int(bool(novel)), red=pin(red_path), green=pin(green_path),
                      previousPmd=pin(previous), source=green["source"], productionCore=green["productionCore"],
                      typeMethodRaw=row, retainedStaticFindings=sum(rules.values())-sum(novel.values()),
                      newStaticFindings=[dict(rule=r, method=m, sourceLine=l, count=count)
                                         for (r,m,l),count in novel.items()],
                      steps=terminals, productTests=0, productClasses=0, currentOrNkChr=False,
                      terminalAtUTC=datetime.now(timezone.utc).isoformat()))
    print(pin(output),[(p,t["actualExit"]) for p,t in terminals.items()],novel,row[5:])


if __name__=="__main__":
    main()
