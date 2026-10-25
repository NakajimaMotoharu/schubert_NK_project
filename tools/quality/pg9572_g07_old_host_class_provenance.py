"""Bind historical residual captures to existing old NORMAL host class bytes and public Git source."""
from collections import Counter
import datetime as dt
import io
import json
import os
from pathlib import Path
import re
import subprocess
import tarfile
import zipfile
import class_reference_metadata as classfile
import g07_old_host_inputs as data
from public_java_digest_provenance import captures
from host_tool_invocation import capture,verify

ROOT=data.ROOT;BASE=data.BASE;SOURCE=data.SOURCE
OUT=BASE/'PG9572-g07-old-host-main-class-provenance-v1'
SLOT=ROOT.parent/'pgpt-runs/PG379/pg9572-g07-old-host-main-class-provenance-v1'

def main():
    invocation=capture(Path(__file__));assert not OUT.exists() and not SLOT.exists()
    v=data.inputs();hashes=v['sourceHashes'];c=data.common
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=ROOT)==b''
    subprocess.run(['git','merge-base','--is-ancestor',data.ARTIFACT_SOURCE,SOURCE],cwd=ROOT,check=True)
    # Public source files only, in-memory archive; no extraction or old tests/build replay.
    archived=subprocess.check_output(['git','archive','--format=tar',data.ARTIFACT_SOURCE,'--',*sorted(hashes)],cwd=ROOT)
    git_sources={}
    with tarfile.open(fileobj=io.BytesIO(archived)) as archive:
        for member in archive.getmembers():
            if member.isdir():continue
            assert member.isfile() and member.name in hashes
            stream=archive.extractfile(member);assert stream is not None
            git_sources[member.name]=c.sha(stream.read())
    assert git_sources==hashes
    for path,digest in hashes.items():
        file=data.NORMAL/path
        assert file.resolve()==file and not file.is_symlink() and c.sha(file.read_bytes())==digest
    os.umask(0o077);SLOT.mkdir()
    c.write(SLOT/'begin.safe.json',dict(source=SOURCE,artifactSource=data.ARTIFACT_SOURCE,
      startUTC=dt.datetime.now(dt.timezone.utc).isoformat(),ownerPid=os.getpid(),normalManifestSha256=data.NORMAL_SHA,
      specSha256=data.SPEC_SHA,actualTargetActions=0,actualNativeActions=0))
    registry={};names=set();source_paths=set()
    for module,item in sorted(v['normal']['jars'].items()):
        jar=data.jar(module,item)
        with zipfile.ZipFile(jar) as archive:
            entries=sorted(n for n in archive.namelist() if n.endswith('.class'))
            assert len(entries)==len(set(entries))
            for entry in entries:
                raw=archive.read(entry);value=classfile.read(raw);name=value['className']
                assert entry==name+'.class' and name.startswith('dev/codex/schubert/nk/') and name not in names
                names.add(name)
                path='src/schubert-nk-'+module+'/src/main/java/'+name.rpartition('/')[0]+'/'+value['sourceFile']
                assert path in hashes;source_paths.add(path);digest=c.sha(raw);assert digest not in registry
                registry[digest]=dict(proofKind='PUBLIC_OLD_NORMAL_HOST_COMPILED_MAIN_CLASS_SHA256',
                  artifactSource=data.ARTIFACT_SOURCE,normalManifestSha256=data.NORMAL_SHA,module=module,
                  jarSha256=item['sha256'],jarEntry=entry,className=name,sourcePath=path,sourceSha256=hashes[path],sha256=digest)
        assert c.sha(jar.read_bytes())==item['sha256']
    assert source_paths==set(hashes)
    proofs=dict(v['oldProofs'])
    for digest,p in registry.items():proofs.setdefault(digest,p)
    fresh=set(registry)-set(v['oldProofs']);rules={k:re.compile(r['regex'],re.ASCII) for k,r in v['rules'].items()}
    cache={};updates=[];remaining=Counter()
    for row in v['pending']:
        path=row['path']
        if path not in cache:
            text=c.finding_text(row,v['inventory'])
            cache[path]=None if any(ch in text for ch in '\v\f\r\x1c\x1d\x1e\x85\u2028\u2029') else text.splitlines(keepends=True)
        if cache[path] is None:remaining['UNSUPPORTED_LINE_SEPARATOR']+=1;continue
        values=captures(cache[path],row,rules[row['ruleId']])
        if not values or not values<=set(proofs) or not values&fresh:
            remaining['NO_EXACT_CAPTURE' if not values else 'CAPTURE_UNPROVEN_OR_NO_NEW_OLD_HOST_PROOF']+=1;continue
        updates.append(dict(**{k:row[k] for k in ('path','ruleId','startLine','endLine','inputSha256')},
          disposition='FALSE_POSITIVE_ALL_EXACT_CAPTURES_PUBLIC_ARTIFACT_DIGESTS',priorDisposition='UNCLASSIFIED',
          exactCaptureCount=len(values),newOldHostClassProofCount=len(values&fresh),
          publicArtifactProofRefs=sorted(values)))
    assert len(updates)+sum(remaining.values())==4550 and Counter(map(c.key,updates))<=Counter(map(c.key,v['pending']))
    verify(invocation);OUT.mkdir()
    c.write(OUT/'public-old-main-class-proofs.json',[registry[k] for k in sorted(registry)])
    c.write(OUT/'updates.json',updates)
    value=dict(actualExit=0,source=SOURCE,artifactSource=data.ARTIFACT_SOURCE,historicalScanSource=c.HISTORICAL,contentCommit=c.CONTENT,
      timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,specSha256=data.SPEC_SHA,
      normalManifestSha256=data.NORMAL_SHA,publicMainClasses=len(registry),publicMainSourceFiles=len(hashes),
      publicSourceHashMethod='LIMITED_GIT_ARCHIVE_IN_MEMORY_922_MAIN_SOURCES_NO_EXTRACTION',
      registrySha256=c.sha((OUT/'public-old-main-class-proofs.json').read_bytes()),updatesSha256=c.sha((OUT/'updates.json').read_bytes()),
      originalFindingCount=40086,priorPublicProofs=35536,priorUnclassified=4550,additionalFalsePositives=len(updates),
      cumulativeFalsePositiveProof=35536+len(updates),remainingUnclassified=sum(remaining.values()),remainingReasons=dict(remaining),
      originalMultiplicityPreserved=True,proofRefsResolveToPriorOrThisRegistry=True,candidateValuesPersisted=False,
      actualSecretCount=None,currentSourceWholeG07Qualified=False,productTestsExecuted=0,newTestIds=0,newMain=0,
      coverage=None,formalUpdated=False,newAccepted=0,effortPercent=None,targetClassLoading=0,targetRuntimeInvocations=0,
      privateRawRead=False,nativeArtifactRead=False,scannerExecuted=False,wholeScanReplayed=False)
    c.write(SLOT/'manifest.safe.json',value);c.write(OUT/'manifest.json',value)
    print(json.dumps({k:value[k] for k in ('actualExit','publicMainClasses','publicMainSourceFiles','additionalFalsePositives','remainingUnclassified')}))
    print('manifestSha256='+c.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
