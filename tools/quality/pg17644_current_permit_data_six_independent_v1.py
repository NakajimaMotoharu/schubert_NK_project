"""Independent original permit-data6 literals, null-before-I/O and Java line-pair guard metadata."""
import copy
import os
from pathlib import Path
import re
import shutil
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg9666_pagination_static as runner
import pg17641_current_permit_data_six_pt_v2 as original
SOURCE=original.SOURCE
POST=('PG17642-current-permit-data-six-post-v1','f59b1db5c4b23ed3981bad802ab621b9f90dce497ac030ce73d4a7892b87cfea')
RAW='48db9be724e1cd42954cd54e9fd48367ed199bb472490df14f253041c3b98a53'
RUN=data.ROOT.parent/'pgpt-runs/PG379/pg17641-current-permit-data-six-pt-v2'
OUT=data.BASE/'PG17644-current-permit-data-six-independent-v1'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg17644-current-permit-data-six-independent-v1'
METHODS={"dev.codex.schubert.nk.batch.file.RootCurrentPermitPreflightTest":["rpermit001WebBootAndReleaseAgree","rpermit002ApiHasSameFixedCorrelationWithoutWebAlias","rpermit003OldBootOrReleaseCannotPass","rpermit004OnlyServiceActorAndNonnullInputs","rpermit005NoPermitIsNeverSubstitutedWithInvalidOrMissing","rpermit006RootEntryStillRejectsEvenIfSyntheticGateAgrees"]}
def require(ok,why):
    if not ok:raise ValueError(why)
def main():
    invocation=capture(__file__);require(not OUT.exists() and not SLOT.exists(),'new-only')
    p=data.read_checked(data.BASE/POST[0]/'manifest.json',POST[1]);raw=data.read_checked(data.BASE/'PG17641-current-permit-data-six-pt-v2/manifest.json',RAW)
    expected={(c,n) for c,ns in METHODS.items() for n in ns}
    def contract(v):
        require(type(v['actualExit']) is int and v['actualExit']==0 and v['source']==SOURCE and v['originalManifestSha256']==RAW,'exact source/run')
        require((v['tests'],v['suites'],v['targetSourceUnits'],len(v['physicalClasses']))==(6,1,1,2),'one complete Source denominator')
        require(set(v['metadataClasses'])==original.METADATA and len(v['unexecutedCodeClasses'])==1,'Factory NoCode, all Main Code denominators')
        require(len(v['cases'])==6 and {(x['classname'],x['name']) for x in v['cases']}==expected and all(x['result']=='PASS' for x in v['cases']),'whole original11 only')
        require(v['singleSession'] is True and v['crcMismatch']==0 and v['execSha256']==raw['execSha256'] and v['sessionIdentity']==original.SESSION,'one session/CRC')
        require(v['totals']=={'LINE':{'missed':28,'covered':9},'METHOD':{'missed':6,'covered':1},'CLASS':{'missed':1,'covered':1},'BRANCH':{'missed':8,'covered':8}},'complete partial counters')
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
    text=original.TESTS['RootCurrentPermitPreflightTest'].read_text()
    for token in ['"11111111-1111-4111-8111-111111111111"','"a".repeat(64)','RootStartupContext.Service.WEB','RootStartupContext.Service.API','"22222222-2222-4222-8222-222222222222"','permit("b".repeat(64))','RootStartupContext.Service.MORNING','RootStartupContext.Service.CLEANUP','RootCurrentPermitPreflight.verify(null,','RootCurrentPermitPreflight.verifyNative(','null, snapshot(RootStartupContext.Service.API), RELEASE','permit("not-a-sha256")','30, RootServiceLauncher.run(new String[] {"WEB"}, ignored -> calls.incrementAndGet())','assertEquals(1, calls.get())','Instant.parse("2026-09-29T00:00:00Z")']:
        require(token in text,'independent fixed permit-data oracle '+token)
    require(p['syntheticPermitRecordConstructionOnly'] is p['nativeNamedReadNullGuardOnlyInvoked'] is p['syntheticRootAdmissionCallbackInvoked'] is True and p['actualPermitNamespaceLookups']==0 and p['actualRootOsAdmissionInvoked'] is False,'record/native-named null guard is not real permit or OS operation')
    require('new RootServiceLauncher(' not in text and 'RootServiceLauncher.main(' not in text and 'RootStartupContext.create(' not in text and 'new RootStartupContext.NativeIo' not in text,'whole original call scope, no real Root')
    def adjacent(lines):return any(a.strip()=='admission.verify(service);' and b.strip()=='return 30;' for a,b in zip(lines,lines[1:]))
    lines=(data.ROOT/'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/file/RootServiceLauncher.java').read_text().splitlines()
    require(adjacent(lines),'actual Java LF pair')
    line_labels=[]
    for label,values in [('encoded-lf',[r'admission.verify(service);\n      return 30;']),('wrong-return',['admission.verify(service);','return 0;']),('not-adjacent',['admission.verify(service);','','return 30;'])]:
        require(not adjacent(values),'invalid source guard accepted '+label);line_labels.append(label)
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
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,postSha256=POST[1],originalRawSha256=RAW,tests=6,suites=1,sourceLinePairNegativeVectors=len(line_labels),sourceLinePairNegativeLabels=line_labels,semanticNegativeVectors=len(labels),negativeLabels=labels,independentOracleVectors=6,originalTestSourceHashes=input_hashes,testPhysicalHashes=physical,testCrcIdentityClasses={r[1]:r[2] for r in crc},passiveTestCrcStage=stage,newSourcePrograms=0,newPhysicalClasses=0,metadataPhysicalClasses=0,partialSourcePrograms=1,actualOwnedLoopbackFixtureNetwork=False,networkOperationCount=0,actualExternalNetworkActions=0,actualProductionServiceActions=0,originalProductTestsReexecuted=0,oldSourceTransferred=False,coverageExecUnion=False,actualDatabaseActions=0,actualVmActions=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
