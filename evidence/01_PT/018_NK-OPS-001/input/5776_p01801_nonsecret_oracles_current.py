"""Run the original privately scoped 14 tests with independent canonical YAML oracles."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
from zipfile import ZipFile


ROOT = Path.cwd()
STORE = (ROOT.parent / "pgpt-runs/PG379").resolve()
PUBLISHED = Path("evidence/01_PT/018_NK-OPS-001/evidence")
RUN_PREFIX = "PG43118-nonsecret-config-independent-concurrent-oracles"
CORE = "87927ea17c1c8dbef528bc0c6882c24b1fe7c871"
API = "dev/codex/schubert/nk/api/bootstrap"
WEB = "dev/codex/schubert/nk/web/bootstrap"
STORAGE = "dev/codex/schubert/nk/storage"
EXPECTED = {
    "bootstrap": (f"{API}/ApiNonSecretConfig.class", f"{API}/JdbcFailureGraph.class",
                  f"{WEB}/WebNonSecretConfig.class"),
    "storage": (f"{STORAGE}/StorageIoException.class", f"{STORAGE}/StorageIoException$Reason.class"),
}
FIXTURES = (f"{API}/ApiNonSecretConfigTest", f"{WEB}/WebNonSecretConfigTest")


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(payload):
    return hashlib.sha256(payload).hexdigest()


def pin(path):
    return dict(path=str(path), sha256=sha(path.read_bytes()))


def read(path):
    return json.loads(path.read_bytes())


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, timeout=30)


def write(path, value):
    with path.open("x") as out:
        out.write(json.dumps(value, ensure_ascii=False,indent=2)+"\n")


def main(version):
    diagnostics = version == "diagnostics"
    run_id = "PG43122-config-diagnostics-no-nested-cause-v1" if diagnostics else f"{RUN_PREFIX}-{version}"
    earlier_suite, = PUBLISHED.glob("PG38862*/manifest.json")
    original_cases = sorted(
        (case["classname"], case["name"].removesuffix("()")) for case in read(earlier_suite)["cases"]
    )
    assert len(original_cases) == 14
    selected = (
        [case for case in original_cases if case[1][9:12] in {"003", "004", "007"}]
        if diagnostics else original_cases
    )
    assert len(selected) == (6 if diagnostics else 14)
    folder = STORE / run_id
    folder.mkdir(mode=0o700)
    for name in ("target/classes", "test", "meter", "xml", "fixture-repo/src/deployment/config"):
        (folder/name).mkdir(parents=True)
    source=git("rev-parse","HEAD").decode().strip()
    tests=[Path("src/schubert-nk-bootstrap/src/test/java")/(fixture+".java") for fixture in FIXTURES]
    assert all(path.read_bytes()==git("show",f"{source}:{path}") for path in tests)
    result,=PUBLISHED.glob("PG43066*/manifest.json")
    closed_classpath=read(result)["normalArtifacts"]
    earlier,=PUBLISHED.glob("PG42390*/manifest.json")
    baseline=read(earlier)
    measured=baseline["currentThreeProductClassesEqualPriorMeasured"]
    classes={}
    for module, entries in EXPECTED.items():
        regular=closed_classpath[module]
        assert git("rev-parse",f"{CORE}:src/schubert-nk-{module}/src/main").decode().strip()==regular["mainTree"]
        jar=Path(regular["jar"]["path"])
        assert pin(jar)==regular["jar"]
        with ZipFile(jar) as archive:
            for name in entries:
                assert archive.namelist().count(name)==1
                payload=archive.read(name)
                if module=="bootstrap":
                    assert sha(payload)==measured[name]["current"]
                target=folder/"target/classes"/name
                target.parent.mkdir(parents=True,exist_ok=True)
                target.write_bytes(payload)
                classes[name]=pin(target)
    assert len(classes)==5
    templates=[]
    for name in ("common","api","web"):
        rel=Path("src/deployment/config")/(name+".yml.template")
        payload=git("show",f"{CORE}:{rel}")
        assert payload==git("show",f"{source}:{rel}")
        target=folder/"fixture-repo"/rel
        target.write_bytes(payload)
        templates.append(pin(target))
    retained=read(Path(baseline["proof"][0]["path"]))
    assert pin(Path(baseline["proof"][0]["path"]))==baseline["proof"][0]
    deps=[Path(x["path"]) for x in retained["sdk"]]
    assert [pin(path) for path in deps]==retained["sdk"]
    cp=os.pathsep.join([str(folder/"target/classes"),*map(str,deps)])
    prior=STORE/"PG43080-scenario-stream-finite-current-v1"
    original=read(prior/"begin.json")
    artifact=next(arg.split("=",1)[0] for arg in original["commands"]["junit"] if arg.startswith("-javaagent:"))
    sdk=ROOT.parent/"toolchain/jdk-25.0.4/bin"
    fmt=ROOT.parent/"toolchain/google-java-format-1.36.1-all-deps.jar"
    steps={
        "format":[str(sdk/"java"),"-jar",str(fmt),"--dry-run","--set-exit-if-changed",*map(str,tests)],
        "compile":[str(sdk/"javac"),"--release","25","-g","-Xlint:all","-Werror","-proc:none","-implicit:none",
                   "-cp",cp,"-d",str(folder/"test"),*map(str,tests)],
        "junit":[str(sdk/"java"),"-Dfile.encoding=UTF-8","-Duser.timezone=Asia/Tokyo",
                 "-Djunit.jupiter.extensions.autodetection.enabled=false","-Djunit.jupiter.execution.parallel.enabled=false",
                 "-Djunit.jupiter.execution.timeout.default=15 s",f"-Dnk.pt.repository={folder/'fixture-repo'}",
                 f"{artifact}=destfile={folder/'unit.exec'},append=false,sessionid={run_id}",
                 "-cp",os.pathsep.join([str(folder/"test"),cp]),"org.junit.platform.console.ConsoleLauncher",
                 "execute","--disable-ansi-colors","--fail-if-no-tests","--reports-dir",str(folder/"xml")],
    }
    if diagnostics:
        for classname, name in selected:
            steps["junit"].extend(["--select-method", f"{classname}#{name}"])
    else:
        for name in FIXTURES:
            steps["junit"].extend(["--select-class", name.replace("/", ".")])
    for key in ("rawCompile","unfiltered","style","pmd","spotbugs"):
        code=original["commands"][key]
        stages=[arg.replace(str(prior),str(folder)) for arg in code]
        if key=="style":
            stages=stages[:-2]+list(map(str,tests))
        if key=="unfiltered":
            stages=stages[:-1]+[str(folder/"target/classes"/name) for name in
               (f"{API}/ApiNonSecretConfig.class",f"{WEB}/WebNonSecretConfig.class")]
        if key in ("pmd","spotbugs"):
            index=stages.index("--aux-classpath" if key=="pmd" else "-auxclasspath")+1
            stages[index]=cp
            if key=="spotbugs":
                assert stages[-2:]==[str(folder/"target/classes"),str(folder/"test")]
                stages.pop(-2)
        steps[key]=stages
    (folder/"current-static-sources.txt").write_text("".join(f"{path}\n" for path in tests))
    write(folder/"begin.json",dict(source=source,productCore=CORE,startedAtUTC=now(),
        testInputs=list(map(pin,tests)),classes=classes,templates=templates,
        vendor=retained["sdk"],stages=steps,artifactQualification=pin(result),earlierFixture=pin(earlier)))
    results={}
    for stage, cmd in steps.items():
        process=subprocess.run(cmd,cwd=ROOT,capture_output=True,timeout=120)
        (folder/f"{stage}.stdout").write_bytes(process.stdout)
        (folder/f"{stage}.stderr").write_bytes(process.stderr)
        results[stage]=dict(exit=process.returncode,at=now())
        print(stage,process.returncode,flush=True)
        if process.returncode not in {"pmd":{0,4},"spotbugs":{0,1}}.get(stage,{0}):
            raise SystemExit(process.returncode)
        if stage=="compile":
            assert {p.relative_to(folder/"test").as_posix() for p in (folder/"test").rglob("*.class")}=={
                f"{name}.class" for name in FIXTURES}
    junit=folder/"xml/TEST-junit-jupiter.xml"
    suite=ET.parse(junit).getroot()
    assert suite.get("tests")==str(len(selected)) and all(suite.get(f)=="0" for f in ("failures","errors","skipped"))
    cases=sorted((c.get("classname"),c.get("name").removesuffix("()")) for c in suite.findall("testcase"))
    assert cases==selected
    write(folder/"terminal.json",dict(actualExit=0,source=source,productCore=CORE,terminalAtUTC=now(),
         results=results,cases=cases,priorCaseList=pin(earlier_suite),junit=pin(junit),exec=pin(folder/"unit.exec"),
         coverage=pin(folder/"unfiltered.stdout"),externalIo=0,controlledTemplateFiles=3))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", choices=("v1", "v2", "v3", "diagnostics"), required=True)
    main(parser.parse_args().version)
