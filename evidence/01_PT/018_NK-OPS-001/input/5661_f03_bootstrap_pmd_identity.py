"""Reconcile exact current PMD sites without inheriting reports across changed method bodies."""

from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import re
import runpy
from xml.etree import ElementTree as XML


H = runpy.run_path(str(Path(__file__).with_name("5660_f03_bootstrap_static_delta.py")))
OPS, NS, read, pin, checked, write, git = (H[n] for n in ("OPS", "NS", "read", "pin", "checked", "write", "git"))


def method_region(source, name, line):
    """Select only a normal two-space Java declaration whose closing brace is unambiguous."""
    if not name:
        return None
    header = re.compile(r"^  (?:public |private |protected |static |final ).*\b" + re.escape(name) + r"\(")
    for index in range(line - 1, -1, -1):
        if header.match(source[index]):
            for end in range(index + 1, len(source)):
                if source[end] == "  }":
                    if index <= line - 1 <= end:
                        return "\n".join(source[index:end + 1])
                    break
    return None


def main():
    new_path = next(OPS.glob("PG41314-*/manifest.json"))
    new = read(new_path)
    prior = next(OPS.glob("PG37092-*/manifest.json"))
    qualified = read(prior)
    assert qualified["finalNotApplicable"] == 922 and qualified["unclassified"] == 49
    assert not any(new["spotbugsCounters"].values())
    raw = checked(new["pmd"])
    root = XML.parse(raw).getroot()
    names = {Path(path).name: path for path in new["analyzedSourceSha256"]}
    assert len(names) == 11
    source = {path: git("show", f'{new["core"]}:{path}').decode().splitlines() for path in names.values()}
    before = {path: git("show", f'{qualified["sourceCore"]}:{path}').decode().splitlines()
              for path in names.values() if not path.endswith("/JdbcFailureGraph.java")}
    records = prior.with_name("all-current-dispositions.json")
    assert pin(records)["sha256"] in str(qualified["dispositions"])
    previous = defaultdict(list)
    for entry in read(records):
        file, method = entry.get("path"), entry.get("method")
        if file not in before or not method or entry.get("column") is None:
            continue
        line = int(entry["line"])
        assert entry["decision"].startswith("NOT_APPLICABLE") and entry["reason"]
        snapshot = before[file]
        block = method_region(snapshot, method, line)
        if block is not None:
            key = (file, method, entry["rule"], snapshot[line - 1].strip(), block)
            previous[key].append(entry)
    findings = []
    for item in root.findall("p:file", NS):
        path = names[Path(item.attrib["name"]).name]
        for row in item.findall("p:violation", NS):
            line = int(row.attrib["beginline"])
            rule, method = row.attrib["rule"], row.attrib.get("method", "")
            current_source = source[path]
            region = method_region(current_source, method, line)
            text = current_source[line - 1].strip()
            key = (path, method, rule, text, region)
            compared = previous[key]
            match = None
            if region is not None:
                current_column = row.attrib["begincolumn"]
                candidates = [value for value in compared if str(value["column"]) == current_column]
                if len(candidates) == 1:
                    match = candidates[0]
                    compared.remove(match)
            if match:
                state = "EXACT_PRIOR_METHOD_AND_SITE"
                reason = match["reason"]
            else:
                state = "UNCLASSIFIED_CURRENT_FLOW"
                reason = "Needs an applicable current statement and enclosing contract review."
            findings.append(dict(path=path, method=method, line=line, rule=rule,
                beginColumn=int(row.attrib["begincolumn"]), state=state, reason=reason,
                matchedPriorIndex=match["rawFindingIndex"] if match else None,
                methodSha256=hashlib.sha256(region.encode()).hexdigest() if region else None))
    assert len(findings) == len(new["rawPmd"]) == 51
    origin = [r["matchedPriorIndex"] for r in findings if r["matchedPriorIndex"] is not None]
    assert len(origin) == len(set(origin))
    states = Counter(item["state"] for item in findings)
    out = OPS / "PG41316-f03-bootstrap-pmd-site-reconcile-v1"
    out.mkdir()
    write(out / "site-dispositions.json", findings)
    write(out / "manifest.json", dict(
        actualExit=0, source=new["source"], core=new["core"], static=pin(new_path),
        originalPmdDispositions=pin(records), sites=pin(out / "site-dispositions.json"), rawPmd=51,
        exactPriorSites=states["EXACT_PRIOR_METHOD_AND_SITE"], remaining=states["UNCLASSIFIED_CURRENT_FLOW"],
        staticallyHeldPhysical=1, completeF03=False, whole451=False, newFormalAcceptance=0,
        pmdRerun=0, productTests=0, terminalAtUTC=datetime.now(timezone.utc).isoformat()))
    print(states)


if __name__ == "__main__":
    main()
