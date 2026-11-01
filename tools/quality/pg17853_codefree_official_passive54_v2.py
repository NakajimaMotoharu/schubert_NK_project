"""Official JaCoCo zero-counter check for fixed code-free declarations; no Product replay."""
import os
from pathlib import Path
import shutil
import zipfile
import g07_host_class_provenance_inputs as data
import pg9666_pagination_static as runner
import jacoco_readonly_exec_subset as execution
from host_tool_invocation import capture,verify
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
DIAG='04763edb92a176b5c043b191af2266e281947590805c17cbf8d264e0c7b1b04d'
RAW='6eddd61a889e0ebb85a9f1eb3451ace5a272c803e1ee3b606cada04a21203f8e'
OUT=data.BASE/'PG17853-codefree-official-passive54-v2'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg17853-codefree-official-passive54-v2'
RUN=data.ROOT.parent/'pgpt-runs/PG379/pg17816-admission-actual-wait-five-pt-v1'
def main():
    invocation=capture(__file__);assert not OUT.exists() and not SLOT.exists()
    diag=data.read_checked(data.BASE/'PG17842-codefree-main-diagnosis-v1/manifest.json',DIAG)
    raw=data.read_checked(RUN/'manifest.safe.json',RAW)
    normal_path=data.ROOT.parent/'pgpt-runs/PG379/pg14216-typed-marker-guard-six-compile-v1'
    normal=data.read_checked(normal_path/'manifest.safe.json',diag['normalManifestSha256'])
    assert diag['source']==raw['source']==normal['source']==SOURCE and diag['actualExit']==raw['actualExit']==normal['actualExit']==0
    assert diag['newCandidateSources']==diag['newCandidatePhysical']==54 and diag['coverageCountersMeasured'] is False
    assert raw['execSha256']==data.sha((RUN/'jacoco.exec').read_bytes()) and len(raw['cases'])==5 and all(v['result']=='PASS' for v in raw['cases'])
    parsed=execution.decode((RUN/'jacoco.exec').read_bytes(),set())
    assert len(parsed['sessions'])==1 and parsed['sessions'][0]['labelBytesHex']=='PG17816-ADMISSION-REAL-WAIT-JOINT5'.encode().hex()
    runtime=data.read_checked(data.BASE/'PG13378-db-duration-eight-post-recovery-v3/manifest.json','adcb55b80aa70a449e74280aa465f752308310c41c876cf83a5a78c3dda3c882')
    receipt=data.read_checked(data.ROOT.parent/'pgpt-runs/PG379/pg13376-db-duration-eight-post-v1/session-identity-exit.safe.json','2bbd55eefa4fc2b0532660748a0f35bfeca6cb69e45e732fc67759add964a84b')
    assert runtime['actualExit']==0 and all(data.sha(Path(p).read_bytes())==h for p,h in runtime['toolAndDependencyHashes'].items())
    cp=receipt['command'][2];assert len(cp.split(os.pathsep))==5
    reader=data.ROOT.parent/'pgpt-runs/PG379/pg15713-caddy-public-value-nine-post-v2/diagnostic-classes'
    assert data.sha((reader/'WholeSourceCoverageMeasureV1.class').read_bytes())=='9977e1c733e40e4752261c38e6a679a91cf2d33b6d2be72180e1f67af01a94a3'
    assert data.sha((data.ROOT/'tools/quality/architecture/WholeSourceCoverageMeasureV1.java').read_bytes())=='97cecbbff82e9c93d41f13e94872b792f374f84d34973a930daefb79bb7be260'
    qualified=data.read_checked(data.BASE/'PG15714-caddy-public-value-nine-independent-v1/manifest.json','d3900d79c6dc63338d18804f0b4aaa05fc00e1f88dcbe54451aba898cc565242')
    assert qualified['actualExit']==0 and qualified['passiveReaderNegativeChecks']==5
    from pg17842_codefree_main_diagnosis_v1 import codefree
    for path,unit in diag['newCodefreeCandidates'].items():
        assert codefree(unit['metadata']) and data.sha((data.ROOT/path).read_bytes())==unit['sourceSha256']==normal['begin']['inputHashes'][path]
    SLOT.mkdir();component=SLOT/'component';component.mkdir();physical={}
    for path,unit in diag['newCodefreeCandidates'].items():
        jar_info=normal['jars'][unit['module']];assert data.sha(Path(jar_info['path']).read_bytes())==jar_info['sha256']
        with zipfile.ZipFile(jar_info['path']) as jar:
            actual={n[:-6] for n in jar.namelist() if n==unit['sourceOuter']+'.class' or n.startswith(unit['sourceOuter']+'$') and n.endswith('.class')}
            assert actual==set(unit['physical'])
            for name,pin in unit['physical'].items():
                blob=jar.read(name+'.class')
                source=normal_path/'snapshot'/('src/schubert-nk-'+unit['module']+'/target/classes')/(name+'.class')
                assert data.sha(blob)==data.sha(source.read_bytes())==pin
                target=component/(name+'.class');target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
                assert data.sha(target.read_bytes())==pin and name not in physical;physical[name]=pin
    assert len(physical)==54
    data.write(SLOT/'begin.safe.json',dict(source=SOURCE,invocation=invocation,diagnosisSha256=DIAG,originalRawSha256=RAW,originalExecSha256=raw['execSha256'],physicalClasses=physical,productClassesLoaded=False,productTestsReexecuted=0))
    expected_metadata={n for n in physical if not n.endswith('/package-info')}
    package_info={n for n in physical if n.endswith('/package-info')}
    assert len(expected_metadata)==17 and len(package_info)==37
    annotations={}
    for path,unit in diag['newCodefreeCandidates'].items():
        if not path.endswith('/package-info.java'):continue
        assert len(unit['physical'])==1
        name=next(iter(unit['physical']));value=unit['metadata'][name]
        assert name in package_info and value['flags']==5632 and value['fields']==0 and value['methods']==[] and value['sourceFile']=='package-info.java'
        annotations[path]=dict(sourceSha256=unit['sourceSha256'],physical=unit['physical'],flags=value['flags'],fields=0,methods=[],modelCounterStatus='OFFICIAL_PACKAGE_INFO_FILTERED_NO_CODE_NO_RUNTIME_COUNTERS',coverageCountersMeasured=False,productCodeExecuted=False)
    runner.SLOT=SLOT
    stage=runner.step('official-passive-zero-counters',[str(runner.TC/'jdk-25.0.4/bin/java'),'-cp',str(reader)+os.pathsep+cp,'WholeSourceCoverageMeasureV1',str(RUN/'jacoco.exec'),str(component),*['--metadata='+n for n in sorted(expected_metadata)]],SLOT,timeout=120)
    data.write(SLOT/'official-passive-zero-counters-stage.safe.json',stage)
    assert stage['actualExit']==0 and not stage['timedOut']
    lines=(SLOT/'official-passive-zero-counters.stdout').read_text().splitlines()
    assert len(lines)==17 and all(v.startswith('METADATA'+chr(9)) for v in lines) and {v.split(chr(9))[1] for v in lines}==expected_metadata
    counters={k:dict(covered=0,missed=0) for k in ['LINE','METHOD','CLASS','BRANCH']}
    units={unit['sourceOuter']:dict(path=path,sourceSha256=unit['sourceSha256'],physical=sorted(unit['physical']),totals=counters,metadataOnly=True,four100=False,branchNaturallyZero=False,threeCounter100=False) for path,unit in diag['newCodefreeCandidates'].items() if not path.endswith('/package-info.java')}
    assert len(units)==17
    for v in [diag,normal['begin'],raw['begin'],runtime,qualified]:
        verify(v['invocation'])
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,diagnosisSha256=DIAG,normalManifestSha256=diag['normalManifestSha256'],originalRawSha256=RAW,originalExecSha256=raw['execSha256'],sessionIdentity='PG17816-ADMISSION-REAL-WAIT-JOINT5',stage=stage,allInputPhysicalClasses=physical,physicalClasses={n:physical[n] for n in expected_metadata},fullSourceUnits=units,metadataClasses=sorted(expected_metadata),officialPackageInfoDefinitions=annotations,officialPackageInfoDefinitionCount=37,interfaceZeroCounterSourceCount=17,officialFiltersUnchanged=True,officialZeroCounterRows=lines,officialSdkRuntimeSha256='adcb55b80aa70a449e74280aa465f752308310c41c876cf83a5a78c3dda3c882',passiveReaderClassSha256='9977e1c733e40e4752261c38e6a679a91cf2d33b6d2be72180e1f67af01a94a3',allFourCounterTotalsZeroVerified=True,executableCounterExclusions=[],applicableCodeCrcClasses=0,noCodeCrcQualification='NOT_APPLICABLE_NO_EXECUTABLE_CODE_BYTE_IDENTITY_BY_NORMAL_JAR_SNAPSHOT_SHA',tests=0,suites=0,newTestIds=0,productClassesLoaded=False,productTestsExecuted=0,productTestsReexecuted=0,compilerCommandsIssued=0,passiveAnalyzerJvmCommandsIssued=1,actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,registryChanged=False,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
