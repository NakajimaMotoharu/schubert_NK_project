"""Reuse immutable syntax evidence; parse only 38 changed/added public Test sources."""
from pathlib import Path
from collections import Counter
import datetime
import hashlib
import json
import os
import re
import stat
import subprocess

R = Path(__file__).resolve().parents[4]
B = R / 'evidence/01_PT/018_NK-OPS-001'
C = B / 'input/589_test_wait_delta38_scope.json'
O = B / 'evidence/PG23952-test-wait-delta38-static-v1'
S = R.parent / 'pgpt-runs/PG379/pg23952-test-wait-delta38-static-v1'
sha = lambda data: hashlib.sha256(data).hexdigest()
load = lambda p: json.loads(p.read_bytes())
write = lambda p, v: p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
HELD = {'RootFailedStartRecoveryTest.java','RootFailedStartPairRecoveryTest.java'}


def checked(ref):
    p = R / ref['path']
    assert sha(p.read_bytes()) == ref['sha256']
    return load(p)


def stage(label, command):
    start = datetime.datetime.now().astimezone().isoformat()
    write(O/(label+'-begin.safe.json'),dict(startJST=start,command=command,scope='OWN_TOOL_ONLY_NO_PRODUCT_TEST'))
    try:
        result = subprocess.run(command,cwd=R,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=45)
        exit_code, stdout, stderr, timeout = result.returncode,result.stdout,result.stderr,False
    except subprocess.TimeoutExpired as error:
        exit_code, stdout, stderr, timeout = 124,error.stdout or b'',error.stderr or b'',True
    (O/(label+'.stdout')).write_bytes(stdout)
    (O/(label+'.stderr')).write_bytes(stderr)
    result = dict(actualExit=exit_code,timedOut=timeout,startJST=start,
                  endJST=datetime.datetime.now().astimezone().isoformat(),command=command,
                  stdoutSha256=sha(stdout),stderrSha256=sha(stderr))
    write(O/(label+'-exit.safe.json'),result)
    assert exit_code == 0 and timeout is False, label
    return result


def main():
    assert not O.exists() and not S.exists()
    cfg = load(C)
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip() == cfg['observerHead']
    old = checked(cfg['priorInputs'])
    producer = checked(cfg['priorProducer'])
    independent = checked(cfg['priorIndependent'])
    prior_sites = checked(cfg['priorSites'])
    catalog = {v['path']:v for v in checked(cfg['currentIndex'])}
    assert len(catalog)==968 and len(old['inputs'])==956
    assert independent['actualExit']==producer['actualExit']==0
    assert independent['allReceiverTypesUnresolved'] is True and independent['productTestsExecuted']==0
    assert producer['frozenInputs']==cfg['priorInputs']
    same = set(cfg['sameGitBlobSourcePaths'])
    delta = cfg['deltaSourcePaths']
    assert len(same)==930 and len(delta)==len(set(delta))==38
    assert same.isdisjoint(delta) and same|set(delta)==set(catalog)
    assert all(Path(n).name not in HELD and n.startswith('src/') and '/src/test/java/' in n for n in catalog)
    # Metadata for explicit allowed paths only; never request held blob identities.
    current_tree = {}
    raw = subprocess.check_output(['git','--literal-pathspecs','ls-tree','-r','-z','HEAD','--',*sorted(catalog)],cwd=R)
    for line in raw.decode().strip('\0').split('\0'):
        head,name=line.split('\t',1)
        mode,kind,oid=head.split()
        assert name in catalog and kind=='blob'
        current_tree[name]=(mode,oid)
    assert set(current_tree)==set(catalog)
    for n,v in catalog.items():
        assert current_tree[n]==(v['gitIndexMode'],v['gitBlobObjectIdSHA1'])
    for n in same:
        assert current_tree[n]==(old['inputs'][n]['mode'],old['inputs'][n]['gitBlob'])
        assert producer['inputHashes'][n]==old['inputs'][n]['sha256']
    source_hashes={n:old['inputs'][n]['sha256'] for n in same}
    for n in delta:
        assert Path(n).name not in HELD and not any(x in n for x in ['RootFailedStart','SnapshotKeyCloseWitness','pg9892_'])
        path=R/n
        assert not path.is_symlink() and stat.S_ISREG(path.lstat().st_mode)
        data=path.read_bytes()
        assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==catalog[n]['gitBlobObjectIdSHA1']
        text=data.decode()
        assert not any(ch in text for ch in '\r\t\x85\u2028\u2029')
        source_hashes[n]=sha(data)
    helper=R/cfg['tool']['path']
    assert sha(helper.read_bytes())==cfg['tool']['sha256']==producer['tool']['sha256']
    code=helper.read_text()
    assert 'task.parse()' in code and 'List.of("-proc:none", "--release", "25")' in code
    assert not any(s in code for s in ['task.analyze(','task.generate(','Class.forName','newInstance(','System.getenv','System.load'])
    env_keys=['JAVA_TOOL_OPTIONS','JDK_JAVA_OPTIONS','_JAVA_OPTIONS','CLASSPATH']
    assert all(not os.environ.get(k) for k in env_keys)
    jdk=R.parent/'toolchain'/cfg['jdkRelease']
    release=(jdk/'release').read_bytes()
    version=re.search(rb'^JAVA_VERSION="([^"]+)"$',release,re.M)[1].decode()
    assert version=='25.0.4'
    os.umask(0o077)
    S.mkdir()
    (S/'source').mkdir()
    classes=S/'classes'
    classes.mkdir()
    mirror=S/'source/TrackedTestWaitAstCheck.java'
    mirror.write_bytes(helper.read_bytes())
    O.mkdir()
    write(O/'preflight.safe.json',dict(actualExit=0,deltaSourcePaths=delta,inputHashes={n:source_hashes[n] for n in delta},
          sourceGitObjectsMatch=True,reusedOldSources=930,excludedHeldNamesOnly=cfg['excludedHeldNamesOnly'],
          helper=cfg['tool'],toolScope='JDK_COMPILER_PARSE_ONLY',analyze=False,generate=False,
          productClasspath=[],productClassesCompiled=0,injectionVariablesUnset=env_keys,
          javaVersion=version,jdkReleaseSha256=sha(release),os=dict(system=os.uname().sysname,release=os.uname().release,machine=os.uname().machine)))
    stages={}
    try:
        stages['tool-javac']=stage('tool-javac',[str(jdk/'bin/javac'),'-proc:none','-encoding','UTF-8','-Xlint:all','-Werror','-d',str(classes),str(mirror)])
        class_hashes={p.name:sha(p.read_bytes()) for p in classes.iterdir()}
        assert set(class_hashes)==set(cfg['toolClassWhitelist']) and class_hashes==producer['ownToolClassHashes']
        stages['parse-delta']=stage('parse-delta',[str(jdk/'bin/java'),'-cp',str(classes),'TrackedTestWaitAstCheck',str(R),*delta])
        lines=[line.split('\t') for line in (O/'parse-delta.stdout').read_text().splitlines()]
        assert sorted(row[1] for row in lines if row[0]=='FILE')==sorted(delta)
        assert all(row[0] in ['FILE','IMPORT','VAR','CALL','REF'] and row[1] in delta for row in lines)
        assert all(not any(ch in row[5]+row[6] for ch in ['"',"'",'\\']) for row in lines if row[0]=='VAR')
        delta_sites=[]
        for row in lines:
            if row[0] not in ['CALL','REF']:continue
            assert len(row)==9
            delta_sites.append(dict(kind=row[0],path=row[1],owner=row[2],method=row[3],receiver=row[4],name=row[5],
                                    arity=int(row[6]) if row[0]=='CALL' else None,line=int(row[7]),columnUtf16=int(row[8]),
                                    receiverClassification='UNKNOWN_NOT_YET_RESOLVED',sourceSha256=source_hashes[row[1]]))
        reused=[v for v in prior_sites if v['path'] in same]
        assert all(v['sourceSha256']==source_hashes[v['path']] and v['receiverClassification']=='UNKNOWN_NOT_YET_RESOLVED' for v in reused)
        combined=reused+delta_sites
        keys=[(v['path'],v['line'],v['columnUtf16'],v['kind']) for v in combined]
        assert len(keys)==len(set(keys))
        for n in delta:assert sha((R/n).read_bytes())==source_hashes[n]
        assert sha(helper.read_bytes())==cfg['tool']['sha256']
        write(O/'delta-sites.json',delta_sites)
        write(O/'combined-sites.json',combined)
        write(O/'current-source-bindings.json',[dict(path=n,sourceSha256=source_hashes[n],gitBlobObjectIdSHA1=catalog[n]['gitBlobObjectIdSHA1'],
              syntaxEvidence='REUSED_SAME_GIT_BLOB_PRIOR_PARSE_NOT_NEW_PARSE' if n in same else 'CURRENT_DELTA_SOURCE_PARSE_ONLY') for n in sorted(catalog)])
        result=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=cfg['source'],observerHead=cfg['observerHead'],
                    config=dict(path=str(C.relative_to(R)),sha256=sha(C.read_bytes())),reusedSyntaxSources=930,parsedDeltaSources=38,
                    changedExistingSources=26,addedSources=12,combinedSyntaxSources=968,
                    reusedSiteCount=len(reused),deltaSiteCount=len(delta_sites),combinedSiteCount=len(combined),
                    methodInvocationSites=sum(v['kind']=='CALL' for v in combined),methodReferenceSites=sum(v['kind']=='REF' for v in combined),
                    nameCounts=dict(Counter(v['name'] for v in combined)),
                    noArgumentInvocationCandidates=sum(v['kind']=='CALL' and v['arity']==0 for v in combined),
                    allReceiverTypesUnresolved=True,noBlockingOrSafeInference=True,waitAuditOrLateralClosureComplete=False,
                    stages=stages,ownToolClassHashes=class_hashes,ownToolCompilerExecutions=1,ownToolJvmExecutions=1,
                    compilerOrJvmExecuted=True,targetClassesCompiled=0,targetClassLoading=0,targetRuntimeInvocations=0,
                    productTestsExecuted=0,actualBackendActions=0,newAcceptance=0,formalUpdated=False,effortRate=None,
                    wholeF03Accepted=False,whole451Accepted=False,sourceBytesUnchanged=True,
                    files={p.name:sha(p.read_bytes()) for p in O.iterdir() if p.is_file()},
                    tool=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(Path(__file__).read_bytes())))
        write(O/'manifest.json',result)
        print(json.dumps(dict(actualExit=0,reusedSources=930,parsedSources=38,sites=len(combined),manifestSha256=sha((O/'manifest.json').read_bytes()))))
    except BaseException:
        write(O/'failure.safe.json',dict(actualExit=1,atJST=datetime.datetime.now().astimezone().isoformat(),stages=stages,
              productTestsExecuted=0,targetClassesCompiled=0,scope='OWN_TOOL_OR_METADATA_FAILURE_NOT_PRODUCT_FAILURE',
              sourceAndExistingEvidencePreserved=True))
        raise


if __name__=='__main__':
    main()
