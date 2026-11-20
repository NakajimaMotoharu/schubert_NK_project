"""Perform one pinned, read-only ownership and capacity check for the admitted local host."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import runpy
import shlex
from uuid import UUID

import pexpect

RUN = "PG41034-p020-current-reader3-owned-filestore-v1"
HERE = Path(__file__).resolve()
DOCS = next(Path("documents/400_PGPT/470_PMO").glob("601_*"))
EVIDENCE = Path("evidence/01_PT/018_NK-OPS-001/evidence")


def pin(path):
    return dict(path=str(path), sha256=sha256(path.read_bytes()).hexdigest())


def utc():
    return datetime.now(timezone.utc).isoformat()


def main():
    start = next(DOCS.glob("1485_*.json"))
    group = json.loads(start.read_bytes())
    scope = group["values"]
    refs = scope["oracleReferences"]
    assert all(pin(Path(row["path"])) == row for row in refs)
    old_pmo = json.loads(Path(refs[3]["path"]).read_bytes())
    pinned = Path(refs[4]["path"]).resolve()
    legacy = runpy.run_path(refs[5]["path"])
    preflight = runpy.run_path(str(HERE.with_name("5296_haruka_filestore_precheck.py")))
    code = preflight["COMMAND"].replace(preflight["RUN"], RUN)
    assert code.count(RUN) == 1
    route = legacy["config"]("haruka")
    assert old_pmo["host"] == "haruka" and old_pmo["owner"] == "mini"
    observed, state, prompts = None, "NO_RECEIPT", 0
    began = utc()
    task = pexpect.spawn("/usr/bin/ssh", [*legacy["ssh_options"](route, pinned),
                                         "python3 -u -c " + shlex.quote(code)],
                         encoding=None, echo=False, timeout=45, maxread=8192)
    try:
        while True:
            marker = task.expect([rb"(?i)password(?: for [^:\r\n]+)?:",
                                  rb'(\{"host": "haruka", [^\r\n]+\})\r?\n',
                                  rb"Permission denied", rb"Host key verification failed",
                                  pexpect.EOF, pexpect.TIMEOUT])
            if marker == 0:
                prompts += 1
                if prompts != 1 or observed is not None:
                    state = "AUTHENTICATION_REFUSED"
                    break
                task.sendline(route["users"]["mini"].encode())
            elif marker == 1:
                assert observed is None
                observed = json.loads(task.match.group(1))
            elif marker == 2:
                state = "AUTHENTICATION_OR_PERMISSION_REFUSED"
                break
            elif marker == 3:
                state = "PINNED_HOST_KEY_REFUSED"
                break
            elif marker == 4:
                state = "TERMINAL_RETURNED" if observed else "NO_OWNED_RECEIPT"
                break
            else:
                state = "UNKNOWN_TIMEOUT"
                break
    finally:
        task.close(force=task.isalive())
    if observed is not None:
        boot = observed.pop("boot")
        assert str(UUID(boot)) == boot
        observed["bootIdSha256"] = sha256(boot.encode("ascii") + b"\n").hexdigest()
        observed["matchesLastApprovedBootReceipt"] = observed["bootIdSha256"] == old_pmo["bootIdSha256"]
    valid = (state == "TERMINAL_RETURNED" and task.exitstatus == 0 and observed is not None
             and observed["matchesLastApprovedBootReceipt"] and observed["ownerUid"] == 1000
             and observed["availableBytes"] >= 20 * 1024**3 and observed["runAbsent"]
             and observed["activeJobsUnderWorkspace"] == [] and prompts == 1)
    out = EVIDENCE / scope["run"]
    out.mkdir()
    manifest = out / "manifest.json"
    record = dict(actualExit=0 if valid else 1, source=scope["source"], core=scope["productionCoreMain"],
                  startEvent=group["eventId"], checkRun=scope["run"], proposedUnitRun=RUN,
                  startedAtUTC=began, terminalAtUTC=utc(), state=state, sshExit=task.exitstatus,
                  sshSignal=task.signalstatus, pinnedHostKey=refs[4], authPrompts=prompts,
                  ownerReceipt=observed, originalApprovedEnvironment=refs[3],
                  rawPrivateOutputSaved=False, capsuleTransferred=False, testsStarted=0,
                  applicationOrServiceOperations=0)
    manifest.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    print(state, valid, observed["availableBytes"] if observed else None)
    raise SystemExit(0 if valid else 1)


if __name__ == "__main__":
    main()
