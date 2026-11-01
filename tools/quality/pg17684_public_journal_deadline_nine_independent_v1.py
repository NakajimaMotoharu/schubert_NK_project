"""Independent original permit-data6 literals, null-before-I/O and Java line-pair guard metadata."""
import copy
import os
from pathlib import Path
import re
import shutil
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg9666_pagination_static as runner
import pg17680_public_journal_deadline_nine_pt_v1 as original
SOURCE=original.SOURCE
POST=('PG17682-public-journal-deadline-nine-post-v1','1aa5ae001a9df7d4db9c140370c5f604b792b0e15d6e7f67359795a5d68707f1')
RAW='49473246237052e405cfbab6a41539fac97ffb6815b3bb6f9b1868191d55519c'
RUN=data.ROOT.parent/'pgpt-runs/PG379/pg17680-public-journal-deadline-nine-pt-v1'
OUT=data.BASE/'PG17684-public-journal-deadline-nine-independent-v1'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg17684-public-journal-deadline-nine-independent-v1'
METHODS={"dev.codex.schubert.nk.batch.platform.BrokerJournalEvidenceTest":["bj2478001AnchorMetadataAndExactByteBoundariesRejectForeignOrMissingEvidence","bj2478002CanonicalAndStrictJsonBoundariesDoNotNormalizeUnavailableEvidence","bj2478003ClosedHistoryRequiresIndependentCursorTimeAndCanonicalDigest","bj2478004CryptoProviderOutageIsRedactedAndRegistryRestored","issbrokerstop001ActualStopEventNeedsSameBootInvocationWholeIntervalAndExactBytes","allThreePrimaryVendorEventsBoundToActualGenerationAndExactBytes","emptyOldMalformedDuplicatedOrErrorCannotProveRecovery"],"dev.codex.schubert.nk.batch.mq.ArtemisParentDeadlineTest":["eachExchangeBorrowsActualRemainingAndNeverRoundsUp","exceptionExpiryNestedAndOtherThreadNeverEscapeOwnerLifetime"]}
def require(ok,why):
    if not ok:raise ValueError(why)
def main():
    invocation=capture(__file__);require(not OUT.exists() and not SLOT.exists(),'new-only')
    p=data.read_checked(data.BASE/POST[0]/'manifest.json',POST[1]);raw=data.read_checked(data.BASE/'PG17680-public-journal-deadline-nine-pt-v1/manifest.json',RAW)
    expected={(c,n) for c,ns in METHODS.items() for n in ns}
    def contract(v):
        require(type(v['actualExit']) is int and v['actualExit']==0 and v['source']==SOURCE and v['originalManifestSha256']==RAW,'exact source/run')
        require((v['tests'],v['suites'],v['targetSourceUnits'],len(v['physicalClasses']))==(9,2,2,9),'one complete Source denominator')
        require(set(v['metadataClasses'])==original.METADATA and len(v['unexecutedCodeClasses'])==0,'Factory NoCode, all Main Code denominators')
        require(len(v['cases'])==9 and {(x['classname'],x['name']) for x in v['cases']}==expected and all(x['result']=='PASS' for x in v['cases']),'whole original11 only')
        require(v['singleSession'] is True and v['crcMismatch']==0 and v['execSha256']==raw['execSha256'] and v['sessionIdentity']==original.SESSION,'one session/CRC')
        require(v['totals']=={'LINE':{'missed':141,'covered':173},'METHOD':{'missed':39,'covered':18},'CLASS':{'missed':0,'covered':4},'BRANCH':{'missed':53,'covered':103}},'complete partial counters')
        require(set(v['fullSourceUnits'])==set(original.MAIN_UNITS) and all(set(v['fullSourceUnits'][n]['physical'])==set(original.CLOSURES[n]) and v['fullSourceUnits'][n]['four100'] is False for n in original.MAIN_UNITS),'one whole partial closure')
        require(v['strictFour100GateExit']==1 and v['targetUnitFour100'] is False and v['manualCounterExclusions']==[] and v['officialGeneratedFiltersUnchanged'] is True,'no exclusions')
        require(v['actualNetworkActions']==0,'actual self-owned network, operation count unknown not zero')
        require(v['testOwnJavaMonotonicClockRead'] is v['ownCurrentThreadInterruptFlagModifiedAndFinallyCleared'] is False and v['ownThreadCount']==1 and v['cryptoOrKeyOperationsInvoked'] is True and v['actualNativeHookOrProviderOperation'] is False,'owned JDK clock/interrupt, no invented thread total/native')
        require(v['forbiddenProductProbeHits']==0 and all(not x['recordPresent'] for k in ['rootRecoveryProbeAudit','syntheticBackupCycleProbeAudit','reviewedInactiveBoundaryAudit'] for x in v[k].values()),'held/Root/native absent')
        require(v['actualFilesOpenedByProduct'] is v['actualJdbcBackendConnected'] is False and v['actualBackendSqlOperations']==v['actualVmActions']==0,'no real DB/file/VM')
        require(v['productTestsReexecutedByPost']==0 and v['oldCoverageTransferred'] is v['priorProductResultsReused'] is v['formalUpdated'] is v['whole451Accepted'] is False and v['newAccepted']==0 and v['effortPercent'] is None,'no formal/replay transfer')
    contract(p);labels=[]
    for key,value in [('source','OLD'),('actualExit',True),('tests',0),('suites',0),('targetSourceUnits',0),('physicalClasses',{}),('metadataClasses',['unknown']),('unexecutedCodeClasses',['unknown']),('cases',[]),('singleSession',False),('crcMismatch',1),('totals',{}),('fullSourceUnits',{}),('strictFour100GateExit',0),('targetUnitFour100',True),('manualCounterExclusions',['x']),('actualNetworkActions',1),('testOwnJavaMonotonicClockRead',True),('ownCurrentThreadInterruptFlagModifiedAndFinallyCleared',True),('ownThreadCount',2),('cryptoOrKeyOperationsInvoked',False),('forbiddenProductProbeHits',1),('actualFilesOpenedByProduct',True),('actualJdbcBackendConnected',True),('oldCoverageTransferred',True),('formalUpdated',True),('newAccepted',1),('effortPercent',100)]:
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
    journal=original.TESTS['BrokerJournalEvidenceTest'].read_text()
    for token in ['Security.removeProvider(provider.getName())','Security.insertProviderAt(original[i], i + 1)','assertArrayEquals(original, Security.getProviders())','finally {','ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad','65536','65537','4 * 1024 * 1024 + 1','BigInteger.valueOf(1234567)','Broker journal evidence unavailable','NKJOURNAL1','AMQ221002','assertEquals(3, actual.entries())']:
        require(token in journal,'independent literal public journal oracle '+token)
    deadline=original.TESTS['ArtemisParentDeadlineTest'].read_text()
    for token in ['5_000_000_000L','1_999_999_999L','999_999L','remaining[0] = 0','assertEquals(1999,','assertEquals(1,','thread.start();','thread.join();','assertEquals(2000, other[0])','no nested replacement budget','no operation after exhausted parent','NullPointerException.class']:
        require(token in deadline,'independent fixed timeout/ownership oracle '+token)
    import hashlib
    require(hashlib.sha256(b'abc').hexdigest()=='ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad','independent public standard vector')
    for nanos,expected_ms in [(5000000000,2000),(1999999999,1999),(1000000,1)]:
        require(min(2000,nanos//1000000)==expected_ms,'independent integer floor, not Production result')
    require(p['testOwnJcaProviderRegistryTemporarilyModifiedAndFinallyRestored'] is p['publicDigestOnly'] is p['cryptoOrKeyOperationsInvoked'] is True and p['ownThreadCount']==1 and p['actualSecretKeysLoaded'] is False,'own JVM provider restoration and one own Thread only')
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
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,postSha256=POST[1],originalRawSha256=RAW,tests=9,suites=2,independentPublicDigestVectors=1,independentIntegerFloorVectors=3,ownProviderRegistryRestoredOriginalAssertion=True,semanticNegativeVectors=len(labels),negativeLabels=labels,independentOracleVectors=9,originalTestSourceHashes=input_hashes,testPhysicalHashes=physical,testCrcIdentityClasses={r[1]:r[2] for r in crc},passiveTestCrcStage=stage,newSourcePrograms=0,newPhysicalClasses=0,metadataPhysicalClasses=5,partialSourcePrograms=2,actualOwnedLoopbackFixtureNetwork=False,networkOperationCount=0,actualExternalNetworkActions=0,actualProductionServiceActions=0,originalProductTestsReexecuted=0,oldSourceTransferred=False,coverageExecUnion=False,actualDatabaseActions=0,actualVmActions=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
