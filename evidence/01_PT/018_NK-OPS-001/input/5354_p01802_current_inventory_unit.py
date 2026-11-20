"""Requalify the identical public BOM fixtures with today's shared value classes."""

import gzip
import os
from pathlib import Path
import runpy
from tempfile import TemporaryDirectory
from zipfile import ZipFile


PREVIOUS = runpy.run_path(str(Path(__file__).with_name("5353_p01802_current_release_lineage.py")))
UPPER, STORE, PLAN, COMMON, SCHEMA, ROOT = (PREVIOUS[name] for name in (
    "UPPER", "STORE", "PLAN", "COMMON", "SCHEMA", "ROOT"))
TARGETS = {ROOT + "ReleaseInventory" + suffix for suffix in ("", "$Artifact", "$Dependency")}
SHARED = {SCHEMA, SCHEMA + "$Row"}
FIXTURES = ("ReleaseInventoryTest", "ReleaseInventoryRawContractTest")
SESSION = "PG40422-CURRENT-INVENTORY-ORDINARY-18"


def main():
    read, pin, git, sha, dump = (UPPER["read"], *(COMMON[name] for name in ("pin", "git", "sha", "dump")))
    start = read(next(PLAN.glob("848_*")))
    values = start["values"]
    assert all(pin(Path(ref["path"])) == ref for ref in values["oracleReferences"])
    previous, jar_manifest, compiled, old, prepare, old_post = (
        read(ref["path"]) for ref in values["oracleReferences"][1:])
    source, core = values["source"], values["productionCoreMain"]
    assert source == git("rev-parse", "HEAD").decode().strip()
    assert core == previous["productionCore"] == jar_manifest["productionCore"]
    assert old["actualExit"] == old_post["actualExit"] == 0 and old["tests"] == old_post["tests"] == 18
    keys = [f"src/schubert-nk-bootstrap/src/test/java/{ROOT}{fixture}.java" for fixture in FIXTURES]
    assert all(sha(git("show", f"{source}:{key}")) == old["inputHashes"][key] for key in keys)
    assert not git("diff", "--name-only", core, source, "--", "src", ":(exclude)src/**/src/test/**")
    inventory = compiled["classHashes"]["bootstrap"]
    assert all(inventory[key + ".class"] == old_post["allPhysicalHashes"][key + ".class"] for key in TARGETS)
    assert all(inventory[key + ".class"] != old_post["allPhysicalHashes"][key + ".class"] for key in SHARED)
    archive = jar_manifest["qualifiedLocalArtifacts"]["bootstrap"]["artifact"]
    artifact = Path(archive["path"])
    assert artifact.resolve() == artifact and pin(artifact) == archive
    old_tools = prepare["toolDependencyHashes"]
    gson, = [Path(k) for k in old_tools if "/repository/" in k and Path(k).name == "gson-2.14.0.jar"]
    assert pin(gson)["sha256"] == old_tools[str(gson)]
    base = read(next(STORE.glob("PG40128-*/begin.json")))
    java = Path(base["jdk"]["path"])
    assert pin(java) == base["jdk"]

    def tool(basename):
        ref = base["tools"][basename]
        p = Path(ref["path"])
        assert pin(p) == ref
        return p

    junit = tool("junit-platform-console-standalone-1.13.4.jar")
    agent = tool("org.jacoco.agent-0.8.15-runtime.jar")
    cli = tool("org.jacoco.cli-0.8.15-nodeps.jar")
    annotations = tool("jspecify-1.0.1.jar")
    out = (STORE / values["run"]).resolve()
    out.mkdir()
    evidence_xml = out / "xml"
    evidence_xml.mkdir()
    exec_path = out / "jacoco.exec"
    raw_tool = read(next(STORE.glob("PG40212-*/manifest.json")))["raw"]
    assert pin(Path(raw_tool["tool"]["path"])) == raw_tool["tool"]
    language = {"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8", "TZ": "Asia/Tokyo"}
    crc = runpy.run_path(str(STORE.parent / "input/5257_p01810_broker_evidence_value_post.py"))["crc64"]
    shapes = {}
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-inventory18-current-") as temporary:
        root = Path(temporary)
        classes = root / "classes"
        tests = root / "tests"
        files, inputs = [], []
        with ZipFile(artifact) as jar:
            for key in sorted(TARGETS | SHARED):
                entry = key + ".class"
                data = jar.read(entry)
                assert sha(data) == inventory[entry]
                p = classes / entry
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(data)
                files.append(p)
                shapes[key] = dict(sha256=sha(data), crc64=crc(data))
        for key in keys:
            p = root / Path(key).name
            p.write_bytes(git("show", f"{source}:{key}"))
            inputs.append(p)
        cp = os.pathsep.join(map(str, (classes, junit, gson, annotations)))
        trace = root / "class-init.log"
        command = {
            "compile": [java.with_name("javac"), "--release", "25", "-Xlint:all", "-Werror",
                        "-proc:none", "-cp", cp, "-d", tests, *inputs],
            "unit": [java, "-Xmx384m", "-Duser.timezone=Asia/Tokyo", f"-Xlog:class+init=info:file={trace}",
                     f"-javaagent:{agent}=destfile={exec_path},sessionid={SESSION},append=false",
                     "-jar", junit, "execute", "--disable-banner", "--fail-if-no-tests", "--details=summary",
                     "--class-path", str(tests) + os.pathsep + cp, "--reports-dir", evidence_xml,
                     "--config=junit.jupiter.execution.parallel.enabled=false",
                     *(f"--select-class={ROOT.replace('/', '.')}{name}" for name in FIXTURES)],
            "standard": [java, "-jar", cli, "report", exec_path, "--classfiles", classes,
                         "--xml", out / "coverage.xml"],
            "raw": [*raw_tool["command"][:5], exec_path, *files],
        }
        stages = {}
        for label, cmd in command.items():
            stages[label] = UPPER["run"](out, label, cmd, root, language)
            if stages[label]["actualExit"] != 0:
                break
        if trace.is_file():
            (out / "class-init.log.gz").write_bytes(gzip.compress(trace.read_bytes(), mtime=0))
    okay = len(stages) == len(command) and not stages["raw"]["actualExit"]
    data = dict(actualExit=0 if okay else 1, source=source, productionCore=core,
                prior24NotCombined=True, testSources=[dict(path=p, sha256=old["inputHashes"][p]) for p in keys],
                expectedCases=18, selectedSuites=list(FIXTURES), inputClasses=shapes,
                priorTargetOwnByteSame=3, sharedCurrentChanges=2, actualBackendActions=0,
                executableProductEntryPoints=0, newProductDefinitions=0, stages=stages,
                session=SESSION, formalDelta=0, whole451Accepted=False,
                terminalAtUTC=COMMON["timestamp"]())
    dump(out / "manifest.json", data)
    print(pin(out / "manifest.json"), {k: x["actualExit"] for k, x in stages.items()})
    return data["actualExit"]


if __name__ == "__main__":
    raise SystemExit(main())
