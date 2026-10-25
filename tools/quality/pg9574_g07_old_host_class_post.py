"""Independent JDK metadata and Git batch-source proof for old host classes; never target execution."""
from collections import Counter
import copy
import datetime as dt
import json
import os
from pathlib import Path
import re
import subprocess
import g07_old_host_inputs as data
import pg9346_direct_companion_jdk_post as steps
from host_tool_invocation import capture,verify

ROOT=data.ROOT;BASE=data.BASE;SOURCE=data.SOURCE
OUT=BASE/'PG9574-g07-old-host-main-class-post-v1'
SLOT=ROOT.parent/'pgpt-runs/PG379/pg9574-g07-old-host-main-class-post-v1'
SUBJECT=BASE/'PG9572-g07-old-host-main-class-provenance-v1'
SUBJECT_SHA='7cb508e23ab7f35e07ed82271885bae50d2ab2c8a07b97a7295f189fbc899c79'
HELPER=ROOT/'tools/quality/architecture/PublicMainClassDigestAudit.java'

def validate(observed,expected):
    if observed!=expected:raise ValueError('exact independent public artifact/source/finding proof required')

def main():
    invocation=capture(Path(__file__));assert not OUT.exists() and not SLOT.exists()
    c=data.common;subject=c.read_checked(SUBJECT/'manifest.json',SUBJECT_SHA)
    assert subject['actualExit']==0 and subject['source']==SOURCE and subject['artifactSource']==data.ARTIFACT_SOURCE
    assert subject['actualSecretCount'] is None and not subject['currentSourceWholeG07Qualified']
    registry=c.read_checked(SUBJECT/'public-old-main-class-proofs.json',subject['registrySha256'])
    updates=c.read_checked(SUBJECT/'updates.json',subject['updatesSha256']);v=data.inputs();hashes=v['sourceHashes']
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=ROOT)==b''
    # Independent Git cat-file batch, not producer's tar parser; fixed public Main paths only.
    paths=sorted(hashes)
    raw=subprocess.check_output(['git','cat-file','--batch'],cwd=ROOT,
      input=''.join(data.ARTIFACT_SOURCE+':'+p+'\n' for p in paths).encode())
    cursor=0
    for path in paths:
        end=raw.index(b'\n',cursor);header=raw[cursor:end].split();assert len(header)==3 and header[1]==b'blob'
        size=int(header[2]);cursor=end+1;body=raw[cursor:cursor+size]
        assert len(body)==size and c.sha(body)==hashes[path] and raw[cursor+size:cursor+size+1]==b'\n'
        cursor+=size+1
        file=data.NORMAL/path
        assert file.resolve()==file and not file.is_symlink() and c.sha(file.read_bytes())==hashes[path]
    assert cursor==len(raw)
    os.umask(0o077);SLOT.mkdir();classes=SLOT/'reader';classes.mkdir();catalog=SLOT/'normal-jars.tsv'
    jars={module:data.jar(module,item) for module,item in sorted(v['normal']['jars'].items())}
    with catalog.open('x') as stream:
        for module,path in jars.items():stream.write(module+'\t'+str(path)+'\n')
    helper_sha=c.sha(HELPER.read_bytes());steps.SLOT=SLOT;jdk=ROOT.parent/'toolchain/jdk-25.0.4/bin'
    stages=[steps.step('compile-class-reader',[str(jdk/'javac'),'--release','25','-proc:none','-Xlint:all','-Werror','-d',str(classes),str(HELPER)])]
    assert stages[0]['actualExit']==0 and not stages[0]['timedOut']
    stages.append(steps.step('read-old-normal-main-classes',[str(jdk/'java'),'-cp',str(classes),HELPER.stem,str(data.NORMAL),str(catalog)]))
    assert stages[-1]['actualExit']==0 and not stages[-1]['timedOut']
    lines=(SLOT/'read-old-normal-main-classes.stdout').read_text().splitlines();assert lines[0]=='SELFTEST\t6'
    observed={};names=set();source_paths=set()
    for line in lines[1:]:
        module,entry,name,sourcefile,digest=line.split('\t')
        assert module in jars and entry==name+'.class' and name not in names and digest not in observed;names.add(name)
        path='src/schubert-nk-'+module+'/src/main/java/'+name.rpartition('/')[0]+'/'+sourcefile
        assert path in hashes;source_paths.add(path)
        observed[digest]=dict(proofKind='PUBLIC_OLD_NORMAL_HOST_COMPILED_MAIN_CLASS_SHA256',
          artifactSource=data.ARTIFACT_SOURCE,normalManifestSha256=data.NORMAL_SHA,module=module,
          jarSha256=v['normal']['jars'][module]['sha256'],jarEntry=entry,className=name,sourcePath=path,sourceSha256=hashes[path],sha256=digest)
    assert source_paths==set(hashes) and len(hashes)==922
    validate(registry,[observed[k] for k in sorted(observed)])
    assert all(c.sha(path.read_bytes())==v['normal']['jars'][module]['sha256'] for module,path in jars.items())
    known=set(v['oldProofs'])|set(observed);fresh=set(observed)-set(v['oldProofs'])
    # Literal proof-set oracle: unknown, empty and old-only remain unclassified.
    def admissible(values,all_proofs,new_proofs):return bool(values) and values<=all_proofs and bool(values&new_proofs)
    assert admissible({'a','b'},{'a','b','old'},{'a','b'})
    assert admissible({'a','old'},{'a','b','old'},{'a','b'})
    assert not admissible(set(),{'a'},{'a'}) and not admissible({'old'},{'old','a'},{'a'})
    assert not admissible({'a','unknown'},{'a'},{'a'}) and not admissible({'unknown'},{'a'},{'a'})
    patterns={name:re.compile(rule['regex'],re.ASCII) for name,rule in v['rules'].items()}
    cache={};expected=[];remaining=Counter()
    for row in v['pending']:
        path=row['path']
        if path not in cache:
            text=c.finding_text(row,v['inventory'])
            cache[path]=None if any(ch in text for ch in '\v\f\r\x1c\x1d\x1e\x85\u2028\u2029') else text.splitlines(keepends=True)
        if cache[path] is None:remaining['UNSUPPORTED_LINE_SEPARATOR']+=1;continue
        low=max(0,row['startLine']-2);window=''.join(cache[path][low:min(len(cache[path]),row['endLine']+1)])
        values=set()
        for match in patterns[row['ruleId']].finditer(window):
            begin,end=match.span(1)
            first=low+1+window[:begin].count('\n');last=low+1+window[:end].count('\n')
            if row['startLine']<=first and last<=row['endLine']:values.add(match.group(1))
        if not admissible(values,known,fresh):
            remaining['NO_EXACT_CAPTURE' if not values else 'CAPTURE_UNPROVEN_OR_NO_NEW_OLD_HOST_PROOF']+=1;continue
        expected.append(dict(**{k:row[k] for k in ('path','ruleId','startLine','endLine','inputSha256')},
          disposition='FALSE_POSITIVE_ALL_EXACT_CAPTURES_PUBLIC_ARTIFACT_DIGESTS',priorDisposition='UNCLASSIFIED',
          exactCaptureCount=len(values),newOldHostClassProofCount=len(values&fresh),publicArtifactProofRefs=sorted(values)))
    validate(updates,expected)
    assert Counter(map(c.key,updates))<=Counter(map(c.key,v['pending']))
    assert len(updates)==subject['additionalFalsePositives'] and len(updates)+sum(remaining.values())==4550
    assert dict(remaining)==subject['remainingReasons'] and sum(remaining.values())==subject['remainingUnclassified']
    assert subject['cumulativeFalsePositiveProof']==35536+len(updates)
    rejected=[]
    for label,edit in (('digest',lambda x:x[0].update(sha256='0'*64)),
      ('artifact-source',lambda x:x[0].update(artifactSource=SOURCE)),
      ('jar',lambda x:x[0].update(jarSha256='0'*64)),('source',lambda x:x[0].update(sourceSha256='0'*64)),
      ('SourceFile',lambda x:x[0].update(sourcePath='src/Other.java')),('missing',lambda x:x.pop()),
      ('duplicate',lambda x:x.append(copy.deepcopy(x[0]))),('runtime-invented',lambda x:x[0].update(targetRuntimeInvocations=1))):
        changed=copy.deepcopy(registry);edit(changed)
        try:validate(changed,registry)
        except ValueError:rejected.append(label)
        else:raise AssertionError('invalid registry proof accepted')
    if updates:
        for label,edit in (('range',lambda x:x[0].update(startLine=x[0]['startLine']+1)),
          ('proof-omitted',lambda x:x[0]['publicArtifactProofRefs'].pop()),('capture-count',lambda x:x[0].update(exactCaptureCount=0)),
          ('duplicate-finding',lambda x:x.append(copy.deepcopy(x[0])))):
            changed=copy.deepcopy(updates);edit(changed)
            try:validate(changed,updates)
            except ValueError:rejected.append(label)
            else:raise AssertionError('invalid finding proof accepted')
    assert helper_sha==c.sha(HELPER.read_bytes()) and all(p.name.startswith(HELPER.stem) for p in classes.rglob('*.class'))
    verify(invocation);OUT.mkdir()
    value=dict(actualExit=0,source=SOURCE,artifactSource=data.ARTIFACT_SOURCE,historicalScanSource=c.HISTORICAL,contentCommit=c.CONTENT,
      timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,subjectManifestSha256=SUBJECT_SHA,specSha256=data.SPEC_SHA,
      helperSha256=helper_sha,stages=stages,independentGitSourceMethod='LIMITED_CAT_FILE_BATCH_922_PUBLIC_MAIN_SOURCE_BLOBS',
      independentMainClasses=len(observed),independentMainSourceFiles=len(hashes),classFileVectors=6,proofSetVectors=6,
      metadataCounterexamples=rejected,additionalFalsePositives=len(updates),cumulativeFalsePositiveProof=35536+len(updates),
      remainingUnclassified=sum(remaining.values()),originalFindingMultiplicityPreserved=True,actualSecretCount=None,
      currentSourceWholeG07Qualified=False,productTestsExecuted=0,newTestIds=0,newMain=0,coverage=None,
      formalUpdated=False,newAccepted=0,effortPercent=None,targetClassLoading=0,targetRuntimeInvocations=0,
      privateRawRead=False,nativeArtifactRead=False,scannerExecuted=False,wholeScanReplayed=False)
    c.write(SLOT/'manifest.safe.json',value);c.write(OUT/'manifest.json',value)
    print(json.dumps({k:value[k] for k in ('actualExit','independentMainClasses','additionalFalsePositives','remainingUnclassified')}))
    print('manifestSha256='+c.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
