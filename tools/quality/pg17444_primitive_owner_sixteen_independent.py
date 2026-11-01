"""Independent fixed close-priority goldens and passive unchanged original owner Test CRC."""
import copy
import os
from pathlib import Path
import re
import shutil
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg9666_pagination_static as runner
import pg17440_primitive_owner_sixteen_pt as original
SOURCE=original.SOURCE
POST=('PG17442-primitive-owner-sixteen-post-v1','1be28e136e936315ddf5228cc1b142d6016cd9d67a2ee0fad90b4249754739e8')
RAW='5b57c7ddf85dc5d968c8d9559855dde8eac90adfca542903ca109576447d4fb9'
RUN=data.ROOT.parent/'pgpt-runs/PG379/pg17440-primitive-owner-sixteen-pt-v1'
OUT=data.BASE/'PG17444-primitive-owner-sixteen-independent-v1'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg17444-primitive-owner-sixteen-independent-v1'
METHODS={
'dev.codex.schubert.nk.batch.platform.CgroupPrimitiveOwnerTest':[
'cgroupfd001SixPrimitiveHighDescriptorsKeepOriginalForwardCloseOrder',
'cgroupfd002NullCapacityClosedAndForeignParentFailBeforeNativeIo',
'cgroupfd003NegativeAndDuplicateNeverOwnAnExtraFdButZeroIsValid',
'cgroupfd004AllOpenFailuresReleaseOnlyPreviouslyOwnedDescriptors',
'cgroupfd005All64ForwardCloseStatesMatchLiteralIndependentGolden',
'cgroupfd006ExistingAndRepeatedSuppressionKeepIdentityAndSanitizeLaterFailures',
'cgroupfd007SixSlotsDrainEveryLaterFdBeforeUnknownAggregationAndNeverRetry',
'cgroupfd008ParallelOwnersNeverShareSlotsOrConsumeEachOther'],
'dev.codex.schubert.nk.batch.file.StartupAdmissionViewOwnerTest':[
'viewfd001PrimitiveHighDescriptorsCloseInReverseExactlyOnce',
'viewfd002CapacityClosedNullAndParentRefuseBeforeNativeOpen',
'viewfd003NegativeAndDuplicateNeverCreateAnExtraOwnershipSlot',
'viewfd004AllNativeOpenFailureKindsRetainOnlyPriorOwnedDescriptors',
'viewfd005All64ReverseCloseStatesMatchFixedIndependentGolden',
'viewfd006ExistingSuppressedAndRepeatedThrowableStaySanitized',
'viewfd007BodyAndOwnerCloseKeepExistingIndependentPriority',
'viewfd008IndependentParallelOwnersNeverShareSlotsOrConsumeEachOther']}
def require(ok,why):
    if not ok:raise ValueError(why)
def main():
    invocation=capture(__file__);require(not OUT.exists() and not SLOT.exists(),'new-only')
    p=data.read_checked(data.BASE/POST[0]/'manifest.json',POST[1]);raw=data.read_checked(data.BASE/'PG17440-primitive-owner-sixteen-pt-v1/manifest.json',RAW)
    expected={(c,n) for c,ns in METHODS.items() for n in ns}
    def contract(v):
        require(type(v['actualExit']) is int and v['actualExit']==0 and v['source']==SOURCE and v['originalManifestSha256']==RAW,'exact source/run')
        require((v['tests'],v['suites'],v['targetSourceUnits'],len(v['physicalClasses']))==(16,2,2,15),'two whole Source denominators')
        require(set(v['metadataClasses'])==original.METADATA and len(v['unexecutedCodeClasses'])==7,'NoCode5 plus all Code denominators')
        require(len(v['cases'])==16 and {(x['classname'],x['name']) for x in v['cases']}==expected and all(x['result']=='PASS' for x in v['cases']),'whole original12 only')
        require(v['singleSession'] is True and v['crcMismatch']==0 and v['execSha256']==raw['execSha256'] and v['sessionIdentity']==original.SESSION,'one session/CRC')
        require(v['totals']=={'LINE':{'missed':143,'covered':144},'METHOD':{'missed':34,'covered':21},'CLASS':{'missed':7,'covered':3},'BRANCH':{'missed':116,'covered':82}},'all partial counters')
        require(set(v['fullSourceUnits'])==set(original.MAIN_UNITS) and all(set(v['fullSourceUnits'][n]['physical'])==set(original.CLOSURES[n]) and v['fullSourceUnits'][n]['four100'] is False for n in original.MAIN_UNITS),'complete partial closures')
        require(v['strictFour100GateExit']==1 and v['targetUnitFour100'] is False and v['manualCounterExclusions']==[] and v['officialGeneratedFiltersUnchanged'] is True,'partial not excluded')
        require(v['syntheticOriginalOwnerPortsOnly'] is True and v['syntheticCompletionPublicationCallbacksInvoked'] is False and v['syntheticIntegerDescriptorPortsOnly'] is True and v['ownThreadCount'] is None and v['declaredOwnExecutorInstances']==2 and v['declaredOwnTaskCount']==4 and v['cryptoOrKeyOperationsInvoked'] is v['actualNativeHookOrProviderOperation'] is False,'fake guard and capture, not native authority')
        require(v['forbiddenProductProbeHits']==0 and all(not x['recordPresent'] for k in ['rootRecoveryProbeAudit','syntheticBackupCycleProbeAudit','reviewedInactiveBoundaryAudit'] for x in v[k].values()),'held/Root/native absent')
        require(v['actualFilesOpenedByProduct'] is v['actualJdbcBackendConnected'] is False and v['actualBackendSqlOperations']==v['actualVmActions']==0,'memory only')
        require(v['productTestsReexecutedByPost']==0 and v['oldCoverageTransferred'] is v['priorProductResultsReused'] is v['formalUpdated'] is v['whole451Accepted'] is False and v['newAccepted']==0 and v['effortPercent'] is None,'no formal/replay transfer')
    contract(p);labels=[]
    for key,value in [('source','OLD'),('actualExit',True),('tests',17),('suites',1),('targetSourceUnits',1),('physicalClasses',{}),('metadataClasses',[]),('unexecutedCodeClasses',['unknown']),('cases',[]),('singleSession',False),('crcMismatch',1),('totals',{}),('fullSourceUnits',{}),('strictFour100GateExit',0),('targetUnitFour100',True),('manualCounterExclusions',['x']),('syntheticOriginalOwnerPortsOnly',False),('syntheticCompletionPublicationCallbacksInvoked',True),('cryptoOrKeyOperationsInvoked',True),('actualNativeHookOrProviderOperation',True),('forbiddenProductProbeHits',1),('actualFilesOpenedByProduct',True),('actualJdbcBackendConnected',True),('oldCoverageTransferred',True),('formalUpdated',True),('newAccepted',1),('effortPercent',100),('syntheticIntegerDescriptorPortsOnly',False),('ownThreadCount',0),('declaredOwnExecutorInstances',0),('declaredOwnTaskCount',0)]:
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
    cgroup=original.TESTS['CgroupPrimitiveOwnerTest'].read_text();view=original.TESTS['StartupAdmissionViewOwnerTest'].read_text()
    golden_type=['NIREIIRERRRREEEE','IIREIIRERRRREEEE','RRRRRRRRRRRRRRRR','EEEEEEEEEEEEEEEE']
    golden_suppressed=['0000000001110111','0000000001110111','0111122212221222','0111122212221222']
    golden_winner=['xx22xx2211111111','xx22xx2211111111','0000000000000000','0000000000000000']
    for text in [cgroup,view]:
        require(all(('"'+v+'"') in text for v in golden_type+golden_suppressed+golden_winner),'original literal priority tables')
        require(all(t in text for t in ['Proxy.newProxyInstance','new Class<?>[] {DirectoryCalls.class}','no other native capability','Executors.newFixedThreadPool(2)','assertSame(','assertThrows(','ResourceScope','fixture.owner.close()']),'injected original oracle/whole null/error/parallel boundary')
        for first in range(4):
            for middle in range(4):
                for last in range(4):
                    values=(first,middle,last);unknown=[i for i,x in enumerate(values) if x in (2,3)]
                    index=middle*4+last
                    if unknown:
                        winner=unknown[0];kind='R' if values[winner]==2 else 'E';suppressed=sum(x!=0 for x in values[winner+1:])
                        require(golden_winner[first][index]==str(winner),'independent literal unknown precedence')
                    else:kind='I' if 1 in values else 'N';suppressed=0;require(golden_winner[first][index]=='x','no unknown winner')
                    require(golden_type[first][index]==kind and int(golden_suppressed[first][index])==suppressed,'independent fixed 64 Cartesian priority table')
    for token in ['List.of(319, 320, 321, 322, 323, 324)','fixture.owner.descriptor(-1)','fixture.owner.descriptor(6)','List.of(0)','new CountDownLatch(2)','ready.await(10, TimeUnit.SECONDS)','fixture.owner.openDirectory(999, "foreign")']:
        require(token in cgroup,'literal forward/boundary/parallel '+token)
    for token in ['List.of(321, 320, 319)','new StartupAdmissionFile.ViewOwner(null, 1)','new StartupAdmissionFile.ViewOwner(fixture.calls, 0)','new StartupAdmissionFile.ViewOwner(fixture.calls, -1)','List.of(0)','assertNotSame(secondary, actual.getSuppressed()[0])']:
        require(token in view,'literal reverse/null/exception '+token)
    body=[['IO','CLOSE','CLOSE'],['FIXTURE_PRIMARY_9466F7E5']*3,['FIXTURE_PRIMARY_9466F7E5']*3]
    require('{"IO", "CLOSE", "CLOSE"}' in view and view.count('{FIXTURE_PRIMARY_9466F7E5, FIXTURE_PRIMARY_9466F7E5, FIXTURE_PRIMARY_9466F7E5}')==2,'fixed independent body-close nine priorities')
    require(all(body[b][c]==('IO' if b==c==0 else 'CLOSE' if b==0 else 'FIXTURE_PRIMARY_9466F7E5') for b in range(3) for c in range(3)),'body-close Cartesian oracle')
    SLOT.mkdir();runner.SLOT=SLOT;component=SLOT/'original-test-component';component.mkdir();physical={}
    names=[n.replace('.','/')+suffix for n in METHODS for suffix in ['', '$Fixture']]
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
    require(len(crc)==4 and {r[1] for r in crc}==set(names) and not any(v.startswith('METADATA'+chr(9)) for v in lines),'two original Code Test classes only')
    verify(p['invocation']);verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,postSha256=POST[1],originalRawSha256=RAW,tests=16,suites=2,semanticNegativeVectors=len(labels),negativeLabels=labels,independentOracleVectors=16,independentClosePriorityVectors=128,independentBodyClosePriorityVectors=9,originalTestSourceHashes=input_hashes,testPhysicalHashes=physical,testCrcIdentityClasses={r[1]:r[2] for r in crc},passiveTestCrcStage=stage,newSourcePrograms=2,newPhysicalClasses=15,metadataPhysicalClasses=5,partialSourcePrograms=2,originalProductTestsReexecuted=0,oldSourceTransferred=False,coverageExecUnion=False,actualDatabaseActions=0,actualVmActions=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
