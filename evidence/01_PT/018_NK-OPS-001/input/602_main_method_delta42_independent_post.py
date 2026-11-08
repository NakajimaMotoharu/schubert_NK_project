"""Compare only 42 delta structures with JDK ClassFile API; reuse old 1801 identities."""
from pathlib import Path
from collections import Counter
from copy import deepcopy
import datetime
import hashlib
import importlib.util
import json
import os
import subprocess

R=Path(__file__).resolve().parents[4]
B=R/'evidence/01_PT/018_NK-OPS-001'
P=B/'evidence/PG23972-current-main-method-delta42-v1'
O=B/'evidence/PG23974-current-main-method-delta42-independent-v1'
S=R.parent/'pgpt-runs/PG379/pg23974-current-main-method-delta42-independent-v1'
load=lambda p:json.loads(p.read_bytes())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')


def checked(ref):
    p=Path(ref['path']);p=p if p.is_absolute() else R/p
    assert sha(p)==ref['sha256']
    return load(p)


def assess(m,rows,sources,expected,expected_sources):
    assert m['actualExit']==0 and m['source']=='7aed8eace7c844c2f79f2e39db766faf914890d5'
    for k,v in [('sourceFiles',967),('physicalClasses',1845),('knownMetadataClasses',1843),('reusedMetadataClasses',1801),('decodedDeltaClasses',42)]:
        assert type(m[k]) is int and m[k]==v
    assert rows==expected and sources==expected_sources
    assert m['methodsOfHeldClasses'] is None and m['totalMethodDenominatorComplete'] is False
    assert m['heldEntriesReadOrHashed'] is False and m['automaticGeneratedCodeExclusions'] is False
    assert m['targetClassesDefinedInitializedOrInvoked'] is False and m['currentCoverageComputed'] is False
    assert m['oldRuntimeTransferred'] is False and m['wholeG13Accepted'] is False and m['whole451Accepted'] is False
    assert type(m['productTestsExecuted']) is int and m['productTestsExecuted']==0
    assert m['newAcceptance']==0 and m['formalUpdated'] is False and m['effortRate'] is None
    methods=[x for row in rows if row['structure'] is not None for x in row['structure']['methods']]
    assert len(methods)==m['observedMethods']==11942
    assert sum(v['hasCode'] for v in methods)==m['codeMethodsObserved']
    assert sum(not v['hasCode'] for v in methods)==m['noCodeMethodsObserved']


def main():
    assert not O.exists() and not S.exists()
    m=load(P/'manifest.json');cfg=checked(m['config'])
    for name,digest in m['files'].items():assert sha(P/name)==digest
    normal=checked(cfg['normalManifest'])
    old=checked(cfg['oldManifest'])
    old_rows={v['physicalKey']:v for v in checked(cfg['oldClassInventory'])}
    index=checked(cfg['currentIndex'])
    current={v['path'].split('/')[1].removeprefix('schubert-nk-')+':'+n+'.class':v for n,v in index.items()}
    held=set(cfg['heldClassEntryKeys']);reuse=set(cfg['reusedClassKeys']);delta=set(cfg['deltaClassKeys'])
    assert held==set(old['heldClasses']) and len(held)==2
    assert len(reuse)==1801 and len(delta)==42 and held|reuse|delta==set(current)
    assert not (held&reuse or held&delta or reuse&delta)
    for key in reuse:assert old_rows[key]['classSha256']==current[key]['sha256']
    for jar in normal['jars'].values():assert sha(Path(jar['path']))==jar['sha256']
    helper=B/'input/603_MainClassMethodDeltaAudit.java'
    code=helper.read_text()
    assert code.index('if (HELD.contains(key))')<code.index('if (!selected.contains(key))')<code.index('archive.getInputStream(entry)')<code.index('ClassFile.of().parse(bytes)')
    assert not any(x in code for x in ['Class.forName','ClassLoader','System.load','System.getenv','java.lang.reflect'])
    assert all(not os.environ.get(k) for k in ['JAVA_TOOL_OPTIONS','JDK_JAVA_OPTIONS','_JAVA_OPTIONS','CLASSPATH'])
    # Reuse only the previously reviewed own-stage capture function, not its original main.
    capture_source=B/'input/591_test_wait_delta38_parse.py'
    capture_proof=load(B/'evidence/PG23952-test-wait-delta38-static-v1/manifest.json')
    assert sha(capture_source)==capture_proof['tool']['sha256']
    spec=importlib.util.spec_from_file_location('own_stage_capture_definitions_only',capture_source)
    capture=importlib.util.module_from_spec(spec);spec.loader.exec_module(capture)
    os.umask(0o077);S.mkdir();(S/'source').mkdir();classes=S/'classes';classes.mkdir();O.mkdir()
    mirror=S/'source/MainClassMethodDeltaAudit.java';mirror.write_bytes(helper.read_bytes())
    catalog=S/'jars.tsv';catalog.write_text(''.join(k+'\t'+v['path']+'\n' for k,v in sorted(normal['jars'].items())))
    selection=S/'delta-entries.txt';selection.write_text('\n'.join(sorted(delta))+'\n')
    snapshots={Path(v['path']).parents[3] for v in normal['jars'].values()};assert len(snapshots)==1;snapshot=snapshots.pop()
    jdk=R.parent/'toolchain/jdk-25.0.4'
    write(O/'preflight.safe.json',dict(actualExit=0,normalManifest=cfg['normalManifest'],deltaEntries=sorted(delta),
          reusedEntries=1801,heldEntries=sorted(held),targetClasspath=[],targetClassesCompiled=0,
          helperSourceSha256=sha(helper),ownStageCaptureSourceSha256=sha(capture_source),
          sourceMetadataCount=967,physicalNameCount=1845,javaVersion='25.0.4',
          os=dict(system=os.uname().sysname,release=os.uname().release,machine=os.uname().machine)))
    capture.O=O
    stages={}
    stages['tool-javac']=capture.stage('tool-javac',[str(jdk/'bin/javac'),'-proc:none','-encoding','UTF-8','-Xlint:all','-Werror','-d',str(classes),str(mirror)])
    assert {p.name for p in classes.iterdir()}=={'MainClassMethodDeltaAudit.class'}
    stages['read-delta']=capture.stage('read-delta',[str(jdk/'bin/java'),'-cp',str(classes),'MainClassMethodDeltaAudit',str(snapshot),str(catalog),str(selection)])
    lines=(O/'read-delta.stdout').read_text().splitlines();assert lines[-1]=='TOTAL\t42\t2\t1801'
    jdk_models={};held_observed=set()
    for line in lines[:-1]:
        v=line.split('\t')
        if v[0]=='HOLD':assert v[1] in held and v[1] not in held_observed;held_observed.add(v[1])
        elif v[0]=='CLASS':
            assert len(v)==6 and v[1] in delta and v[1] not in jdk_models
            jdk_models[v[1]]=dict(flags=int(v[2]),sourceFile=v[3],fields=int(v[4]),expectedMethods=int(v[5]),methods=[])
        else:
            assert v[0]=='METHOD' and len(v)==7 and v[1] in jdk_models and v[5] in ['true','false']
            jdk_models[v[1]]['methods'].append(dict(name=v[2],descriptor=v[3],flags=int(v[4]),hasCode=v[5]=='true',codeLength=int(v[6])))
    assert set(jdk_models)==delta and held_observed==held
    for model in jdk_models.values():assert len(model['methods'])==model.pop('expectedMethods')
    artifacts={v['path']:v for v in checked(cfg['wbsInventory'])['artifacts']}
    source_hashes={n:h for n,h in normal['begin']['inputHashes'].items() if n.startswith('src/') and '/src/main/java/' in n and n.endswith('.java')}
    expected=[]
    for key in sorted(current):
        src=current[key]['path'];owner=artifacts[src]
        if key in held:model,digest,status,origin=None,None,'UNOBSERVED_HOLD_GRAPH9','HELD_NOT_READ_HASHED_OR_PARSED'
        elif key in reuse:
            model,digest=old_rows[key]['structure'],old_rows[key]['classSha256']
            status,origin='STATIC_METADATA_NOT_RUNTIME_OR_COVERAGE','REUSED_EXACT_CLASS_BYTE_METADATA_NOT_RUNTIME'
        else:
            model,digest=jdk_models[key],current[key]['sha256']
            status,origin='STATIC_METADATA_NOT_RUNTIME_OR_COVERAGE','CURRENT_NORMAL_DELTA_READONLY_DECODE'
        expected.append(dict(physicalKey=key,sourcePath=src,sourceSha256=source_hashes[src],owner=owner['owner'],costOwner=owner['costOwner'],
                        ownershipMeaning='SOURCE_RESPONSIBILITY_NOT_METHOD_ORACLE_TRACE',classSha256=digest,
                        metadataStatus=status,metadataProvenance=origin,structure=model,methodTestRequirementTrace='NOT_VERIFIED',coverage=None,accepted=False))
    actual=load(P/'class-method-inventory.json');actual.sort(key=lambda v:v['physicalKey'])
    sources=load(P/'source-denominator.json');counts=Counter(v['sourcePath'] for v in expected)
    expected_sources=[dict(path=n,sha256=source_hashes[n],physicalClasses=counts[n],heldPhysicalClasses=sum(v['sourcePath']==n and v['structure'] is None for v in expected),exactMethodTrace='NOT_VERIFIED') for n in sorted(source_hashes)]
    assess(m,actual,sources,expected,expected_sources)
    negatives=[]
    for field,value in [('physicalClasses',1843),('decodedDeltaClasses',1843),('reusedMetadataClasses',0),('observedMethods',11922),
                        ('methodsOfHeldClasses',0),('totalMethodDenominatorComplete',True),('heldEntriesReadOrHashed',True),
                        ('automaticGeneratedCodeExclusions',True),('currentCoverageComputed',True),('oldRuntimeTransferred',True),('wholeG13Accepted',True),('productTestsExecuted',11942)]:
        bad=deepcopy(m);bad[field]=value
        try:assess(bad,actual,sources,expected,expected_sources)
        except AssertionError:negatives.append(field)
        else:raise AssertionError('metadata mutation accepted: '+field)
    for label in ['drop-class','duplicate','wrong-owner','missing-method','held-parse','held-hash','coverage','method-trace']:
        rr=deepcopy(actual)
        if label=='drop-class':rr.pop()
        elif label=='duplicate':rr[0]=rr[1]
        elif label=='wrong-owner':rr[0]['owner']='WBS-G13.07'
        elif label=='missing-method':next(v for v in rr if v['structure'] is not None and v['structure']['methods'])['structure']['methods'].pop()
        elif label=='held-parse':next(v for v in rr if v['structure'] is None)['structure']={}
        elif label=='held-hash':next(v for v in rr if v['structure'] is None)['classSha256']='0'*64
        elif label=='coverage':rr[0]['coverage']=100
        elif label=='method-trace':rr[0]['methodTestRequirementTrace']='VERIFIED'
        try:assess(m,rr,sources,expected,expected_sources)
        except AssertionError:negatives.append(label)
        else:raise AssertionError('metadata row mutation accepted: '+label)
    for jar in normal['jars'].values():assert sha(Path(jar['path']))==jar['sha256']
    result=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=m['source'],
                producerManifest=dict(path=str((P/'manifest.json').relative_to(R)),sha256=sha(P/'manifest.json')),
                sourceFiles=967,physicalClasses=1845,knownMetadataClasses=1843,reusedMetadataClasses=1801,
                independentlyDecodedDeltaClasses=42,heldClasses=sorted(held),observedMethods=11942,
                codeMethodsObserved=m['codeMethodsObserved'],noCodeMethodsObserved=m['noCodeMethodsObserved'],
                previousKnownMethodMetadataCount=11922,knownMethodMetadataDelta=20,methodsOfHeldClasses=None,
                totalMethodDenominatorComplete=False,heldEntriesReadOrHashed=False,
                metadataNegativeChecks=negatives,stages=stages,helperSourceSha256=sha(helper),helperClassSha256=sha(classes/'MainClassMethodDeltaAudit.class'),
                ownToolCompilerExecutions=1,ownToolJvmExecutions=1,targetClassesDefinedInitializedOrInvoked=False,
                targetClasspathContainsProduct=False,productTestsExecuted=0,actualBackendActions=0,
                currentCoverageComputed=False,oldRuntimeTransferred=False,wholeG13Accepted=False,whole451Accepted=False,
                newAcceptance=0,formalUpdated=False,effortRate=None,
                files={p.name:sha(p) for p in O.iterdir() if p.is_file()},
                verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(Path(__file__))))
    write(O/'manifest.json',result)
    print(json.dumps(dict(actualExit=0,knownMethods=11942,reusedClasses=1801,independentDelta=42,negativeMetadataChecks=len(negatives),manifestSha256=sha(O/'manifest.json'))))


if __name__=='__main__':
    main()
