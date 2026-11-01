"""Independent retained-audit literal violations and fixed nanosecond arithmetic; original Test CRC only."""
import copy
import os
from pathlib import Path
import re
import shutil
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg9666_pagination_static as runner
import pg17580_retained_audit_caddy_fifteen_pt_v1 as original
SOURCE=original.SOURCE
POST=('PG17582-retained-audit-caddy-fifteen-post-v1','6f43a60465ff60cf9e35bf70cc6fc6b53760c0b738f51f5fe57300ffd8699c01')
RAW='53f590aa8e3877d3b918b6344043e3edb9598ff47071694e7025d7ed38877222'
RUN=data.ROOT.parent/'pgpt-runs/PG379/pg17580-retained-audit-caddy-fifteen-pt-v1'
OUT=data.BASE/'PG17584-retained-audit-caddy-fifteen-independent-v1'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg17584-retained-audit-caddy-fifteen-independent-v1'
METHODS={"dev.codex.schubert.nk.batch.file.RetainedExpiryAuditTest":["ssc302001ExactAuditAndIndependentArithmeticBoundaries","ssc302002StatusMustBeSuccess","ssc302003EndedMustMatchRetainedReference","ssc302004ExactSevenDayCutoffMustMatch","ssc302005BeforeNullIsNotZero","ssc302006AfterNullIsNotZero","ssc302007BeforeCannotBeBelowAfter","ssc302008BeforeMinusAfterMustEqualSuccess","ssc302009TargetMustEqualSuccess","ssc302010FailureCountMustBeZero","ssc302011SuccessfulAuditCannotCarryErrorCode","ssc302012SuccessfulAuditCannotCarryErrorSummary","ssc302013NullReferenceAndAuditAreContractViolations","ssc302014NonSkipAndNonzeroSelectedRejectBeforeAnyJdbc"],"dev.codex.schubert.nk.batch.file.CaddyParentRemainingBudgetTest":["caddyfence004SingleParentDomainWindowAndExactBoundaryNeverRenew"]}
def require(ok,why):
    if not ok:raise ValueError(why)
def main():
    invocation=capture(__file__);require(not OUT.exists() and not SLOT.exists(),'new-only')
    p=data.read_checked(data.BASE/POST[0]/'manifest.json',POST[1]);raw=data.read_checked(data.BASE/'PG17580-retained-audit-caddy-fifteen-pt-v1/manifest.json',RAW)
    expected={(c,n) for c,ns in METHODS.items() for n in ns}
    def contract(v):
        require(type(v['actualExit']) is int and v['actualExit']==0 and v['source']==SOURCE and v['originalManifestSha256']==RAW,'exact source/run')
        require((v['tests'],v['suites'],v['targetSourceUnits'],len(v['physicalClasses']))==(15,2,2,12),'one complete Source denominator')
        require(set(v['metadataClasses'])==original.METADATA and len(v['unexecutedCodeClasses'])==4,'Factory NoCode, all Main Code denominators')
        require(len(v['cases'])==15 and {(x['classname'],x['name']) for x in v['cases']}==expected and all(x['result']=='PASS' for x in v['cases']),'whole original11 only')
        require(v['singleSession'] is True and v['crcMismatch']==0 and v['execSha256']==raw['execSha256'] and v['sessionIdentity']==original.SESSION,'one session/CRC')
        require(v['totals']=={'LINE':{'missed':637,'covered':21},'METHOD':{'missed':64,'covered':3},'CLASS':{'missed':4,'covered':2},'BRANCH':{'missed':135,'covered':29}},'complete partial counters')
        require(set(v['fullSourceUnits'])==set(original.MAIN_UNITS) and all(set(v['fullSourceUnits'][n]['physical'])==set(original.CLOSURES[n]) and v['fullSourceUnits'][n]['four100'] is False for n in original.MAIN_UNITS),'one whole partial closure')
        require(v['strictFour100GateExit']==1 and v['targetUnitFour100'] is False and v['manualCounterExclusions']==[] and v['officialGeneratedFiltersUnchanged'] is True,'no exclusions')
        require(v['actualNetworkActions']==0,'actual self-owned network, operation count unknown not zero')
        require(v['testOwnJavaMonotonicClockRead'] is v['ownCurrentThreadInterruptFlagModifiedAndFinallyCleared'] is False and v['ownThreadCount']==0 and v['cryptoOrKeyOperationsInvoked'] is v['actualNativeHookOrProviderOperation'] is False,'owned JDK clock/interrupt, no invented thread total/native')
        require(v['forbiddenProductProbeHits']==0 and all(not x['recordPresent'] for k in ['rootRecoveryProbeAudit','syntheticBackupCycleProbeAudit','reviewedInactiveBoundaryAudit'] for x in v[k].values()),'held/Root/native absent')
        require(v['actualFilesOpenedByProduct'] is v['actualJdbcBackendConnected'] is False and v['actualBackendSqlOperations']==v['actualVmActions']==0,'no real DB/file/VM')
        require(v['productTestsReexecutedByPost']==0 and v['oldCoverageTransferred'] is v['priorProductResultsReused'] is v['formalUpdated'] is v['whole451Accepted'] is False and v['newAccepted']==0 and v['effortPercent'] is None,'no formal/replay transfer')
    contract(p);labels=[]
    for key,value in [('source','OLD'),('actualExit',True),('tests',0),('suites',0),('targetSourceUnits',0),('physicalClasses',{}),('metadataClasses',[]),('unexecutedCodeClasses',[]),('cases',[]),('singleSession',False),('crcMismatch',1),('totals',{}),('fullSourceUnits',{}),('strictFour100GateExit',0),('targetUnitFour100',True),('manualCounterExclusions',['x']),('actualNetworkActions',1),('testOwnJavaMonotonicClockRead',True),('ownCurrentThreadInterruptFlagModifiedAndFinallyCleared',True),('ownThreadCount',1),('cryptoOrKeyOperationsInvoked',True),('forbiddenProductProbeHits',1),('actualFilesOpenedByProduct',True),('actualJdbcBackendConnected',True),('oldCoverageTransferred',True),('formalUpdated',True),('newAccepted',1),('effortPercent',100)]:
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
    audit=original.TESTS['RetainedExpiryAuditTest'].read_text();budget=original.TESTS['CaddyParentRemainingBudgetTest'].read_text()
    for token in ['"2026-09-30T00:00:00Z"','"2026-09-23T00:00:00Z"','"2026-09-30T00:00:02Z"','new long[] {0, Long.MAX_VALUE}','StorageIoException.Reason.UNAVAILABLE','"transfer storage operation failed"','assertNull(failure.getCause())','assertEquals(0, failure.getSuppressed().length)','assertEquals(0, calls.get())','request(false), 0','request(true), 1','verifyPriorAudit(null,','verifyPriorAudit(reference(), null)']:
        require(token in audit,'literal audit oracle '+token)
    for fault in ['STATUS','ENDED','CUTOFF','BEFORE_NULL','AFTER_NULL','ORDER','DIFFERENCE','TARGET','FAILURE','CODE','SUMMARY']:require('rejected(audit("'+fault+'"))' in audit,'one independent audit rejection '+fault)
    for token in ['100_000_000_000L','assertEquals(70_000_000_000L, floor)','95_000_000_000L > floor','80_000_000_000L > floor','70_000_000_001L > floor','assertFalse(70_000_000_000L > floor)','assertFalse(69_999_999_999L > floor)','caddyRemainingFloor(18_000_000_000L)','caddyRemainingFloor(30_000_000_000L)','assertEquals(1, MorningStartupLaunchOwner.caddyRemainingFloor(30_000_000_001L))','1_770_000_000_000L','0, -1, Long.MIN_VALUE, 1_800_000_000_001L, Long.MAX_VALUE','assertThrows(IOException.class,']:require(token in budget,'independent ns floor literal '+token)
    arithmetic=[]
    for remaining,expected_floor in [(100_000_000_000,70_000_000_000),(18_000_000_000,0),(30_000_000_000,0),(30_000_000_001,1),(1_800_000_000_000,1_770_000_000_000)]:
        independent=0 if remaining<=30_000_000_000 else remaining-30_000_000_000
        require(independent==expected_floor,'independent Python integer subtraction');arithmetic.append(dict(parentRemaining=remaining,expectedFloor=expected_floor))
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
    require(len(crc)==2 and {r[1] for r in crc}==set(names) and not any(v.startswith('METADATA'+chr(9)) for v in lines),'two original Code Test classes only')
    verify(p['invocation']);verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,postSha256=POST[1],originalRawSha256=RAW,tests=15,suites=2,independentArithmeticVectors=arithmetic,semanticNegativeVectors=len(labels),negativeLabels=labels,independentOracleVectors=15,originalTestSourceHashes=input_hashes,testPhysicalHashes=physical,testCrcIdentityClasses={r[1]:r[2] for r in crc},passiveTestCrcStage=stage,newSourcePrograms=0,newPhysicalClasses=0,metadataPhysicalClasses=6,partialSourcePrograms=2,actualOwnedLoopbackFixtureNetwork=False,networkOperationCount=0,actualExternalNetworkActions=0,actualProductionServiceActions=0,originalProductTestsReexecuted=0,oldSourceTransferred=False,coverageExecUnion=False,actualDatabaseActions=0,actualVmActions=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
