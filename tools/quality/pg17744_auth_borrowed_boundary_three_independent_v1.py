"""Independent original permit-data6 literals, null-before-I/O and Java line-pair guard metadata."""
import copy
import os
from pathlib import Path
import re
import shutil
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg9666_pagination_static as runner
import pg17740_auth_borrowed_boundary_three_pt_v1 as original
SOURCE=original.SOURCE
POST=('PG17742-auth-borrowed-boundary-three-post-v1','f1082ea1d6aa3d8aad341dd00a03dde5f61b8bb1562bce759ab1304576af22bf')
RAW='827e6ab1aeeb00140d978867cebad6b97fe9f1240426de9aa699c769f4cc238c'
RUN=data.ROOT.parent/'pgpt-runs/PG379/pg17740-auth-borrowed-boundary-three-pt-v1'
OUT=data.BASE/'PG17744-auth-borrowed-boundary-three-independent-v1'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg17744-auth-borrowed-boundary-three-independent-v1'
METHODS={"dev.codex.schubert.nk.api.security.AuthenticationJdbcBoundary329Test":["authBoundary329001LockPreservesFatalAfterOwnedStatementClose","authBoundary329002BothRecordOutcomesPreserveFatalWithoutOwningConnection","authBoundary329003AuditFatalCannotBecomeRetryAndAlwaysWipesInput"]}
def require(ok,why):
    if not ok:raise ValueError(why)
def main():
    invocation=capture(__file__);require(not OUT.exists() and not SLOT.exists(),'new-only')
    p=data.read_checked(data.BASE/POST[0]/'manifest.json',POST[1]);raw=data.read_checked(data.BASE/'PG17740-auth-borrowed-boundary-three-pt-v1/manifest.json',RAW)
    expected={(c,n) for c,ns in METHODS.items() for n in ns}
    def contract(v):
        require(type(v['actualExit']) is int and v['actualExit']==0 and v['source']==SOURCE and v['originalManifestSha256']==RAW,'exact source/run')
        require((v['tests'],v['suites'],v['targetSourceUnits'],len(v['physicalClasses']))==(3,1,3,3),'one complete Source denominator')
        require(set(v['metadataClasses'])==original.METADATA and v['unexecutedCodeClasses']==[],'Factory NoCode, all Main Code denominators')
        require(len(v['cases'])==3 and {(x['classname'],x['name']) for x in v['cases']}==expected and all(x['result']=='PASS' for x in v['cases']),'whole original11 only')
        require(v['singleSession'] is True and v['crcMismatch']==0 and v['execSha256']==raw['execSha256'] and v['sessionIdentity']==original.SESSION,'one session/CRC')
        require(v['totals']=={'LINE':{'missed':56,'covered':122},'METHOD':{'missed':2,'covered':13},'CLASS':{'missed':0,'covered':3},'BRANCH':{'missed':40,'covered':26}},'complete partial counters')
        require(set(v['fullSourceUnits'])==set(original.MAIN_UNITS) and all(set(v['fullSourceUnits'][n]['physical'])==set(original.CLOSURES[n]) and v['fullSourceUnits'][n]['four100'] is False for n in original.MAIN_UNITS),'one whole partial closure')
        require(v['strictFour100GateExit']==1 and v['targetUnitFour100'] is False and v['manualCounterExclusions']==[] and v['officialGeneratedFiltersUnchanged'] is True,'no exclusions')
        require(set(v['physicalClasses'])=={n for group in original.CLOSURES.values() for n in group},'exact whole physical identity')
        require(v['syntheticBorrowedAuthenticationJdbcFaultPortsOnly'] is v['syntheticJdbcPortsOnly'] is v['syntheticJdbcApiCallsInvoked'] is v['syntheticJdbcPrepareBindUpdateCloseInvoked'] is True,'borrowed JDBC interface calls, not actual backend')
        require(type(v['publicZeroAuthCodecFixtureBytes']) is int and v['publicZeroAuthCodecFixtureBytes']==32 and type(v['jdkSecureRandomObjectsConstructed']) is int and v['jdkSecureRandomObjectsConstructed']==2 and type(v['jdkSha256ObjectsConstructed']) is int and v['jdkSha256ObjectsConstructed']==1 and v['jdkProviderInternalEntropyReads'] is None,'explicit constructor scope, unknown internal JDK IO not fabricated')
        require(v['publicSyntheticUuidFixture'] is v['publicFixedUuidFixtureOnly'] is True and v['publicZeroKeyFixtureCopiedAndWipedOnly'] is v['sessionIssueNotCalledByFixedFalsePredicateAndSourceProof'] is True,'public fixed fixture and no session issue source proof')
        require(v['actualNetworkActions']==0,'actual self-owned network, operation count unknown not zero')
        require(v['testOwnJavaMonotonicClockRead'] is v['ownCurrentThreadInterruptFlagModifiedAndFinallyCleared'] is False and v['ownThreadCount']==0 and v['cryptoOrKeyOperationsInvoked'] is True and v['actualNativeHookOrProviderOperation'] is False,'owned JDK clock/interrupt, no invented thread total/native')
        require(v['forbiddenProductProbeHits']==0 and all(not x['recordPresent'] for k in ['rootRecoveryProbeAudit','syntheticBackupCycleProbeAudit','reviewedInactiveBoundaryAudit'] for x in v[k].values()),'held/Root/native absent')
        require(v['actualFilesOpenedByProduct'] is v['actualJdbcBackendConnected'] is False and v['actualBackendSqlOperations']==v['actualVmActions']==0,'no real DB/file/VM')
        require(v['productTestsReexecutedByPost']==0 and v['oldCoverageTransferred'] is v['priorProductResultsReused'] is v['formalUpdated'] is v['whole451Accepted'] is False and v['newAccepted']==0 and v['effortPercent'] is None,'no formal/replay transfer')
    contract(p);labels=[]
    for key,value in [('source','OLD'),('actualExit',True),('tests',0),('suites',0),('targetSourceUnits',0),('physicalClasses',{}),('metadataClasses',['unknown']),('unexecutedCodeClasses',['unknown']),('cases',[]),('singleSession',False),('crcMismatch',1),('totals',{}),('fullSourceUnits',{}),('strictFour100GateExit',0),('targetUnitFour100',True),('manualCounterExclusions',['x']),('actualNetworkActions',1),('testOwnJavaMonotonicClockRead',True),('ownCurrentThreadInterruptFlagModifiedAndFinallyCleared',True),('ownThreadCount',1),('cryptoOrKeyOperationsInvoked',False),('forbiddenProductProbeHits',1),('actualFilesOpenedByProduct',True),('actualJdbcBackendConnected',True),('oldCoverageTransferred',True),('formalUpdated',True),('newAccepted',1),('effortPercent',100),('syntheticBorrowedAuthenticationJdbcFaultPortsOnly',False),('publicZeroAuthCodecFixtureBytes',0),('jdkProviderInternalEntropyReads',0)]:
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
    text=original.TESTS['AuthenticationJdbcBoundary329Test'].read_text()
    for token in ['for (int mode = 0; mode < 3; mode++)','mode == 0 ? fatal : null','next.initCause(fatal)','next.setNextException(sql)','assertSame(fatal,','"authentication storage is unavailable"','assertNull(actual.getCause())','assertEquals(0, actual.getSuppressed().length)','assertEquals(failAt, fixture.prepares)','assertEquals(failAt, fixture.executes)','assertEquals(failAt, fixture.statementCloses)','assertEquals(failAt == 5 ? 2 : 0, fixture.resultCloses)','assertEquals(0, fixture.connectionCloses)','assertEquals(0, fixture.commits)','assertEquals(0, fixture.rollbacks)','assertArrayEquals(new char[3], password)','assertEquals(3, passwordCalls.get())','new AuthContextCodec("v1", new byte[32], null, null)','return false;','InetAddress.ofLiteral("127.0.0.1")']:
        require(token in text,'independent original ownership/fatal/wipe oracle '+token)
    require('DriverManager' not in text and 'TemporaryInfrastructureException' not in text and 'FingerprintKeyRing' not in text and 'UUID.randomUUID()' not in text,'no actual backend/held classifier or generated UUID')
    require(3+2*3+5*3==24 and 2*3==6,'independent original per-mode arithmetic, not backend counts')
    for relative,pin in original.PUBLIC_READS.items():
        require(data.sha((data.ROOT/relative).read_bytes())==pin,'exact auxiliary constructor/callee source')
    service=(data.ROOT/original.source_path(original.MAIN_UNITS[original.NAME])).read_text()
    require('if (active && matches)' in service and 'sessions.issue(' in service and 'finally {' in service and "Arrays.fill(password, '\\0')" in service,'reviewed deny branch and unconditional input wipe')
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
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,postSha256=POST[1],originalRawSha256=RAW,tests=3,suites=1,independentPreparedStatementLifecycleVectors=24,independentResultSetCloseVectors=6,providerObjectCountsBasis='DIRECT_EXPLICIT_CONSTRUCTORS_IN_REVIEWED_TEST_CALLEE_SOURCE_NOT_TOTAL_JDK_ALLOCATIONS',jdkProviderInternalEntropyReads=None,semanticNegativeVectors=len(labels),negativeLabels=labels,independentOracleVectors=3,originalTestSourceHashes=input_hashes,testPhysicalHashes=physical,testCrcIdentityClasses={r[1]:r[2] for r in crc},passiveTestCrcStage=stage,newSourcePrograms=3,newPhysicalClasses=3,metadataPhysicalClasses=0,partialSourcePrograms=3,actualOwnedLoopbackFixtureNetwork=False,networkOperationCount=0,actualExternalNetworkActions=0,actualProductionServiceActions=0,originalProductTestsReexecuted=0,oldSourceTransferred=False,coverageExecUnion=False,actualDatabaseActions=0,actualVmActions=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
