"""Independent audit five oracles and original Test/fixture CRC; no Product replay."""
import copy
import os
from pathlib import Path
import re
import shutil
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg9666_pagination_static as runner
import pg17270_scenario_audit_five_pt as original

SOURCE=original.SOURCE
POST=('PG17272-scenario-audit-five-post-v1','d8cc4985b0290ff4e83ae1219ba953b261b9049e99549f167fd11543a9df1874')
RAW='6562a8d80e17617c678ad9b76e03a784e0e6163888ce29a67cbfe458155dfdcc'
OUT=data.BASE/'PG17274-scenario-audit-five-independent-v1'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg17274-scenario-audit-five-independent-v1'
ROOT_NAME='dev/codex/schubert/nk/api/application/scenario/'
TEST_NAME=ROOT_NAME+'ScenarioAuditWriterTest'
ORACLE_NAMES=['searchCountAndSensitiveConditionsNeverLeak','inlineAndFileUseTheirIndependentRecordCounts','nonCatalogListQueriesDoNotTouchDatabase','sqlFailuresArePropagatedWithStatementOwnership','nullBoundaryFailsBeforeDatabaseEffects']
RUN=data.ROOT.parent/'pgpt-runs/PG379/pg17270-scenario-audit-five-pt-v1'
def require(ok,why):
    if not ok:raise ValueError(why)
def main():
    invocation=capture(__file__);require(not OUT.exists() and not SLOT.exists(),'new-only independent metadata/passive reader')
    p=data.read_checked(data.BASE/POST[0]/'manifest.json',POST[1])
    raw=data.read_checked(data.BASE/'PG17270-scenario-audit-five-pt-v1/manifest.json',RAW)
    expected={(TEST_NAME.replace('/','.'),n) for n in ORACLE_NAMES}
    def contract(v):
        require(type(v['actualExit']) is int and v['actualExit']==0 and v['source']==SOURCE and v['originalManifestSha256']==RAW,'same genuine post/source')
        require((v['tests'],v['suites'],v['targetSourceUnits'],len(v['physicalClasses']),len(v['metadataClasses']))==(5,1,1,1,0),'full Source denominator')
        require(len(v['cases'])==5 and {(r['classname'],r['name']) for r in v['cases']}==expected and all(r['result']=='PASS' for r in v['cases']),'exact original seven')
        require(v['singleSession'] is True and v['crcMismatch']==0 and v['execSha256']==raw['execSha256'] and v['sessionIdentity']==original.SESSION,'original CRC/session no transfer')
        require(v['strictFour100GateExit']==0 and v['targetUnitFour100'] is True and v['manualCounterExclusions']==[] and v['officialGeneratedFiltersUnchanged'] is True,'partial denominator unchanged')
        require(v['totals']=={'LINE':{'missed':0,'covered':35},'METHOD':{'missed':0,'covered':2},'CLASS':{'missed':0,'covered':1},'BRANCH':{'missed':0,'covered':7}},'measured counts not merged old records')
        require(v['forbiddenProductProbeHits']==0 and all(not r['recordPresent'] for r in v['rootRecoveryProbeAudit'].values()) and all(not r['recordPresent'] for r in v['syntheticBackupCycleProbeAudit'].values()) and all(not r['recordPresent'] for r in v['reviewedInactiveBoundaryAudit'].values()),'Root/native/real fixture absent')
        require(v['actualJdbcBackendConnected'] is False and v['actualBackendSqlOperations']==v['actualJmsConnectionsCreated']==v['actualVmActions']==0,'fake JDBC not backend')
        require(v['productTestsReexecutedByPost']==0 and v['priorProductResultsReused'] is v['oldCoverageTransferred'] is v['formalUpdated'] is v['whole451Accepted'] is False and v['newAccepted']==0 and v['effortPercent'] is None,'no replay/whole claim')
    contract(p);labels=[]
    vectors=[('source','OLD'),('actualExit',True),('tests',6),('suites',2),('targetSourceUnits',2),('physicalClasses',{}),('metadataClasses',[]),('cases',[]),('singleSession',False),('crcMismatch',1),('strictFour100GateExit',1),('targetUnitFour100',False),('manualCounterExclusions',['excluded']),('totals',{}),('forbiddenProductProbeHits',1),('actualJdbcBackendConnected',True),('actualBackendSqlOperations',1),('productTestsReexecutedByPost',1),('oldCoverageTransferred',True),('formalUpdated',True),('newAccepted',1),('effortPercent',100)]
    for key,value in vectors:
        v=copy.deepcopy(p);v[key]=value;require(v!=p,'nondegenerate '+key)
        try:contract(v)
        except ValueError:labels.append(key)
        else:raise ValueError('false semantic post '+key)
    test_path=str(original.TESTS['ScenarioAuditWriterTest'].relative_to(data.ROOT));text=(data.ROOT/test_path).read_text()
    require(re.findall(r'@Test\s+void\s+(\w+)\(',text)==ORACLE_NAMES,'whole original seven source')
    require(data.sha(text.encode())==raw['begin']['sourceHashes'][test_path]=='a9d54940e22d9bb51f7e122346a2bb34e6e28b9c08ab880e3041ad8a8faacb45','exact source oracle')
    tokens=['99_999_900','SCENARIO_SEARCHED','SCENARIO_VIEWED','assertEquals(Set.of(1, 2, 3, 4, 5, 6, 7, 8)','assertEquals("é     "','for (String fault :','for (int changed : new int[] {0, 2})','assertSame(jdbc.failure, failure)','audit must not own connection lifecycle','synthetic-private']
    require(all(t in text for t in tokens),'independent SQL/bind/count/NFC/closed JSON/ownership/null oracle')
    fixture='src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/scenario/ScenarioRequestFixture.java'
    require(data.sha((data.ROOT/fixture).read_bytes())==raw['begin']['sourceHashes'][fixture]=='59b79a09aa45f9878e551e4f7943c9f88b597b1f5976f46daa038a9811ae23f8','original hand-built fixture')
    require('UUID.randomUUID()' in (data.ROOT/fixture).read_text() and all(t not in text for t in ['@Before','@After','@TempDir','DriverManager','ProcessBuilder','TemporaryInfrastructureException','WebStartupException','FingerprintKeyRing','ResponseSnapshotCodec']),'random public UUID not runtime authority')
    SLOT.mkdir();runner.SLOT=SLOT;component=SLOT/'original-test-component';component.mkdir()
    names=[TEST_NAME,TEST_NAME+'$Jdbc',ROOT_NAME+'ScenarioRequestFixture']
    physical={}
    for name in names:
        src=RUN/'fresh-test-classes'/(name+'.class');dst=component/(name+'.class');dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst);physical[name]=data.sha(src.read_bytes())
    receipt=data.read_checked(data.ROOT.parent/'pgpt-runs/PG379/pg13376-db-duration-eight-post-v1/session-identity-exit.safe.json','2bbd55eefa4fc2b0532660748a0f35bfeca6cb69e45e732fc67759add964a84b')
    cp=receipt['command'][2];reader=data.ROOT.parent/'pgpt-runs/PG379/pg15713-caddy-public-value-nine-post-v2/diagnostic-classes'
    require(data.sha((reader/'WholeSourceCoverageMeasureV1.class').read_bytes())=='9977e1c733e40e4752261c38e6a679a91cf2d33b6d2be72180e1f67af01a94a3','qualified passive class')
    runtime=data.read_checked(data.BASE/'PG13378-db-duration-eight-post-recovery-v3/manifest.json','adcb55b80aa70a449e74280aa465f752308310c41c876cf83a5a78c3dda3c882')
    require(all(data.sha(Path(k).read_bytes())==v for k,v in runtime['toolAndDependencyHashes'].items()),'fixed reader SDK')
    stage=runner.step('passive-original-test-crc',[str(runner.TC/'jdk-25.0.4/bin/java'),'-cp',str(reader)+os.pathsep+cp,'WholeSourceCoverageMeasureV1',str(RUN/'jacoco.exec'),str(component),*names],SLOT,timeout=120)
    require(stage['actualExit']==0 and not stage['timedOut'],'original Test/Probe CRC identity')
    out=(SLOT/'passive-original-test-crc.stdout').read_text().splitlines()
    crc_rows=[line.split(chr(9)) for line in out if line.startswith('CLASS'+chr(9))]
    require(len(crc_rows)==3 and {r[1] for r in crc_rows}==set(names) and not any(line.startswith('METADATA'+chr(9)) for line in out),'exact three Code/one genuine NoCode')
    verify(p['invocation']);verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir()
    value=dict(actualExit=0,source=SOURCE,invocation=invocation,postSha256=POST[1],originalRawSha256=RAW,tests=5,suites=1,semanticNegativeVectors=len(labels),negativeLabels=labels,independentOracleVectors=5,originalTestSourceSha256=data.sha(text.encode()),independentOracleBasis='LITERAL_SQL_EIGHT_BINDS_NFC_CLOSED_JSON_COUNT_FIXED_FAULT_AND_API_NULL',originalWholeTestClasses=1,originalHelperClasses=1,originalTestInnerClasses=1,originalTestPhysicalHashes=physical,testCrcIdentityClasses={r[1]:r[2] for r in crc_rows},passiveTestCrcStage=stage,guardNegativeVectorsNotClaimed=True,metadataNegativeVectorsNotProductTests=True,originalProductTestsReexecuted=0,oldSourceTransferred=False,coverageExecUnion=False,actualDatabaseActions=0,actualVmActions=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,effortPercent=None)
    data.write(OUT/'manifest.json',value);print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
