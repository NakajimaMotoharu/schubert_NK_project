"""Run the original public Caddy parser and committed template contract locally."""

import gzip
import os
from pathlib import Path
import runpy
from tempfile import TemporaryDirectory
from zipfile import ZipFile


UPPER = runpy.run_path(str(Path(__file__).with_name("5326_f02_group_lookup_upper.py")))
STORE, PLAN, COMMON = (UPPER[k] for k in ("EVIDENCE", "PLAN", "COMMON"))
CADDY = "dev/codex/schubert/nk/batch/file/CaddyPublicConfiguration"
TEST = CADDY.replace("/", ".") + "Test"
SESSION = "PG40440-PUBLIC-CADDY-CONTENT-THREE"


def main():
    read, pin, git, sha = (UPPER["read"], *(COMMON[k] for k in ("pin", "git", "sha")))
    start = read(next(PLAN.glob("863_*")))
    v = start["values"]
    refs = v["oracleReferences"]
    assert all(pin(Path(ref["path"])) == ref for ref in refs)
    prior, artifact, build = (read(ref["path"]) for ref in refs[1:4])
    assert prior["actualExit"] == 0 and prior["tests"] == 3
    assert prior["actualNetworkActions"] == 0
    assert prior["actualPrivateFilesOpened"] is False and prior["actualDnsRequestsIssued"] is False
    assert prior["originalTestPublicTemplateRead"] is True and prior["actualFilesOpenedByProduct"] is True
    source, core = v["source"], v["productionCoreMain"]
    assert core == artifact["productionCore"] and prior["source"] != core
    assert not git("diff", "--name-only", core, source, "--", "src", ":(exclude)src/**/src/test/**")
    assert all(sha(git("show", f"{source}:{ref['path']}")) == ref["sha256"] for ref in refs[-2:])
    current = artifact["qualifiedLocalArtifacts"]["batch"]["artifact"]
    jar = Path(current["path"])
    assert pin(jar) == current
    tools = read(next(STORE.glob("PG40128-*/begin.json")))
    assert pin(Path(tools["jdk"]["path"])) == tools["jdk"]
    java = Path(tools["jdk"]["path"])

    def dependency(name):
        pin_entry = tools["tools"][name]
        path = Path(pin_entry["path"])
        assert pin(path) == pin_entry
        return path

    junit = dependency("junit-platform-console-standalone-1.13.4.jar")
    agent = dependency("org.jacoco.agent-0.8.15-runtime.jar")
    annotations = dependency("jspecify-1.0.1.jar")
    raw_tool = read(next(STORE.glob("PG40212-*/manifest.json")))["raw"]
    assert pin(Path(raw_tool["tool"]["path"])) == raw_tool["tool"]
    output = (STORE / v["run"]).resolve()
    output.mkdir()
    cases = output / "xml"
    cases.mkdir()
    data = output / "jacoco.exec"
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-public-caddy-config-") as directory:
        root = Path(directory)
        environment = {"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8"}
        cwd = root / "src/schubert-nk-batch"
        cwd.mkdir(parents=True)
        template = root / refs[-1]["path"]
        template.parent.mkdir(parents=True)
        template.write_bytes(git("show", f"{source}:{refs[-1]['path']}"))
        assert template.resolve() == template and pin(template)["sha256"] == refs[-1]["sha256"]
        fixture = root / (Path(refs[-2]["path"]).name)
        fixture.write_bytes(git("show", f"{source}:{refs[-2]['path']}"))
        product = root / "classes"
        binary = product / (CADDY + ".class")
        binary.parent.mkdir(parents=True)
        with ZipFile(jar) as source_jar:
            binary.write_bytes(source_jar.read(CADDY + ".class"))
        digest = pin(binary)["sha256"]
        assert digest == build["classHashes"]["batch"][CADDY + ".class"]
        crc = runpy.run_path(str(STORE.parent / "input/5257_p01810_broker_evidence_value_post.py"))["crc64"](
            binary.read_bytes())
        test = root / "test"
        init = root / "init.log"
        cp = os.pathsep.join(map(str, (product, junit, annotations)))
        commands = {
            "compile": [java.with_name("javac"), "--release", "25", "-Xlint:all", "-Werror", "-proc:none",
                        "-cp", cp, "-d", test, fixture],
            "unit": [java, "-Xmx192m", f"-Xlog:class+init=info:file={init}",
                     f"-javaagent:{agent}=destfile={data},sessionid={SESSION},append=false",
                     "-jar", junit, "execute", "--disable-banner", "--fail-if-no-tests", "--details=summary",
                     "--class-path", str(test) + os.pathsep + cp, "--select-class", TEST, "--reports-dir", cases,
                     "--config=junit.jupiter.execution.parallel.enabled=false"],
            "raw": [*raw_tool["command"][:5], data, binary],
        }
        stages = {}
        for label, command in commands.items():
            stage = UPPER["run"](output, label, command, cwd, environment)
            stages[label] = stage
            if stage["actualExit"] != 0:
                break
        if init.exists():
            (output / "class-init.log.gz").write_bytes(gzip.compress(init.read_bytes(), mtime=0))
        assert pin(template)["sha256"] == refs[-1]["sha256"]
    status = 0 if len(stages) == len(commands) and stages["raw"]["actualExit"] == 0 else 1
    report = dict(actualExit=status, source=source, productionCore=core, stages=stages,
                  oldScope=refs[1], actualTemplateSnapshotInput=refs[-1], testInput=refs[-2],
                  inputArtifact=current, exactCurrentPhysicalSha256=digest, exactCurrentPhysicalCrc=crc,
                  noNetworkOrNativeInFixture=True, caseCountExpected=3, actualServiceActions=0,
                  session=SESSION, newTestDefinitions=0, whole451Accepted=False,
                  wholeP01807Accepted=False, formalDelta=0, terminalAtUTC=COMMON["timestamp"]())
    COMMON["dump"](output / "manifest.json", report)
    print(pin(output / "manifest.json"), {label: stage["actualExit"] for label, stage in stages.items()})
    return status


if __name__ == "__main__":
    raise SystemExit(main())
