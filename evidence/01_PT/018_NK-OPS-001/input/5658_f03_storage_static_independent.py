"""Independently check the exact Storage byte census and raw static report scope."""

from datetime import datetime, timezone
import gzip
import hashlib
from pathlib import Path
import runpy
from xml.etree import ElementTree as XML
from zipfile import ZipFile


H = runpy.run_path(str(Path(__file__).with_name("5657_f03_storage_exact_static.py")))
OPS, ROOT, pin, checked, read, write, git = (H[n] for n in
    ("OPS", "ROOT", "pin", "checked", "read", "write", "git"))


def main():
    witness = next(OPS.glob("PG41310-*/manifest.json"))
    current = read(witness)
    assert current["actualExit"] == 0 and current["currentMain"] == 25
    old = read(checked(current["oldPmdAndSpotbugs"]))
    old_compile = read(checked(current["oldInputCompiled"]))
    pmd_records = witness.parent / "pmd.xml"
    spot_report = witness.parent / "spotbugs.xml"
    dispositions = checked(current["oldPmdAndSpotbugs"]).with_name("pmd18-site-dispositions.json")
    entries = read(dispositions)
    assert len(entries) == old["pmdRaw"] == 18
    for item in entries:
        file = item["raw"]["path"]
        assert item["disposition"] == "NOT_APPLICABLE"
        assert "ResourceScope.java" == Path(file).name
        assert current["currentMainSha"][file] == item["sourceSha256"] == old_compile["inputHashes"][file]
        assert item["reason"] and item["currentContract"]
    assert current["inputCore"] == "e7bfd5e1f2ec4b4e16ecf32601bed052b5330461"
    assert git("rev-parse", "HEAD").decode().strip() == current["source"]
    assert not git("diff", "--name-only", current["inputCore"], current["core"],
                   "--", "pom.xml", "src/schubert-nk-storage/pom.xml", "src/schubert-nk-storage/src/main")
    current_package = read(next(OPS.glob("PG40498-*/manifest.json")))
    compile_log = checked(current_package["recoveredCompileTerminal"]["compile"]["log"])
    with gzip.open(compile_log, "rt") as stream:
        log = stream.read()
    assert "Building Schubert NK Storage" in log and "BUILD SUCCESS" in log
    assert "-Xep:NullAway:ERROR" in (ROOT / "pom.xml").read_text()
    observed_names = {row.attrib["class"] for row in XML.parse(spot_report).findall(".//ClassStats")}
    expected_names = {name.removesuffix(".class").replace("/", ".") for name in current["changedClassBytes"]}
    assert expected_names == observed_names and len(observed_names) == 5
    assert not current["rawPmd"] and not any(current["spotbugs"].values())
    assert not XML.parse(pmd_records).findall(".//{*}violation")
    with ZipFile(checked(current["currentJar"])) as jar:
        newer = {name: hashlib.sha256(jar.read(name)).hexdigest() for name in jar.namelist()
                 if name.endswith(".class")}
    historical = old_compile["physicalClassHashes"]
    same = {name for name, value in newer.items() if historical.get(name) == value}
    assert len(newer) == 79 and len(same) == 74
    assert set(newer) - same == set(current["changedClassBytes"])
    assert set(historical) - set(newer) == set(current["retiredGenerated"])
    out = OPS / "PG41312-f03-storage-static-independent-v1"
    out.mkdir()
    write(out / "current-class-sha256.json", newer)
    write(out / "manifest.json", dict(
        actualExit=0, source=current["source"], core=current["core"], currentJar=current["currentJar"],
        oldStaticFingerprint=pin(checked(current["oldPmdAndSpotbugs"])), currentStatic=pin(witness),
        historicalPmdDispositions=pin(dispositions), sourceAndReasonUnchangedPmdSites=18,
        currentChangedPhysicalClassStats=len(observed_names), exactUnchangedPhysical=len(same),
        totalCurrentPhysical=len(newer), totalMainFiles=25, retiredGenerated=len(current["retiredGenerated"]),
        currentPmdRaw=0, currentCheckstyle=0, currentSpotbugs=0, productTestsRerun=0,
        priorCompileSucceeded=pin(compile_log), sameRootStorageCompileConfig=True,
        noOldExecMerged=True, wholeCoverage=False, wholeF03=False, whole451=False, formalDelta=0,
        rawSpotbugs=pin(spot_report), rawPmd=pin(pmd_records),
        currentPhysicalFingerprint=pin(out / "current-class-sha256.json"),
        terminalAtUTC=datetime.now(timezone.utc).isoformat()))
    print(79, 74, 5, 18, 0)


if __name__ == "__main__":
    main()
