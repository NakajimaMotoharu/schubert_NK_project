"""Verify the SS311 HTTP-boundary fixture from test definitions and original receipts."""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

EVIDENCE = Path("evidence/01_PT/018_NK-OPS-001/evidence")
AUDIT = "tools/quality/architecture/ModuleDependencyAudit.java"
ROOT = "dev.codex.schubert.nk."
EXPECTED = (
    ("031", ROOT + "protocol.ClientRequest", "java.net.http.HttpRequest", True),
    ("032", ROOT + "protocol.ServerExchange", "com.sun.net.httpserver.HttpExchange", True),
    ("033", ROOT + "storage.ClientResponse", "java.net.http.HttpResponse", True),
    ("034", ROOT + "storage.ServerHandle", "com.sun.net.httpserver.HttpServer", True),
    ("035", ROOT + "protocol.GeneralUri", "java.net.URI", False),
    ("036", ROOT + "storage.DirectoryPath", "java.nio.file.Path", False),
    ("037", ROOT + "api.LocalListener", "com.sun.net.httpserver.HttpExchange", False),
)
PHASES = (
    ("before", "PG40198-f02-library-http-before-v1", 0),
    ("after", "PG40200-f02-library-http-after-v1", 1),
)


def reference(path):
    file = Path(path)
    return dict(path=str(file), sha256=hashlib.sha256(file.read_bytes()).hexdigest())


def main():
    refs = []
    records = []
    for phase, run, exit_code in PHASES:
        path = EVIDENCE / run / "manifest.json"
        record = json.loads(path.read_bytes())
        refs.append(reference(path))
        records.append(record)
        assert record["phase"] == phase and record["actualExit"] == 0
        assert record["productTests"] == record["productJars"] == 0
        assert record["wholeF02Accepted"] is False
        audit = subprocess.check_output(["git", "show", f"{record['source']}:{AUDIT}"], timeout=20)
        assert hashlib.sha256(audit).hexdigest() == record["auditSha256"]
        receipts = record["receipts"]
        for name, expected_exit in (("tool-compile", 0), ("fixture-compile", 0), ("audit", exit_code)):
            receipt = receipts[name]
            assert receipt["actualExit"] == expected_exit
            assert reference(receipt["stdout"]["path"]) == receipt["stdout"]
            assert reference(receipt["stderr"]["path"]) == receipt["stderr"]
        actual = Path(receipts["audit"]["stdout"]["path"]).read_text().splitlines()
        assert {line for line in actual if line.startswith("FINDING\t")} == {
            f"FINDING\tFRAMEWORK_FENCES\t{origin}\t{target}"
            for _, origin, target, denied in EXPECTED if denied and phase == "after"
        }
        assert [(t["testId"], t["origin"], t["target"], t["expected"], t["observed"])
                for t in record["tests"]] == [
            ("PT-F02-ARCH-" + n, origin, target, denied, denied and phase == "after")
            for n, origin, target, denied in EXPECTED
        ]

    old, corrected = records
    physical = corrected["physical"]
    assert old["physical"] == physical
    assert len(physical) == 6 and sum(map(len, physical.values())) == 13
    assert old["productionCore"] == corrected["productionCore"]
    assert old["auditSha256"] != corrected["auditSha256"]
    assert old["matched"] == 3 and corrected["matched"] == 7
    assert not subprocess.check_output(
        ["git", "diff", "--name-only", old["source"], corrected["source"], "--", "src"], timeout=20
    )
    out = EVIDENCE / "PG40202-f02-library-http-independent-v1" / "manifest.json"
    out.parent.mkdir()
    result = dict(actualExit=0, source=corrected["source"], productionCore=corrected["productionCore"],
                  independentOracle="SS311 §2 explicit test table",
                  beforeMatched=3, afterMatched=7, denied=4, permitted=3, evidence=refs,
                  tests=corrected["tests"], sameSyntheticClassHashes=13, compileWarningsTreatedAsErrors=True,
                  productTests=0, productJars=0, wholeF02Accepted=False, whole451Accepted=False,
                  newFormalAcceptance=0, terminalAtUTC=datetime.now(timezone.utc).isoformat())
    with out.open("x") as f:
        f.write(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(reference(out))


if __name__ == "__main__":
    main()
