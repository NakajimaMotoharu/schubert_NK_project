"""Independent original permit-data6 literals, null-before-I/O and Java line-pair guard metadata."""
import copy
import os
from pathlib import Path
import re
import shutil
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg9666_pagination_static as runner
import pg17661_root_entry_denial_four_pt_v2 as original
SOURCE=original.SOURCE
POST=('PG17662-root-entry-denial-four-post-v1','733fdc388fe8048c75b75a2a386b6aadce3b071339970bf786351eae051cd508')
RAW='638615bb93d36af608318815228274452ca998a047ea77fe87ad3677a3d2af4c'
RUN=data.ROOT.parent/'pgpt-runs/PG379/pg17661-root-entry-denial-four-pt-v2'
OUT=data.BASE/'PG17664-root-entry-denial-four-independent-v1'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg17664-root-entry-denial-four-independent-v1'
METHODS={"dev.codex.schubert.nk.batch.file.RootEntryRejectionTest":["guard001SetprivRejectsEveryNonServiceRoleBeforeAnyIo","guard002ObserveRejectsEveryNonServiceRoleBeforeAnyIo","guard003AllNativeEntryNullContractsPrecedeIoAndCallbacks","guard004RootDescriptorPreallocatesAndPreservesPrimitiveFailureOwnership"]}
def require(ok,why):
    if not ok:raise ValueError(why)
def main():
    invocation=capture(__file__);require(not OUT.exists() and not SLOT.exists(),'new-only')
    p=data.read_checked(data.BASE/POST[0]/'manifest.json',POST[1]);raw=data.read_checked(data.BASE/'PG17661-root-entry-denial-four-pt-v2/manifest.json',RAW)
    expected={(c,n) for c,ns in METHODS.items() for n in ns}
    def contract(v):
        require(type(v['actualExit']) is int and v['actualExit']==0 and v['source']==SOURCE and v['originalManifestSha256']==RAW,'exact source/run')
        require((v['tests'],v['suites'],v['targetSourceUnits'],len(v['physicalClasses']))==(4,1,2,9),'one complete Source denominator')
        require(set(v['metadataClasses'])==original.METADATA and len(v['unexecutedCodeClasses'])==1,'Factory NoCode, all Main Code denominators')
        require(len(v['cases'])==4 and {(x['classname'],x['name']) for x in v['cases']}==expected and all(x['result']=='PASS' for x in v['cases']),'whole original11 only')
        require(v['singleSession'] is True and v['crcMismatch']==0 and v['execSha256']==raw['execSha256'] and v['sessionIdentity']==original.SESSION,'one session/CRC')
        require(v['totals']=={'LINE':{'missed':261,'covered':26},'METHOD':{'missed':62,'covered':6},'CLASS':{'missed':1,'covered':3},'BRANCH':{'missed':122,'covered':6}},'complete partial counters')
        require(set(v['fullSourceUnits'])==set(original.MAIN_UNITS) and all(set(v['fullSourceUnits'][n]['physical'])==set(original.CLOSURES[n]) and v['fullSourceUnits'][n]['four100'] is False for n in original.MAIN_UNITS),'one whole partial closure')
        require(v['strictFour100GateExit']==1 and v['targetUnitFour100'] is False and v['manualCounterExclusions']==[] and v['officialGeneratedFiltersUnchanged'] is True,'no exclusions')
        require(v['actualNetworkActions']==0,'actual self-owned network, operation count unknown not zero')
        require(v['testOwnJavaMonotonicClockRead'] is v['ownCurrentThreadInterruptFlagModifiedAndFinallyCleared'] is False and v['ownThreadCount']==0 and v['cryptoOrKeyOperationsInvoked'] is v['actualNativeHookOrProviderOperation'] is False,'owned JDK clock/interrupt, no invented thread total/native')
        require(v['forbiddenProductProbeHits']==0 and all(not x['recordPresent'] for k in ['rootRecoveryProbeAudit','syntheticBackupCycleProbeAudit','reviewedInactiveBoundaryAudit'] for x in v[k].values()),'held/Root/native absent')
        require(v['actualFilesOpenedByProduct'] is v['actualJdbcBackendConnected'] is False and v['actualBackendSqlOperations']==v['actualVmActions']==0,'no real DB/file/VM')
        require(v['productTestsReexecutedByPost']==0 and v['oldCoverageTransferred'] is v['priorProductResultsReused'] is v['formalUpdated'] is v['whole451Accepted'] is False and v['newAccepted']==0 and v['effortPercent'] is None,'no formal/replay transfer')
    contract(p);labels=[]
    for key,value in [('source','OLD'),('actualExit',True),('tests',0),('suites',0),('targetSourceUnits',0),('physicalClasses',{}),('metadataClasses',['unknown']),('unexecutedCodeClasses',[]),('cases',[]),('singleSession',False),('crcMismatch',1),('totals',{}),('fullSourceUnits',{}),('strictFour100GateExit',0),('targetUnitFour100',True),('manualCounterExclusions',['x']),('actualNetworkActions',1),('testOwnJavaMonotonicClockRead',True),('ownCurrentThreadInterruptFlagModifiedAndFinallyCleared',True),('ownThreadCount',1),('cryptoOrKeyOperationsInvoked',True),('forbiddenProductProbeHits',1),('actualFilesOpenedByProduct',True),('actualJdbcBackendConnected',True),('oldCoverageTransferred',True),('formalUpdated',True),('newAccepted',1),('effortPercent',100)]:
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
    text=original.TESTS['RootEntryRejectionTest'].read_text()
    for token in ['RootStartupContext.Service.MORNING','RootStartupContext.Service.CLEANUP','RootStartupContext.Service.EXPIRY','assertEquals(0, fixture.calls())','assertEquals(0, work.get())','StorageIoException.Reason.UNAVAILABLE','"transfer storage operation failed"','assertNull(failure.getCause())','int value = 319;','assertEquals(319, actual)','assertEquals(1, calls.opens)','assertEquals(1, calls.closes)','assertEquals(0, bad.closes)','assertEquals(0, failed.closes)','assertSame(','NullPointerException.class']:
        require(token in text,'independent original guard/descriptor oracle '+token)
    require('RootStartupContext.create(' not in text and 'new RootStartupContext.NativeIo' not in text,'no real Root construction')
    require(p['rootContextInjectedAllDenyConstructorOnly'] is p['declaredFakeDescriptor319Only'] is True and p['syntheticRootAdmissionCallbackInvoked'] is False,'fake Root fields, not authority')
    audit=p['injectedRootContextCtorAudit']
    require(audit['constructorRecorded'] is audit['negativeForgedContextRejected'] is audit['methodEntryAbsenceNotInferredFromProbes'] is True and audit['otherContextMethodsCoveredInstructions']==0 and audit['productClassesLoaded'] is audit['productMethodsInvoked'] is False,'precise constructor-only passive proof')
    require([v['actualExit'] for v in audit['stages']]==[0,0,1],'compiled/original/forged outcomes')
    import jacoco_readonly_exec_subset as decoder
    blob=(RUN/'jacoco.exec').read_bytes();unused={}
    for suffix in ['batch/file/BackupPublicationFixture','batch/file/BackupArtifactFixture','batch/backup/BackupManifestFixture']:
        name='dev/codex/schubert/nk/'+suffix
        try:decoder.decode(blob,{name})
        except ValueError as error:
            require(error.args==('one session and all exact target records required',),'exact missing record signal');unused[name]=False
        else:raise ValueError('compile-only Backup helper unexpectedly recorded')
    helper_hashes={}
    for path,h in original.EXTRAS.items():
        require(data.sha((data.ROOT/path).read_bytes())==raw['begin']['sourceHashes'][path]==h,'original compile-only helper byte')
        helper_hashes[path]=h
    SLOT.mkdir();runner.SLOT=SLOT;component=SLOT/'original-test-component';component.mkdir();physical={}
    names=[n.replace('.','/') for n in METHODS]
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
    require(len(crc)==1 and {r[1] for r in crc}==set(names) and not any(v.startswith('METADATA'+chr(9)) for v in lines),'two original Code Test classes only')
    verify(p['invocation']);verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,postSha256=POST[1],originalRawSha256=RAW,tests=4,suites=1,unusedBackupHelperRecordPresent=unused,originalHelperHashes=helper_hashes,injectedRootContextCtorAudit=audit,semanticNegativeVectors=len(labels),negativeLabels=labels,independentOracleVectors=4,originalTestSourceHashes=input_hashes,testPhysicalHashes=physical,testCrcIdentityClasses={r[1]:r[2] for r in crc},passiveTestCrcStage=stage,newSourcePrograms=0,newPhysicalClasses=0,metadataPhysicalClasses=5,partialSourcePrograms=2,actualOwnedLoopbackFixtureNetwork=False,networkOperationCount=0,actualExternalNetworkActions=0,actualProductionServiceActions=0,originalProductTestsReexecuted=0,oldSourceTransferred=False,coverageExecUnion=False,actualDatabaseActions=0,actualVmActions=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
