"""Collect current raw PMD and Checkstyle results for the three complete Main modules."""

from collections import Counter, defaultdict
from io import BytesIO
import json
from pathlib import Path
import runpy
import tarfile
from tempfile import TemporaryDirectory
from xml.etree import ElementTree


G = runpy.run_path(str(Path(__file__).with_name("5364_f02_utc42_four_current_jars.py")))
OPS, PLAN, UPPER, COMMON = (G[name] for name in ("OPS", "PLAN", "UPPER", "COMMON"))
MODULES = {"protocol":169, "storage":25, "bootstrap":88}
BASE = Path("tools/quality/static")


def main():
    read = UPPER["read"]
    pin, git, dump = (COMMON[n] for n in ("pin","git","dump"))
    start = read(next(PLAN.glob("890_*")))
    w = start["values"]
    p = w["oracleReferences"]
    assert all(pin(Path(ref["path"])) == ref for ref in p)
    jars, three, batch, targeted, old = (read(ref["path"]) for ref in p[1:])
    core = w["productionCoreMain"]
    assert core == jars["sourceCore"] == three["productionCore"] == batch["productionCore"] == targeted["productionCore"]
    assert three["allObserved456"] and batch["closed"] == 277
    assert pin(BASE/"pmd.xml")["sha256"] == old["fullRootRulesetSha256"]
    for rule in (BASE/"pmd.xml", BASE/"checkstyle.xml"):
        assert rule.read_bytes() == git("show", f"{core}:{rule}")
    template_pmd = old["stages"]["pmd"]["command"]
    template_check = old["stages"]["checkstyle"]["command"]
    java = Path(template_pmd[0])
    assert template_check[0] == str(java)
    policy = read(next(OPS.glob("PG40128-*/begin.json")))
    assert pin(java) == policy["jdk"]
    curr = {key: Path(jars["packagedJars"][key]["artifact"]["path"]) for key in MODULES}
    assert all(pin(path)==jars["packagedJars"][key]["artifact"] for key,path in curr.items())
    closures = [f"src/schubert-nk-{key}/src/main/java" for key in MODULES]
    names = git("ls-tree", "-r", "--name-only", core, *closures).decode().splitlines()
    assert len(names) == 282 and all(file.endswith(".java") for file in names)
    assert Counter(name.split("/")[1].removeprefix("schubert-nk-") for name in names) == MODULES
    disallowed = ("TemporaryInfrastructureException", "FingerprintKeyRing", "ResponseSnapshotCodec", "WebStartupException")
    assert all(Path(name).stem not in disallowed for name in names)
    companion = read(next(OPS.glob("PG39810-*/begin.json")))
    sdk = dict(companion["sdkJars"])
    for ref in (read(next(OPS.glob("PG39812-*/manifest.json")))["onlyAdditionalAux"],
                read(next(OPS.glob("PG40370-*/manifest.json")))["explicitMetricsSdk"]):
        sdk[ref["path"]] = ref["sha256"]
    assert all(pin(Path(key))["sha256"]==sha for key,sha in sdk.items())
    output = (OPS/w["run"]).resolve()
    output.mkdir()
    statuses = {}
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-f03-282-main-static-") as folder:
        root = Path(folder)
        with tarfile.open(fileobj=BytesIO(git("archive", core, *closures))) as repo:
            repo.extractall(root, filter="data")
        listing = root / "sources.txt"
        listing.write_text("\n".join(str(root / name) for name in names) + "\n")
        env = {"PATH":"/usr/bin:/bin","LANG":"C.UTF-8"}
        aux = ":".join([str(java.parents[1]/"lib/jrt-fs.jar"), *map(str,curr.values()), *sorted(sdk)])
        pmd = [*template_pmd[:template_pmd.index("check")+1], "--file-list", listing,
               "--rulesets", (BASE/"pmd.xml").resolve(), "--use-version", "java-25",
               "--aux-classpath", aux, "--no-cache", "--format", "xml", "--report-file", output/"pmd.xml"]
        check = [*template_check[:3], "-c", (BASE/"checkstyle.xml").resolve(),
                 "-f","xml","-o",output/"checkstyle.xml","@"+str(listing)]
        for label,args in (("pmd",pmd),("checkstyle",check)):
            statuses[label] = UPPER["run"](output,label,args,root,env)
    pmd_xml = ElementTree.parse(output/"pmd.xml").getroot()
    check_xml = ElementTree.parse(output/"checkstyle.xml").getroot()
    ts = lambda symbol: symbol.rsplit("}",1)[-1]
    processing = [element.attrib for element in pmd_xml if ts(element.tag) in ("error","configerror")]
    distribution = defaultdict(Counter)
    affected = defaultdict(set)
    for node in pmd_xml:
        if ts(node.tag)!="file":
            continue
        path=Path(node.get("name")).relative_to(root).as_posix()
        assert path in names
        group=path.split("/")[1].removeprefix("schubert-nk-")
        for violation in node:
            assert ts(violation.tag) == "violation"
            rule=violation.get("rule")
            distribution[group][rule] += 1
            affected[rule].add(path)
    styles = list(check_xml.iter("error"))
    check_paths = {Path(n.get("name")).relative_to(root).as_posix() for n in check_xml.iter("file")}
    assert check_paths==set(names)
    count = sum(sum(c.values()) for c in distribution.values())
    status = dict(actualExit=0 if not processing and statuses["pmd"]["actualExit"] in (0,4) else 1,
        source=w["source"],productionCore=core,mainSources=MODULES,inspectedMavenPhysical=456,typedInputs={k:pin(v) for k,v in curr.items()},
        reports={f:pin(output/f) for f in ("pmd.xml","checkstyle.xml")},stages=statuses,
        checkstyleCount=len(styles),checkstyleFiles=len(check_paths),pmdRawCount=count,pmdProcessing=processing,
        rawRulesByModule=distribution,ruleSourceAffectedCounts={rule:len(files) for rule,files in affected.items()},
        productTests=0,approvedWholeScopesOnly=True,pmdExcludedRules=0,unreviewedFindingsAreNotQualified=True,
        wholeF03Accepted=False,whole451Accepted=False,terminalAtUTC=COMMON["timestamp"]())
    dump(output/"manifest.json",status)
    print(pin(output/"manifest.json"),statuses["pmd"]["actualExit"],count,len(processing),
          statuses["checkstyle"]["actualExit"],len(styles))
    return status["actualExit"]


if __name__=="__main__":
    raise SystemExit(main())
