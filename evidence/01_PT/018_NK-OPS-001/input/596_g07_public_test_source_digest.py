"""Prove a typed public Test source digest; never write capture values or execute source."""
from pathlib import Path,PurePosixPath
from collections import Counter,defaultdict
import datetime
import hashlib
import json
import re
import subprocess

R=Path(__file__).resolve().parents[4]
B=R/'evidence/01_PT/018_NK-OPS-001'
C=B/'input/594_g07_test_source_digest_scope.json'
O=B/'evidence/PG23962-g07-public-test-source-digest-v1'
load=lambda p:json.loads(p.read_bytes())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
key=lambda v:tuple(v[n] for n in ['path','ruleId','startLine','endLine','inputSha256'])


def checked(ref):
    p=R/ref['path']
    assert sha(p)==ref['sha256']
    return load(p)


def source_name(name,cfg):
    if not isinstance(name,str):return None
    for prefix in cfg['absolutePublicSourceRoots']:
        if name.startswith(prefix+'/'):name=name[len(prefix)+1:];break
    if not name.startswith(tuple(cfg['allowedSourcePrefixes'])) or not name.endswith('.java'):return None
    if str(PurePosixPath(name))!=name or '..' in PurePosixPath(name).parts or '\\' in name or '\0' in name:return None
    if PurePosixPath(name).name in cfg['protectedSourceBasenames']:return None
    return name


def maps(text,obj,roles):
    result=[]
    for role in roles:
        mapping=obj
        for name in role:mapping=mapping.get(name) if isinstance(mapping,dict) else None
        if not isinstance(mapping,dict):continue
        parent=(0,len(text))
        if len(role)==2:
            found=list(re.finditer(r'^  '+re.escape(json.dumps(role[0]))+': ',text,re.M))
            if len(found)!=1:continue
            at=found[0].end();value,end=json.JSONDecoder().raw_decode(text,at)
            if value!=obj[role[0]]:continue
            parent=(at,end)
        marker=r'^'+' '*(2*len(role))+'"'+re.escape(role[-1])+'": '
        found=[m for m in re.finditer(marker,text,re.M) if parent[0]<=m.start()<parent[1]]
        if len(found)!=1:continue
        at=found[0].end();value,end=json.JSONDecoder().raw_decode(text,at)
        if value==mapping:result.append((at,end,mapping,'.'.join(role)))
    return result


def main():
    assert not O.exists()
    cfg=load(C)
    previous=checked(cfg['previousUpdateManifest'])
    refs=[*previous['priorUpdateRefs'],dict(path=str((R/cfg['previousUpdateManifest']['path']).with_name('updates.json').relative_to(R)),sha256=previous['updatesSha256'])]
    prior=[]
    for ref in refs:prior+=checked(ref)
    old=Counter(map(key,prior));assert len(prior)==1178
    findings=checked(cfg['originalMetadata']);original=Counter(map(key,findings))
    assert len(findings)==4493 and sum((original-old).values())==3315
    current=checked(cfg['currentBindings']);cp=checked(cfg['currentProof'])
    prior_inputs=checked(cfg['priorInputs']);pp=checked(cfg['priorProof'])
    older=checked(cfg['olderSourceManifest']);op=checked(cfg['olderIndependent'])
    assert cp['actualExit']==pp['actualExit']==op['actualExit']==older['actualExit']==0
    assert cp['combinedSyntaxSources']==968 and pp['checkedSources']==956 and older['sourceFiles']==824
    assert op['subjectManifestSha256']==cfg['olderSourceManifest']['sha256']
    known=defaultdict(dict)
    def add(name,digest,epoch,kind,ref):
        n=source_name(name,cfg)
        if n is None:return
        assert isinstance(digest,str) and re.fullmatch('[0-9a-f]{64}',digest)
        assert re.fullmatch('[0-9a-f]{40}',epoch)
        known[n].setdefault(digest,dict(sourceCommit=epoch,sourceWitnessKind=kind,sourceWitnessManifest=ref))
    for v in current:add(v['path'],v['sourceSha256'],cfg['currentSourceCommit'],'CURRENT_SOURCE_BINDING_NOT_EXECUTION',cfg['currentBindings'])
    for n,v in prior_inputs['inputs'].items():add(n,v['sha256'],prior_inputs['source'],'HISTORICAL_GIT_INPUT_NOT_EXECUTION',cfg['priorInputs'])
    for n,digest in older['sourceHashes'].items():add(n,digest,older['source'],'HISTORICAL_PUBLIC_SOURCE_NOT_EXECUTION',cfg['olderSourceManifest'])
    rule=checked(cfg['rule']);rx=re.compile(rule['rules']['generic-api-key']['regex'],re.ASCII)
    updates=[];kept=[];cache={};roles=Counter();typed=0;candidate_count=0
    def git_source(n,value,witness):
        assert source_name(n,cfg)==n and n in known and value in known[n]
        epoch=witness['sourceCommit'];identity=(epoch,n,value)
        if identity in cache:return cache[identity]
        status='UNKNOWN_PUBLIC_GIT_SOURCE_UNAVAILABLE';matched=False;size=None
        try:
            tree=subprocess.check_output(['git','--literal-pathspecs','ls-tree','-z',epoch,'--',n],cwd=R,stderr=subprocess.PIPE,timeout=10)
            entries=tree.decode().strip('\0').split('\0')
            if len(entries)==1:
                meta,path=entries[0].split('\t',1);mode,kind,oid=meta.split()
                if path==n and mode in ['100644','100755'] and kind=='blob' and re.fullmatch('[0-9a-f]{40}',oid):
                    data=subprocess.check_output(['git','cat-file','blob',oid],cwd=R,stderr=subprocess.PIPE,timeout=10)
                    data.decode('utf-8');assert b'\0' not in data
                    size=len(data);matched=hashlib.sha256(data).hexdigest()==value
                    status='ACTUAL_REGULAR_PUBLIC_GIT_SOURCE_BYTE_DIGEST_MATCH' if matched else 'UNKNOWN_PUBLIC_GIT_SOURCE_BYTE_MISMATCH'
                else:status='UNKNOWN_NONREGULAR_PUBLIC_SOURCE_OBJECT'
        except (subprocess.CalledProcessError,subprocess.TimeoutExpired,UnicodeError,ValueError):pass
        answer=dict(testSourcePath=n,sourceCommit=epoch,sourceWitnessKind=witness['sourceWitnessKind'],sourceWitnessManifest=witness['sourceWitnessManifest'],actualRegularPublicGitSourceBytesMatched=matched,bytesHashed=size,status=status)
        cache[identity]=answer
        return answer
    for path,pin in cfg['inputFiles'].items():
        assert re.fullmatch(cfg['metadataPathRegex'],path) and not re.search(r'(?i)(raw|gitleaks|capture|secret|scan)',path)
        p=R/path;assert p.stat().st_size<5000000 and sha(p)==pin
        text=p.read_text();obj=json.loads(text);lines=text.splitlines(keepends=True)
        typed_maps=maps(text,obj,cfg['fieldRoles']);typed+=len(typed_maps)
        for f in [v for v in findings if v['path']==path and not old[key(v)]]:
            candidate_count+=1;assert f['inputSha256']==pin
            base={n:f[n] for n in ['path','ruleId','startLine','endLine','inputSha256']}
            def retain(reason):kept.append(dict(**base,status=reason))
            if f['ruleId']!='generic-api-key' or f['shape']!='ALL_HEX64' or f['startLine']!=f['endLine']:
                retain('UNKNOWN_UNSUPPORTED_RULE_SHAPE_OR_MULTILINE');continue
            a=sum(map(len,lines[:f['startLine']-1]));z=sum(map(len,lines[:f['endLine']]))
            pair=re.fullmatch(r'\s+("(?:\\.|[^"\\])*"): "([a-f0-9]{64})",?\n?',lines[f['startLine']-1])
            selected=[v for v in typed_maps if v[0]<=a<z<=v[1]+1]
            if pair is None or len(selected)!=1:
                retain('UNKNOWN_OUTSIDE_TYPED_PUBLIC_SOURCE_MAP');continue
            name=json.loads(pair[1]);n=source_name(name,cfg)
            if n is None:
                retain('NON_ALLOWLISTED_OR_PROTECTED_SOURCE_EXCLUDED_BEFORE_GIT_IO');continue
            value=pair[2];assert selected[0][2].get(name)==value
            if n not in known or value not in known[n]:
                retain('UNKNOWN_NO_EXACT_PUBLIC_TEST_SOURCE_WITNESS');continue
            lo=max(0,f['startLine']-2);win=''.join(lines[lo:min(len(lines),f['endLine']+1)])
            captured={m[1] for m in rx.finditer(win) if f['startLine']<=lo+win[:m.start(1)].count('\n')+1<=lo+win[:m.end(1)].count('\n')+1<=f['endLine']}
            if captured!={value}:
                retain('UNKNOWN_CAPTURE_NOT_SINGLE_WHOLE_SOURCE_DIGEST');continue
            witness=known[n][value];proof=git_source(n,value,witness)
            if proof['actualRegularPublicGitSourceBytesMatched'] is not True:
                retain(proof['status']);continue
            updates.append(dict(**base,disposition='FALSE_POSITIVE_ACTUAL_PUBLIC_GIT_TEST_SOURCE_DIGEST',fieldRole=selected[0][3],
                           testSourcePath=n,**witness,actualRegularPublicGitSourceBytesMatched=True,
                           wholeExactCapturePubliclyDerived=True,exactCaptureCount=1,
                           sourceBodyCopiedOrExecuted=False,currentOrHistoricalTestExecutionQualified=False,
                           capturedValueWritten=False,captureValueHashWritten=False))
            roles[selected[0][3]]+=1
    new=Counter(map(key,updates));assert not new.keys()&old.keys() and all(v==original[k]==1 for k,v in new.items())
    assert Counter(map(key,updates+kept))==Counter(key(v) for v in findings if v['path'] in cfg['inputFiles'] and not old[key(v)])
    remaining=sum((original-old-new).values());assert remaining==3315-len(updates)
    O.mkdir();write(O/'updates.json',updates);write(O/'retained.json',kept);write(O/'public-source-readset.json',list(cache.values()))
    result=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=cfg['source'],
                config=dict(path=str(C.relative_to(R)),sha256=sha(C)),originalMetadata=cfg['originalMetadata'],priorUpdateRefs=refs,
                inputFiles=cfg['inputFiles'],typedSourceMaps=typed,candidateRows=candidate_count,
                knownPublicTestSourcePaths=len(known),knownPublicSourceDigests=sum(len(v) for v in known.values()),
                actualDistinctGitSourceObjectsRead=sum(v['bytesHashed'] is not None for v in cache.values()),
                provenanceRoleCounts=dict(roles),newFalsePositives=len(updates),remainingUnclassified=remaining,
                retainedStatusCounts=dict(Counter(v['status'] for v in kept)),updatesSha256=sha(O/'updates.json'),
                retainedSha256=sha(O/'retained.json'),sourceReadsetSha256=sha(O/'public-source-readset.json'),
                actualSecretCount=None,binaryOrContainerLimited=22,capturedValuesWritten=False,captureValueHashesWritten=False,
                sourceBodiesWritten=False,protectedSourceObjectsRead=False,actualCredentialOrKeyFilesRead=False,
                productTestsExecuted=0,compilerOrJvmExecuted=False,actualBackendActions=0,
                privateRawOrRuntimeArchiveRead=False,originalProducerOrScannerExecuted=False,
                currentOrHistoricalTestExecutionQualified=False,wholeG07Accepted=False,whole451Accepted=False,
                newAcceptance=0,formalUpdated=False,effortRate=None,
                tool=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(Path(__file__))))
    write(O/'manifest.json',result)
    print(json.dumps(dict(actualExit=0,inputFiles=len(cfg['inputFiles']),sourceObjects=result['actualDistinctGitSourceObjectsRead'],newFalsePositives=len(updates),remaining=remaining,retainedStatuses=result['retainedStatusCounts'],manifestSha256=sha(O/'manifest.json'))))


if __name__=='__main__':
    main()
