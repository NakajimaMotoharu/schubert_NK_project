"""Connect verified media and comparison-tool evidence to the original WBS66 rows."""

from pathlib import Path
import runpy
import sys
from datetime import datetime, timezone
import json


H = runpy.run_path(str(Path(__file__).with_name("5641_g08_current_short_trace.py")))
DOCS, OPS, MEDIA, OPERATIONS = (H[k] for k in ("DOCS", "OPS", "MEDIA", "OPERATIONS"))
pin, named, read, git = (H[k] for k in ("pin", "named", "json_file", "git"))
CHR = OPERATIONS.parent / "020_NK-CHR-001"
RUN = "PG41284-g08-media-compare-current-v1"
KEY = "currentMediaAndComparatorPG41284"


def attach(path, name, body):
    old = path.read_text()
    assert name not in json.loads(old)
    assert old.endswith("\n}\n")
    extra = json.dumps({name: body}, ensure_ascii=False, indent=2)
    path.write_text(old[:-3] + "," + extra[1:-1] + "}\n")


def main(mode):
    out = OPS / RUN
    if mode == "verify":
        ctx = read(named(DOCS, "601_*/1685_*.json"))["values"]
        refs = [Path(row["path"]) for row in ctx["oracleReferences"]]
        assert [pin(path) for path in refs] == ctx["oracleReferences"]
        media, scan, disposition, admission, chr_raw = refs[1:]
        m, s, d, a, c = map(read, (media, scan, disposition, admission, chr_raw))
        assert m["source"] == s["source"] == d["source"] == c["productionCore"] == ctx["productionCoreMain"]
        assert all(v["missed"] == 0 for v in m["wholeRaw"].values())
        assert s["matchingMainToRawUnit"] == 13 and s["stages"]["nullaway"]["exit"] == 0
        assert d["applicableFindings"] == d["unclassified"] == 0 and d["publicDescriptorEqual"]
        assert a["state"] == "CURRENT_ADMISSION_NOT_ESTABLISHED_NO_TRANSFER"
        assert a["terminal"] is None and not a["capsuleTransferred"]
        assert c["testCounts"] == dict(tests=216, failures=0, errors=0, skipped=0)
        assert c["suites"] == 20 and c["crcVerified"] == 12 and c["physicallyVerified"] == 17
        assert c["notRunOutsideSelectedScope"] == c["rawCounters"]["BRANCH"]["missed"] == 1
        assert a["source"] == c["packageSource"]
        assert not git("diff", "--name-only", c["packageSource"], c["testedSource"],
                       "--", "program/characterization", "pom.xml")
        wbs = named(Path("../PMO/hourly-monitor/wbs66-20261116"), "58_*/WBS.tsv")
        data = wbs.read_text().splitlines()
        media_spec = named(MEDIA, "4101_*")
        chr_spec = named(CHR, "060_比較*")
        specs = [
            (392, "WBS-P009-04/2", media_spec, ("PT-MED-FAILURE-NAME-001",), (media,)),
            (1004, "WBS-F03/2-2", media_spec, (), (scan, disposition)),
            (816, "WBS-P020-01.02/2", chr_spec, ("PT-CHR-DEF077", "PT-CHR-DEF078"), (chr_raw,)),
            (1007, "WBS-F04-条件対応", named(CHR, "062_現包装*"), (), (admission,)),
        ]
        rows = []
        for number, task, spec, test_ids, evidence in specs:
            fields = data[number - 1].split("\t")
            assert fields[0] == task
            assert all(test_id in spec.read_text() for test_id in test_ids)
            rows.append(dict(workId=task, row=number, originalPricePp=float(fields[6]),
                             originalDescription=fields[5], aliases=[], testIds=test_ids,
                             specification=pin(spec), evidence=list(map(pin, evidence)),
                             formalDelta=0))
        assert git("rev-parse", "origin/main").decode().strip() == ctx["canonicalDesignSource"]
        out.mkdir()
        result = dict(actualExit=0, source=ctx["source"], productionCore=ctx["productionCoreMain"],
                      canonicalDesign=ctx["canonicalDesignSource"], wbs=pin(wbs), bindings=rows,
                      observedMediaPhysical=13, comparatorPhysical=2, localToolTests=216,
                      ownedFileStoreUnstarted=1, formalDelta=0, wholeG08=False, whole451=False,
                      originalRowPriceRecorded=0, terminalAtUTC=datetime.now(timezone.utc).isoformat())
        with (out / "manifest.json").open("x") as stream:
            json.dump(result, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        print(pin(out / "manifest.json"))
    elif mode == "bind":
        manifest = out / "manifest.json"
        result = read(manifest)
        inventory = named(DOCS, "485_*.json")
        status = named(DOCS, "486_*.json")
        before = pin(inventory)["sha256"]
        old_status = status.read_text()
        assert read(status)["inventorySha256"] == before and KEY not in read(status)
        value = dict(productionCore=result["productionCore"], verification=pin(manifest),
                     bindings=result["bindings"], acceptedOriginalDelta=0, complete451=False)
        attach(inventory, KEY, value)
        attach(status, KEY, value)
        after = pin(inventory)["sha256"]
        old = f'"inventorySha256": "{before}"'
        state = status.read_text()
        assert old_status.count(old) == state.count(old) == 1
        status.write_text(state.replace(old, f'"inventorySha256": "{after}"', 1))
    else:
        raise SystemExit("Use verify or bind")


if __name__ == "__main__":
    main(sys.argv[1])
