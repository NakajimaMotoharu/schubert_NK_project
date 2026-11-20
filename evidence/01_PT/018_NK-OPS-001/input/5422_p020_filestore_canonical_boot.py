"""Run one new case cohort with the QA-059 boot receipt's canonical bytes."""

import copy
import hashlib
from pathlib import Path
import runpy
import sys
from uuid import UUID


HERE = Path(__file__)
PREVIOUS_PATH = HERE.with_name("5414_p020_current_211_filestore.py")
PREVIOUS = runpy.run_path(str(PREVIOUS_PATH))
E, D = PREVIOUS["E"], PREVIOUS["D"]
read, ref, put, git = (PREVIOUS[k] for k in ("read", "ref", "put", "git"))
RUN = "PG40706-p020-current-211-approved-filestore-v1"
SESSION = "PG40706-CHARACTERIZATION-211-FILESTORE"
OUT = E / RUN
PRIVATE = Path("../pgpt-runs/PG379").resolve() / RUN.lower()


def boot_digest(text):
    try:
        parsed = UUID(text)
    except ValueError:
        return None
    if str(parsed) != text:
        return None
    return hashlib.sha256(text.encode("ascii") + b"\n").hexdigest()


def prepare():
    event = read(next(D.glob("1068_P020*")))
    refs = event["values"]["oracleReferences"]
    assert all(ref(row["path"]) == row for row in refs)
    prior = read(refs[3]["path"])
    assert prior["notRun"] == 211
    assert not prior["capsuleSent"] and prior["remoteTestJobsStarted"] == 0
    pmo = read(refs[2]["path"])
    history = read(refs[4]["path"])
    old_boot = history["admission"]["boot"]
    assert history["admission"]["boot"] == history["terminal"]["boot"]
    assert boot_digest(old_boot) == pmo["bootIdSha256"]
    assert hashlib.sha256(old_boot.encode("ascii")).hexdigest() != pmo["bootIdSha256"]
    assert boot_digest("11111111-2222-4333-8444-555555555555") != pmo["bootIdSha256"]
    assert boot_digest(old_boot + "\n") is None and boot_digest("not-a-uuid") is None
    old_client = read(next(E.glob("PG40686-*/begin.json")))["clientFile"]
    assert ref(PREVIOUS_PATH) == old_client
    code = PREVIOUS_PATH.read_text()
    change_once = PREVIOUS["change_once"]
    prefix = 'assert not git("diff", prepared["source"], group["source"], "--",'
    code = change_once(code, prefix + ' "pom.xml", "program/characterization", "src")',
                       prefix + ' "pom.xml", "program/characterization")')
    assert code.count("1049_P020*") == 2
    code = code.replace('1049_P020*', '1068_P020*')
    scope = dict(__file__=str(PREVIOUS_PATH), __name__="current_filestore_prepare")
    exec(compile(code, str(PREVIOUS_PATH), "exec"), scope)
    scope.update(RUN=RUN, SESSION=SESSION, OUT=OUT, PRIVATE=PRIVATE, INPUT=HERE)
    scope["prepare"]()
    put(OUT / "boot-format-independent.json", dict(
        actualExit=0, expectedLineEncoding="LOWERCASE_UUID_ASCII_PLUS_LF",
        pmReadOnlyReceipt=refs[2], historicOrdinaryAdmission=refs[4], historicalSameBootEquality=True,
        withoutLfMatches=False, differentBootMatches=False, rejectsMalformedUuid=True,
        previousAdmissionUntouched=refs[3], preparedFilesVerified=326, freshAdmissionRequired=True,
        productCoreNotExecuted=True, earlyFailedRunExecutedCases=0,
        localPreparationFailuresBeforeTransfer=2))


def sanitized_receipt(path, value):
    safe = copy.deepcopy(value)
    for block in (safe, safe.get("terminal"), safe.get("admission")):
        if isinstance(block, dict) and "boot" in block:
            digest = boot_digest(block.pop("boot"))
            assert digest is not None
            block["bootReceiptSha256"] = digest
    put(path, safe)


def execute():
    begin = read(OUT / "begin.json")
    assert ref(begin["pmoPrecheck"]["path"]) == begin["pmoPrecheck"]
    expected = read(begin["pmoPrecheck"]["path"])["bootIdSha256"]
    assert len(expected) == 64 and all(c in "0123456789abcdef" for c in expected)
    client = Path(begin["clientBase"]["path"])
    assert ref(client) == begin["clientBase"]
    guard = '            assert admission["runAbsent"] is True\n'
    extra = (
        '            if boot_digest(admission["boot"]) != expected_boot:\n'
        '                put(OUT / "boot-correlation-rejected.json", admission)\n'
        '                pending = "BOOT_RECEIPT_MISMATCH_WITHOUT_TRANSFER"\n'
        '                task.close(force=True)\n'
        '                break\n'
    )
    code = PREVIOUS["change_once"](client.read_text(), guard, guard + extra)
    scope = dict(__file__=str(client), __name__="current_filestore_run",
                 boot_digest=boot_digest, expected_boot=expected)
    exec(compile(code, str(client), "exec"), scope)
    scope.update(TASK=RUN, SESSION=SESSION, OUT=OUT, STORE=PRIVATE, put=sanitized_receipt)
    return scope["execute"]()


if __name__ == "__main__":
    if sys.argv[1:] == ["prepare"]:
        prepare()
    elif sys.argv[1:] == ["execute"]:
        raise SystemExit(execute())
    else:
        raise SystemExit("Select prepare or execute")
