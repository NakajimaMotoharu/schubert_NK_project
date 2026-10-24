"""Independent exact capture/file-byte proof for every waived finding, no full scanner rerun."""
from collections import Counter
import copy
import datetime as dt
import json
from pathlib import Path
import re
from host_tool_invocation import capture,verify
from public_blob_scan import sha

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
SCAN=BASE/'PG8968-public-blob-scan-v1'
RAW=BASE/'PG8980-public-finding-provenance-v1'
PROVENANCE=BASE/'PG8979-gitleaks-rule-provenance-v1/manifest.json'
SNAPSHOT=ROOT.parent/'pgpt-runs/PG379/pg8968-public-blob-scan-v1/tracked'
OUT=BASE/'PG8982-public-finding-provenance-post-v1'


def check(row, original, input_bytes, proof_bytes, rule):
    if any(row.get(key)!=original[key] for key in ('ruleId','path','startLine','endLine','inputSha256')):
        raise ValueError('original finding changed')
    if sha(input_bytes)!=row['inputSha256']:
        raise ValueError('public input changed')
    if row['disposition']!='FALSE_POSITIVE_PUBLIC_BLOB_SHA256':
        raise ValueError('not a classified false positive')
    if sha(proof_bytes)!=row['publicArtifactProof']['sha256']:
        raise ValueError('actual public proof bytes mismatch')
    lines=input_bytes.decode('utf-8').splitlines(keepends=True)
    low=max(0,row['startLine']-2)
    window=''.join(lines[low:min(len(lines),row['endLine']+1)])
    matched=[]
    for candidate in re.compile(rule['regex'],re.ASCII).finditer(window):
        first=low+window.count('\n',0,candidate.start(1))+1
        last=low+window.count('\n',0,candidate.end(1))+1
        if row['startLine']<=first<=last<=row['endLine']:
            matched.append(candidate.group(1))
    if set(matched)!={sha(proof_bytes)}:
        raise ValueError('actual capture not exactly public proof digest')
    if set(row)!=set(original)|{'disposition','reason','publicArtifactProof'}:
        raise ValueError('unknown field in public false-positive record')


def main():
    invocation=capture(Path(__file__));assert not OUT.exists()
    manifest=json.loads((RAW/'manifest.json').read_bytes())
    assert manifest['actualExit']==0 and manifest['source']=='fb9fce0f91de3d9fdfa634fe277592700f915e45'
    assert sha((RAW/'classifications.json').read_bytes())==manifest['classificationSha256']
    assert sha((RAW/'vendor-path-limits.json').read_bytes())==manifest['vendorPathLimitsSha256']
    provenance=json.loads(PROVENANCE.read_bytes())
    assert sha(PROVENANCE.read_bytes())==manifest['ruleProvenanceSha256']
    assert manifest['configSha256']==provenance['configSha256']=='e163e53b9e7e8a8511e77271e2b323ed057759542a6d988258afe3a1fa329caf'
    originals=json.loads((SCAN/'findings.json').read_bytes())
    original_keys=Counter(tuple(row[key] for key in ('path','ruleId','startLine','endLine','inputSha256')) for row in originals)
    rows=json.loads((RAW/'classifications.json').read_bytes())
    assert original_keys==Counter(tuple(row[key] for key in ('path','ruleId','startLine','endLine','inputSha256')) for row in rows)
    inventory={row['path']:row for row in json.loads((SCAN/'inventory.json').read_bytes())['rows']}
    cache={};golden=None;counts=Counter()
    for row in rows:
        counts[row['disposition']]+=1
        if row['disposition']=='UNCLASSIFIED':
            assert set(row)=={'path','ruleId','startLine','endLine','inputSha256','disposition','reason'}
            continue
        assert row['disposition']=='FALSE_POSITIVE_PUBLIC_BLOB_SHA256'
        if row['path'] not in cache:
            cache[row['path']]=(SNAPSHOT/row['path']).read_bytes()
        proof=row['publicArtifactProof'];binding=inventory[proof['path']]
        assert proof['sha256']==binding['sha256'] and proof['gitObject']==binding['gitObject']
        proof_bytes=(SNAPSHOT/proof['path']).read_bytes()
        original={key:row[key] for key in ('path','ruleId','startLine','endLine','inputSha256')}
        rule=provenance['rules'][row['ruleId']]
        check(row,original,cache[row['path']],proof_bytes,rule)
        if golden is None:golden=(row,original,cache[row['path']],proof_bytes,rule)
    assert dict(counts)==manifest['dispositions'] and sum(counts.values())==len(originals)==40086
    assert golden is not None
    rejected=[]
    for name,changes in [('wrong-input-hash',{'inputSha256':'0'*64}),('wrong-rule',{'ruleId':'linear-client-secret'}),
                         ('outside-finding',{'startLine':0}),('extra-sensitive-field',{'Secret':'DO_NOT_PUBLISH'})]:
        row,original,data,proof_bytes,rule=golden
        altered=copy.deepcopy(row);altered.update(changes)
        try:check(altered,original,data,proof_bytes,rule)
        except ValueError:rejected.append(name)
        else:raise AssertionError('invalid evidence accepted')
    row,original,data,proof_bytes,rule=golden
    try:check(row,original,data,b'NOT-THE-PUBLIC-PROOF',rule)
    except ValueError:rejected.append('wrong-public-bytes')
    else:raise AssertionError('false proof accepted')
    assert sha((SCAN/'findings.json').read_bytes())==json.loads((SCAN/'manifest.json').read_bytes())['findingsSha256']
    verify(invocation);OUT.mkdir()
    value=dict(actualExit=0,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
       source=manifest['source'],contentCommit=manifest['contentCommit'],originalScanManifestSha256=sha((SCAN/'manifest.json').read_bytes()),
       classificationManifestSha256=sha((RAW/'manifest.json').read_bytes()),findings=len(rows),dispositions=dict(counts),
       everyFalsePositiveBoundToExactCaptureAndActualPublicBytes=True,rejectedMetadataCases=rejected,
       originalFindingsUnchanged=True,scanRerun=False,productTestsExecuted=0,productCoverage=None,
       whole451SecretGateAccepted=False,formalUpdated=False,newAccepted=0)
    with (OUT/'manifest.json').open('x',encoding='utf-8') as stream:
        json.dump(value,stream,ensure_ascii=False,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps({key:value[key] for key in ('actualExit','findings','dispositions')}))


if __name__=='__main__':main()
