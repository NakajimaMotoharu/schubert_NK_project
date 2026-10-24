"""Independent reachable object/byte proof + original finding join; no original scanner rerun."""
import copy
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess
from host_tool_invocation import capture,verify
from public_blob_scan import sha
from pg8982_public_finding_provenance_post import check

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
RAW=BASE/'PG8990-public-ancestor-provenance-v1'
PRIOR=BASE/'PG8980-public-finding-provenance-v1'
SNAPSHOT=ROOT.parent/'pgpt-runs/PG379/pg8968-public-blob-scan-v1/tracked'
OUT=BASE/'PG8992-public-ancestor-provenance-post-v1'
ANCHOR='05d73a7974da8df92228160b96d91e7a006768f3'
ENV={'PATH':'/usr/bin:/bin','LANG':'C.UTF-8','GIT_NO_LAZY_FETCH':'1','GIT_TERMINAL_PROMPT':'0'}


def proof_check(proof,objects,data):
    required={'anchorCommit','gitObject','sha256','bytes','proofKind'}
    if set(proof)!=required or proof['anchorCommit']!=ANCHOR or proof['gitObject'] not in objects:
        raise ValueError('explicit public ancestry proof required')
    if proof['proofKind']!='HASH_OF_PUBLIC_REACHABLE_ANCESTOR_GIT_BLOB_NOT_A_SECRET_HASH':
        raise ValueError('not public artifact hash proof')
    if len(data)!=proof['bytes'] or sha(data)!=proof['sha256']:
        raise ValueError('actual public blob digest mismatch')
    if hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()!=proof['gitObject']:
        raise ValueError('actual Git object mismatch')


def main():
    invocation=capture(Path(__file__));assert not OUT.exists()
    manifest=json.loads((RAW/'manifest.json').read_bytes())
    assert manifest['actualExit']==0 and manifest['contentCommit']==ANCHOR
    assert manifest['source']=='fb9fce0f91de3d9fdfa634fe277592700f915e45'
    assert sha((RAW/'updates.json').read_bytes())==manifest['updatesSha256']
    assert sha((RAW/'public-proofs.json').read_bytes())==manifest['proofsSha256']
    assert sha((PRIOR/'manifest.json').read_bytes())==manifest['priorManifestSha256']
    original=json.loads((PRIOR/'classifications.json').read_bytes())
    key=lambda row:tuple(row[name] for name in ('path','ruleId','startLine','endLine','inputSha256'))
    pending={key(row):row for row in original if row['disposition']=='UNCLASSIFIED'}
    assert len(pending)==10618
    raw_objects=subprocess.check_output(['git','rev-list','--objects','--no-object-names',ANCHOR],cwd=ROOT,env=ENV,timeout=120)
    assert sha(raw_objects)==manifest['ancestorObjectListSha256']
    objects=set(raw_objects.decode('ascii').splitlines())
    proofs=json.loads((RAW/'public-proofs.json').read_bytes());data_by_hash={}
    child=subprocess.Popen(['git','cat-file','--batch'],cwd=ROOT,env=ENV,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
    complete=False
    try:
        for proof in proofs:
            assert proof['gitObject'] in objects
            child.stdin.write((proof['gitObject']+'\n').encode());child.stdin.flush()
            assert child.stdout.readline().decode('ascii').split()==[proof['gitObject'],'blob',str(proof['bytes'])]
            data=child.stdout.read(proof['bytes']);assert child.stdout.read(1)==b'\n'
            proof_check(proof,objects,data);data_by_hash[proof['sha256']]=data
        complete=True
    finally:
        child.stdin.close()
        if not complete:child.terminate()
        child.wait(timeout=30)
    assert child.returncode==0 and len(data_by_hash)==len(proofs)==manifest['publicMatchingBlobCount']
    rules=json.loads((BASE/'PG8979-gitleaks-rule-provenance-v1/manifest.json').read_bytes())['rules']
    updates=json.loads((RAW/'updates.json').read_bytes());seen=set();cache={}
    for row in updates:
        identifier=key(row);assert identifier in pending and identifier not in seen;seen.add(identifier)
        assert row['priorDisposition']=='UNCLASSIFIED'
        if row['path'] not in cache:cache[row['path']]=(SNAPSHOT/row['path']).read_bytes()
        validated={name:value for name,value in row.items() if name!='priorDisposition'}
        old={name:pending[identifier][name] for name in ('path','ruleId','startLine','endLine','inputSha256')}
        data=data_by_hash[row['publicArtifactProof']['sha256']]
        check(validated,old,cache[row['path']],data,rules[row['ruleId']])
    assert len(updates)==manifest['additionalPublicBlobFalsePositives']
    assert len(pending)-len(updates)==manifest['remainingUnclassified']
    assert proofs
    proof=proofs[0];data=data_by_hash[proof['sha256']];rejected=[]
    for name,delta in [('wrong-anchor',{'anchorCommit':'0'*40}),('unreachable-object',{'gitObject':'0'*40}),
                       ('wrong-bytes',{'bytes':len(data)+1}),('wrong-digest',{'sha256':'0'*64}),
                       ('extra-field',{'Secret':'DO_NOT_PUBLISH'})]:
        changed=copy.deepcopy(proof);changed.update(delta)
        try:proof_check(changed,objects,data)
        except ValueError:rejected.append(name)
        else:raise AssertionError('unsafe public proof accepted')
    verify(invocation);OUT.mkdir()
    value=dict(actualExit=0,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
          source=manifest['source'],contentCommit=ANCHOR,ancestorManifestSha256=sha((RAW/'manifest.json').read_bytes()),
          everyAdditionalFindingBoundToActualPublicBlob=True,allOriginalFindingsPreserved=True,
          additionalPublicBlobFalsePositives=len(updates),remainingUnclassified=manifest['remainingUnclassified'],
          actualUniquePublicBlobProofs=len(proofs),rejectedMetadataCases=rejected,scanRerun=False,
          historySecretPatternScan=False,allRefsOrStashRead=False,privateFilesystemRead=False,
          productTestsExecuted=0,productCoverage=None,whole451SecretGateAccepted=False,formalUpdated=False,newAccepted=0)
    with (OUT/'manifest.json').open('x',encoding='utf-8') as stream:
        json.dump(value,stream,ensure_ascii=False,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps({name:value[name] for name in ('actualExit','additionalPublicBlobFalsePositives','remainingUnclassified','actualUniquePublicBlobProofs')}))


if __name__=='__main__':main()
