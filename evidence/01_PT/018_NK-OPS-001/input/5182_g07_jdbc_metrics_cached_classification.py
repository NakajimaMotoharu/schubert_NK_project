"""Join scanner coordinates and independently qualified origins without rereading large blobs per hit."""
from collections import Counter
from datetime import datetime, timezone
from functools import lru_cache
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import re

S = spec_from_file_location("exact_origins", Path(__file__).with_name("5181_g07_jdbc_metrics_exact_origins.py"))
t = module_from_spec(S)
S.loader.exec_module(t)
OUT, WORK = t.OUT, t.WORK
B = t.BIND
TOKEN = re.compile(rb"(?<![0-9a-f])([0-9a-f]{40}|[0-9a-f]{64})(?![0-9a-f])")


@lru_cache(maxsize=32)
def projection_lines(file, expected_sha):
    data = file.read_bytes()
    assert B.sha(data) == expected_sha
    return data.splitlines()


def exact_previous():
    before = t.PRIOR / "origins-pass2.json"
    m = B.load(before)
    assert m["resultQualifiedForRange"] and m["confirmedSecrets"] == m["unresolvedCandidates"] == 0
    witnesses = [Path(m["findings"]["path"]), Path(m["additionalOrigins"]["path"])]
    assert [B.ref(p) for p in witnesses] == [m["findings"],m["additionalOrigins"]]
    known = set()
    for p in witnesses:
        for row in B.load(p):
            if row["ground"] is not None:
                known.add((row["rule"], row["lineSha256"], row["startColumn"], row["endColumn"]))
    return known, B.ref(before)


def proven_content(line, a, z, digests, reachable):
    candidates = [token for token in TOKEN.finditer(line)
                  if max(0,min(token.end(1),z+1)-max(token.start(1),a-2)) >= len(token[1])-1]
    if len(candidates) != 1:
        return None
    candidate = candidates[0][1]
    origin = digests.get(candidate)
    if origin:
        return dict(kind="Exact published file digest at scanner coordinate",origin=origin)
    if candidate in reachable:
        return dict(kind="Reachable Git object identity at scanner coordinate")
    return None


def main():
    p = OUT / "scan-terminal.json"
    scan = B.load(p)
    head = scan["throughCommit"]
    rows = B.load(WORK/"projection.json")
    assert B.ref(WORK/"projection.json")["sha256"]==scan["projectionSha256"]
    assert B.ref(WORK/"scanner-redacted.json")["sha256"]==scan["reportSha256"]
    assert B.ref(t.WRAPPER.RETAIN/"projection.json")["sha256"]==scan["projectionSha256"]
    assert B.ref(t.WRAPPER.RETAIN/"scanner-redacted.json")["sha256"]==scan["reportSha256"]
    raws=B.load(WORK/"scanner-redacted.json")
    by_key={(r["path"],r["blobOid"]):r for r in rows}
    digests={}
    for row in rows:
        if row["treatment"] in ("text","binary"):
            for k in ("blobSha256","decodedSha256"):
                digests[row[k].encode()]={"path":row["path"],"blob":row["blobOid"]}
    reachable=set(B.git("rev-list","--objects","--no-object-names",head,"origin/main").splitlines())
    previous,pref=exact_previous()
    prior, prior_index=t.prior_index()
    actual_cls=t.prepare_index()
    receipts=[]
    pending=[]
    counts=Counter()
    assert len(raws)==scan["findingsCount"]==len(scan["findings"])
    for i,(raw,hit) in enumerate(zip(raws,scan["findings"],strict=True),1):
        item=by_key[hit["path"],hit["blob"]]
        assert item["treatment"]=="text"
        assert Path(raw["File"])==WORK/item["relativeProjection"]
        assert raw["StartLine"]==hit["line"] and raw["RuleID"]==hit["rule"]
        line=projection_lines(WORK/item["relativeProjection"],item["decodedSha256"])[hit["line"]-1]
        assert B.sha(line)==hit["lineSha256"]
        a,z=raw["StartColumn"],raw["EndColumn"]
        decision=None
        if (hit["rule"],hit["lineSha256"],a,z) in previous:
            decision=dict(kind="Exact prior adjudicated line and scanner coordinate",prior=pref)
        if not decision:
            decision=proven_content(line,a,z,digests,reachable)
        if not decision:
            literal=t.FIELD.fullmatch(line)
            if literal and max(literal.start(2),a-1)<min(literal.end(2),z):
                key,value=(arg.decode() for arg in literal.groups())
                location=Path(hit["path"])
                if hit["rule"]=="generic-api-key":
                    decision=t.checked_source(key,value,head) or actual_cls.get((key,value)) or t.checked_run_id(location,key,value)
                if hit["rule"]=="sourcegraph-access-token":
                    decision=t.checked_prior(location,key,value,prior,prior_index)
        row=dict(hit,ground=decision,findingIndex=i,startColumn=a,endColumn=z)
        receipts.append(row)
        if decision:
            counts[decision["kind"]]+=1
        else:
            pending.append(row)
    assert sum(counts.values())+len(pending)==scan["findingsCount"]
    original_binary=t.WRAPPER.load_stage("ground").binary_evidence(rows,head)
    supplemental=t.extra_binary(original_binary,by_key,scan)
    value_by_path={(r["path"],r["blob"]):r for r in supplemental}
    combined=[value_by_path.get((r["path"],r["blob"]),r) for r in original_binary]
    assert len(combined)==scan["binary"]
    unqualified=sum(r.get("actualExit")!=0 for r in combined)
    terminal=OUT/"classified-findings.json"
    unresolved=OUT/"remaining-origins.json"
    binaries=OUT/"binary-qualification.json"
    B.write(terminal,receipts)
    B.write(unresolved,pending)
    B.write(binaries,combined)
    value=dict(actualExit=0,toCommit=head,source=head,fromCommit=scan["fromCommit"],throughCommit=head,
        commits=scan["commits"],trackedBlobVersions=scan["trackedBlobVersions"],text=scan["text"],binary=scan["binary"],
        expandedGzip=scan["expandedGzip"],heldMetadataOnly=scan["heldMetadataOnly"],
        findingsCount=scan["findingsCount"],actualScannerExit=scan["actualScannerExit"],categories=dict(counts),
        unresolvedCandidates=len(pending),confirmedSecrets=None if pending else 0,unqualifiedBinary=unqualified,
        scan=B.ref(p),findings=B.ref(terminal),unclassified=B.ref(unresolved),binaryProof=B.ref(binaries),
        scannerInputTemporaryOnly=True,rawNotExported=True,sourceReplays=0,productTests=0,
        resultQualifiedForRange=not pending and not unqualified,wholeG07Accepted=False,
        terminalAtUTC=datetime.now(timezone.utc).isoformat())
    B.write(OUT/"qualified-cached-initial.json",value)
    print(dict(counts=dict(counts),pending=len(pending),unqualifiedBinary=unqualified,
        pendingTypes=Counter((Path(row["path"]).name,row["rule"]) for row in pending)))


if __name__=="__main__":
    main()
