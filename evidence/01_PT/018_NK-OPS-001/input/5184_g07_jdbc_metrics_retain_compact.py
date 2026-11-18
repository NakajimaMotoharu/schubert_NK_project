"""Retain exact scan details and release only the verified disposable projection."""
from datetime import datetime, timezone
from importlib.util import module_from_spec, spec_from_file_location
import json
import os
from pathlib import Path
import shutil
import stat

S=spec_from_file_location("range",Path(__file__).with_name("5180_g07_jdbc_metrics_delta.py"))
w=module_from_spec(S)
S.loader.exec_module(w)
p=w.load_stage("bind")
DETAILS=("scan-terminal.json","qualified-cached-initial.json","qualified-final-private-detail.json",
         "classified-findings.json","remaining-origins.json","remaining-after-build-origins.json",
         "additional-build-origins.json","binary-qualification.json")


def ordinary_file(f):
    info=f.lstat()
    return (stat.S_ISREG(info.st_mode) and info.st_uid==os.getuid()
            and info.st_nlink==1 and f.resolve()==f)


def main():
    qualified=w.OUT/"qualified-final-private-detail.json"
    value=p.load(qualified)
    assert (value["resultQualifiedForRange"] and value["confirmedSecrets"]==0
            and value["unresolvedCandidates"]==value["unqualifiedBinary"]==0)
    scan=p.load(w.OUT/"scan-terminal.json")
    assert value["throughCommit"]==scan["throughCommit"]
    assert sum(value["categories"].values())==scan["findingsCount"]
    assert w.TEMP.parent==Path("/dev/shm") and w.TEMP.is_dir() and w.TEMP.resolve()==w.TEMP
    mode=w.TEMP.stat()
    assert mode.st_uid==os.getuid() and stat.S_IMODE(mode.st_mode)==0o700
    expected={w.TEMP/n:scan[k] for n,k in (("scanner-redacted.json","reportSha256"),("projection.json","projectionSha256"))}
    assert all(p.ref(w.RETAIN/f.name)["sha256"]==sha for f,sha in expected.items())
    for row in p.load(w.RETAIN/"projection.json"):
        local=Path(row["relativeProjection"])
        assert len(local.parts)==3 and local.parts[0] in ("text","binary") and local.parts[1].isdigit()
        assert ".." not in local.parts
        file=w.TEMP/local
        assert file not in expected
        expected[file]=row["decodedSha256"]
    observed={f for f in w.TEMP.rglob("*") if f.is_file() or f.is_symlink()}
    assert observed==expected.keys()
    assert all(ordinary_file(f) and p.ref(f)["sha256"]==sha for f,sha in expected.items())
    disk_before=shutil.disk_usage(w.RETAIN).free
    memory_before=shutil.disk_usage(w.TEMP).free
    slot=w.RETAIN/"qualification-detail"
    slot.mkdir(exist_ok=False,mode=0o700)
    receipts={}
    # Same filesystem move retains the exact original scan details and does not create extra copies.
    for name in DETAILS:
        frm=w.OUT/name
        observed=p.ref(frm)["sha256"]
        dest=slot/name
        frm.rename(dest)
        assert p.ref(dest)["sha256"]==observed
        receipts[name]=p.ref(dest)
    retained = {k:p.ref(w.RETAIN/k) for k in ("projection.json","scanner-redacted.json")}
    directories=sorted({f.parent for f in expected if f.parent not in (w.TEMP,w.TEMP/"text",w.TEMP/"binary")},reverse=True)
    for file in expected:
        file.unlink()
    for directory in directories:
        directory.rmdir()
    for sub in ("text","binary"):
        folder=w.TEMP/sub
        if folder.is_dir():
            folder.rmdir()
    w.TEMP.rmdir()
    assert all(p.ref(Path(x["path"]))==x for x in [*retained.values(),*receipts.values()])
    no_exports=["scanner match strings","credential values","private runtime content","raw HTTP or database output"]
    terminal=dict(actualExit=0,terminalAtUTC=datetime.now(timezone.utc).isoformat(),
       fromCommit=scan["fromCommit"],throughCommit=scan["throughCommit"],
       source=scan["throughCommit"],commits=scan["commits"],trackedBlobVersions=scan["trackedBlobVersions"],
       text=scan["text"],binary=scan["binary"],heldMetadataOnly=scan["heldMetadataOnly"],
       scannerCommand=scan["scannerCommand"],scannerSha256=scan["scannerSha256"],
       scannerExit=scan["actualScannerExit"],scannerStartUTC=scan["startedAtUTC"],
       scannerTerminalUTC=scan["terminalAtUTC"],findingsCount=scan["findingsCount"],
       confirmedSecrets=0,unresolvedCandidates=0,unqualifiedBinary=0,grounds=value["categories"],
       exactPrivateProjectionReceipts=retained,exactPrivateProofFiles=receipts,
       projectionPersistedAsVolatileDuplicateOnly=True,releasedProjectionFiles=scan["trackedBlobVersions"],
       allReleasedFilesIndividuallyHashChecked=True,originalGitBlobsPreserved=True,
       projectionReconstructionBasis="Exact Git blob and gzip-decoded SHA per retained projection index",
       compactPublicReceipt=True,secretCandidateOutput=no_exports,
       retainedReportHasValuesRedacted=True,activeRemoteBusinessWork=0,productTests=0,
       localFreeBeforeCleanup=disk_before,localFreeAfterCleanup=shutil.disk_usage(w.RETAIN).free,
       tmpFreeBeforeCleanup=memory_before,tmpFreeAfterCleanup=shutil.disk_usage("/dev/shm").free,
       sameRangeScannerRepeated=False,qualifiedRangeOnly=True,wholeG07Accepted=False,whole451Accepted=False)
    p.write(w.OUT/"manifest.json",terminal)
    print(dict(versions=terminal["trackedBlobVersions"],findings=terminal["findingsCount"],
               memoryReleased=terminal["tmpFreeAfterCleanup"]-memory_before,
               privateProofFiles=len(receipts),sha256=p.ref(w.OUT/"manifest.json")["sha256"]))


if __name__=="__main__":
    main()
