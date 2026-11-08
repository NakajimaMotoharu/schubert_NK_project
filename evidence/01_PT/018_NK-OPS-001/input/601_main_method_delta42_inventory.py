"""Reuse identical compiled metadata; decode only current normal delta, not runtime artifacts."""
from pathlib import Path
from collections import Counter
from copy import deepcopy
import datetime
import hashlib
import importlib.util
import json
import subprocess
import zipfile

R=Path(__file__).resolve().parents[4]
B=R/'evidence/01_PT/018_NK-OPS-001'
C=B/'input/599_main_method_delta42_scope.json'
O=B/'evidence/PG23972-current-main-method-delta42-v1'
load=lambda p:json.loads(p.read_bytes())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')


def checked(ref):
    p=Path(ref['path'])
    p=p if p.is_absolute() else R/p
    assert sha(p)==ref['sha256']
    return load(p)


def main():
    assert not O.exists()
    cfg=load(C)
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()==cfg['observerHead']
    old_manifest=checked(cfg['oldManifest'])
    old_rows={v['physicalKey']:v for v in checked(cfg['oldClassInventory'])}
    old_post=checked(cfg['oldIndependent'])
    assert old_manifest['actualExit']==old_post['actualExit']==0
    assert old_post['parentManifestSha256']==cfg['oldManifest']['sha256']
    normal=checked(cfg['normalManifest'])
    identity=checked(cfg['sourceIdentity'])
    assert normal['actualExit']==normal['testsExecuted']==0 and normal['source']==cfg['source']
    assert identity['actualExit']==0 and identity['productionMainSource']==cfg['source']
    normal_index=checked(cfg['currentIndex'])
    current={v['path'].split('/')[1].removeprefix('schubert-nk-')+':'+name+'.class':v for name,v in normal_index.items()}
    source_hashes={n:h for n,h in normal['begin']['inputHashes'].items() if n.startswith('src/') and '/src/main/java/' in n and n.endswith('.java')}
    artifacts={v['path']:v for v in checked(cfg['wbsInventory'])['artifacts']}
    held=set(cfg['heldClassEntryKeys']);reuse=set(cfg['reusedClassKeys']);delta=set(cfg['deltaClassKeys'])
    assert len(current)==1845 and len(source_hashes)==967 and set(v['path'] for v in current.values())==set(source_hashes)
    assert held==set(old_manifest['heldClasses']) and len(held)==2
    assert len(reuse)==1801 and len(delta)==42 and held|reuse|delta==set(current)
    assert not (held&reuse or held&delta or reuse&delta)
    assert not any(any(t in k for t in ['FingerprintKeyRing','ResponseSnapshotCodec','TemporaryInfrastructureException','WebStartupException']) for k in delta)
    assert len(set(current)-set(old_rows))==2 and not set(old_rows)-set(current)
    for key in reuse:assert old_rows[key]['classSha256']==current[key]['sha256'] and old_rows[key]['structure'] is not None
    qualification=checked(cfg['decoderQualification'])
    assert qualification['actualExit']==0 and qualification['parserVectors']==35
    assert qualification['independentParserSha256']==cfg['decoder']['sha256']=='2227e1e8df1ff91b606f094c7ee64366023273ca740d4d47126ed0928190e2f0'
    decoder_path=R/cfg['decoder']['path'];assert sha(decoder_path)==cfg['decoder']['sha256']
    spec=importlib.util.spec_from_file_location('qualified_class_metadata_decoder_only',decoder_path)
    decoder=importlib.util.module_from_spec(spec);spec.loader.exec_module(decoder)
    rows=[];decoded=[];observed=set()
    for module,jar in sorted(normal['jars'].items()):
        path=Path(jar['path']);assert not path.is_symlink() and sha(path)==jar['sha256']
        with zipfile.ZipFile(path) as archive:
            for entry in sorted(n for n in archive.namelist() if n.endswith('.class')):
                key=module+':'+entry
                assert key in current and key not in observed
                observed.add(key)
                # Do not read, hash or parse either held member. Container identity is separate.
                if key in held:
                    model,digest,status,origin=None,None,'UNOBSERVED_HOLD_GRAPH9','HELD_NOT_READ_HASHED_OR_PARSED'
                elif key in reuse:
                    model=deepcopy(old_rows[key]['structure']);digest=old_rows[key]['classSha256']
                    status,origin='STATIC_METADATA_NOT_RUNTIME_OR_COVERAGE','REUSED_EXACT_CLASS_BYTE_METADATA_NOT_RUNTIME'
                else:
                    assert key in delta
                    raw=archive.read(entry)
                    digest=hashlib.sha256(raw).hexdigest()
                    assert digest==current[key]['sha256']
                    model=decoder.decode(raw,entry)
                    decoded.append(key)
                    status,origin='STATIC_METADATA_NOT_RUNTIME_OR_COVERAGE','CURRENT_NORMAL_DELTA_READONLY_DECODE'
                source_path=current[key]['path'];owner=artifacts[source_path]
                if model is not None:assert model['sourceFile']==Path(source_path).name
                rows.append(dict(physicalKey=key,sourcePath=source_path,sourceSha256=source_hashes[source_path],
                                 owner=owner['owner'],costOwner=owner['costOwner'],
                                 ownershipMeaning='SOURCE_RESPONSIBILITY_NOT_METHOD_ORACLE_TRACE',
                                 classSha256=digest,metadataStatus=status,metadataProvenance=origin,structure=model,
                                 methodTestRequirementTrace='NOT_VERIFIED',coverage=None,accepted=False))
    assert observed==set(current) and set(decoded)==delta and len(decoded)==42
    counts=Counter(v['sourcePath'] for v in rows)
    assert set(counts)==set(source_hashes)
    sources=[dict(path=n,sha256=source_hashes[n],physicalClasses=counts[n],
                  heldPhysicalClasses=sum(v['sourcePath']==n and v['structure'] is None for v in rows),
                  exactMethodTrace='NOT_VERIFIED') for n in sorted(source_hashes)]
    methods=[v for row in rows if row['structure'] is not None for v in row['structure']['methods']]
    for jar in normal['jars'].values():assert sha(Path(jar['path']))==jar['sha256']
    O.mkdir();write(O/'class-method-inventory.json',rows);write(O/'source-denominator.json',sources)
    write(O/'delta-entries.json',sorted(delta))
    result=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=cfg['source'],
                config=dict(path=str(C.relative_to(R)),sha256=sha(C)),oldManifest=cfg['oldManifest'],normalManifest=cfg['normalManifest'],
                sourceIdentity=cfg['sourceIdentity'],oldIndependent=cfg['oldIndependent'],
                sourceFiles=967,physicalClasses=1845,knownMetadataClasses=1843,reusedMetadataClasses=1801,
                decodedDeltaClasses=42,heldClasses=sorted(held),addedPhysicalClasses=2,removedPhysicalClasses=0,
                changedExistingClassBytes=40,observedMethods=len(methods),
                codeMethodsObserved=sum(v['hasCode'] for v in methods),noCodeMethodsObserved=sum(not v['hasCode'] for v in methods),
                previousKnownMethodMetadataCount=old_manifest['methodsObserved'],
                knownMethodMetadataDelta=len(methods)-old_manifest['methodsObserved'],
                methodsOfHeldClasses=None,totalMethodDenominatorComplete=False,sourceFilesWithoutPhysicalClass=0,
                files={p.name:sha(p) for p in O.iterdir() if p.is_file()},heldEntriesReadOrHashed=False,
                automaticGeneratedCodeExclusions=False,targetClassesDefinedInitializedOrInvoked=False,
                currentCoverageComputed=False,productTestsExecuted=0,compilerOrJvmExecuted=False,actualBackendActions=0,
                oldRuntimeTransferred=False,wholeG13Accepted=False,whole451Accepted=False,
                newAcceptance=0,formalUpdated=False,effortRate=None,
                tool=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(Path(__file__))))
    write(O/'manifest.json',result)
    print(json.dumps(dict(actualExit=0,reusedClasses=1801,decodedDelta=42,knownMethodMetadata=len(methods),methodMetadataDelta=result['knownMethodMetadataDelta'],heldMethodDenominator=None,manifestSha256=sha(O/'manifest.json'))))


if __name__=='__main__':
    main()
