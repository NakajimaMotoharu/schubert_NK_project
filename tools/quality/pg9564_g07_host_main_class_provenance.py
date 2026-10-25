"""Classify exact historical G07 captures only by actual public normal-host Main class digests."""
from collections import Counter
import datetime as dt
import os
from pathlib import Path
import re
import subprocess
import zipfile
import class_reference_metadata as classfile
import g07_host_class_provenance_inputs as data
from public_java_digest_provenance import captures,proven_set
from host_tool_invocation import capture,verify

ROOT=data.ROOT;BASE=data.BASE;SOURCE=data.SOURCE
OUT=BASE/'PG9564-g07-host-main-class-provenance-v1'
SLOT=ROOT.parent/'pgpt-runs/PG379/pg9564-g07-host-main-class-provenance-v1'
SPEC=ROOT/'evidence/01_PT/018_NK-OPS-001/1938_G07HostMainDigest_公開artifact根拠仕様.md'
SPEC_SHA='81221cf1bfb7f71d15f9b6816e6db019940cdad86dd8576f235c1bf6169a7bf9'
LINE_SEPARATORS='\v\f\r\x1c\x1d\x1e\x85\u2028\u2029'

def main():
    invocation=capture(Path(__file__));assert not OUT.exists() and not SLOT.exists()
    assert data.sha(SPEC.read_bytes())==SPEC_SHA
    inputs=data.inputs();normal=inputs['manifests']['normal'];main_map=inputs['mainMap'];hashes=normal['begin']['inputHashes']
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=ROOT)==b''
    assert len(main_map)==1843 and len({x['path'] for x in main_map.values()})==965
    os.umask(0o077);SLOT.mkdir()
    data.write(SLOT/'begin.safe.json',dict(source=SOURCE,ownerPid=os.getpid(),timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),
      historicalScanSource=data.HISTORICAL,contentCommit=data.CONTENT,inputPins=data.PINS,sourceProof='NORMAL_HOST_BUILD_ONLY',
      candidateValuesPersisted=False,scannerExecuted=False,targetRuntimeInvocations=0))
    registry={};names=set();source_proofs={};jar_proofs={}
    for module,jar in sorted(normal['jars'].items()):
        path=data.regular_normal_jar(module,jar);jar_proofs[module]=dict(path=str(path),sha256=jar['sha256'])
        with zipfile.ZipFile(path) as archive:
            entries=sorted(n for n in archive.namelist() if n.endswith('.class'))
            assert len(entries)==len(set(entries))
            for entry in entries:
                raw=archive.read(entry);actual=classfile.read(raw);name=actual['className']
                assert name not in names and name+'.class'==entry;names.add(name)
                reference=main_map[name];source_path='src/schubert-nk-'+module+'/src/main/java/'+name.rpartition('/')[0]+'/'+actual['sourceFile']
                assert reference['module']==module and reference['path']==source_path and reference['sha256']==data.sha(raw)
                if source_path not in source_proofs:
                    assert data.sha((ROOT/source_path).read_bytes())==hashes[source_path]==data.sha((data.NORMAL/source_path).read_bytes())
                    source_proofs[source_path]=hashes[source_path]
                digest=data.sha(raw);assert digest not in registry
                registry[digest]=dict(proofKind='PUBLIC_NORMAL_HOST_COMPILED_MAIN_CLASS_SHA256',source=SOURCE,
                  normalManifestSha256=data.PINS['normal'][1],module=module,jarSha256=jar['sha256'],jarEntry=entry,
                  className=name,sourcePath=source_path,sourceSha256=hashes[source_path],sha256=digest)
        assert data.sha(path.read_bytes())==jar['sha256']
    assert names==set(main_map) and len(registry)==1843 and len(source_proofs)==965
    # Independent literal hash oracle and closed proof-set semantics; no real candidate is output.
    assert data.sha(b'abc')=='ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'
    fixture={'public-a':dict(proof='A'),'public-b':dict(proof='B')}
    assert proven_set({'public-a','public-b'},fixture)==[dict(proof='A'),dict(proof='B')]
    assert proven_set({'public-a','unknown'},fixture) is None and proven_set(set(),fixture) is None
    proofs=dict(inputs['oldProofs'])
    for digest,proof in registry.items():proofs.setdefault(digest,proof)
    rules={n:re.compile(r['regex'],re.ASCII) for n,r in inputs['rules'].items()}
    text_cache={};updates=[];unclassified=Counter();unknown_inputs=set()
    for row in inputs['pending']:
        path=row['path']
        if path not in text_cache:
            text=data.finding_text(row,inputs['inventory'])
            text_cache[path]=None if any(ch in text for ch in LINE_SEPARATORS) else text.splitlines(keepends=True)
        lines=text_cache[path]
        if lines is None:
            unclassified['UNSUPPORTED_LINE_SEPARATOR_REQUIRES_SEPARATE_POSITION_PROOF']+=1;unknown_inputs.add(path);continue
        values=captures(lines,row,rules[row['ruleId']])
        bound=proven_set(values,proofs)
        fresh=values & (set(registry)-set(inputs['oldProofs']))
        if bound is None or not fresh:
            unclassified['NO_EXACT_CAPTURE' if not values else 'AT_LEAST_ONE_CAPTURE_UNPROVEN_OR_NO_NEW_MAIN_PROOF']+=1;continue
        fields={k:row[k] for k in ('path','ruleId','startLine','endLine','inputSha256')}
        updates.append(dict(**fields,disposition='FALSE_POSITIVE_ALL_EXACT_CAPTURES_PUBLIC_ARTIFACT_DIGESTS',
          reason='ALL_EXACT_CAPTURES_BOUND_IN_REPORTED_RANGE_AT_LEAST_ONE_ACTUAL_NORMAL_HOST_MAIN_CLASS_PROOF',
          priorDisposition='UNCLASSIFIED',exactCaptureCount=len(values),newMainClassProofCount=len(fresh),publicArtifactProofs=bound))
    assert len(updates)+sum(unclassified.values())==8379
    assert Counter(map(data.key,updates))<=Counter(map(data.key,inputs['pending']))
    assert all(data.sha((ROOT/p).read_bytes())==digest for p,digest in source_proofs.items())
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=ROOT)==b''
    verify(invocation);OUT.mkdir()
    data.write(OUT/'public-main-class-proofs.json',[registry[k] for k in sorted(registry)])
    data.write(OUT/'updates.json',updates)
    value=dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
      specSha256=SPEC_SHA,inputPins=data.PINS,historicalScanSource=data.HISTORICAL,contentCommit=data.CONTENT,
      sourceArtifactProofScope='CURRENT_PUBLIC_NORMAL_HOST_MAIN_BYTES_NOT_NATIVE_OR_PRODUCT_TEST_RESULTS',
      publicMainClasses=1843,publicMainSourceFiles=965,normalJarProofs=jar_proofs,independentLiteralProofSetVectors=4,
      originalFindingCount=40086,priorPublicProofs=31707,priorUnclassified=8379,additionalFalsePositives=len(updates),
      cumulativeFalsePositiveProof=31707+len(updates),remainingUnclassified=sum(unclassified.values()),
      remainingReasons=dict(unclassified),unsupportedLineSeparatorInputs=sorted(unknown_inputs),
      publicClassProofsSha256=data.sha((OUT/'public-main-class-proofs.json').read_bytes()),
      updatesSha256=data.sha((OUT/'updates.json').read_bytes()),originalFindingMultiplicityPreserved=True,
      candidateValuesOrStandaloneCandidateHashesPersisted=False,scannerExecuted=False,wholeScanReplayed=False,
      ancestorWholeHashReplayed=False,nativeArtifactOrPrivateRawRead=False,actualSecretCount=None,
      productTestsExecuted=0,productCoverage=None,newTestIds=0,newMain=0,whole451SecretGateAccepted=False,
      currentSourceWholeG07Qualified=False,formalUpdated=False,newAccepted=0,effortPercent=None)
    data.write(SLOT/'manifest.safe.json',value);data.write(OUT/'manifest.json',value)
    print(__import__('json').dumps({k:value[k] for k in ('actualExit','additionalFalsePositives','remainingUnclassified','publicMainClasses')}),flush=True)
    print('manifestSha256='+data.sha((OUT/'manifest.json').read_bytes()),flush=True)

if __name__=='__main__':main()
