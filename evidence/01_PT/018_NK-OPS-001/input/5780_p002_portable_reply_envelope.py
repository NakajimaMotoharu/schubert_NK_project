"""Run the original eight portable reply-envelope cases against the current Protocol JAR."""

from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
from zipfile import ZipFile


ROOT = Path.cwd()
RUNS = ROOT.parent / "pgpt-runs/PG379"
OPS = Path("evidence/01_PT/018_NK-OPS-001/evidence")
MSG = Path("evidence/01_PT/005_NK-MSG-001/evidence")
RECORDS = next(Path("documents/400_PGPT/470_PMO").glob("601_*"))
API = Path("src/schubert-nk-api/src")
PKG = "dev/codex/schubert/nk/api/messaging/outbound"
HEADER = "dev/codex/schubert/nk/protocol/codec/HeaderCodec.class"
JAVA = ROOT.parent / "toolchain/jdk-25.0.4/bin"


def get(path):
    return json.loads(Path(path).read_bytes())


def pin(path):
    return dict(path=str(path), sha256=sha256(Path(path).read_bytes()).hexdigest())


def begin_file(path, data):
    with path.open("x") as out:
        out.write(json.dumps(data, indent=2) + "\n")


def now():
    return datetime.now(timezone.utc).isoformat()


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, timeout=25)


def main():
    point, = RECORDS.glob("3405_*")
    start = get(point)["values"]
    core, seed = start["productionCoreMain"], start["source"]
    assert git("rev-parse", "HEAD").decode().strip() == seed
    original_path, = MSG.glob("PG23074*/manifest.json")
    original = get(original_path)
    assert original["actualExit"] == 0 and original["tests"] == 8
    earlier = original_path.with_name("original-begin.json")
    assert pin(earlier)["sha256"] == original["files"][earlier.name]
    dep = get(earlier)["dependencies"]
    product = API / f"main/java/{PKG}/JmsMessageFactory.java"
    fixture = API / f"test/java/{PKG}/JmsReplyEnvelopeContractTest.java"
    paths = [product, fixture]
    for path in paths:
        assert pin(path)["sha256"] == original["inputHashes"][str(path)]
        assert path.read_bytes() == git("show", f"{seed}:{path}") == git("show", f"{core}:{path}")
    current, = OPS.glob("PG43046*/manifest.json")
    protocol = get(current)["currentJar"]
    assert pin(protocol["path"]) == protocol
    assert get(current)["sameProtocolTree"] == git("rev-parse", f"{core}:src/schubert-nk-protocol").decode().strip()
    old, = (Path(p) for p in dep if Path(p).name.startswith("schubert-nk-protocol-"))
    assert pin(old)["sha256"] == dep[str(old)]
    with ZipFile(old) as saved, ZipFile(protocol["path"]) as candidate:
        old_header, new_header = saved.read(HEADER), candidate.read(HEADER)
        assert old_header != new_header
    sdk = [Path(p) for p in dep if Path(p).name.startswith(("jakarta.jms-api-", "jspecify-"))]
    assert len(sdk) == 2 and all(pin(p)["sha256"] == dep[str(p)] for p in sdk)
    config, = OPS.glob("PG43118*/manifest.json")
    console, = (p for p in get(config)["classpath"] if "junit-platform-console-standalone" in p["path"])
    assert pin(console["path"]) == console
    fixture_cp = os.pathsep.join([protocol["path"], *map(str, sdk), console["path"]])
    folder = RUNS / start["run"]
    folder.mkdir(mode=0o700)
    for name in ("target/classes", "test", "meter", "xml"):
        (folder/name).mkdir(parents=True)
    base_run = RUNS / "PG43118-nonsecret-config-independent-concurrent-oracles-v3"
    previous = get(base_run/"begin.json")["stages"]
    agent = next(arg.split("=", 1)[0] for arg in previous["junit"] if arg.startswith("-javaagent:"))
    javac = [str(JAVA/"javac"), "--release", "25", "-g", "-Xlint:all", "-Werror", "-proc:none", "-implicit:none"]
    inherited_inputs = os.pathsep.join([str(folder/"target/classes"), fixture_cp])
    steps = {
        "format": [*previous["format"][:-2], *map(str, paths)],
        "main": [*javac, "-cp", fixture_cp, "-d", str(folder/"target/classes"), str(product)],
        "fixture": [*javac, "-cp", inherited_inputs, "-d", str(folder/"test"), str(fixture)],
        "junit": [
            str(JAVA/"java"), "-Dfile.encoding=UTF-8", "-Duser.timezone=Asia/Tokyo",
            "-Djunit.jupiter.extensions.autodetection.enabled=false",
            "-Djunit.jupiter.execution.parallel.enabled=false", "-Djunit.jupiter.execution.timeout.default=15 s",
            f"{agent}=destfile={folder/'unit.exec'},append=false,sessionid={start['run']}",
            "-cp", os.pathsep.join([str(folder/"test"), inherited_inputs]),
            "org.junit.platform.console.ConsoleLauncher", "execute", "--disable-ansi-colors",
            "--fail-if-no-tests", "--reports-dir", str(folder/"xml"),
            "--select-class", f"{PKG.replace('/', '.')}.JmsReplyEnvelopeContractTest",
        ],
    }
    for stage in ("rawCompile", "unfiltered", "style", "pmd", "spotbugs"):
        cmd = [arg.replace(str(base_run), str(folder)) for arg in previous[stage]]
        if stage == "style":
            cmd = cmd[:-2] + list(map(str, paths))
        if stage == "unfiltered":
            cmd = cmd[:-2] + [str(folder/"target/classes"/PKG/"JmsMessageFactory.class")]
        if stage in ("pmd", "spotbugs"):
            idx = cmd.index("--aux-classpath" if stage == "pmd" else "-auxclasspath") + 1
            cmd[idx] = inherited_inputs
            if stage == "spotbugs":
                cmd.insert(len(cmd)-1, str(folder/"target/classes"))
        steps[stage] = cmd
    (folder/"current-static-sources.txt").write_text("".join(f"{p}\n" for p in paths))
    begin_file(folder/"begin.json", dict(source=seed, productCore=core, startedAtUTC=now(), stages=steps,
        inputs=list(map(pin,paths)), original=pin(original_path), protocol=protocol,
        oldHeaderSha256=sha256(old_header).hexdigest(), currentHeaderSha256=sha256(new_header).hexdigest(),
        borrowedVendorArtifacts=list(map(pin,sdk)), junitConsole=console))
    stage_receipts = {}
    for name, cmd in steps.items():
        result = subprocess.run(cmd, cwd=ROOT, capture_output=True, timeout=115, check=False)
        (folder/f"{name}.stdout").write_bytes(result.stdout)
        (folder/f"{name}.stderr").write_bytes(result.stderr)
        stage_receipts[name] = dict(actualExit=result.returncode, atUTC=now())
        print(name, result.returncode, flush=True)
        if result.returncode not in {"pmd":{0,4},"spotbugs":{0,1}}.get(name,{0}):
            begin_file(folder/"interrupted.json", dict(stage=name, exit=result.returncode, stages=stage_receipts))
            return result.returncode
    xml = folder/"xml/TEST-junit-jupiter.xml"
    suite = ET.parse(xml).getroot()
    known = original_path.with_name("original-TEST-junit-jupiter.xml")
    assert pin(known)["sha256"] == original["files"][known.name]
    baseline = ET.parse(known).getroot()
    def cases(root):
        return sorted((case.get("classname"),case.get("name")) for case in root.findall("testcase"))
    assert suite.get("tests") == "8" and all(suite.get(k) == "0" for k in ("errors", "failures", "skipped"))
    assert cases(suite) == cases(baseline)
    target = folder/"target/classes"/PKG/"JmsMessageFactory.class"
    assert list((folder/"target/classes").rglob("*.class")) == [target]
    begin_file(folder/"terminal.json", dict(source=seed, productCore=core, actualExit=0, terminalAtUTC=now(),
        stages=stage_receipts, junit=pin(xml), cases=cases(suite), exec=pin(folder/"unit.exec"),
        physical=pin(target), unfiltered=pin(folder/"unfiltered.stdout"),
        actualBrokerConnections=0, acquiredLiveSessions=0, declaredActualSend=0))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
