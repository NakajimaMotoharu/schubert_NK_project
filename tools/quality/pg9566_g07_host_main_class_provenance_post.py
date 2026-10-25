"""Independently reconstruct public host class digests with JDK API and all residual capture joins."""
from collections import Counter
import copy
import datetime as dt
import json
import os
from pathlib import Path
import re
import subprocess
import g07_host_class_provenance_inputs as data
import pg9346_direct_companion_jdk_post as steps
from host_tool_invocation import capture,verify

ROOT=data.ROOT;BASE=data.BASE;SOURCE=data.SOURCE
OUT=BASE/'PG9566-g07-host-main-class-provenance-post-v1'
SLOT=ROOT.parent/'pgpt-runs/PG379/pg9566-g07-host-main-class-provenance-post-v1'
SUBJECT=BASE/'PG9564-g07-host-main-class-provenance-v1'
HELPER=ROOT/'tools/quality/architecture/PublicMainClassDigestAudit.java'
SPEC=ROOT/'evidence/01_PT/018_NK-OPS-001/1938_G07HostMainDigest_公開artifact根拠仕様.md'
SPEC_SHA='81221cf1bfb7f71d15f9b6816e6db019940cdad86dd8576f235c1bf6169a7bf9'

def validate_registry(proofs,expected):
    if proofs!=expected:raise ValueError('exact normal host class/source/Jar artifact provenance required')
def validate_updates(updates,expected,pending):
    if updates!=expected or not Counter(map(data.key,updates))<=Counter(map(data.key,pending)):
        raise ValueError('all exact captures, original tuple multiplicity and public proof closure required')
def verdict(values,old,new):
    if not values or not values<=set(old)|set(new) or not (values & (set(new)-set(old))):return None
    proofs=dict(old)
    for k,v in new.items():proofs.setdefault(k,v)
    return [proofs[v] for v in sorted(values)]

def main():
    invocation=capture(Path(__file__));assert not OUT.exists() and not SLOT.exists()
    assert data.sha(SPEC.read_bytes())==SPEC_SHA
    raw=(SUBJECT/'manifest.json').read_bytes()
    assert data.sha(raw)=='458970306a06b661c558c67f25b5769308fffb91d2c7d8603f996084a70de2ff'
    subject=json.loads(raw)
    assert subject['actualExit']==0 and subject['source']==SOURCE and subject['historicalScanSource']==data.HISTORICAL
    assert subject['actualSecretCount'] is None and not subject['currentSourceWholeG07Qualified']
    registry=data.read_checked(SUBJECT/'public-main-class-proofs.json',subject['publicClassProofsSha256'])
    updates=data.read_checked(SUBJECT/'updates.json',subject['updatesSha256'])
    inputs=data.inputs();normal=inputs['manifests']['normal'];hashes=normal['begin']['inputHashes'];main_map=inputs['mainMap']
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=ROOT)==b''
    os.umask(0o077);SLOT.mkdir();classes=SLOT/'reader';classes.mkdir()
    catalog=SLOT/'normal-jars.tsv';helper_sha=data.sha(HELPER.read_bytes());jars={}
    for module,jar in sorted(normal['jars'].items()):jars[module]=data.regular_normal_jar(module,jar)
    with catalog.open('x') as f:
        for module,path in jars.items():f.write(module+'\t'+str(path)+'\n')
    steps.SLOT=SLOT;jdk=ROOT.parent/'toolchain/jdk-25.0.4/bin'
    stages=[steps.step('compile-jdk-class-reader',[str(jdk/'javac'),'--release','25','-proc:none','-Xlint:all','-Werror','-d',str(classes),str(HELPER)])]
    assert stages[0]['actualExit']==0 and not stages[0]['timedOut']
    stages.append(steps.step('read-normal-main-classes',[str(jdk/'java'),'-cp',str(classes),HELPER.stem,str(data.NORMAL),str(catalog)]))
    assert stages[-1]['actualExit']==0 and not stages[-1]['timedOut']
    lines=(SLOT/'read-normal-main-classes.stdout').read_text().splitlines();assert lines[0]=='SELFTEST\t6'
    observed={};source_proofs={};names=set()
    for line in lines[1:]:
        module,entry,name,sourcefile,digest=line.split('\t')
        assert module in jars and entry==name+'.class' and name not in names and digest not in observed
        names.add(name);reference=main_map[name]
        path='src/schubert-nk-'+module+'/src/main/java/'+name.rpartition('/')[0]+'/'+sourcefile
        assert reference['module']==module and reference['path']==path and reference['sha256']==digest
        if path not in source_proofs:
            assert data.sha((ROOT/path).read_bytes())==hashes[path]==data.sha((data.NORMAL/path).read_bytes())
            source_proofs[path]=hashes[path]
        observed[digest]=dict(proofKind='PUBLIC_NORMAL_HOST_COMPILED_MAIN_CLASS_SHA256',source=SOURCE,
          normalManifestSha256=data.PINS['normal'][1],module=module,jarSha256=normal['jars'][module]['sha256'],jarEntry=entry,
          className=name,sourcePath=path,sourceSha256=hashes[path],sha256=digest)
    expected_registry=[observed[k] for k in sorted(observed)]
    assert names==set(main_map) and len(observed)==len(registry)==1843 and len(source_proofs)==965
    validate_registry(registry,expected_registry)
    assert all(data.sha(p.read_bytes())==normal['jars'][m]['sha256'] for m,p in jars.items())
    # Distinct literal set oracle: unknown/empty/old-only may never become a new public proof.
    old={'old':dict(kind='OLD')};new={'new-a':dict(kind='A'),'new-b':dict(kind='B')}
    assert verdict({'new-a','new-b'},old,new)==[dict(kind='A'),dict(kind='B')]
    assert verdict({'old','new-a'},old,new)==[dict(kind='A'),dict(kind='OLD')]
    assert verdict(set(),old,new) is None and verdict({'old'},old,new) is None
    assert verdict({'new-a','unknown'},old,new) is None and verdict({'unknown'},old,new) is None
    regex={name:re.compile(r['regex'],re.ASCII) for name,r in inputs['rules'].items()}
    cache={};expected=[];remaining=Counter();unsupported=set();new_only=set(observed)-set(inputs['oldProofs'])
    for row in inputs['pending']:
        path=row['path']
        if path not in cache:
            text=data.finding_text(row,inputs['inventory'])
            if any(ch in text for ch in '\v\f\r\x1c\x1d\x1e\x85\u2028\u2029'):cache[path]=None
            else:cache[path]=text.splitlines(keepends=True)
        original_lines=cache[path]
        if original_lines is None:
            remaining['UNSUPPORTED_LINE_SEPARATOR_REQUIRES_SEPARATE_POSITION_PROOF']+=1;unsupported.add(path);continue
        # Independent range extraction, not producer captures()/proven_set().
        low=max(0,row['startLine']-2);window=''.join(original_lines[low:min(len(original_lines),row['endLine']+1)])
        values=set()
        for match in regex[row['ruleId']].finditer(window):
            begin,end=match.span(1)
            first=1+low+window[:begin].count('\n');last=1+low+window[:end].count('\n')
            if row['startLine']<=first and last<=row['endLine']:values.add(match.group(1))
        bound=verdict(values,inputs['oldProofs'],observed)
        if bound is None:
            remaining['NO_EXACT_CAPTURE' if not values else 'AT_LEAST_ONE_CAPTURE_UNPROVEN_OR_NO_NEW_MAIN_PROOF']+=1;continue
        record={k:row[k] for k in ('path','ruleId','startLine','endLine','inputSha256')}
        expected.append(dict(**record,disposition='FALSE_POSITIVE_ALL_EXACT_CAPTURES_PUBLIC_ARTIFACT_DIGESTS',
          reason='ALL_EXACT_CAPTURES_BOUND_IN_REPORTED_RANGE_AT_LEAST_ONE_ACTUAL_NORMAL_HOST_MAIN_CLASS_PROOF',
          priorDisposition='UNCLASSIFIED',exactCaptureCount=len(values),newMainClassProofCount=len(values&new_only),publicArtifactProofs=bound))
    validate_updates(updates,expected,inputs['pending'])
    assert len(updates)==subject['additionalFalsePositives']==3829
    assert len(updates)+sum(remaining.values())==8379 and sum(remaining.values())==subject['remainingUnclassified']==4550
    assert dict(remaining)==subject['remainingReasons'] and sorted(unsupported)==subject['unsupportedLineSeparatorInputs']
    assert subject['cumulativeFalsePositiveProof']==31707+len(updates)==35536
    rejected=[]
    for label,edit in (('missing-finding',lambda v:v.pop()),('duplicate-finding',lambda v:v.append(copy.deepcopy(v[0]))),
      ('reported-range-forged',lambda v:v[0].update(startLine=v[0]['startLine']+1)),
      ('input-byte-forged',lambda v:v[0].update(inputSha256='0'*64)),
      ('public-proof-missing',lambda v:v[0]['publicArtifactProofs'].pop()),
      ('capture-count-forged',lambda v:v[0].update(exactCaptureCount=0)),
      ('unknown-classified',lambda v:v[0].update(reason='UNKNOWN_IS_PUBLIC')),
      ('runtime-success-invented',lambda v:v[0].update(productTestsExecuted=1))):
        changed=copy.deepcopy(updates);edit(changed);assert changed!=updates
        try:validate_updates(changed,expected,inputs['pending'])
        except ValueError:rejected.append(label)
        else:raise AssertionError('forged public finding classification accepted')
    for label,edit in (('class-digest-forged',lambda v:v[0].update(sha256='0'*64)),
      ('source-rebound',lambda v:v[0].update(source=data.HISTORICAL)),
      ('SourceFile-forged',lambda v:v[0].update(sourcePath='src/Forged.java')),
      ('jar-byte-forged',lambda v:v[0].update(jarSha256='0'*64))):
        changed=copy.deepcopy(registry);edit(changed)
        try:validate_registry(changed,expected_registry)
        except ValueError:rejected.append(label)
        else:raise AssertionError('forged public class proof accepted')
    assert data.sha(HELPER.read_bytes())==helper_sha and all(p.name.startswith(HELPER.stem) for p in classes.rglob('*.class'))
    assert all(data.sha((ROOT/p).read_bytes())==h for p,h in source_proofs.items())
    verify(invocation);OUT.mkdir()
    value=dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
      subjectManifestSha256=data.sha(raw),specSha256=SPEC_SHA,inputPins=data.PINS,helperPath=str(HELPER.relative_to(ROOT)),helperSha256=helper_sha,
      helperStages=stages,independentClassFileApiVectors=6,independentProofSetVectors=6,metadataCounterexamples=rejected,
      historicalScanSource=data.HISTORICAL,contentCommit=data.CONTENT,sourceArtifactProofScope='CURRENT_PUBLIC_NORMAL_HOST_MAIN_BYTES_ONLY',
      independentMainClasses=1843,independentMainSourceFiles=965,originalFindingCount=40086,priorPublicProofs=31707,
      additionalFalsePositives=len(updates),cumulativeFalsePositiveProof=35536,remainingUnclassified=4550,oneNoExactCaptureStillUnclassified=True,
      originalFindingMultiplicityPreserved=True,allExactCapturesProved=True,
      publicClassProofsSha256=subject['publicClassProofsSha256'],updatesSha256=subject['updatesSha256'],
      actualSecretCount=None,candidateValuesOrStandaloneCandidateHashesPersisted=False,scannerExecuted=False,
      wholeScanReplayed=False,ancestorWholeHashReplayed=False,nativeArtifactOrPrivateRawRead=False,
      targetClassLoading=0,targetRuntimeInvocations=0,productTestsExecuted=0,productCoverage=None,newTestIds=0,newMain=0,
      whole451SecretGateAccepted=False,currentSourceWholeG07Qualified=False,formalUpdated=False,newAccepted=0,effortPercent=None)
    data.write(SLOT/'manifest.safe.json',value);data.write(OUT/'manifest.json',value)
    print(json.dumps({k:value[k] for k in ('actualExit','additionalFalsePositives','remainingUnclassified','independentMainClasses')}),flush=True)
    print('manifestSha256='+data.sha((OUT/'manifest.json').read_bytes()),flush=True)

if __name__=='__main__':main()
