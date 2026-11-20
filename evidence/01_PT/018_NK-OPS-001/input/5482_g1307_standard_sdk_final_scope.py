"""Join existing SDK owner and consumer receipts without rerunning product tests."""
import json
import subprocess
from collections import Counter
from hashlib import sha256
from pathlib import Path


def digest(data):
    return sha256(data).hexdigest()


def pin(path):
    return dict(path=str(path), sha256=digest(path.read_bytes()))


def add(raw, key, value):
    assert raw.endswith(b"\n}\n")
    addition = json.dumps({key: value}, ensure_ascii=False, indent=2).encode()
    updated = raw[:-3] + b",\n" + addition[2:-2] + b"\n}\n"
    parsed = json.loads(updated)
    assert parsed.pop(key) == value and parsed == json.loads(raw)
    return updated


pmo = Path("documents/400_PGPT/470_PMO")
group = json.loads(next(pmo.glob("601_*/1325_*")).read_bytes())
ctx = group["values"]
core = ctx["productionCoreMain"]
heads = subprocess.check_output(
    ["git", "rev-parse", "HEAD", "origin/dev-foundation"], text=True, timeout=10)
assert heads.splitlines() == [ctx["source"]] * 2
pins = ctx["oracleReferences"]
assert all(pin(Path(row["path"])) == row for row in pins)
unit, raw, assembly, consumers, text, typed = [
    json.loads(Path(row["path"]).read_bytes()) for row in pins[1:]]
assert all(d["source"] == core for d in [unit, assembly, consumers, text])
assert raw["currentCore"] == typed["core"] == core
assert all(d["actualExit"] == 0 for d in [raw, assembly, consumers, text, typed])
assert unit["productBuildByteMatched"] and unit["steps"]["unit"]["exit"] == 0
assert unit["steps"]["unfiltered"]["exit"] == 1 and unit["actualExit"] == 1
assert raw["before"] == pins[1] and raw["actualProductReruns"] == 0
cases = unit["tests"]
assert len({(t["classname"], t["method"]) for t in cases}) == len(cases) == 51
assert all(t["outcome"] == "passed" for t in cases)
assert sorted(Counter(t["classname"] for t in cases).values()) == [17, 17, 17]
assert all(sum(t["method"].startswith(prefix + "017") for t in cases) == 1
           for prefix in ("apihost", "batchhost", "webhost"))
for receipt, count in [(consumers, 66), (text, 37)]:
    assert len(receipt["observedCases"]) == receipt["expectedCaseCount"] == count
    assert all(t["outcome"] == "passed" for t in receipt["observedCases"])

typed_by_name = {binary: row["classSha256"] for binary, row in typed["exactTargetByteJoins"].items()}
selected_by_name = {Path(row["path"]).name: row["sha256"] for row in raw["chosenClassFiles"]}
assert selected_by_name == {Path(binary).name: sha for binary, sha in typed_by_name.items()}
batch = assembly["approvedSingleClassComparison"]
assert batch["matchesIndependentTypedAndScopedPt"] and batch["sha256"] == typed_by_name[batch["classPath"]]
totals = Counter()
for row in raw["measuredClasses"]:
    assert row["className"] + ".class" in typed_by_name
    for name, counter in row["counters"].items():
        assert counter["missed"] == 0
        totals[name] += counter["covered"]
assert all(totals[k] == v for k, v in dict(LINE=138, METHOD=27, CLASS=3, BRANCH=58, INSTRUCTION=651).items())
index = next(pmo.glob("485_WBS*"))
acceptance = next(pmo.glob("486_WBS*"))
before, acceptance_before = index.read_bytes(), acceptance.read_bytes()
prior = json.loads(before)["currentStandardSdkOwnerAndCleanupQueryTracePG40884"]["rows"]
ids = [row["testId"] for row in prior if row["owner"] == "WBS-P018-09"]
assert set(ids) == {"APIHOST017", "BATCHHOST017", "WEBHOST017"}
entry = dict(
    source=core, wbs="WBS-G13.07", productOwner="WBS-P018-09", reusedOriginalTestIds=ids,
    sameExecUnit=51, exactRawClasses=raw["measuredClasses"], exactRawCovered=dict(totals),
    consumerApiWebSeparateRun=66, consumerBatchSeparateRun=37, receipts=pins[1:],
    newExecutions=0, arithmeticRunMerges=0, whole451=False, formalDelta=0, addedPricePp=0)
key = "currentStandardSdkSameRunTracePG40910"
new = add(before, key, entry)
old_hash = digest(before)
assert json.loads(acceptance_before)["inventorySha256"] == old_hash
assert acceptance_before.count(old_hash.encode()) == 1
new_acceptance = add(acceptance_before.replace(old_hash.encode(), digest(new).encode()), key, entry)
assert json.loads(new_acceptance)["inventorySha256"] == digest(new)
out = Path(pins[1]["path"]).parent.parent / ctx["run"]
out.mkdir()
index.write_bytes(new)
acceptance.write_bytes(new_acceptance)
manifest = out / "manifest.json"
manifest.write_text(json.dumps(dict(actualExit=0, startEvent=group["eventId"], trace=entry,
                                    inventory=pin(index), acceptance=pin(acceptance)),
                               ensure_ascii=False, indent=2) + "\n")
