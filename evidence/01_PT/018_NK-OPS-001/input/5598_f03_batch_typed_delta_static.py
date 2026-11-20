"""Run current bytecode checks only on the changed part of the admitted Batch closure."""

from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import subprocess
from tempfile import TemporaryDirectory
from xml.etree import ElementTree
from zipfile import ZipFile, ZIP_DEFLATED

OPS = Path("evidence/01_PT/018_NK-OPS-001/evidence")
PREFIX = "dev.codex.schubert.nk."


def pin(path):
    return dict(path=str(path), sha256=sha256(path.read_bytes()).hexdigest())


def data(pin_value):
    p = Path(pin_value["path"])
    assert pin(p) == pin_value
    return json.loads(p.read_bytes())


def archive(path, contents):
    with ZipFile(path,"x",compression=ZIP_DEFLATED) as pack:
        for name, content in sorted(contents.items()):
            pack.writestr(name, content)


def pick(path, wanted):
    with ZipFile(path) as jar:
        inventory = jar.namelist()
        assert all(inventory.count(member) == 1 for member in wanted)
        return {member: jar.read(member) for member in sorted(wanted)}


def hash_classes(contents):
    return {name: sha256(value).hexdigest() for name, value in contents.items()}


def binary(name):
    return name.replace(".", "/")+".class"


def close_symbol_edges(candidates, peers, edges):
    selected = set(candidates)
    pruned = {}
    while True:
        missing = {name: sorted(edges.get(name,set())-selected-peers) for name in selected}
        excluded = {name: targets for name,targets in missing.items() if targets}
        if not excluded:
            return selected, pruned
        selected.difference_update(excluded)
        pruned.update(excluded)


def main():
    begin, = Path("documents/400_PGPT/470_PMO").glob("601_*/1570_*.json")
    task = json.loads(begin.read_bytes())
    start = task["values"]
    delta, old, oldpost, current, alert, alertpost = map(data,start["oracleReferences"][1:])
    assert all(x["actualExit"]==0 for x in (delta,old,oldpost,current,alert,alertpost))
    core = start["productionCoreMain"]
    assert delta["productionCore"] == current["source"] == alert["source"] == alertpost["productionCore"] == core
    assert alert["spotbugs"]["exit"] == alert["spotbugs"]["findings"] == alert["spotbugs"]["missing"] == 0
    scope = data(old["evidence"]["graph"])
    old_reported = set(scope["checkedSet"])
    held = set(scope["explicitPhysicalHoldMetadataOnly"])|set(scope["deferredTransitive"])
    assert len(old_reported)==277 and len(held)==369 and not old_reported&held
    safe_alert = {row["classPath"]:row["sha256"] for row in current["qualifiedAlertPhysical"]}
    new_companion = set(safe_alert)-old_reported
    assert len(safe_alert)==7 and len(new_companion)==1
    assert next(iter(new_companion)).endswith("/AlertLifecycle$State.class")
    assert not (old_reported|new_companion)&held
    original = data(oldpost["packageReference"])
    allowed_peers = {}
    for name in ("protocol","storage","bootstrap"):
        old_jar = original["packagedJars"][name]["artifact"]
        current_jar = current["savedUnchangedLibraryReferences"][name]
        assert pin(Path(current_jar["path"]))["sha256"] == current_jar["sha256"]
        with ZipFile(old_jar["path"]) as jar:
            members = {member for member in jar.namelist() if member.endswith(".class")}
        with ZipFile(current_jar["path"]) as jar:
            assert members == {member for member in jar.namelist() if member.endswith(".class")}
        assert not members & allowed_peers.keys() and not members & held
        allowed_peers.update(pick(current_jar["path"],members))
    assert len(allowed_peers)==456
    batch = pick(current["batchArtifact"]["path"],old_reported|new_companion)
    hashes = hash_classes(batch)
    assert all(hashes[name] == identity for name,identity in safe_alert.items())
    assert all(hashes[name] == identity for name,identity in delta["sameMeasuredPhysical"].items())
    selected = set(delta["scopeWithMainOrDependencyChanges"])
    assert len(selected)==78 and (set(delta["sameMeasuredPhysical"])|selected)==old_reported
    old_spot = old["stages"]["spotbugs"]["command"]
    old_jdeps = old["stages"]["typed"]["command"]
    sdk = [Path(word) for word in old_jdeps[old_jdeps.index("--class-path")+1].split(":")[1:]]
    sdk_paths = [pin(path) for path in sdk]
    assert len(sdk)==len(set(sdk))==12
    original_xml = Path(alert["spotbugs"]["report"]["path"])
    assert pin(original_xml) == alert["spotbugs"]["report"]
    reported_in_alert = {binary(row.attrib["class"]) for row in ElementTree.parse(
        original_xml).findall(".//ClassStats")}
    assert safe_alert.keys() <= reported_in_alert
    out = OPS/start["run"]
    out.mkdir()
    stages = {}

    def execute(label, argv, allowed):
        command = list(map(str, argv))
        env = dict(PATH="/usr/bin:/bin", LANG="C.UTF-8")
        entered = datetime.now(timezone.utc).isoformat()
        p = subprocess.run(command,capture_output=True,timeout=90,check=False,env=env)
        stdout,stderr = out/(label+".stdout"),out/(label+".stderr")
        stdout.write_bytes(p.stdout)
        stderr.write_bytes(p.stderr)
        stages[label] = dict(args=command,actualExit=p.returncode,stdout=pin(stdout),stderr=pin(stderr),
                             started=entered,terminal=datetime.now(timezone.utc).isoformat())
        with (out/(label+"-terminal.json")).open("x") as f:
            json.dump(stages[label],f,indent=2)
            f.write("\n")
        assert p.returncode in allowed
        return p.stdout

    with TemporaryDirectory(dir="/dev/shm",prefix="pgpt-admitted-batch-delta-") as work:
        scratch = Path(work)
        peer, eligible, dependency, target = [scratch/(name+".jar") for name in
                                               ("peers","eligible","dependency","affected")]
        archive(peer,allowed_peers)
        archive(eligible,batch)
        cmd = [*old_jdeps[:old_jdeps.index("--class-path")+1],
               os.pathsep.join(map(str,[peer,*sdk])),eligible]
        typed = execute("jdeps",cmd,(0,))
        edges = {}
        for row in typed.decode().splitlines():
            fields = re.match(r"^\s*(\S+)\s+->\s+(\S+)",row)
            if fields is None:
                continue
            first,second = fields.groups()
            if binary(first) in batch and second.startswith(PREFIX):
                edges.setdefault(binary(first),set()).add(binary(second))
        closed, blocked = close_symbol_edges(batch,allowed_peers.keys(),edges)
        qualified_alert = safe_alert.keys() & closed
        new_targets = (selected & closed)-qualified_alert
        assert new_targets and not (new_targets&held)
        archive(target,{name:batch[name] for name in new_targets})
        archive(dependency,{name:batch[name] for name in closed-new_targets})
        aux = scratch/"classpath.txt"
        aux.write_text("\n".join(map(str,[dependency,peer,*sdk]))+"\n")
        report = out/"spotbugs.xml"
        command = [*old_spot[:old_spot.index("-auxclasspathFromFile")+1], aux,"-output",report.resolve(),target]
        execute("spotbugs",command,(0,1,2,4,6))
    scan = ElementTree.parse(report).getroot()
    actual = {binary(row.attrib["class"]) for row in scan.findall(".//ClassStats")}
    bugs = [dict(kind=node.get("type"), owner=node.find("Class").get("classname"))
            for node in scan.findall("BugInstance")]
    missing = [node.text for node in scan.findall(".//MissingClass")]
    errors = len(scan.findall(".//Error"))
    pass_static = stages["spotbugs"]["actualExit"]==0 and actual==new_targets and not any((bugs,missing,errors))
    output = out/"manifest.json"
    rendered = dict(actualExit=0 if pass_static else 1,source=core,group=task["eventId"],
                    oldScope=277,currentTypedAdmitted=len(batch),unchangedReference=199,
                    priorCurrentAlertReused=sorted(qualified_alert),newStaticTargets=sorted(new_targets),
                    notAdmittedCurrent=blocked,actualAnalyzed=sorted(actual),errors=errors,
                    missing=missing,findings=bugs,unexpected=sorted(actual-new_targets),
                    notMeasured=sorted(new_targets-actual),previousAdmissibility=start["oracleReferences"][2],
                    rawSpotBugs=pin(report),currentPhysicalSha256={name:hashes[name] for name in new_targets},
                    toolDependencies=sdk_paths,steps=stages,heldClassBytesRead=0,actualRuntimeActions=0,
                    reproducedEarlierProductTests=0,whole451=False,wholeF03=False,formalDelta=0,
                    terminalAtUTC=datetime.now(timezone.utc).isoformat())
    with output.open("x") as f:
        json.dump(rendered,f,ensure_ascii=False,indent=2,sort_keys=True)
        f.write("\n")
    print(pin(output),len(new_targets),len(actual),len(blocked),len(bugs),len(missing),errors)
    return rendered["actualExit"]


if __name__=="__main__":
    raise SystemExit(main())
