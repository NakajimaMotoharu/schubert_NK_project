"""Reuse prior source identities, independently check only the 38 current syntax inputs."""
from pathlib import Path
from collections import Counter
from copy import deepcopy
import datetime
import hashlib
import importlib.util
import json
import subprocess

R = Path(__file__).resolve().parents[4]
B = R/'evidence/01_PT/018_NK-OPS-001'
P = B/'evidence/PG23952-test-wait-delta38-static-v1'
O = B/'evidence/PG23954-test-wait-delta38-independent-v1'
load = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def checked(ref):
    p=R/ref['path']
    assert sha(p)==ref['sha256']
    return load(p)


def partition(same,delta,catalog,old):
    assert len(same)==len(set(same))==930 and len(delta)==len(set(delta))==38
    assert set(same).isdisjoint(delta) and set(same)|set(delta)==set(catalog)
    for n in catalog:
        assert Path(n).name not in {'RootFailedStartRecoveryTest.java','RootFailedStartPairRecoveryTest.java'}
        equal=n in old and (catalog[n]['gitIndexMode'],catalog[n]['gitBlobObjectIdSHA1'])==(old[n]['mode'],old[n]['gitBlob'])
        assert (n in same)==equal
    assert len(set(delta)-set(old))==12 and len(set(delta)&set(old))==26


def main():
    assert not O.exists()
    m=load(P/'manifest.json')
    assert m['actualExit']==0 and m['productTestsExecuted']==m['targetClassesCompiled']==m['targetClassLoading']==0
    assert m['ownToolCompilerExecutions']==m['ownToolJvmExecutions']==1 and m['compilerOrJvmExecuted'] is True
    cp=R/m['config']['path']
    assert sha(cp)==m['config']['sha256']
    cfg=load(cp)
    for name,digest in m['files'].items():assert sha(P/name)==digest
    old=checked(cfg['priorInputs'])
    prior=checked(cfg['priorProducer'])
    original_post=checked(cfg['priorIndependent'])
    old_sites=checked(cfg['priorSites'])
    catalog={v['path']:v for v in checked(cfg['currentIndex'])}
    same,delta=cfg['sameGitBlobSourcePaths'],cfg['deltaSourcePaths']
    partition(same,delta,catalog,old['inputs'])
    assert original_post['actualExit']==0 and original_post['checkedSources']==956
    # Both held names are excluded before the tree command that reads blob identities.
    data=subprocess.check_output(['git','--literal-pathspecs','ls-tree','-r','-z','HEAD','--',*sorted(catalog)],cwd=R)
    observed={}
    for item in data.decode().strip('\0').split('\0'):
        left,name=item.split('\t',1)
        mode,kind,oid=left.split()
        assert name in catalog and kind=='blob'
        observed[name]=(mode,oid)
    assert set(observed)==set(catalog)
    for n,v in catalog.items():assert observed[n]==(v['gitIndexMode'],v['gitBlobObjectIdSHA1'])
    texts={}
    for n in delta:
        assert n in catalog and Path(n).name not in {'RootFailedStartRecoveryTest.java','RootFailedStartPairRecoveryTest.java'}
        source=(R/n).read_bytes()
        assert hashlib.sha1(b'blob '+str(len(source)).encode()+b'\0'+source).hexdigest()==catalog[n]['gitBlobObjectIdSHA1']
        texts[n]=source.decode()
        assert not any(c in texts[n] for c in '\r\t\x85\u2028\u2029')
    validator_path=R/original_post['verifier']['path']
    assert sha(validator_path)==original_post['verifier']['sha256']=='47e695cd1c82a1b1e6c53e97ef8a3fd1142035e6975b121bc58f19d3a48a2462'
    # Definition-only import; never invoke its original main or read the old private run.
    spec=importlib.util.spec_from_file_location('prior_wait_lexical_validator_definitions_only',validator_path)
    validator=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validator)
    raw=[line.split('\t') for line in (P/'parse-delta.stdout').read_text().splitlines()]
    assert sorted(v[1] for v in raw if v[0]=='FILE')==sorted(delta)
    parsed=load(P/'delta-sites.json')
    declarations=[v for v in raw if v[0] in ('CALL','REF')]
    assert len(parsed)==len(declarations)
    for site,row in zip(parsed,declarations):
        assert tuple(site[k] for k in ('kind','path','owner','method','receiver','name'))==tuple(row[:6])
        assert site['arity']==(int(row[6]) if row[0]=='CALL' else None)
        assert site['line']==int(row[7]) and site['columnUtf16']==int(row[8])
        assert site['sourceSha256']==hashlib.sha256(texts[site['path']].encode()).hexdigest()
        assert site['receiverClassification']=='UNKNOWN_NOT_YET_RESOLVED'
        assert validator.valid(site,texts[site['path']]),(site['path'],site['line'],site['name'])
    reused=[v for v in old_sites if v['path'] in set(same)]
    assert all(v['sourceSha256']==old['inputs'][v['path']]['sha256']==prior['inputHashes'][v['path']] for v in reused)
    combined=load(P/'combined-sites.json')
    assert combined==reused+parsed and len(combined)==7415
    keys=[(v['path'],v['line'],v['columnUtf16'],v['kind']) for v in combined]
    assert len(keys)==len(set(keys))
    assert dict(Counter(v['name'] for v in combined))==m['nameCounts']
    assert len(reused)==m['reusedSiteCount'] and len(parsed)==m['deltaSiteCount']
    assert sum(v['kind']=='CALL' for v in combined)==m['methodInvocationSites']
    assert sum(v['kind']=='REF' for v in combined)==m['methodReferenceSites']
    assert sum(v['kind']=='CALL' and v['arity']==0 for v in combined)==m['noArgumentInvocationCandidates']
    bindings=load(P/'current-source-bindings.json')
    assert len(bindings)==len({v['path'] for v in bindings})==968
    for row in bindings:
        n=row['path']
        assert row['gitBlobObjectIdSHA1']==catalog[n]['gitBlobObjectIdSHA1']
        assert row['sourceSha256']==(old['inputs'][n]['sha256'] if n in same else hashlib.sha256(texts[n].encode()).hexdigest())
        assert row['syntaxEvidence']==('REUSED_SAME_GIT_BLOB_PRIOR_PARSE_NOT_NEW_PARSE' if n in same else 'CURRENT_DELTA_SOURCE_PARSE_ONLY')
    for label,s in m['stages'].items():
        assert s==load(P/(label+'-exit.safe.json')) and s['actualExit']==0 and s['timedOut'] is False
        assert sha(P/(label+'.stdout'))==s['stdoutSha256'] and sha(P/(label+'.stderr'))==s['stderrSha256']
    command=m['stages']['parse-delta']['command']
    assert command[1]=='-cp' and command[3]=='TrackedTestWaitAstCheck' and command[4]==str(R) and command[5:]==delta
    current_slot=R.parent/'pgpt-runs/PG379/pg23952-test-wait-delta38-static-v1'
    assert command[2]==str(current_slot/'classes')
    classes={p.name:sha(p) for p in (current_slot/'classes').iterdir()}
    assert classes==m['ownToolClassHashes']==prior['ownToolClassHashes']
    assert set(classes)==set(cfg['toolClassWhitelist'])
    assert sha(current_slot/'source/TrackedTestWaitAstCheck.java')==cfg['tool']['sha256']
    assert m['allReceiverTypesUnresolved'] is True and m['noBlockingOrSafeInference'] is True and m['waitAuditOrLateralClosureComplete'] is False
    negative=[]
    sample=next(v for v in parsed if v['kind']=='CALL')
    for key,value in [('line',0),('columnUtf16',0),('name','missing'),('kind','OTHER'),('arity',True),('arity',1 if sample['arity']==0 else 0)]:
        changed=deepcopy(sample)
        changed[key]=value
        assert not validator.valid(changed,texts[sample['path']])
        negative.append('site-'+key)
    for label,s,d in [('missing-reuse',same[:-1],delta),('missing-delta',same,delta[:-1]),('duplicate-delta',same,delta[:-1]+[delta[0]])]:
        try:partition(s,d,catalog,old['inputs'])
        except AssertionError:negative.append(label)
        else:raise AssertionError('invalid partition accepted')
    O.mkdir()
    result=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=m['source'],
                producerManifest=dict(path=str((P/'manifest.json').relative_to(R)),sha256=sha(P/'manifest.json')),
                reusedSyntaxSources=930,parsedDeltaSources=38,changedExistingSources=26,addedSources=12,combinedSyntaxSources=968,
                verifiedCurrentDeltaSourcePositions=len(parsed),combinedSiteCount=len(combined),reusedSiteCount=len(reused),
                methodInvocationSites=m['methodInvocationSites'],methodReferenceSites=m['methodReferenceSites'],
                noArgumentInvocationCandidates=m['noArgumentInvocationCandidates'],nameCounts=m['nameCounts'],
                independentlyVerifiedZeroArgVsNonzeroCalls=sum(v['kind']=='CALL' for v in parsed),nonzeroExactArityNumbersFromParserOnly=True,
                allReceiverTypesUnresolved=True,noBlockingOrSafeInference=True,waitAuditOrLateralClosureComplete=False,
                metadataNegativeChecks=negative,oldPrivateRunArchiveOrRawRead=False,ownFreshToolClassesOnly=True,
                targetClassesCompiled=0,targetClassLoading=0,targetRuntimeInvocations=0,productTestsExecuted=0,
                actualBackendActions=0,newAcceptance=0,formalUpdated=False,effortRate=None,wholeF03Accepted=False,whole451Accepted=False,
                verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(Path(__file__))))
    write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
    write(O/'manifest.json',result)
    print(json.dumps(dict(actualExit=0,reusedSources=930,parsedSources=38,checkedNewPositions=len(parsed),sites=7415,manifestSha256=sha(O/'manifest.json'))))


if __name__=='__main__':
    main()
