"""Independent literal owner/receipt ordering and passive unchanged original Test CRC."""
import copy
import os
from pathlib import Path
import re
import shutil
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg9666_pagination_static as runner
import pg17330_inspector_owner_entry_twelve_pt as original
SOURCE=original.SOURCE
POST=('PG17332-inspector-owner-entry-twelve-post-v1','d78ef841d40ac5d74e9f884d4f5b3b818a2379e776856ba9819a8c3d1ffe7a1d')
RAW='816dbd62724f0ca942e19827b0d21ace4f68afc3ebd71a45df7cb49948e0bf7d'
RUN=data.ROOT.parent/'pgpt-runs/PG379/pg17330-inspector-owner-entry-twelve-pt-v1'
OUT=data.BASE/'PG17334-inspector-owner-entry-twelve-independent-v1'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg17334-inspector-owner-entry-twelve-independent-v1'
METHODS={
'dev.codex.schubert.nk.api.file.InspectorOwnerContractTest':['exactOwnerAndEachMismatch','checksBeforeDuringAfterAndReturnsSameResult','expiredOrLostParentPreventsProbeAndWork','inspectorChangeOrReadFailurePreventsWork','postWorkExpiryAndTypedFailureNeverReturnResult','nullDependenciesDoNoObservationOrWork'],
'dev.codex.schubert.nk.api.maintenance.InspectorEntryBoundaryTest':['close743001ClosingRunsAfterCompleteReturnsWithLiteralReceiptAndDiagnostic','close743002ClosingFailureAndMissingNeverManufactureSuccess','fixedReceiptBeforeOptionalCaptureWithNoConfigurationIo','captureFailurePropagatesWithoutCompleteDiagnostic','outputFailureMustPreventCapture','missingEntryPortsRejectBeforeReceiptOrCapture']}
def require(ok,why):
    if not ok:raise ValueError(why)
def main():
    invocation=capture(__file__);require(not OUT.exists() and not SLOT.exists(),'new-only')
    p=data.read_checked(data.BASE/POST[0]/'manifest.json',POST[1]);raw=data.read_checked(data.BASE/'PG17330-inspector-owner-entry-twelve-pt-v1/manifest.json',RAW)
    expected={(c,n) for c,ns in METHODS.items() for n in ns}
    def contract(v):
        require(type(v['actualExit']) is int and v['actualExit']==0 and v['source']==SOURCE and v['originalManifestSha256']==RAW,'exact source/run')
        require((v['tests'],v['suites'],v['targetSourceUnits'],len(v['physicalClasses']))==(12,2,2,7),'two whole Source denominators')
        require(set(v['metadataClasses'])==original.METADATA and v['unexecutedCodeClasses']==[],'NoCode5 plus all Code denominators')
        require(len(v['cases'])==12 and {(x['classname'],x['name']) for x in v['cases']}==expected and all(x['result']=='PASS' for x in v['cases']),'whole original12 only')
        require(v['singleSession'] is True and v['crcMismatch']==0 and v['execSha256']==raw['execSha256'] and v['sessionIdentity']==original.SESSION,'one session/CRC')
        require(v['totals']=={'LINE':{'missed':66,'covered':37},'METHOD':{'missed':11,'covered':9},'CLASS':{'missed':0,'covered':2},'BRANCH':{'missed':6,'covered':46}},'all partial counters')
        require(set(v['fullSourceUnits'])==set(original.MAIN_UNITS) and all(set(v['fullSourceUnits'][n]['physical'])==set(original.CLOSURES[n]) and v['fullSourceUnits'][n]['four100'] is False for n in original.MAIN_UNITS),'complete partial closures')
        require(v['strictFour100GateExit']==1 and v['targetUnitFour100'] is False and v['manualCounterExclusions']==[] and v['officialGeneratedFiltersUnchanged'] is True,'partial not excluded')
        require(v['syntheticOriginalOwnerPortsOnly'] is v['syntheticCompletionPublicationCallbacksInvoked'] is True and v['cryptoOrKeyOperationsInvoked'] is v['actualNativeHookOrProviderOperation'] is False,'fake guard and capture, not native authority')
        require(v['forbiddenProductProbeHits']==0 and all(not x['recordPresent'] for k in ['rootRecoveryProbeAudit','syntheticBackupCycleProbeAudit','reviewedInactiveBoundaryAudit'] for x in v[k].values()),'held/Root/native absent')
        require(v['actualFilesOpenedByProduct'] is v['actualJdbcBackendConnected'] is False and v['actualBackendSqlOperations']==v['actualVmActions']==0,'memory only')
        require(v['productTestsReexecutedByPost']==0 and v['oldCoverageTransferred'] is v['priorProductResultsReused'] is v['formalUpdated'] is v['whole451Accepted'] is False and v['newAccepted']==0 and v['effortPercent'] is None,'no formal/replay transfer')
    contract(p);labels=[]
    for key,value in [('source','OLD'),('actualExit',True),('tests',13),('suites',1),('targetSourceUnits',1),('physicalClasses',{}),('metadataClasses',[]),('unexecutedCodeClasses',['unknown']),('cases',[]),('singleSession',False),('crcMismatch',1),('totals',{}),('fullSourceUnits',{}),('strictFour100GateExit',0),('targetUnitFour100',True),('manualCounterExclusions',['x']),('syntheticOriginalOwnerPortsOnly',False),('syntheticCompletionPublicationCallbacksInvoked',False),('cryptoOrKeyOperationsInvoked',True),('actualNativeHookOrProviderOperation',True),('forbiddenProductProbeHits',1),('actualFilesOpenedByProduct',True),('actualJdbcBackendConnected',True),('oldCoverageTransferred',True),('formalUpdated',True),('newAccepted',1),('effortPercent',100)]:
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
    owner=original.TESTS['InspectorOwnerContractTest'].read_text();entry=original.TESTS['InspectorEntryBoundaryTest'].read_text()
    for token in ['RUN.cutoff().plusNanos(1000)','new UUID(0, 5)','new UUID(0, 6)','RUN.cutoff(), false','assertSame(RESULT, actual)','held.orElseThrow().remainingNanos()','return events.contains(FIXTURE_WORK_DD3E8955) ? 0 : 500','assertSame(crypto ? hash : io, actual)','fail("work before live parent")','fail("work after changed inspector")']:
        require(token in owner,'literal owner oracle '+token)
    for token in ['NKINSPECTOR1 70\\n','Inspector fixed PT native capture complete\\n','Inspector fixed PT native closing complete\\n','assertSame(','inspector receipt unavailable','assertNull(failure.getCause())','assertEquals(0, failure.getSuppressed().length)','fail("no capture after bad receipt")','assertEquals(0, out.size())','new ByteArrayOutputStream()']:
        require(token in entry,'literal receipt oracle '+token)
    SLOT.mkdir();runner.SLOT=SLOT;component=SLOT/'original-test-component';component.mkdir();physical={}
    names=[n.replace('.','/') for n in METHODS]+['dev/codex/schubert/nk/api/maintenance/InspectorEntryBoundaryTest$1']
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
    require(len(crc)==3 and {r[1] for r in crc}==set(names) and not any(v.startswith('METADATA'+chr(9)) for v in lines),'two original Code Test classes only')
    verify(p['invocation']);verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,postSha256=POST[1],originalRawSha256=RAW,tests=12,suites=2,semanticNegativeVectors=len(labels),negativeLabels=labels,independentOracleVectors=12,originalTestSourceHashes=input_hashes,testPhysicalHashes=physical,testCrcIdentityClasses={r[1]:r[2] for r in crc},passiveTestCrcStage=stage,newSourcePrograms=2,newPhysicalClasses=7,metadataPhysicalClasses=5,partialSourcePrograms=2,originalProductTestsReexecuted=0,oldSourceTransferred=False,coverageExecUnion=False,actualDatabaseActions=0,actualVmActions=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
