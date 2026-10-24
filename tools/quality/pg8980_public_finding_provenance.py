"""Classify only exact rule capture equal to proven public blob digest; never rerun scanner."""
from collections import Counter
import datetime as dt
import json
from pathlib import Path
import re
from host_tool_invocation import capture,verify
from public_blob_scan import sha
from public_finding_provenance import classify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
SCAN=BASE/'PG8968-public-blob-scan-v1'
PROVENANCE=BASE/'PG8979-gitleaks-rule-provenance-v1/manifest.json'
SNAPSHOT=ROOT.parent/'pgpt-runs/PG379/pg8968-public-blob-scan-v1/tracked'
OUT=BASE/'PG8980-public-finding-provenance-v1'


def main():
    invocation=capture(Path(__file__))
    assert not OUT.exists()
    provenance=json.loads(PROVENANCE.read_bytes())
    assert provenance['actualExit']==0
    config=Path(provenance['path']);assert sha(config.read_bytes())==provenance['configSha256']=='e163e53b9e7e8a8511e77271e2b323ed057759542a6d988258afe3a1fa329caf'
    rules=provenance['rules']
    # Independent fixture values are derived locally, never a live credential or serialized candidate.
    public_digest=sha(b'G07-INDEPENDENT-PUBLIC-FIXTURE')
    unknown_digest=sha(b'G07-UNKNOWN-NOT-PROVEN')
    proof=dict(path='fixture/public.txt',sha256=public_digest)
    known={public_digest:proof}
    rule=rules['generic-api-key']
    cases=[('public-exact','api_key = "'+public_digest+'"\n',1,1,'FALSE_POSITIVE_PUBLIC_BLOB_SHA256'),
           ('unknown-same-shape','api_key = "'+unknown_digest+'"\n',1,1,'UNCLASSIFIED'),
           ('nearby-public-not-match','api_key = "'+unknown_digest+'"; plain = "'+public_digest+'"\n',1,1,'UNCLASSIFIED'),
           ('two-different-captures','api_key = "'+public_digest+'"; secret = "'+unknown_digest+'"\n',1,1,'UNCLASSIFIED'),
           ('outside-range','safe documentation\napi_key = "'+public_digest+'"\n',1,1,'UNCLASSIFIED'),
           ('safe-no-key','plain = "'+public_digest+'"\n',1,1,'UNCLASSIFIED')]
    for _,text,first,end,expected in cases:
        actual=classify(text,rule,first,end,known)
        assert actual['disposition']==expected
        if expected=='UNCLASSIFIED':
            assert public_digest not in json.dumps(actual) and unknown_digest not in json.dumps(actual)
    negatives=[]
    for name,first,end in [('zero',0,1),('bool',True,1),('reversed',2,1),('past-eof',1,2)]:
        try:classify('safe\n',rule,first,end,known)
        except ValueError:negatives.append(name)
        else:raise AssertionError('invalid range accepted')
    scan=json.loads((SCAN/'manifest.json').read_bytes())
    assert scan['actualExit']==0 and scan['source']=='fb9fce0f91de3d9fdfa634fe277592700f915e45'
    assert sha((SCAN/'inventory.json').read_bytes())==scan['inventorySha256']
    assert sha((SCAN/'findings.json').read_bytes())==scan['findingsSha256']
    inventory=json.loads((SCAN/'inventory.json').read_bytes())['rows']
    public_hashes={}
    for row in sorted(inventory,key=lambda row:row['path']):
        public_hashes.setdefault(row['sha256'],dict(path=row['path'],sha256=row['sha256'],gitObject=row['gitObject']))
    rows=[];current=None;text='';dispositions=Counter();reasons=Counter()
    for finding in sorted(json.loads((SCAN/'findings.json').read_bytes()),key=lambda row:(row['path'],row['startLine'],row['ruleId'])):
        if current!=finding['path']:
            data=(SNAPSHOT/finding['path']).read_bytes();assert sha(data)==finding['inputSha256']
            text=data.decode('utf-8');current=finding['path']
        result=classify(text,rules[finding['ruleId']],finding['startLine'],finding['endLine'],public_hashes)
        dispositions[result['disposition']]+=1;reasons[result['reason']]+=1
        rows.append(dict(**finding,**result))
    vendor_limited=[]
    for row in inventory:
        matches=[index for index,pattern in enumerate(provenance['globalAllowlist']['paths']) if re.search(pattern,row['path'],re.ASCII)]
        if matches:vendor_limited.append(dict(path=row['path'],ruleIndexes=matches,reason='DEFAULT_VENDOR_PATH_ALLOWLIST_NOT_CONTENT_PASS'))
    assert len(rows)==scan['findings']==40086
    verify(invocation);OUT.mkdir()
    for name,value in [('classifications.json',rows),('vendor-path-limits.json',vendor_limited)]:
        with (OUT/name).open('x',encoding='utf-8') as stream:
            json.dump(value,stream,ensure_ascii=False,sort_keys=True,indent=2);stream.write('\n')
    value=dict(actualExit=0,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
       source=scan['source'],contentCommit=scan['contentCommit'],scanManifestSha256=sha((SCAN/'manifest.json').read_bytes()),
       ruleProvenanceSha256=sha(PROVENANCE.read_bytes()),configSha256=provenance['configSha256'],
       classificationSha256=sha((OUT/'classifications.json').read_bytes()),vendorPathLimitsSha256=sha((OUT/'vendor-path-limits.json').read_bytes()),
       findings=len(rows),dispositions=dict(dispositions),reasons=dict(reasons),vendorPathLimitedCount=len(vendor_limited),
       syntheticGoldenCases=[row[0] for row in cases],rejectedRanges=negatives,
       originalFindingsPreserved=True,scannerRerun=False,ruleOrIgnoreModified=False,
       rawCandidatesOrStandaloneCandidateHashPersisted=False,liveSecretsConfirmed=None,
       productTestsExecuted=0,productCoverage=None,whole451SecretGateAccepted=False,formalUpdated=False,newAccepted=0)
    with (OUT/'manifest.json').open('x',encoding='utf-8') as stream:
        json.dump(value,stream,ensure_ascii=False,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps({key:value[key] for key in ('actualExit','findings','dispositions','reasons','vendorPathLimitedCount')}))


if __name__=='__main__':main()
