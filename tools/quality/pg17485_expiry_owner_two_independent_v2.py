"""Independent public ELF hash vectors, semantic negative metadata and passive original Test CRC."""
import copy
import os
from pathlib import Path
import re
import shutil
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg9666_pagination_static as runner
import pg17480_expiry_owner_two_pt as original
SOURCE=original.SOURCE
POST=('PG17482-expiry-owner-two-post-v1','cf4ea8e6a6095fb25c20b562a030fce1dbb639a6e4e7fec8312bb37a8c216a71')
RAW='51797f2b4a343b94450640ebe74cfc0b7c0a0485ff2020c7e8c317476b878140'
RUN=data.ROOT.parent/'pgpt-runs/PG379/pg17480-expiry-owner-two-pt-v1'
OUT=data.BASE/'PG17485-expiry-owner-two-independent-v2'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg17485-expiry-owner-two-independent-v2'
METHODS={'dev.codex.schubert.nk.batch.file.ExpiryOwnerTest':['exactMorningClaimsRejectEveryIndependentCorrelationMismatch','networkBudgetRoundsDownAndUnitRequiresActualPrivateOwner']}
def require(ok,why):
    if not ok:raise ValueError(why)
def unit_contract(text):
    lines=text.splitlines()
    return (lines.count('LoadCredential=maintenance-owner:/run/schubert-nk/expiry-request/maintenance-owner')==1
        and any(a=='KillMode=control-group' and b=='SendSIGKILL=no' for a,b in zip(lines,lines[1:]))
        and 'RemainAfterExit=yes' in lines)
def main():
    invocation=capture(__file__);require(not OUT.exists() and not SLOT.exists(),'new-only')
    p=data.read_checked(data.BASE/POST[0]/'manifest.json',POST[1]);raw=data.read_checked(data.BASE/'PG17480-expiry-owner-two-pt-v1/manifest.json',RAW)
    expected={(c,n) for c,ns in METHODS.items() for n in ns}
    def contract(v):
        require(type(v['actualExit']) is int and v['actualExit']==0 and v['source']==SOURCE and v['originalManifestSha256']==RAW,'exact source/run')
        require((v['tests'],v['suites'],v['targetSourceUnits'],len(v['physicalClasses']))==(2,1,1,3),'whole Source denominator')
        require(set(v['metadataClasses'])==original.METADATA and v['unexecutedCodeClasses']==[original.NAME+'$1'],'NoCode3 plus unexecuted descriptor kept')
        require(len(v['cases'])==2 and {(x['classname'],x['name']) for x in v['cases']}==expected and all(x['result']=='PASS' for x in v['cases']),'whole original8 only')
        require(v['singleSession'] is True and v['crcMismatch']==0 and v['execSha256']==raw['execSha256'] and v['sessionIdentity']==original.SESSION,'one session/CRC')
        require(v['totals']=={'LINE':{'missed':213,'covered':11},'METHOD':{'missed':18,'covered':2},'CLASS':{'missed':1,'covered':1},'BRANCH':{'missed':64,'covered':12}},'all partial counters')
        require(set(v['fullSourceUnits'])=={original.NAME} and set(v['fullSourceUnits'][original.NAME]['physical'])==set(original.CLOSURES[original.NAME]) and v['fullSourceUnits'][original.NAME]['four100'] is False,'one complete partial closure')
        require(v['strictFour100GateExit']==1 and v['targetUnitFour100'] is False and v['manualCounterExclusions']==[] and v['officialGeneratedFiltersUnchanged'] is True,'partial not excluded')
        require(v['publicDigestOnly'] is v['cryptoOrKeyOperationsInvoked'] is False and v['testPublicSourceRead'] is v['publicSyntheticUuidFixture'] is True and v['publicSourceReadHashes']==original.PUBLIC_READS and v['actualSecretKeysLoaded'] is v['actualNativeHookOrProviderOperation'] is False,'public SHA256 no key/provider mutation')
        require(v['forbiddenProductProbeHits']==0 and all(not x['recordPresent'] for k in ['rootRecoveryProbeAudit','syntheticBackupCycleProbeAudit','reviewedInactiveBoundaryAudit'] for x in v[k].values()),'held/Root/native absent')
        require(v['actualFilesOpenedByProduct'] is v['actualJdbcBackendConnected'] is False and v['actualBackendSqlOperations']==v['actualVmActions']==0,'memory only')
        require(v['productTestsReexecutedByPost']==0 and v['oldCoverageTransferred'] is v['priorProductResultsReused'] is v['formalUpdated'] is v['whole451Accepted'] is False and v['newAccepted']==0 and v['effortPercent'] is None,'no formal/replay transfer')
    contract(p);labels=[]
    for key,value in [('source','OLD'),('actualExit',True),('tests',9),('suites',2),('targetSourceUnits',2),('physicalClasses',{}),('metadataClasses',[]),('unexecutedCodeClasses',[]),('cases',[]),('singleSession',False),('crcMismatch',1),('totals',{}),('fullSourceUnits',{}),('strictFour100GateExit',0),('targetUnitFour100',True),('manualCounterExclusions',['x']),('publicDigestOnly',True),('cryptoOrKeyOperationsInvoked',True),('actualSecretKeysLoaded',True),('actualNativeHookOrProviderOperation',True),('forbiddenProductProbeHits',1),('actualFilesOpenedByProduct',True),('actualJdbcBackendConnected',True),('oldCoverageTransferred',True),('formalUpdated',True),('newAccepted',1),('effortPercent',100),('testPublicSourceRead',False),('publicSourceReadHashes',{}),('publicSyntheticUuidFixture',False)]:
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
    budget_vectors=[]
    for nanos,expected_ms in [(30_000_000_000,5000),(1_999_999_999,1000),(999_999_999,None),(0,None)]:
        actual=None if nanos<1_000_000_000 else min(5,nanos//1_000_000_000)*1000
        require(actual==expected_ms,'independent whole second truncation/cap')
        budget_vectors.append(dict(nanos=nanos,expectedMillis=expected_ms))
    for token in ['owner(BOOT, RUN, ACTIVATION, CUTOFF, EPOCH, Optional.empty())','owner(OTHER, RUN, ACTIVATION, CUTOFF, EPOCH, Optional.empty())','owner(BOOT, OTHER, ACTIVATION, CUTOFF, EPOCH, Optional.empty())','owner(BOOT, RUN, OTHER, CUTOFF, EPOCH, Optional.empty())','CUTOFF.plusNanos(1000)','owner(BOOT, RUN, ACTIVATION, CUTOFF, OTHER, Optional.empty())','Optional.of(new MaintenanceOwnerFrame.Parent("3".repeat(32), 124, 457))','CleanupExpiryExecution.requireOwner(null, request)','assertEquals(5000, CleanupExpiryExecution.mqTimeoutMillis(() -> 30_000_000_000L))','assertEquals(1000, CleanupExpiryExecution.mqTimeoutMillis(() -> 1_999_999_999L))','mqTimeoutMillis(() -> 999_999_999L)','mqTimeoutMillis(() -> 0)','mqTimeoutMillis(null)','System.getProperty("nk.pt.repository")','KillMode=control-group\\nSendSIGKILL=no\\n','RemainAfterExit=yes\\n']:
        require(token in text,'original independent literal owner/budget/Unit oracle '+token)
    snapshot=original.COMPILE/'snapshot';normal=data.read_checked(original.COMPILE/'manifest.safe.json',original.COMPILE_SHA)
    require(text.count('Files.readString(')==1 and len(original.PUBLIC_READS)==1,'one fixed public source read')
    for path,pin in original.PUBLIC_READS.items():
        blob=(snapshot/path).read_bytes();require(data.sha(blob)==data.sha((data.ROOT/path).read_bytes())==normal['begin']['inputHashes'][path]==pin,'unchanged public Unit bytes')
        template=blob.decode();require(unit_contract(template),'independent explicit Unit values, not actual Unit execution')
        wire_negatives={
            'encoded-newline-literal':template.replace(chr(10),chr(92)+'n'),
            'wrong-kill-mode':template.replace('KillMode=control-group','KillMode=process'),
            'duplicate-owner-credential':template+'LoadCredential=maintenance-owner:/run/schubert-nk/expiry-request/maintenance-owner'+chr(10),
            'missing-remain':template.replace('RemainAfterExit=yes',''),
            'nonadjacent-send-kill':template.replace('KillMode=control-group'+chr(10)+'SendSIGKILL=no','KillMode=control-group'+chr(10)+'PUBLIC_EXTRA=yes'+chr(10)+'SendSIGKILL=no')}
        require(len(wire_negatives)==5 and all(v!=template and not unit_contract(v) for v in wire_negatives.values()),'all finite Unit expression counterexamples')
    SLOT.mkdir();runner.SLOT=SLOT;component=SLOT/'original-test-component';component.mkdir();physical={}
    names=[next(iter(METHODS)).replace('.','/')]
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
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,postSha256=POST[1],originalRawSha256=RAW,tests=2,suites=1,semanticNegativeVectors=len(labels),negativeLabels=labels,independentOracleVectors=2,independentBudgetVectors=budget_vectors,unitWireNegativeVectors=len(wire_negatives),unitWireNegativeLabels=sorted(wire_negatives),independentOwnerMismatchFields=['boot','run','activation','cutoff','epoch','cleanup'],publicReadHashes=original.PUBLIC_READS,originalTestSourceHashes=input_hashes,testPhysicalHashes=physical,testCrcIdentityClasses={r[1]:r[2] for r in crc},passiveTestCrcStage=stage,newSourcePrograms=1,newPhysicalClasses=3,metadataPhysicalClasses=1,partialSourcePrograms=1,originalProductTestsReexecuted=0,oldSourceTransferred=False,coverageExecUnion=False,actualDatabaseActions=0,actualVmActions=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
