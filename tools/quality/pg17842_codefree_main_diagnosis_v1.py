"""Code-free whole-Source diagnosis; passive class bytes, never a Product class definition."""
import zipfile
from pathlib import Path, PurePosixPath
import g07_host_class_provenance_inputs as data
import classfile_code_metadata as code
from host_tool_invocation import capture,verify
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
NORMAL_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
REG_SHA='8110527ffbaa8152c358418fab5b113f48ec2568bde424778766d2a66c395d2c'
OUT=data.BASE/'PG17842-codefree-main-diagnosis-v1'
EXCLUDED=[
'dev/codex/schubert/nk/batch/file/RootFailed',
'dev/codex/schubert/nk/api/error/TemporaryInfrastructureException',
'dev/codex/schubert/nk/web/bootstrap/WebStartupException',
'dev/codex/schubert/nk/api/idempotency/FingerprintKeyRing',
'dev/codex/schubert/nk/api/idempotency/ResponseSnapshotCodec',
'dev/codex/schubert/nk/bootstrap/ServiceStartupAdmission$NativeGate',
'dev/codex/schubert/nk/bootstrap/ServiceStartupAdmission$NativeObservation',
'dev/codex/schubert/nk/bootstrap/ChildStartupContext$NativeIo',
'dev/codex/schubert/nk/api/bootstrap/ApiProcessLifetime',
'dev/codex/schubert/nk/api/file/ServiceProcessResources',
'dev/codex/schubert/nk/storage/ServiceConfigFiles$NioIo']
def codefree(rows):
    return bool(rows) and all((r['flags']&0x0600)==0x0600 and all(not m['hasCode'] and not(m['flags']&0x0100) and bool(m['flags']&0x0400) for m in r['methods']) for r in rows.values())
def main():
    invocation=capture(__file__);assert not OUT.exists()
    assert data.sha((data.ROOT/'tools/quality/classfile_code_metadata.py').read_bytes())=='2227e1e8df1ff91b606f094c7ee64366023273ca740d4d47126ed0928190e2f0'
    selftest=code.selftest();code_vectors=code.code_vectors()
    positive={'p/I':dict(flags=1537,methods=[dict(flags=1025,hasCode=False)])};assert codefree(positive)
    negatives=[{}, {'p/I':dict(flags=33,methods=[])},{'p/I':dict(flags=1537,methods=[dict(flags=9,hasCode=True)])},{'p/I':dict(flags=1537,methods=[dict(flags=1281,hasCode=False)])},{'p/I':dict(flags=1537,methods=[dict(flags=1,hasCode=False)])}]
    assert all(not codefree(v) for v in negatives)
    compile=data.ROOT.parent/'pgpt-runs/PG379/pg14216-typed-marker-guard-six-compile-v1'
    normal=data.read_checked(compile/'manifest.safe.json',NORMAL_SHA)
    registry=data.read_checked(data.BASE/'PG17825-current2827-admission-joint-registry-v2/manifest.json',REG_SHA)
    assert normal['source']==registry['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==registry['actualExit']==0
    units={};skipped=[];decoded=0;all_entries=0
    for module,item in normal['jars'].items():
        jarpath=Path(item['path'])
        assert data.sha(jarpath.read_bytes())==item['sha256']
        with zipfile.ZipFile(jarpath) as jar:
            names=[n[:-6] for n in jar.namelist() if n.endswith('.class')];all_entries+=len(names)
            excluded_outer={n.split('$',1)[0] for n in names if any(n.startswith(p) for p in EXCLUDED)}
            for name in names:
                if name.split('$',1)[0] in excluded_outer:
                    skipped.append(name);continue
                blob=jar.read(name+'.class');value=code.decode(blob,name+'.class');decoded+=1
                sf=value['sourceFile'];assert PurePosixPath(sf).name==sf and sf.endswith('.java')
                path='src/schubert-nk-'+module+'/src/main/java/'+name.rsplit('/',1)[0]+'/'+sf
                assert path in normal['begin']['inputHashes']
                unit=units.setdefault(path,dict(module=module,physical={},metadata={}))
                unit['physical'][name]=data.sha(blob);unit['metadata'][name]=value
    assert all_entries==1843 and decoded+len(skipped)==all_entries
    candidates={};existing={}
    for path,unit in units.items():
        if not codefree(unit['metadata']):continue
        pin=normal['begin']['inputHashes'][path]
        assert data.sha((data.ROOT/path).read_bytes())==data.sha((compile/'snapshot'/path).read_bytes())==pin
        outer=path.split('/src/main/java/',1)[1][:-5]
        unit.update(sourceSha256=pin,sourceOuter=outer,coverageCounterMeasurement=None,productCodeExecuted=False,wholeSourceClosure=True)
        if outer in registry['fullSourceUnits']:existing[path]=unit
        else:candidates[path]=unit
    verify(normal['begin']['invocation']);verify(registry['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,normalManifestSha256=NORMAL_SHA,registryManifestSha256=REG_SHA,decoderSha256='2227e1e8df1ff91b606f094c7ee64366023273ca740d4d47126ed0928190e2f0',decoderSelftestChecks=selftest,decoderCodeAttributeChecks=code_vectors,codefreeNegativeVectors=len(negatives),allNormalPhysical=all_entries,decodedNonHeldPhysical=decoded,excludedPolicyFamilyNames=skipped,exclusionBeforeClassBytes=True,newCodefreeCandidates=candidates,alreadyReferencedCodefree=existing,newCandidateSources=len(candidates),newCandidatePhysical=sum(len(v['physical']) for v in candidates.values()),productClassesLoaded=False,productTestsExecuted=0,jvmCommandsIssued=0,compilerCommandsIssued=0,actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,coverageCountersMeasured=False,javaCounterCoverageClaimed=False,registryChanged=False,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()));print('new code-free candidates',len(candidates))
if __name__=='__main__':main()
