"""Review each current PMD occurrence against the acquired-resource contracts."""

from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from xml.etree import ElementTree as ET


BASE = Path("evidence/01_PT/018_NK-OPS-001/evidence")
REASONS = {
    "read": ("SSC310 primary tracking and phase-specific unknown/SQL propagation", "EXPPORT-J001/J002"),
    "closeReadRows": ("SSC310 close the acquired result set once and preserve the defined priority", "EXPPORT-J002"),
    "closeReadStatement": ("SSC310 close the acquired statement after the result set and preserve priority", "EXPPORT-J002"),
    "stage": ("SS332 record the primary for one close, then preserve the existing exception mapping", "EXPPORT-J003/J010"),
    "finish": ("SS332 record the primary for one close, then preserve the existing exception mapping", "EXPPORT-J004/J010"),
    "closeUpdateStatement": ("SS332 preserve primary identity and Java TWR suppressed-exception order", "EXPPORT-J010"),
    "usingJdbc": ("SSC304 preserve Java TWR sequencing in the existing helper", "EXPPORT-P008"),
}


def pin(path):
    return dict(path=str(path), sha256=sha256(Path(path).read_bytes()).hexdigest())


def main():
    f, j, p = [next(BASE.glob(f"PG{id}-*/manifest.json")) for id in (40736, 40732, 40730)]
    typed, review, pt = [json.loads(item.read_bytes()) for item in (f, j, p)]
    assert typed["actualExit"] == review["actualExit"] == pt["actualExit"] == 0
    assert typed["physicalHashes"] == pt["physical"] and pt["actualTests"] == 30
    assert typed["spotComplete"] and typed["spotCounts"] == dict(BugInstance=0, Error=0, MissingClass=0)
    assert all(not result["missed"] for result in review["rawCounters"].values())
    path = Path(review["candidateMain"]["path"])
    assert pin(path) == review["candidateMain"] and pin(path) == pt["candidateMain"]
    text = path.read_text()
    lines = text.splitlines()
    assert text.count("closeUpdateStatement(statement, primary);") == 2
    assert text.count("closeReadRows(rows, rowFailure);") == 1
    assert text.count("closeReadStatement(statement, statementFailure);") == 1
    assert text.count("if (JdbcResourceFailures.replace(primary, secondary)) throw secondary;") == 2
    assert "primary.addSuppressed(secondary);" in text
    assert "if (value == null) throw new SQLDataException(\"Expiry projection missing\");\n    return value;" in text
    assert "PreparedStatement statement =" in text and "ResultSet rows = query.executeQuery();" in text

    xml = ET.parse(f.with_name("pmd.xml"))
    counts = Counter()
    rows = []
    for value in xml.iter():
        if not value.tag.endswith("}violation"):
            continue
        method, rule, line = value.get("method"), value.get("rule"), int(value.get("beginline"))
        if rule == "CloseResource":
            assert method == "read" and lines[line - 1].strip() in (
                "var query = presentRead(statement);", "var values = presentRead(rows);"
            )
            reasons = ("Nonnull alias denotes the same acquired object closed once in finally", "EXPPORT-J001/J002")
        else:
            assert rule == "AvoidCatchingGenericException" and "catch (" in lines[line - 1]
            reasons = REASONS[method]
        counts[rule] += 1
        rows.append(dict(rule=rule, method=method, line=line, column=int(value.get("begincolumn")),
                         decision="NOT_APPLICABLE_UNCHANGED_REQUIRED_TYPED_CONTRACT",
                         reason=reasons[0], tests=reasons[1]))
    assert len(rows) == typed["rawPmdCurrent"] == 17
    assert counts == {"AvoidCatchingGenericException": 15, "CloseResource": 2}
    output = BASE / "PG40738-f03-expiry-final-ownership-independent-v1"
    output.mkdir()
    report = dict(
        actualExit=0, candidateProductionSource=typed["candidateProductionCore"],
        shape="local ExpiryAudit 7 physical, 4 with bytecode",
        packageAndThirtyExecSameBytes=True, raw=review["rawCounters"], selectedActualTests=30,
        zeroSpotFindingsErrorsMissing=True, pmdRawExit=4, pmdRaw=17,
        classifiedNonApplicable=17, unclassified=0, applicable=0, suppressionsAdded=0,
        staticDispositions=rows, noActualRuntimeOrDb=True,
        firstPostFailure="BUG-3409 acquisition versus nonnull alias diagnostic location",
        sourceEvidence=[pin(k) for k in (f, j, p, path, f.with_name("pmd.xml"), f.with_name("spotbugs.xml"))],
        whole451=False, wholeF03=False, formalDelta=0, terminalAtUTC=datetime.now(timezone.utc).isoformat(),
    )
    (output / "manifest.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(dict(tests=30, pmdClassified=17, spotbugs0=True, allFourMetrics=True))


if __name__ == "__main__":
    main()
