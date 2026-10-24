"""Hash explicit public-commit ancestor blobs, no stash/all-ref/private reads or secret scan rerun."""
from collections import Counter
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import subprocess
import time
from host_tool_invocation import capture,verify
from public_blob_scan import sha
from public_finding_provenance import classify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
SLOT=ROOT.parent/'pgpt-runs/PG379/pg8990-public-ancestor-provenance-v1'
OUT=BASE/'PG8990-public-ancestor-provenance-v1'
PRIOR=BASE/'PG8980-public-finding-provenance-v1'
RULES=BASE/'PG8979-gitleaks-rule-provenance-v1/manifest.json'
SNAPSHOT=ROOT.parent/'pgpt-runs/PG379/pg8968-public-blob-scan-v1/tracked'
ANCHOR='05d73a7974da8df92228160b96d91e7a006768f3'
SOURCE='fb9fce0f91de3d9fdfa634fe277592700f915e45'
ENV={'PATH':'/usr/bin:/bin','LANG':'C.UTF-8','GIT_NO_LAZY_FETCH':'1','GIT_TERMINAL_PROMPT':'0'}


def write(path,value):
    with path.open('x',encoding='utf-8') as stream:
        json.dump(value,stream,ensure_ascii=False,sort_keys=True,indent=2);stream.write('\n')


def exact_captures(text,row,rule):
    lines=text.splitlines(keepends=True);low=max(0,row['startLine']-2)
    window=''.join(lines[low:min(len(lines),row['endLine']+1)])
    matches=set()
    for match in re.compile(rule['regex'],re.ASCII).finditer(window):
        first=low+window.count('\n',0,match.start(1))+1
        last=low+window.count('\n',0,match.end(1))+1
        if row['startLine']<=first<=last<=row['endLine']:
            matches.add(match.group(1))
    return matches


def main():
    invocation=capture(Path(__file__));assert not SLOT.exists() and not OUT.exists()
    SLOT.mkdir(mode=0o700);started=time.monotonic();stage='FIXED_UNCLASSIFIED_INPUT'
    try:
        old=json.loads((PRIOR/'manifest.json').read_bytes())
        assert old['actualExit']==0 and old['source']==SOURCE and old['contentCommit']==ANCHOR
        assert old['classificationSha256']==sha((PRIOR/'classifications.json').read_bytes())
        rules=json.loads(RULES.read_bytes())['rules']
        original=json.loads((PRIOR/'classifications.json').read_bytes())
        residual=[row for row in original if row['disposition']=='UNCLASSIFIED']
        assert len(residual)==10618
        cache={};targets=set()
        for row in residual:
            path=row['path']
            if path not in cache:
                data=(SNAPSHOT/path).read_bytes();assert sha(data)==row['inputSha256']
                cache[path]=data.decode('utf-8')
            candidates=exact_captures(cache[path],row,rules[row['ruleId']])
            if len(candidates)==1:
                candidate=next(iter(candidates))
                if re.fullmatch('[0-9a-f]{64}',candidate):targets.add(candidate)
        stage='EXPLICIT_ANCESTOR_OBJECT_GRAPH'
        command=['git','rev-list','--objects','--no-object-names',ANCHOR]
        raw_ids=subprocess.check_output(command,cwd=ROOT,env=ENV,timeout=120)
        assert len(raw_ids)<32*1024*1024
        ids=raw_ids.decode('ascii').splitlines()
        assert 0<len(ids)<500000 and len(set(ids))==len(ids) and all(re.fullmatch('[0-9a-f]{40}',oid) for oid in ids)
        metadata=subprocess.run(['git','cat-file','--batch-check'],cwd=ROOT,env=ENV,input=raw_ids,
                                capture_output=True,timeout=120,check=False)
        assert metadata.returncode==0 and not metadata.stderr
        headers=[row.split() for row in metadata.stdout.decode('ascii').splitlines()]
        assert len(headers)==len(ids) and all(len(row)==3 and row[0]==oid and row[2].isdigit() for row,oid in zip(headers,ids))
        blobs=[(row[0],int(row[2])) for row in headers if row[1]=='blob' and int(row[2])<=64*1024*1024]
        oversized=[dict(gitObject=row[0],bytes=int(row[2]),reason='ABOVE64MIB_NOT_HASHED_NOT_PASSED') for row in headers if row[1]=='blob' and int(row[2])>64*1024*1024]
        stage='PUBLIC_ANCESTOR_BLOB_HASH_ONLY'
        child=subprocess.Popen(['git','cat-file','--batch'],cwd=ROOT,env=ENV,
                               stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
        ticks=(Path('/proc')/str(child.pid)/'stat').read_text().rsplit(')',1)[1].split()[19]
        write(SLOT/'process.safe.json',dict(pid=child.pid,startTicks=ticks,command=['git','cat-file','--batch'],
              source=SOURCE,anchorCommit=ANCHOR,cwd=str(ROOT),beginUTC=dt.datetime.now(dt.timezone.utc).isoformat()))
        proofs={};hashed=0;byte_count=0;completed=False
        try:
            for oid,size in blobs:
                if time.monotonic()-started>1200:raise TimeoutError('own public hash deadline')
                child.stdin.write((oid+'\n').encode());child.stdin.flush()
                header=child.stdout.readline().decode('ascii').split()
                assert header==[oid,'blob',str(size)]
                data=child.stdout.read(size)
                assert len(data)==size and child.stdout.read(1)==b'\n'
                assert hashlib.sha1(b'blob '+str(size).encode()+b'\0'+data).hexdigest()==oid
                digest=sha(data);hashed+=1;byte_count+=size
                if digest in targets:
                    proofs.setdefault(digest,dict(anchorCommit=ANCHOR,gitObject=oid,sha256=digest,bytes=size,
                        proofKind='HASH_OF_PUBLIC_REACHABLE_ANCESTOR_GIT_BLOB_NOT_A_SECRET_HASH'))
                del data
            completed=True
        finally:
            child.stdin.close()
            if not completed:child.terminate()
            child.wait(timeout=30)
        assert child.returncode==0
        write(SLOT/'terminal.safe.json',dict(actualExit=child.returncode,blobsHashed=hashed,bytes=byte_count,
              endUTC=dt.datetime.now(dt.timezone.utc).isoformat(),rawObjectContentPersisted=False))
        stage='EXACT_FINDING_PROOF_JOIN'
        updates=[];remaining=Counter()
        for row in residual:
            result=classify(cache[row['path']],rules[row['ruleId']],row['startLine'],row['endLine'],proofs)
            if result['disposition']=='FALSE_POSITIVE_PUBLIC_BLOB_SHA256':
                old_fields={key:row[key] for key in ('ruleId','path','startLine','endLine','inputSha256')}
                updates.append(dict(**old_fields,**result,priorDisposition='UNCLASSIFIED'))
            else:remaining[result['reason']]+=1
        verify(invocation);OUT.mkdir()
        write(OUT/'updates.json',updates)
        # Every serialized digest below has an actual public blob object proof, never a bare candidate.
        write(OUT/'public-proofs.json',list(proofs.values()))
        value=dict(actualExit=0,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
           source=SOURCE,contentCommit=ANCHOR,priorManifestSha256=sha((PRIOR/'manifest.json').read_bytes()),
           originalFindingCount=40086,previousFalsePositiveCount=29468,previousUnclassified=10618,
           additionalPublicBlobFalsePositives=len(updates),remainingUnclassified=10618-len(updates),
           remainingReasons=dict(remaining),uniqueTargetCount=len(targets),publicMatchingBlobCount=len(proofs),
           ancestorObjectCount=len(ids),ancestorObjectListSha256=sha(raw_ids),blobsHashed=hashed,bytesHashed=byte_count,
           oversizedUnhashed=oversized,graphCommand=command,historySecretPatternScan=False,
           allRefsOrStashRead=False,lazyFetchAllowed=False,networkActions=0,privateFilesystemRead=False,
           updatesSha256=sha((OUT/'updates.json').read_bytes()),proofsSha256=sha((OUT/'public-proofs.json').read_bytes()),
           rawCandidatesOrObjectContentPersisted=False,originalResultsUnchanged=True,scannerRerun=False,
           productTestsExecuted=0,productCoverage=None,whole451SecretGateAccepted=False,formalUpdated=False,newAccepted=0)
        write(OUT/'manifest.json',value)
        print(json.dumps({key:value[key] for key in ('actualExit','ancestorObjectCount','blobsHashed','bytesHashed','uniqueTargetCount','publicMatchingBlobCount','additionalPublicBlobFalsePositives','remainingUnclassified')}))
        return 0
    except Exception as error:
        failed=BASE/'PG8990-public-ancestor-provenance-failed-v1';failed.mkdir()
        write(failed/'manifest.json',dict(actualExit=1,invocation=invocation,source=SOURCE,contentCommit=ANCHOR,
            stage=stage,errorType=type(error).__name__,rawErrorSuppressed=True,originalEvidencePreserved=True))
        print(json.dumps(dict(actualExit=1,stage=stage,errorType=type(error).__name__,rawErrorSuppressed=True)))
        return 1


if __name__=='__main__':raise SystemExit(main())
