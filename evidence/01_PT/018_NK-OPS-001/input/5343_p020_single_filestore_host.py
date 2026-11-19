"""Prepare and start one SSH job for the unchanged characterization tool and one capacity fixture."""

import base64
import gzip
import io
import json
import os
from pathlib import Path
import runpy
import shlex
import subprocess
import sys
import tarfile
from tempfile import TemporaryDirectory

import pexpect


HERE = Path(__file__)
ORIGINAL = runpy.run_path(str(HERE.with_name("5311_p020_prompted_haruka_one_shot.py")))
E, D, WORK, MIN_BYTES = (ORIGINAL[name] for name in ("E", "D", "WORK", "MIN_BYTES"))
read = lambda path: json.loads(Path(path).read_bytes())
sha, ref, git, now = (ORIGINAL[name] for name in ("sha", "ref", "git", "now"))
TASK = "PG40396-p020-single-session-filestore-target-v1"
SESSION = "PG40396-CHARACTERIZATION-209-FILESTORE"
CASE = "dev.codex.schubert.characterization.GateOwnedFileStoreContract"
STORE = Path("../pgpt-runs/PG379").resolve() / TASK.lower()
OUT = E / TASK


def put(path, obj):
    with path.open("x") as stream:
        json.dump(obj, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def class_bytes(path, expected):
    directory = Path(path)
    assert directory.resolve() == directory
    result = {}
    for name, digest in expected.items():
        entry = directory / name
        assert entry.resolve() == entry
        data = entry.read_bytes()
        assert sha(data) == digest
        result[name] = data
    return result


def select(command):
    return [command[index + 1] for index, arg in enumerate(command) if arg == "--select-class"]


def prepare():
    begin = read(next(D.glob("830_*")))
    task = begin["values"]
    assert task["run"] == TASK
    refs = task["oracleReferences"]
    assert all(ref(row["path"]) == row for row in refs)
    older, prior, previous_host = (read(row["path"]) for row in refs[1:4])
    assert prior["source"] == older["source"]
    assert previous_host["actualExit"] == 0 and older["expected"] == prior["tests"] == 208
    assert older["stages"]["unit"]["actualExit"] == 0
    source = git("rev-parse", "HEAD").decode().strip()
    snapshot = {}
    for path, digest in older["inputHashes"].items():
        assert path == "pom.xml" or path.startswith("program/characterization/")
        data = git("show", f"{source}:{path}")
        assert sha(data) == digest
        snapshot["snapshot/" + path] = data
    command = older["stages"]["unit"]["command"]
    selected = select(command)
    assert len(set(selected)) == 20 and CASE not in selected
    main = class_bytes(older["classesDir"], older["mainPhysical"])
    tests = class_bytes(older["testsDir"], older["testPhysical"])
    begin_tools = read(next(E.glob("PG40128-*/begin.json")))
    tools = begin_tools["tools"]
    assert len(tools) == 8
    sdk = {}
    for jar, entry in tools.items():
        assert ref(entry["path"]) == entry and Path(entry["path"]).name == jar
        sdk["sdk/" + jar] = Path(entry["path"]).read_bytes()
    old_launch = read(next(E.glob("PG40162-*/manifest.json")))
    assert ref(old_launch["java"]["path"]) == old_launch["java"]
    assert ref(old_launch["javac"]["path"]) == old_launch["javac"]
    fixture = HERE.with_name("5341_GateOwnedFileStoreContract.java")
    object_path = fixture.resolve().relative_to(Path.cwd())
    fixture_hash = sha(git("show", f"{source}:{object_path}"))
    test_compile = older["stages"]["test"]["command"]
    cp_end = test_compile.index("-cp") + 2
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-char-owned-current-") as name:
        temp = Path(name)
        assert fixture_hash == ref(fixture)["sha256"]
        args = [*test_compile[:cp_end], "-proc:none", "-d", temp, fixture]
        result = subprocess.run(args, check=False, capture_output=True, timeout=30)
        assert result.returncode == 0
        new_class = CASE.replace(".", "/") + ".class"
        body = (temp / new_class).read_bytes()
    assert new_class not in tests
    tests[new_class] = body
    files = {**snapshot, **{f"classes/{k}": v for k, v in main.items()},
             **{f"testclasses/{k}": v for k, v in tests.items()}, **sdk}
    assert len(main) == 17 and len(tests) == 37
    packed = io.BytesIO()
    with tarfile.open(fileobj=packed, mode="w:", format=tarfile.PAX_FORMAT) as tar:
        for path, data in sorted(files.items()):
            entry = tarfile.TarInfo(path)
            entry.size, entry.mode = len(data), 0o600
            tar.addfile(entry, io.BytesIO(data))
    payload = packed.getvalue()
    assert 0 < len(payload) < 7 * 1024**2
    OUT.mkdir()
    STORE.mkdir(mode=0o700)
    capsule = STORE / "verified-characterization.tar"
    with capsule.open("xb") as stream:
        os.fchmod(stream.fileno(), 0o600)
        stream.write(payload)
    spec = dict(capsuleSha256=sha(payload), size=len(payload), files={k: sha(v) for k, v in files.items()},
                physical=older["mainPhysical"], tests={k: sha(v) for k, v in tests.items()},
                selectors=selected + [CASE], session=SESSION, java=old_launch["java"]["sha256"],
                javac=old_launch["javac"]["sha256"])
    put(OUT / "begin.json", dict(source=source, previousToolSource=prior["source"],
         productionCore=task["productionCoreMain"], groupStart=begin["eventId"], run=TASK, expectedTests=209,
         capsule=ref(capsule), fixture=ref(fixture), runner=ref(HERE.with_name("5342_haruka_single_filestore_runner.py")),
         hostControls=refs[-2], clientFile=ref(HERE), historicInputsVerified=len(snapshot), spec=spec,
         productTests=0, terminalAtUTC=now()))
    print(dict(prepared=True, bytes=len(payload), fileCount=len(files), expectedTests=209))


def execute():
    seed = read(OUT / "begin.json")
    spec = seed["spec"]
    assert git("rev-parse", "HEAD").decode().strip() == seed["source"]
    assert all(ref(seed[k]["path"]) == seed[k] for k in ("capsule", "fixture", "runner", "hostControls", "clientFile"))
    payload = Path(seed["capsule"]["path"]).read_bytes()
    assert len(payload) == spec["size"] and sha(payload) == spec["capsuleSha256"]
    code = (Path(seed["hostControls"]["path"]).read_bytes() + b"\n" +
            Path(seed["runner"]["path"]).read_bytes() +
            f"\nRUN={TASK!r}\nsingle_session({spec!r})\n".encode())
    compressed = base64.b64encode(gzip.compress(code, mtime=0)).decode()
    remote = "python3 -u -c " + shlex.quote(
        f"import base64,gzip;exec(gzip.decompress(base64.b64decode({compressed!r})))")
    pinned = ORIGINAL["PMO"] / "haruka_known_hosts"
    initial = next(E.glob("PG40160-*/begin.json"))
    assert ref(pinned)["sha256"] == read(initial)["pinnedKnownHostsSha256"]
    cfg = ORIGINAL["config"]("haruka")
    route = ORIGINAL["ssh_options"](cfg, pinned)
    put(OUT / "owner-execution-start.json",
        dict(startedAtUTC=now(), source=seed["source"], run=TASK, ordinaryPasswordPromptLimit=1,
             fixedHostKeySha256=ref(pinned)["sha256"]))
    task = pexpect.spawn("/usr/bin/ssh", [*route, remote], encoding=None, echo=False,
                         timeout=130, maxread=32768)
    task.delaybeforesend = 0
    pending = "NO_TERMINAL"
    prompts, admission, sent, terminal = 0, None, False, None
    while True:
        line = task.expect([rb"(?i)password(?: for [^:\r\n]+)?:", rb"HARUKA_READY ([^\r\n]+)\r?\n",
                            rb"HARUKA_TERMINAL ([^\r\n]+)\r?\n", pexpect.EOF, pexpect.TIMEOUT])
        if line == 0:
            prompts += 1
            if prompts != 1 or admission is not None:
                pending = "AUTHENTICATION_REFUSED"
                task.sendintr()
                break
            task.sendline(cfg["users"]["mini"].encode())
        elif line == 1:
            assert prompts == 1 and admission is None and not sent
            admission = json.loads(task.match.group(1))
            assert admission["host"] == "haruka" and admission["uid"] == 1000
            assert admission["workspace"] == WORK and admission["workspaceMode"] == "0700"
            assert admission["freeBytes"] >= MIN_BYTES and admission["activeOwnedWorkspaceJobs"] == 0
            assert admission["runAbsent"] is True
            put(OUT / "admission.json", admission)
            encoded = base64.b64encode(payload)
            for index in range(0, len(encoded), 1800):
                block = encoded[index:index + 1800] + b"\n"
                assert task.send(block) == len(block)
            task.sendline(b"PAYLOAD-END")
            sent = True
        elif line == 2:
            assert terminal is None
            terminal = json.loads(task.match.group(1))
        elif line == 3:
            task.close(force=False)
            pending = "TERMINAL_RETURNED" if terminal else "SSH_ENDED_WITHOUT_REMOTE_TERMINAL"
            break
        else:
            pending = "TIMED_OUT_TERMINAL_UNKNOWN"
            break
    qualification = {}
    if terminal and "payloads" in terminal:
        assert admission is not None and sent and terminal["boot"] == admission["boot"]
        assert terminal["ownerUid"] == admission["uid"] and terminal["workspace"] == f"{WORK}/{TASK}"
        assert terminal["session"] == SESSION
        for name, item in terminal.pop("payloads").items():
            assert name in {"cases.json", "combined.exec", "coverage.xml"}
            body = base64.b64decode(item["data"], validate=True)
            assert sha(body) == item["sha256"]
            with (OUT / name).open("xb") as stream:
                stream.write(body)
            qualification[name] = ref(OUT / name)
    okay = (task.exitstatus == 0 and terminal and terminal["actualExit"] == 0
            and set(qualification) == {"cases.json", "combined.exec", "coverage.xml"})
    result = dict(actualExit=0 if okay else 1, outcome=pending, sshExit=task.exitstatus,
                  sshSignal=task.signalstatus, authPrompts=prompts, admission=admission, capsuleSent=sent,
                  terminal=terminal, artifacts=qualification, newFormalAcceptance=0,
                  productTests=0, actualBackendActions=0, whole451Accepted=False, terminalAtUTC=now())
    put(OUT / "manifest.json", result)
    print(dict(outcome=pending, actualExit=result["actualExit"], capsuleSent=sent,
               qualifiedArtifacts=sorted(qualification)))
    return result["actualExit"]


if __name__ == "__main__":
    if sys.argv[1:] == ["prepare"]:
        prepare()
    elif sys.argv[1:] == ["execute"]:
        raise SystemExit(execute())
    else:
        raise SystemExit("Select prepare or execute as separate stages")
