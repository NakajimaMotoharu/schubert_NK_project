"""Admit one normal named haruka job for the current synthetic comparison tests."""
from collections import Counter
from datetime import datetime, timezone
import base64
import gzip
from hashlib import sha256
import io
import json
from pathlib import Path
import runpy
import shlex
import subprocess
import sys
import tarfile
from uuid import UUID

import pexpect

HERE = Path(__file__).resolve()
OPS = Path("evidence/01_PT/018_NK-OPS-001/evidence")
DOCS = next(Path("documents/400_PGPT/470_PMO").glob("601_*"))
FILESTORE = "dev.codex.schubert.characterization.GateOwnedFileStoreContract"
SESSION = "PG41034-CHARACTERIZATION-214-FILESTORE"


def digest(body):
    return sha256(body).hexdigest()


def pin(path):
    return dict(path=str(path), sha256=digest(path.read_bytes()))


def read(path):
    return json.loads(path.read_bytes())


def write(path, value):
    with path.open("x") as out:
        out.write(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def utc():
    return datetime.now(timezone.utc).isoformat()


def safe_boot(value):
    assert str(UUID(value)) == value
    return digest(value.encode("ascii") + b"\n")


def file_bytes(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*.class")}


def prepare(scope):
    pinned = scope["oracleReferences"]
    assert all(pin(Path(ref["path"])) == ref for ref in pinned)
    local, owner, old, proof, original = [read(Path(ref["path"])) for ref in pinned[1:6]]
    assert local["testExit"] == proof["actualExit"] == owner["actualExit"] == 0
    assert local["testCounts"] == dict(tests=213, failures=0, errors=0, skipped=0)
    assert old["expectedTests"] == 211 and proof["completedTests"] == 214
    previous_run = read(Path(pinned[8]["path"]))
    assert previous_run["actualExit"] == previous_run["terminal"]["actualExit"] == 0
    assert previous_run["state"] == "TERMINAL_RETURNED" and previous_run["run"] != scope["run"]
    assert previous_run["terminal"]["bootReceiptSha256"] == owner["ownerReceipt"]["bootIdSha256"]
    assert owner["ownerReceipt"]["matchesLastApprovedBootReceipt"] and owner["ownerReceipt"]["ownerUid"] == 1000
    assert scope["productionCoreMain"] == local["productionCore"]
    assert subprocess.check_output(["git","rev-parse","HEAD","origin/dev-foundation"], text=True).splitlines() == [
        scope["source"], scope["source"]]
    assert not subprocess.check_output(["git", "diff", "--name-only", local["source"], scope["source"], "--",
                                        "pom.xml", "program/characterization", "src"])

    base = Path("../pgpt-runs/PG379").resolve()
    local_run = base / local["run"]
    snapshot = local_run / "snapshot"
    work = base / scope["run"]
    if work.exists():
        assert {p.name for p in work.iterdir()} == {"filestore-fixture"}
    else:
        work.mkdir(mode=0o700)
    data = {}
    for name, expected in local["inputSha256"].items():
        path = Path(name)
        assert not path.is_absolute() and ".." not in path.parts
        assert path == Path("pom.xml") or path.is_relative_to("program/characterization")
        body = (snapshot / path).read_bytes()
        assert digest(body) == expected
        data["snapshot/" + name] = body
    physical_root = snapshot / "program/characterization/target/classes"
    physical = file_bytes(physical_root)
    assert {p: digest(body) for p, body in physical.items()} == local["physical"]
    tests = file_bytes(local_run / "tests")
    sdk = {name: Path(value["path"]) for name, value in original["tools"].items()}
    assert all(pin(path) == original["tools"][name] for name, path in sdk.items())
    fixture = Path(old["fixture"]["path"])
    assert pin(fixture) == old["fixture"]
    standalone = work / "filestore-fixture"
    java_c = Path(original["javac"]["path"])
    assert pin(java_c) == original["javac"]
    cp = ":".join(str(path) for key, path in sdk.items() if "jacoco" not in key)
    compile_cmd = [str(java_c), "--release", "25", "-Xlint:all", "-Werror", "-proc:none", "-cp",
                   f"{physical_root}:{cp}", "-d", str(standalone), str(fixture)]
    compile_exit = None
    if not standalone.exists():
        compiled = subprocess.run(compile_cmd, capture_output=True, timeout=45, check=False)
        assert compiled.returncode == 0
        compile_exit = compiled.returncode
    file_store = file_bytes(standalone)
    file_store_class = FILESTORE.replace(".", "/") + ".class"
    assert file_store.keys() == {file_store_class} and not tests.keys() & file_store.keys()
    assert digest(file_store[file_store_class]) == old["spec"]["tests"][file_store_class]
    tests.update(file_store)
    data.update({"classes/" + name: body for name, body in physical.items()})
    data.update({"testclasses/" + name: body for name, body in tests.items()})
    data.update({"sdk/" + name: path.read_bytes() for name, path in sdk.items()})
    assert len(physical) == 17 and len(tests) == 37 and len(sdk) == 8
    previous = old["spec"]["files"]
    hashes = {key: digest(body) for key, body in sorted(data.items())}
    assert hashes.keys() == previous.keys() and len(hashes) == 326
    changed = sorted(n for n, value in hashes.items() if previous[n] != value)
    assert len(changed) >= 4 and all(any(name in n for name in ("ArtifactComparator", "GateCli", "GateContractValidator", "GateSyntheticRunPortTest")) for n in changed)

    old_roster = Path(proof["localOracle"]["path"])
    assert pin(old_roster) == proof["localOracle"]
    selectors = old["spec"]["selectors"]
    assert len(selectors) == len(set(selectors)) == 21 and selectors.count(FILESTORE) == 1
    memory = io.BytesIO()
    with tarfile.open(fileobj=memory, mode="w", format=tarfile.PAX_FORMAT) as archive:
        for name, body in sorted(data.items()):
            member = tarfile.TarInfo(name)
            member.size, member.mode = len(body), 0o600
            archive.addfile(member, io.BytesIO(body))
    tar = memory.getvalue()
    payload = gzip.compress(tar, mtime=0)
    assert 0 < len(payload) < 7 * 1024**2 and 0 < len(tar) < 12 * 1024**2
    capsule = work / "characterization-214.tar.gz"
    capsule.write_bytes(payload)
    spec = dict(old["spec"], files=hashes,
                physical={name: digest(body) for name, body in physical.items()},
                tests={name: digest(body) for name, body in tests.items()},
                capsuleSha256=digest(payload), size=len(payload),
                rawTarSha256=digest(tar), rawTarSize=len(tar), session=SESSION, expectedTests=214)
    runner_path = Path(pinned[6]["path"])
    runner = runner_path.read_text()
    old_count = "totals == dict(tests=209,"
    assert runner.count(old_count) == 1
    runner = runner.replace(old_count, "totals == dict(tests=214,")
    compile(runner, str(runner_path), "exec")
    host = Path(old["hostControls"]["path"]).resolve()
    assert pin(host) == old["hostControls"]
    runtime = work / "runner.py"
    runtime.write_text(runner)
    out = OPS / scope["run"]
    out.mkdir()
    write(out / "begin.json", dict(
        source=scope["source"], toolSource=local["source"], productionCore=local["productionCore"],
        sourceDiff=changed, run=scope["run"], session=SESSION, expectedTests=214, selectors=selectors,
        preparedArtifact=pin(capsule), inputScopeCount=len(hashes), originalToolCohort=pinned[3],
        localEvidence=pinned[1], currentPrecheck=pinned[2], resolvedRunner=pin(runtime),
        hostControls=pin(host), compiledFileStore=pin(standalone / file_store_class),
        fileStoreCompileCommand=compile_cmd, fileStoreCompileExit=compile_exit,
        existingFixtureByteProof=compile_exit is None,
        prepTerminalUTC=utc(), backendOperationsAllowed=0))
    write(work / "prepared.json", dict(spec=spec, capsule=pin(capsule), runner=pin(runtime),
                                     hostControls=pin(host), expectedBoot=owner["ownerReceipt"]["bootIdSha256"],
                                     pinnedKey=owner["pinnedHostKey"]))
    print("prepared", len(hashes), len(payload), 214)


def execute(scope, *, session=SESSION, expected_tests=214):
    work = Path("../pgpt-runs/PG379").resolve() / scope["run"]
    out = OPS / scope["run"]
    start = read(out / "begin.json")
    prepared = read(work / "prepared.json")
    assert not (out / "owner-execution-start.json").exists()
    assert start["source"] == subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    assert all(pin(Path(prepared[key]["path"])) == prepared[key]
               for key in ("capsule", "runner", "hostControls", "pinnedKey"))
    spec = prepared["spec"]
    capsule = Path(prepared["capsule"]["path"]).read_bytes()
    assert len(capsule) == spec["size"] and digest(capsule) == spec["capsuleSha256"]
    code = (Path(prepared["hostControls"]["path"]).read_bytes() + b"\n"
            + Path(prepared["runner"]["path"]).read_bytes()
            + f"\nRUN={scope['run']!r}\nsingle_session({spec!r})\n".encode())
    encoded = base64.b64encode(gzip.compress(code, mtime=0)).decode()
    remote = "python3 -u -c " + shlex.quote(
        f"import base64,gzip;exec(gzip.decompress(base64.b64decode({encoded!r})))")
    previous = runpy.run_path(str(HERE.with_name("5311_p020_prompted_haruka_one_shot.py")))
    host = previous["config"]("haruka")
    args = previous["ssh_options"](host, Path(prepared["pinnedKey"]["path"]).resolve())
    write(out / "owner-execution-start.json", dict(
        startedAtUTC=utc(), run=scope["run"], source=start["toolSource"],
        fixedHostKey=prepared["pinnedKey"], bootReceiptSha256=prepared["expectedBoot"],
        admissionBeforeTransfer=True, authPromptLimit=1))
    task = pexpect.spawn("/usr/bin/ssh", [*args, remote], encoding=None, echo=False,
                         timeout=130, maxread=32768)
    task.delaybeforesend = 0
    receipt, terminal, sent, prompt = None, None, False, 0
    state = "NO_TERMINAL"
    try:
        while True:
            marker = task.expect([rb"(?i)password(?: for [^:\r\n]+)?:",
                                  rb"HARUKA_READY ([^\r\n]+)\r?\n",
                                  rb"HARUKA_TERMINAL ([^\r\n]+)\r?\n",
                                  rb"Permission denied", rb"Host key verification failed",
                                  pexpect.EOF, pexpect.TIMEOUT])
            if marker == 0:
                prompt += 1
                if prompt != 1 or receipt is not None:
                    state = "AUTHENTICATION_REFUSED"
                    break
                task.sendline(host["users"]["mini"].encode())
            elif marker == 1:
                assert receipt is None and not sent
                receipt = json.loads(task.match.group(1))
                check = (receipt["host"] == "haruka" and receipt["uid"] == 1000 and prompt == 1
                         and receipt["workspace"] == previous["WORK"] and receipt["workspaceMode"] == "0700"
                         and receipt["freeBytes"] >= previous["MIN_BYTES"] and receipt["activeOwnedWorkspaceJobs"] == 0
                         and receipt["runAbsent"] is True and safe_boot(receipt["boot"]) == prepared["expectedBoot"])
                if not check:
                    state = "CURRENT_ADMISSION_NOT_ESTABLISHED_NO_TRANSFER"
                    break
                public = dict(receipt)
                public["bootReceiptSha256"] = safe_boot(public.pop("boot"))
                write(out / "admission.json", public)
                data = base64.b64encode(capsule)
                for offset in range(0, len(data), 1800):
                    part = data[offset:offset+1800] + b"\n"
                    assert task.send(part) == len(part)
                task.sendline(b"PAYLOAD-END")
                sent = True
            elif marker == 2:
                assert terminal is None
                terminal = json.loads(task.match.group(1))
            elif marker == 3:
                state = "AUTHENTICATION_OR_PERMISSION_REFUSED"
                break
            elif marker == 4:
                state = "PINNED_HOST_KEY_REFUSED"
                break
            elif marker == 5:
                state = "TERMINAL_RETURNED" if terminal else "NO_TERMINAL"
                break
            else:
                state = "UNKNOWN_TIMEOUT_NO_REPLAY"
                break
    except (AssertionError, KeyError, OSError, pexpect.ExceptionPexpect, ValueError) as failure:
        state = "OBSERVATION_FAILURE_" + type(failure).__name__
    if not sent or state == "TERMINAL_RETURNED":
        task.close(force=task.isalive())
    else:
        # Preserve the remote ownership state and do not issue an additional operation.
        state = "REMOTE_UNCONFIRMED_" + state
    retained = {}
    closed = (state == "TERMINAL_RETURNED" and task.exitstatus == 0 and terminal is not None
              and terminal["actualExit"] == 0 and sent and receipt is not None)
    if terminal and "payloads" in terminal:
        assert sent and receipt is not None
        assert terminal["boot"] == receipt["boot"] and terminal["ownerUid"] == receipt["uid"]
        assert terminal["workspace"] == previous["WORK"] + "/" + scope["run"]
        assert terminal["session"] == session
        terminal["bootReceiptSha256"] = safe_boot(terminal.pop("boot"))
        for name, item in terminal.pop("payloads").items():
            assert name in {"cases.json", "combined.exec", "coverage.xml"}
            body = base64.b64decode(item["data"], validate=True)
            assert digest(body) == item["sha256"] and 0 < len(body) <= 1_000_000
            with (work / name).open("xb") as stream:
                stream.write(body)
            retained[name] = pin(work / name)
    if closed:
        assert set(retained) == {"cases.json", "combined.exec", "coverage.xml"}
        assert terminal["totals"] == dict(tests=expected_tests, failures=0, errors=0, skipped=0)
    write(out / "manifest.json", dict(actualExit=0 if closed else 1, state=state, source=start["toolSource"],
                                      run=scope["run"], core=start["productionCore"], authPrompts=prompt,
                                      sshExit=task.exitstatus, terminal=terminal, capsuleTransferred=sent,
                                      returnedEvidence=retained, actualProductTests=0, actualBackendActions=0,
                                      chrStarted=False, whole451=False, formalDelta=0, terminalAtUTC=utc()))
    print(state, closed, sent)
    raise SystemExit(0 if closed else 1)


if __name__ == "__main__":
    g = read(next(DOCS.glob("1488_*.json")))
    if sys.argv[1:] == ["prepare"]:
        prepare(g["values"])
    elif sys.argv[1:] == ["execute"]:
        execute(g["values"])
    else:
        raise SystemExit("Choose prepare or execute")
