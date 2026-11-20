"""Verify and project only the eight checksum signals found in the public interval."""

import io
import json
from pathlib import Path
import re
import runpy


H = runpy.run_path(str(Path(__file__).with_name("5365_g07_public_history_utc42.py")))
OPS, read, git, pin, digest = (H[key] for key in ("OPS", "read", "git", "pin", "digest"))


def main():
    base = next(OPS.glob("PG40466-*/manifest.json"))
    report = read(base)
    assert report["actualExit"] == 1 and report["scans"]["gzipPublicStreams"]["actualExit"] == 0
    trial = report["scans"]["textCommitDiffs"]
    assert trial["rules"] == {"generic-api-key": 8}
    signals = {row["start"] for row in trial["signalLocations"]}
    assert len(signals) == 8 and all(row["start"] == row["end"] for row in trial["signalLocations"])
    result_manifest = next(OPS.glob("PG40444-*/manifest.json"))
    result = read(result_manifest)
    proof = read(next(OPS.glob("PG40446-*/manifest.json")))
    assert proof["run"] == pin(result_manifest) and proof["matchedPhysical"] == 66
    nested, protocol, storage = (read(item["path"]) for item in result["oracleReferences"][3:6])
    saved = {
        **nested["fixtureClassHashes"],
        **{name: sha for module in protocol["inputPhysical"].values() for name, sha in module.items()},
        **{name.removesuffix(".class").replace("/", "."): sha
           for name, sha in storage["fixturePhysicalHashes"].items()},
    }
    assert saved == result["exactInputPhysical"]
    tool_hashes = result["tools"]
    assert all(pin(name)["sha256"] == sha for name, sha in tool_hashes.items())
    original, projected = io.BytesIO(), io.BytesIO()
    proofs = []
    for commit in report["commits"]:
        parent = git("rev-parse", commit + "^").decode().strip()
        for row in git("diff", "--no-renames", "--numstat", "-z", parent, commit).split(b"\0"):
            if not row:
                continue
            a, d, path = row.decode().split("\t", 2)
            if (a, d) == ("-", "-"):
                continue
            patch = git("diff", "--no-ext-diff", "--no-textconv", "--text", "--no-renames",
                        "--unified=0", parent, commit, "--", path)
            header = path + " " + commit
            first, final = H["add"](original, header, patch)
            affected = sorted(i for i in signals if first <= i <= final)
            if affected:
                assert path == str(result_manifest)
                assert digest(git("show", commit + ":" + path)) == pin(result_manifest)["sha256"]
                rows = patch.splitlines(keepends=True)
                for line in affected:
                    m = re.fullmatch(rb'(\+\s*"([^"]+)": ")([a-f0-9]{64})(",?\n)', rows[line-first])
                    assert m is not None
                    key, sha = m[2].decode(), m[3].decode()
                    if key in saved:
                        assert sha == saved[key]
                        class_ = "COMPILED_SYNTHETIC_CLASS_SHA256"
                    else:
                        assert key.endswith("/slf4j-api-2.0.18.jar") and sha == tool_hashes[key]
                        class_ = "PINNED_SLF4J_JAR_SHA256"
                    rows[line-first] = m[1] + class_.encode() + m[4]
                    proofs.append(dict(path=path, scannerLine=line, commit=commit, field=key, verifiedAs=class_))
                patch = b"".join(rows)
            H["add"](projected, header, patch)
    assert digest(original.getvalue()) == trial["sha256"]
    assert {row["scannerLine"] for row in proofs} == signals
    scanner = Path(report["tool"]["path"])
    assert pin(scanner) == report["tool"]
    confirmation = H["scan"](scanner, {"textCommitDiffs": projected})["textCommitDiffs"]
    assert confirmation["actualExit"] == 0 and not confirmation["signalLocations"]
    output = OPS / "PG40468-g07-public-utc42-history-verified-v1"
    output.mkdir()
    record = dict(actualExit=0, source=report["source"], previousCursor=report["previousCursor"],
                  newCursor=report["source"], productionCore=report["productionCore"], first=pin(base),
                  firstSignals=8, verifiedChecksumSignals=proofs, textVersions=sum(report["textPathVersions"].values()),
                  distinctTextPaths=len(report["textPathVersions"]), gzipCount=len(report["gzipVersions"]),
                  binaryMetadataOnly=len(report["binaryMetadataOnly"]), eligibleCommits=len(report["commits"]),
                  fullTextProjectionScan=confirmation, otherStreamsNotReplayed=True, rawSecretsStored=0,
                  secretFindings=0, wholeG07Accepted=False, whole451Accepted=False,
                  terminalAtUTC=H["H"]["datetime"].now(H["H"]["timezone"].utc).isoformat())
    output = output / "manifest.json"
    with output.open("x") as handle:
        json.dump(record, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(pin(output))


if __name__ == "__main__":
    main()
