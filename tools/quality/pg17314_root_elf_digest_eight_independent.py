"""Independent public ELF hash vectors, semantic negative metadata and passive original Test CRC."""
import copy
import hashlib
import os
from pathlib import Path
import re
import shutil
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg9666_pagination_static as runner
import pg17310_root_elf_digest_eight_pt as original
SOURCE=original.SOURCE
POST=('PG17312-root-elf-digest-eight-post-v1','4590d3fae00a2b778203b1e2893d394e3f1d3da4bc42c498334bb93696867307')
RAW='8e1b843cc463d2c8a28e25717d760cf207a1453f5c8ef1d68a6ddaa9174e5858'
RUN=data.ROOT.parent/'pgpt-runs/PG379/pg17310-root-elf-digest-eight-pt-v1'
OUT=data.BASE/'PG17314-root-elf-digest-eight-independent-v1'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg17314-root-elf-digest-eight-independent-v1'
METHODS={'dev.codex.schubert.nk.batch.file.RootElfDigestPortTest':[
'fixedDigestFactoryIsCalledOnceAndBorrowedChannelStaysOpen',
'unavailableAlgorithmIsRedactedAndDoesNotReadOrClose',
'unexpectedRuntimeAndErrorPreserveIdentityWithoutIo','nullContractsFailBeforeInputReads',
'oversizedReadReportIsRejectedAndBufferIsWiped','exactBufferBoundaryAndSplitHeaderKeepLiteralDigest',
'readFailurePreservesIdentityAndWipesWithoutClose','exactMaximumElfHasIndependentFixedHash']}
def require(ok,why):
    if not ok:raise ValueError(why)
def main():
    invocation=capture(__file__);require(not OUT.exists() and not SLOT.exists(),'new-only')
    p=data.read_checked(data.BASE/POST[0]/'manifest.json',POST[1]);raw=data.read_checked(data.BASE/'PG17310-root-elf-digest-eight-pt-v1/manifest.json',RAW)
    expected={(c,n) for c,ns in METHODS.items() for n in ns}
    def contract(v):
        require(type(v['actualExit']) is int and v['actualExit']==0 and v['source']==SOURCE and v['originalManifestSha256']==RAW,'exact source/run')
        require((v['tests'],v['suites'],v['targetSourceUnits'],len(v['physicalClasses']))==(8,1,1,5),'whole Source denominator')
        require(set(v['metadataClasses'])==original.METADATA and v['unexecutedCodeClasses']==[original.NAME+'$RootDescriptor'],'NoCode3 plus unexecuted descriptor kept')
        require(len(v['cases'])==8 and {(x['classname'],x['name']) for x in v['cases']}==expected and all(x['result']=='PASS' for x in v['cases']),'whole original8 only')
        require(v['singleSession'] is True and v['crcMismatch']==0 and v['execSha256']==raw['execSha256'] and v['sessionIdentity']==original.SESSION,'one session/CRC')
        require(v['totals']=={'LINE':{'missed':175,'covered':28},'METHOD':{'missed':50,'covered':3},'CLASS':{'missed':1,'covered':1},'BRANCH':{'missed':70,'covered':22}},'all partial counters')
        require(set(v['fullSourceUnits'])=={original.NAME} and set(v['fullSourceUnits'][original.NAME]['physical'])==set(original.CLOSURES[original.NAME]) and v['fullSourceUnits'][original.NAME]['four100'] is False,'one complete partial closure')
        require(v['strictFour100GateExit']==1 and v['targetUnitFour100'] is False and v['manualCounterExclusions']==[] and v['officialGeneratedFiltersUnchanged'] is True,'partial not excluded')
        require(v['publicDigestOnly'] is v['cryptoOrKeyOperationsInvoked'] is True and v['actualSecretKeysLoaded'] is v['actualNativeHookOrProviderOperation'] is False,'public SHA256 no key/provider mutation')
        require(v['forbiddenProductProbeHits']==0 and all(not x['recordPresent'] for k in ['rootRecoveryProbeAudit','syntheticBackupCycleProbeAudit','reviewedInactiveBoundaryAudit'] for x in v[k].values()),'held/Root/native absent')
        require(v['actualFilesOpenedByProduct'] is v['actualJdbcBackendConnected'] is False and v['actualBackendSqlOperations']==v['actualVmActions']==0,'memory only')
        require(v['productTestsReexecutedByPost']==0 and v['oldCoverageTransferred'] is v['priorProductResultsReused'] is v['formalUpdated'] is v['whole451Accepted'] is False and v['newAccepted']==0 and v['effortPercent'] is None,'no formal/replay transfer')
    contract(p);labels=[]
    for key,value in [('source','OLD'),('actualExit',True),('tests',9),('suites',2),('targetSourceUnits',2),('physicalClasses',{}),('metadataClasses',[]),('unexecutedCodeClasses',[]),('cases',[]),('singleSession',False),('crcMismatch',1),('totals',{}),('fullSourceUnits',{}),('strictFour100GateExit',0),('targetUnitFour100',True),('manualCounterExclusions',['x']),('publicDigestOnly',False),('cryptoOrKeyOperationsInvoked',False),('actualSecretKeysLoaded',True),('actualNativeHookOrProviderOperation',True),('forbiddenProductProbeHits',1),('actualFilesOpenedByProduct',True),('actualJdbcBackendConnected',True),('oldCoverageTransferred',True),('formalUpdated',True),('newAccepted',1),('effortPercent',100)]:
        bad=copy.deepcopy(p);bad[key]=value;require(bad!=p,'nondegenerate '+key)
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false current post '+key)
    input_hashes={}
    for binary,names in METHODS.items():
        path=original.TESTS[binary.rsplit('.',1)[1]];text=path.read_text()
        require(re.findall(r'@Test\s+void\s+(\w+)\(',text)==names,'whole original method catalog')
        require(data.sha(path.read_bytes())==raw['begin']['sourceHashes'][str(path.relative_to(data.ROOT))]==original.PINS[path.stem],'same source')
        input_hashes[str(path.relative_to(data.ROOT))]=data.sha(path.read_bytes())
    vectors=[]
    for length,golden in [(64,'caa6f4f58ad3ed35afa011abfdb3ef06a7799b5545082b32685f75cc9c454fe8'),(8388608,'9c75e29938e99e5c154bf35e94a362e3e4de159e98ca02b25a032956e98aeca0')]:
        value=bytearray(length);value[:7]=bytes([127,69,76,70,2,1,1]);value[18]=62
        actual=hashlib.sha256(value).hexdigest();require(actual==golden and golden in text,'independent hashlib golden')
        vectors.append(dict(length=length,sha256=actual))
    for token in ['assertEquals(1, calls.get())','assertEquals(0, input.reads)','assertNull(failure.getCause())','assertEquals(0, failure.getSuppressed().length)','new int[] {1, 7, 64, 8192}','input.overreport = true','return overreport ? 8193 : count','assertSame(','NullPointerException.class','assertEquals(0, closes)','new byte[buffer.length], buffer','private static final class Input implements SeekableByteChannel']:
        require(token in text,'literal independent assertion '+token)
    SLOT.mkdir();runner.SLOT=SLOT;component=SLOT/'original-test-component';component.mkdir();physical={}
    names=[next(iter(METHODS)).replace('.','/'),next(iter(METHODS)).replace('.','/')+'$Input']
    for name in names:
        src=RUN/'fresh-test-classes'/(name+'.class');dst=component/(name+'.class');dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst);physical[name]=data.sha(src.read_bytes())
    receipt=data.read_checked(data.ROOT.parent/'pgpt-runs/PG379/pg13376-db-duration-eight-post-v1/session-identity-exit.safe.json','2bbd55eefa4fc2b0532660748a0f35bfeca6cb69e45e732fc67759add964a84b')
    cp=receipt['command'][2];reader=data.ROOT.parent/'pgpt-runs/PG379/pg15713-caddy-public-value-nine-post-v2/diagnostic-classes'
    require(data.sha((reader/'WholeSourceCoverageMeasureV1.class').read_bytes())=='9977e1c733e40e4752261c38e6a679a91cf2d33b6d2be72180e1f67af01a94a3','qualified passive class')
    runtime=data.read_checked(data.BASE/'PG13378-db-duration-eight-post-recovery-v3/manifest.json','adcb55b80aa70a449e74280aa465f752308310c41c876cf83a5a78c3dda3c882')
    require(all(data.sha(Path(k).read_bytes())==v for k,v in runtime['toolAndDependencyHashes'].items()),'same reader SDK')
    stage=runner.step('passive-original-test-crc',[str(runner.TC/'jdk-25.0.4/bin/java'),'-cp',str(reader)+os.pathsep+cp,'WholeSourceCoverageMeasureV1',str(RUN/'jacoco.exec'),str(component),*names],SLOT,timeout=120)
    require(stage['actualExit']==0 and not stage['timedOut'],'same original Test CRC')
    lines=(SLOT/'passive-original-test-crc.stdout').read_text().splitlines();crc=[v.split(chr(9)) for v in lines if v.startswith('CLASS'+chr(9))]
    require(len(crc)==2 and {r[1] for r in crc}==set(names) and not any(v.startswith('METADATA'+chr(9)) for v in lines),'two original Code Test classes only')
    verify(p['invocation']);verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,postSha256=POST[1],originalRawSha256=RAW,tests=8,suites=1,semanticNegativeVectors=len(labels),negativeLabels=labels,independentOracleVectors=8,independentPublicHashVectors=vectors,originalTestSourceHashes=input_hashes,testPhysicalHashes=physical,testCrcIdentityClasses={r[1]:r[2] for r in crc},passiveTestCrcStage=stage,newSourcePrograms=1,newPhysicalClasses=5,metadataPhysicalClasses=3,partialSourcePrograms=1,originalProductTestsReexecuted=0,oldSourceTransferred=False,coverageExecUnion=False,actualDatabaseActions=0,actualVmActions=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
