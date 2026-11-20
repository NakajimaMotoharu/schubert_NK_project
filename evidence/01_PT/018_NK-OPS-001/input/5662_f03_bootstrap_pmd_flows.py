"""Reconcile explicit borrowed-resource and strict-reader PMD sites on the fixed source."""

from collections import Counter
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import runpy


H = runpy.run_path(str(Path(__file__).with_name("5661_f03_bootstrap_pmd_identity.py")))
OPS, read, pin, checked, write, git = (H[n] for n in ("OPS", "read", "pin", "checked", "write", "git"))
MIGRATION = {"MigrationGamesVerifier.java", "MigrationMasterContentVerifier.java"}
JDBC = {"SchemaHistoryAdmission.java", "ServiceDatabaseAdmission.java"}
GSON = "2cbd119bf1961c28788310963dc80ba65f58cdeec1dd139c8bdb1240faa2c36f"


def context(lines, number, before=0, after=0):
    return "\n".join(line.strip() for line in lines[number - 1 - before:number + after])


def migration(item, lines):
    line, method, rule = (item[n] for n in ("line", "method", "rule"))
    if rule == "CompareObjectsWithEquals":
        assert context(lines, line) == "if (cleanup != primary) primary.addSuppressed(cleanup);"
        assert method in ("closeRows", "closeStatement", "closeResult")
        return "SUPPRESSION_IDENTITY_GUARD", (
            "Throwable.addSuppressed rejects self by reference identity. A value-based comparison could omit "
            "a distinct cleanup exception. The primary is already being propagated.")
    assert rule == "AvoidCatchingGenericException"
    if method.startswith("close"):
        assert context(lines, line, before=2, after=1) == (
            "try {\nresource.close();\n} catch (SQLException | RuntimeException | Error cleanup) {\n"
            "if (cleanup != primary) primary.addSuppressed(cleanup);")
        assert context(lines, line, before=6).startswith("if (primary == null) {\nresource.close();\nreturn;")
        return "OWNED_CLOSE_WITH_EXISTING_PRIMARY", (
            "The locally acquired result or statement is closed once. Without a primary, close propagates. "
            "With a primary, a distinct cleanup failure is suppressed on that same primary.")
    target = "closeStatement(statement, primary);" if method == "verify" else "closeResult(result, primary);"
    assert context(lines, line, after=4) == (
        "} catch (SQLException | RuntimeException | Error failure) {\nprimary = failure;\n"
        "throw failure;\n} finally {\n" + target)
    return "RETHROW_AND_RELEASE_OWNED_JDBC", (
        "All failures propagate by their original reference after cleanup. The Statement or ResultSet is "
        "owned by this call. The Connection is borrowed and is kept open.")


def jdbc(item, lines):
    line, method, rule = (item[n] for n in ("line", "method", "rule"))
    if rule == "DoNotUseThreads":
        assert method == "inspect" and context(lines, line) == "require(!Thread.currentThread().isInterrupted());"
        return "OBSERVE_EXISTING_THREAD", (
            "The schema reader only inspects its caller thread's interrupt flag. It neither creates threads nor clears the flag.")
    if rule == "CloseResource":
        assert method in ("inspect", "verify")
        current = context(lines, line)
        assert current in ("var query = required(statement);", "var values = required(rows);")
        target = "closeStatement(statement, primary);" if "statement" in current else "closeRows(rows, rowFailure);"
        assert target in lines[line - 1:line + 60] or target in context(lines, line, after=59)
        return "ALIAS_WITH_EXPLICIT_FINALLY", (
            "The named nonnull alias is the acquired JDBC handle. The enclosing finally closes it through the "
            "null-aware typed helper exactly once. No alias acquires a second resource.")
    assert rule == "AvoidCatchingGenericException"
    if method in ("closeRows", "closeStatement"):
        assert context(lines, line, after=1) == (
            "} catch (SQLException | RuntimeException | Error secondary) {\n"
            "if (JdbcAdmissionFailures.replace(primary, secondary)) throw secondary;")
        return "TYPED_JDBC_CLOSE_PRECEDENCE", (
            "The cleanup exception is ruled on by the common typed ownership policy. The close fails or the "
            "existing primary remains observable. The catch does not turn a failure into a successful result.")
    next_line = context(lines, line, after=4)
    assert next_line in (
        "} catch (SQLException | RuntimeException | Error failure) {\nrowFailure = failure;\n"
        "throw failure;\n} finally {\ncloseRows(rows, rowFailure);",
        "} catch (SQLException | RuntimeException | Error failure) {\nprimary = failure;\n"
        "throw failure;\n} finally {\ncloseStatement(statement, primary);")
    return "RETHROW_AND_RELEASE_OWNED_JDBC", (
        "The catch records the exact failure and always rethrows it. The matching finally closes the result "
        "or statement. The borrowed connection is not closed.")


def service_source(item, lines):
    line, method = item["line"], item["method"]
    assert item["rule"] == "AvoidCatchingGenericException"
    if method == "connectWhileLocked":
        assert context(lines, line, after=2) == (
            "} catch (RuntimeException | Error failure) {\ndiscard(connection, failure);\nthrow failure;")
        return "REJECTED_OWNED_CONNECTION", (
            "The connection opened by this source is still owned on admission failure. It is discarded "
            "before the same unexpected failure propagates.")
    assert method == "discard"
    assert context(lines, line, after=4) == (
        "} catch (RuntimeException | Error cleanup) {\n"
        "JdbcAdmissionFailures.beforeDiscard(primary, cleanup);\n"
        "if (primary instanceof SQLException) throw cleanup;\n"
        "// Do not add raw provider data or self-suppression. Unknown primary keeps its identity.\n"
        "primary.addSuppressed(unavailable());")
    return "REJECTED_OWNED_CONNECTION", (
        "The connection close cannot preserve an SQL fallback over a new unknown failure. An existing "
        "unknown primary retains identity and carries only the catalogued secondary notice.")


def main():
    primary = next(OPS.glob("PG41314-*/manifest.json"))
    measured = read(primary)
    baseline = next(OPS.glob("PG41316-*/manifest.json"))
    exact = read(baseline)
    assert exact["remaining"] == 49 and exact["exactPriorSites"] == 2
    assert exact["static"] == pin(primary)
    source = {name: git("show", f'{measured["core"]}:{name}').decode().splitlines()
              for name in measured["analyzedSourceSha256"]}
    for path, lines in source.items():
        assert hashlib.sha256(("\n".join(lines) + "\n").encode()).hexdigest() == measured["analyzedSourceSha256"][path]
    jdbc_policy, = [lines for path, lines in source.items() if Path(path).name == "JdbcAdmissionFailures.java"]
    assert "    beforeDiscard(primary, secondary);" in jdbc_policy
    assert "      primary.addSuppressed(" in jdbc_policy
    gson, = [checked(ref) for ref in measured["allowedDependencyPins"] if ref["path"].endswith("gson-2.14.0.jar")]
    assert pin(gson)["sha256"] == GSON
    proof, = OPS.parent.glob("2118_JSON*.md")
    assert GSON in proof.read_text()
    rows = read(checked(exact["sites"]))
    for row in rows:
        if row["state"] == "EXACT_PRIOR_METHOD_AND_SITE":
            continue
        owner = Path(row["path"]).name
        text = source[row["path"]]
        if owner in MIGRATION:
            state, reason = migration(row, text)
        elif owner in JDBC:
            state, reason = jdbc(row, text)
        elif owner == "ServiceDatabaseSource.java":
            state, reason = service_source(row, text)
        elif owner == "ReleaseInventory.java":
            assert row["rule"] == "UnusedReturnValue" and row["method"] == "parse"
            assert "        reader.setStrictness(Strictness.STRICT);" in text
            assert context(text, row["line"]) == "reader.peek();"
            assert context(text, row["line"], before=4).startswith("reader.endObject();")
            state = "STRICT_READER_EOF_VALIDATION"
            reason = "The established Gson STRICT peek validates remaining input after endObject. Its validating effect is required."
        else:
            assert owner in ("ApiNonSecretConfig.java", "WebNonSecretConfig.java")
            continue
        row["state"], row["reason"] = state, reason
    counts = Counter(row["state"] for row in rows)
    assert len(rows) == 51 and counts["UNCLASSIFIED_CURRENT_FLOW"] == 4
    out = OPS / "PG41318-f03-bootstrap-explicit-pmd-flows-v1"
    out.mkdir()
    write(out / "flow-dispositions.json", rows)
    write(out / "manifest.json", dict(
        actualExit=0, source=measured["source"], core=measured["core"], initial=pin(baseline),
        typedStatic=pin(primary), readOnlyReport=pin(out / "flow-dispositions.json"),
        raw=51, classified=47, alreadyExact=2, newExplicitFlowClassifications=45, unclassified=4,
        classifications=counts, strictGsonPrecedent=pin(proof), pinnedReaderSdk=pin(gson),
        productTests=0, heldPhysical=1, applicableDefectConfirmedHere=0,
        suppressionAdded=0, wholeF03=False, whole451=False, formalDelta=0,
        terminalAtUTC=datetime.now(timezone.utc).isoformat()))
    print(counts)


if __name__ == "__main__":
    main()
