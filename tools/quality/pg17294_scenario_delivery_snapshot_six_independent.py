"""Independent six handwritten wire/boundary oracles and passive Test CRC, no Product replay."""
import copy
import os
from pathlib import Path
import re
import shutil
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg9666_pagination_static as runner
import pg17290_scenario_delivery_snapshot_six_pt as original
SOURCE=original.SOURCE
POST=('PG17292-scenario-delivery-snapshot-six-post-v1','7b20529012b0ffe4964a7216607503184ce24d82537c6c5c61639b0c6f242316')
RAW='b210929cc7505eebd4e9b0935fdb4388b5e3c04eb9492bb9d30d80d16b36ad5a'
RUN=data.ROOT.parent/'pgpt-runs/PG379/pg17290-scenario-delivery-snapshot-six-pt-v1'
OUT=data.BASE/'PG17294-scenario-delivery-snapshot-six-independent-v1'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg17294-scenario-delivery-snapshot-six-independent-v1'
METHODS={
 'dev.codex.schubert.nk.api.application.scenario.ScenarioDetailDeliveryTest':['r01ZeroThrough200RecordsStayInlineAndNeverPublish','r02Above200PublishesOnceAndProjectsEveryFileDescriptorField','r03NullPortFailureAndMismatchedDescriptorNeverFallbackOrRegenerate'],
 'dev.codex.schubert.nk.api.persistence.ScenarioDetailSnapshotBoundaryTest':['snapshotMax001MaximumRowsRemainImmutableAndKeepLastRecord','snapshotMax002InteriorAndTailSequenceGapsRejectWithoutChangingCaller','snapshotMax003TailTextPastWireBoundRejectsBeforeSnapshotEscapes']}
D='dev/codex/schubert/nk/api/application/scenario/ScenarioDetailDelivery'
S='dev/codex/schubert/nk/api/persistence/ScenarioDetailSnapshot'
def require(ok,why):
    if not ok:raise ValueError(why)
def main():
    invocation=capture(__file__);require(not OUT.exists() and not SLOT.exists(),'new-only')
    p=data.read_checked(data.BASE/POST[0]/'manifest.json',POST[1]);raw=data.read_checked(data.BASE/'PG17290-scenario-delivery-snapshot-six-pt-v1/manifest.json',RAW)
    expected={(c,n) for c,ns in METHODS.items() for n in ns}
    def contract(v):
        require(type(v['actualExit']) is int and v['actualExit']==0 and v['source']==SOURCE and v['originalManifestSha256']==RAW,'genuine current post')
        require((v['tests'],v['suites'],v['targetSourceUnits'],len(v['physicalClasses']),len(v['metadataClasses']))==(6,2,2,2,0),'two complete Code Sources')
        require(len(v['cases'])==6 and {(r['classname'],r['name']) for r in v['cases']}==expected and all(r['result']=='PASS' for r in v['cases']),'six whole originals')
        require(v['singleSession'] is True and v['crcMismatch']==0 and v['execSha256']==raw['execSha256'] and v['sessionIdentity']==original.SESSION,'actual one session/CRC')
        require(v['totals']=={'LINE':{'missed':1,'covered':49},'METHOD':{'missed':0,'covered':6},'CLASS':{'missed':0,'covered':2},'BRANCH':{'missed':2,'covered':8}},'actual full denominators')
        units=v['fullSourceUnits'];require(set(units)=={D,S} and units[D]['four100'] is True and units[S]['four100'] is False and units[D]['physical']==[D] and units[S]['physical']==[S],'both whole Source and distinct profiles')
        require(units[D]['totals']=={'LINE':{'missed':0,'covered':32},'METHOD':{'missed':0,'covered':4},'CLASS':{'missed':0,'covered':1},'BRANCH':{'missed':0,'covered':4}} and units[S]['totals']=={'LINE':{'missed':1,'covered':17},'METHOD':{'missed':0,'covered':2},'CLASS':{'missed':0,'covered':1},'BRANCH':{'missed':2,'covered':4}},'no source-counter transfer')
        require(v['strictFour100GateExit']==1 and v['targetUnitFour100'] is False and v['manualCounterExclusions']==[] and v['officialGeneratedFiltersUnchanged'] is True,'partial Snapshot stays partial')
        require(v['cryptoOrKeyOperationsInvoked'] is False and v['syntheticScenarioPublisherCallbackInvoked'] is True and v['stubDescriptorContentHashNotVerified'] is True and v['publicFixedUuidFixtureOnly'] is True,'projection not actual content/hash/crypto')
        require(v['forbiddenProductProbeHits']==0 and all(not r['recordPresent'] for r in v['rootRecoveryProbeAudit'].values()) and all(not r['recordPresent'] for r in v['syntheticBackupCycleProbeAudit'].values()) and all(not r['recordPresent'] for r in v['reviewedInactiveBoundaryAudit'].values()),'held/Root/native absent')
        require(v['actualFilesOpenedByProduct'] is v['actualJdbcBackendConnected'] is False and v['actualBackendSqlOperations']==v['actualVmActions']==0,'no backend')
        require(v['productTestsReexecutedByPost']==0 and v['priorProductResultsReused'] is v['oldCoverageTransferred'] is v['formalUpdated'] is v['whole451Accepted'] is False and v['newAccepted']==0 and v['effortPercent'] is None,'no formal/replay')
    contract(p);labels=[]
    vectors=[('source','OLD'),('actualExit',True),('tests',7),('suites',1),('targetSourceUnits',1),('physicalClasses',{}),('metadataClasses',['unknown']),('cases',[]),('singleSession',False),('crcMismatch',1),('totals',{}),('fullSourceUnits',{}),('strictFour100GateExit',0),('targetUnitFour100',True),('manualCounterExclusions',['excluded']),('cryptoOrKeyOperationsInvoked',True),('stubDescriptorContentHashNotVerified',False),('forbiddenProductProbeHits',1),('actualFilesOpenedByProduct',True),('actualJdbcBackendConnected',True),('oldCoverageTransferred',True),('formalUpdated',True),('newAccepted',1),('effortPercent',100)]
    for key,value in vectors:
        bad=copy.deepcopy(p);bad[key]=value;require(bad!=p,'nondegenerate '+key)
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false current post '+key)
    input_hashes={}
    for binary,names in METHODS.items():
        path=original.TESTS[binary.rsplit('.',1)[1]];text=path.read_text()
        require(re.findall(r'@Test\s+void\s+(\w+)\(',text)==names,'whole original methods')
        require(data.sha(path.read_bytes())==raw['begin']['sourceHashes'][str(path.relative_to(data.ROOT))]==original.PINS[path.stem],'same source')
        input_hashes[str(path.relative_to(data.ROOT))]=data.sha(path.read_bytes())
    delivery=original.TESTS['ScenarioDetailDeliveryTest'].read_text();boundary=original.TESTS['ScenarioDetailSnapshotBoundaryTest'].read_text()
    require(all(t in delivery for t in ['new int[] {0, 1, 199, 200}','new int[] {201, 10000}','byte[] bytes = spaces(1728)','byte[] bytes = spaces(4800)','number(bytes, 1621, 12','number(bytes, 1697, 6','number(bytes, 1703, 9','text(bytes, 1329','text(bytes, 1365','text(bytes, 1633','1984 + count * 4800','assertSame(\n        failure','published scenario record count differs from snapshot']),'handwritten byte offsets/boundaries, no production expected generator')
    require(all(t in boundary for t in ['MAXIMUM_ROWS = 10_000','new int[] {201, 5000, 9999}','"x".repeat(4097)','"row-10000"','assertSame(bad','UnsupportedOperationException.class']),'independent max/interior/tail/null/immutability boundaries')
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
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,postSha256=POST[1],originalRawSha256=RAW,tests=6,suites=2,semanticNegativeVectors=len(labels),negativeLabels=labels,independentOracleVectors=6,originalTestSourceHashes=input_hashes,testPhysicalHashes=physical,testCrcIdentityClasses={r[1]:r[2] for r in crc},passiveTestCrcStage=stage,wholeSourceProfiles=dict(four100=[D],partial=[S]),newSourcePrograms=2,newPhysicalClasses=2,metadataPhysicalClasses=0,snapshotMissedLine=1,snapshotMissedBranches=2,stubFileHashIsNotContentOracle=True,originalProductTestsReexecuted=0,oldSourceTransferred=False,coverageExecUnion=False,actualDatabaseActions=0,actualVmActions=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
