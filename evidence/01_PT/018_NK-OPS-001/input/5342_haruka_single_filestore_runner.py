"""Execute the fixed characterization-only roster after the existing haruka admission."""

from collections import Counter
import gzip
import re


def read_combined_capsule(spec):
    encoded = bytearray()
    while True:
        line = sys.stdin.buffer.readline(2000)
        assert line.endswith(b"\n")
        if line == b"PAYLOAD-END\n":
            break
        encoded.extend(line[:-1])
        assert len(encoded) < 10 * 1024**2
    body = base64.b64decode(encoded, validate=True)
    assert 0 < spec["size"] == len(body) < 7 * 1024**2
    assert sha(body) == spec["capsuleSha256"]
    with gzip.GzipFile(fileobj=io.BytesIO(body)) as stream:
        raw = stream.read(12 * 1024**2)
    assert 0 < spec["rawTarSize"] == len(raw) < 12 * 1024**2
    assert sha(raw) == spec["rawTarSha256"]
    result = {}
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:") as archive:
        for entry in archive.getmembers():
            name = entry.name
            assert entry.isfile() and not Path(name).is_absolute() and ".." not in Path(name).parts
            assert name in spec["files"] and name not in result
            data = archive.extractfile(entry).read()
            assert sha(data) == spec["files"][name]
            result[name] = data
    assert result.keys() == spec["files"].keys()
    return result


def single_session(spec):
    stage = "precheck"
    allocated = False
    owned_run = ROOT / RUN
    steps = {}
    try:
        before = host_proof(spec)
        send("HARUKA_READY ", before)
        stage = "capsule"
        files = read_combined_capsule(spec)
        assert set(files) == set(spec["files"])
        assert boot_id() == before["boot"] and shutil.disk_usage(ROOT).free >= MIN_BYTES
        assert ROOT.stat().st_dev == before["device"]
        os.umask(0o077)
        owned_run.mkdir(mode=0o700)
        allocated = True
        for name, body in files.items():
            target = owned_run / name
            target.parent.mkdir(exist_ok=True, parents=True)
            with target.open("xb") as stream:
                stream.write(body)
        physical = owned_run / "classes"
        testclasses = owned_run / "testclasses"
        snapshot = owned_run / "snapshot"
        assert {p.relative_to(physical).as_posix(): sha(p.read_bytes())
                for p in physical.rglob("*.class")} == spec["physical"]
        assert {p.relative_to(testclasses).as_posix(): sha(p.read_bytes())
                for p in testclasses.rglob("*.class")} == spec["tests"]
        jars = sorted((owned_run / "sdk").glob("*.jar"))
        assert len(jars) == 8
        junit, = [jar for jar in jars if jar.name.startswith("junit-platform-console")]
        agent, = [jar for jar in jars if jar.name.startswith("org.jacoco.agent")]
        cli, = [jar for jar in jars if jar.name.startswith("org.jacoco.cli")]
        resource = snapshot / "program/characterization/tests/resources"
        tmp, xml = (owned_run / name for name in ("tmp", "xml"))
        tmp.mkdir()
        xml.mkdir()
        execution = owned_run / "combined.exec"
        init = owned_run / "class-init.log"
        names = spec["selectors"]
        assert len(names) == 21 and all(name.startswith("dev.codex.schubert.characterization.") for name in names)
        cp = os.pathsep.join(map(str, (physical, testclasses, resource, *jars)))
        stage = "unit"
        args = [TOOL / "java", "-Xmx1g", "-Djava.awt.headless=true", "-Duser.language=ja",
                "-Duser.country=JP", "-Duser.timezone=Asia/Tokyo", f"-Dchr.unitProjectRoot={snapshot}",
                f"-Djava.io.tmpdir={tmp}", f"-Xlog:class+init=info:file={init}",
                f"-javaagent:{agent}=destfile={execution},sessionid={spec['session']},append=false",
                "-jar", junit, "execute", "--disable-banner", "--details=summary", "--fail-if-no-tests",
                "--class-path", cp, "--reports-dir", xml, "--config=junit.jupiter.execution.parallel.enabled=false",
                *[f"--select-class={name}" for name in names]]
        steps["unit"] = command(args, owned_run)
        source_xml = xml / "TEST-junit-jupiter.xml"
        suite = ET.parse(source_xml).getroot()
        fields = ("tests", "failures", "errors", "skipped")
        totals = {name: int(suite.get(name)) for name in fields}
        case_rows = {}
        for entry in suite.iter("testcase"):
            classname, name = entry.get("classname"), entry.get("name")
            assert classname in names and (classname, name) not in case_rows
            outcome = next((tag for tag in ("error", "failure", "skipped") if entry.find(tag) is not None), "pass")
            case_rows[classname, name] = outcome
        assert len(case_rows) == totals["tests"]
        actual = Counter(case_rows.values())
        assert [actual[t] for t in ("failure", "error", "skipped")] == [totals[n] for n in fields[1:]]
        trace = init.read_bytes()
        assert not re.search(rb"Initializing '(?:com/microsoft/playwright|dev/codex/schubert/nk/|org/postgresql)", trace)
        assert boot_id() == before["boot"] and tmp.stat().st_dev == before["device"]
        cases = owned_run / "cases.json"
        with cases.open("x") as stream:
            json.dump([dict(classname=c, name=n, outcome=o) for (c, n), o in sorted(case_rows.items())], stream)
        stage = "report"
        report = owned_run / "coverage.xml"
        steps["report"] = command([TOOL / "java", "-jar", cli, "report", execution,
                                   "--classfiles", physical, "--xml", report], owned_run)
        assert steps["report"]["actualExit"] == 0
        payloads = {}
        for path in (cases, execution, report):
            body = path.read_bytes()
            assert 0 < len(body) <= 1_000_000
            payloads[path.name] = dict(sha256=sha(body), data=base64.b64encode(body).decode())
        okay = steps["unit"]["actualExit"] == 0 and totals == dict(tests=209, failures=0, errors=0, skipped=0)
        send("HARUKA_TERMINAL ", dict(actualExit=0 if okay else 1, stage="terminal", allocatedRun=allocated,
             boot=before["boot"], ownerUid=os.getuid(), workspace=str(owned_run), session=spec["session"],
             terminalAtUTC=utc(), steps=steps, totals=totals, actualBackendActions=0, sourceXmlSha256=sha(source_xml.read_bytes()),
             classInitSha256=sha(trace), methods=method_counters(report), payloads=payloads))
        raise SystemExit(0 if okay else 1)
    except (AssertionError, OSError, ValueError, KeyError, subprocess.SubprocessError) as failure:
        send("HARUKA_TERMINAL ", dict(actualExit=1, stage=stage, errorType=type(failure).__name__,
                                     allocatedRun=allocated, steps=steps, terminalAtUTC=utc()))
        raise SystemExit(1)
