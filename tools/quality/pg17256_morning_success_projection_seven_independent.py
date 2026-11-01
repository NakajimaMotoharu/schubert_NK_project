"""Independent original seven oracles and passive Test CRC/lifecycle audit; no Product replay."""
import copy
import os
from pathlib import Path
import re
import shutil
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg9666_pagination_static as runner
import pg17251_morning_success_projection_seven_pt_v2 as original

SOURCE=original.SOURCE
POST=('PG17254-morning-success-projection-seven-post-v3','ccb6da2bbe37d70d903138e33c775e998b08ef7060ca298b2cf2a33de84a85b2')
RAW='a47fb4f2195d2c52c48222a299dd31063c9cd9f21e9975932eb0f7b3b1a99af1'
OUT=data.BASE/'PG17256-morning-success-projection-seven-independent-v1'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg17256-morning-success-projection-seven-independent-v1'
ROOT_NAME='dev/codex/schubert/nk/batch/repository/'
TEST_NAME=ROOT_NAME+'MorningSuccessfulBackupProjectionTest'
ORACLE_NAMES=[
 'mdbProj1737001BothSqlOrdersReturnLiteralIdsAndNoMutation',
 'mdbProj1737002EmptyMeansNoReusablePairAndIncompleteOrExtraRowsReject',
 'mdbProj1737003EveryRequiredProjectionNullRejectsWithoutNpeOrLeak',
 'mdbProj1737004EachSemanticFieldCounterexampleRejects',
 'mdbProj1737005PairAttemptStartAndEndMustBeOneBundle',
 'mdbProj1737006EndAtObservationAndPositiveByteBoundaryRemainEligible',
 'mdbProj1737007AllowedJdbcFailuresAndUnknownProviderIdentityCloseEveryResource']
def require(ok,why):
    if not ok:raise ValueError(why)
def main():
    invocation=capture(__file__);require(not OUT.exists() and not SLOT.exists(),'new-only independent metadata/passive reader')
    p=data.read_checked(data.BASE/POST[0]/'manifest.json',POST[1])
    raw=data.read_checked(original.OUT/'manifest.json',RAW)
    expected={(TEST_NAME.replace('/','.'),n) for n in ORACLE_NAMES}
    def contract(v):
        require(type(v['actualExit']) is int and v['actualExit']==0 and v['source']==SOURCE and v['originalManifestSha256']==RAW,'same genuine post/source')
        require((v['tests'],v['suites'],v['targetSourceUnits'],len(v['physicalClasses']),len(v['metadataClasses']))==(7,1,1,17,6),'full Source denominator')
        require(len(v['cases'])==7 and {(r['classname'],r['name']) for r in v['cases']}==expected and all(r['result']=='PASS' for r in v['cases']),'exact original seven')
        require(v['singleSession'] is True and v['crcMismatch']==0 and v['execSha256']==raw['execSha256'] and v['sessionIdentity']==original.SESSION,'original CRC/session no transfer')
        require(v['strictFour100GateExit']==1 and v['targetUnitFour100'] is False and v['manualCounterExclusions']==[] and v['officialGeneratedFiltersUnchanged'] is True,'partial denominator unchanged')
        require(v['totals']=={'LINE':{'missed':732,'covered':169},'METHOD':{'missed':81,'covered':23},'CLASS':{'missed':7,'covered':4},'BRANCH':{'missed':460,'covered':65}},'measured counts not merged old records')
        require(v['forbiddenProductProbeHits']==0 and all(not r['recordPresent'] for r in v['rootRecoveryProbeAudit'].values()) and all(not r['recordPresent'] for r in v['syntheticBackupCycleProbeAudit'].values()) and all(not r['recordPresent'] for r in v['reviewedInactiveBoundaryAudit'].values()),'Root/native/real fixture absent')
        require(v['actualJdbcBackendConnected'] is False and v['actualBackendSqlOperations']==v['actualJmsConnectionsCreated']==v['actualVmActions']==0,'fake JDBC not backend')
        require(v['productTestsReexecutedByPost']==0 and v['priorProductResultsReused'] is v['oldCoverageTransferred'] is v['formalUpdated'] is v['whole451Accepted'] is False and v['newAccepted']==0 and v['effortPercent'] is None,'no replay/whole claim')
        life=v['originalUnusedHelperProbeAudit']['originalOuterTestLifecycle']
        require(life['unselectedTestAndLifecycleTrueInstructions']==0 and life['productClassesLoaded'] is life['productMethodsInvoked'] is False,'passive lifecycle proof not invocation')
    contract(p);labels=[]
    vectors=[('source','OLD'),('actualExit',True),('tests',8),('suites',2),('targetSourceUnits',2),('physicalClasses',{}),('metadataClasses',[]),('cases',[]),('singleSession',False),('crcMismatch',1),('strictFour100GateExit',0),('targetUnitFour100',True),('manualCounterExclusions',['excluded']),('totals',{}),('forbiddenProductProbeHits',1),('actualJdbcBackendConnected',True),('actualBackendSqlOperations',1),('productTestsReexecutedByPost',1),('oldCoverageTransferred',True),('formalUpdated',True),('newAccepted',1),('effortPercent',100)]
    for key,value in vectors:
        v=copy.deepcopy(p);v[key]=value;require(v!=p,'nondegenerate '+key)
        try:contract(v)
        except ValueError:labels.append(key)
        else:raise ValueError('false semantic post '+key)
    test_path=next(path for path,n in original.TEST_PATHS.values());text=(data.ROOT/test_path).read_text()
    require(re.findall(r'@Test\s+void\s+(\w+)\(',text)==ORACLE_NAMES,'whole original seven source')
    require(data.sha(text.encode())==raw['begin']['sourceHashes'][test_path]=='fb1e63f70b6d8bdac737cd4423726c339e4bd41673a4ccda3324f92f9d3e5347','exact source oracle')
    tokens=['1737001L','1737002L','2026-09-28T02:00:00Z','2026-09-28T03:00:00.000001Z','2026-09-28T02:00:03.000000001Z','HISTORY.statement.executeQuery','HISTORY.row.close','assertSame(failure','assertNull(actual.getCause())','probe.released();']
    require(all(t in text for t in tokens),'independent literal pair/null/time/identity/resource oracle')
    life=p['originalUnusedHelperProbeAudit']['originalOuterTestLifecycle'];method_rows=life['methodRows']
    catalog=data.read_checked(data.BASE/'PG15950-g13-current-test-declaration-inventory-v1/manifest.json','0173083ac6c1ed92d23a3fad673afc7d545186d718353366398c1ecd28c6c139')
    bindings=data.read_checked(data.BASE/'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json',catalog['files']['exact-ordinary-bindings.json'])
    outer='dev.codex.schubert.nk.batch.repository.MorningDatabaseSessionTest'
    outer_methods={r['method'] for r in bindings if r['className']==outer}
    require(len(outer_methods)==65,'actual unselected whole65 declaration')
    for name in outer_methods|{'database','stop'}:
        rows=[r for r in method_rows if r[1]==name]
        require(len(rows)==1 and int(rows[0][2])==0,'every unselected method/lifecycle zero instructions')
    allowed={'<clinit>','credential','proxy'}
    require(all(int(r[2])==0 or r[1] in allowed or re.fullmatch(r'lambda\$proxy\$[0-9]+',r[1]) for r in method_rows),'no other outer helper executed')
    require(original.projection_guard(text) and set(re.findall(r'java\.sql\.\w+',text))=={'java.sql.SQLException'},'correct explicit JDBC exception-only metadata')
    forbidden=['DriverManager.getConnection(', 'Files.write(', 'System.getenv(', '@BeforeAll', 'java.net.Socket']
    require(all(not original.projection_guard(text+'\n'+s) for s in forbidden) and not original.projection_guard(''),'all six corrected safety boundaries')
    SLOT.mkdir();runner.SLOT=SLOT;component=SLOT/'original-test-component';component.mkdir()
    names=[TEST_NAME,ROOT_NAME+'MorningDatabaseSessionTest',ROOT_NAME+'MorningDatabaseSessionTest$Probe']
    metadata=ROOT_NAME+'MorningDatabaseSessionTest$Invocation'
    physical={}
    for name in [*names,metadata]:
        src=original.SLOT/'fresh-test-classes'/(name+'.class');dst=component/(name+'.class');dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst);physical[name]=data.sha(src.read_bytes())
    receipt=data.read_checked(data.ROOT.parent/'pgpt-runs/PG379/pg13376-db-duration-eight-post-v1/session-identity-exit.safe.json','2bbd55eefa4fc2b0532660748a0f35bfeca6cb69e45e732fc67759add964a84b')
    cp=receipt['command'][2];reader=data.ROOT.parent/'pgpt-runs/PG379/pg15713-caddy-public-value-nine-post-v2/diagnostic-classes'
    require(data.sha((reader/'WholeSourceCoverageMeasureV1.class').read_bytes())=='9977e1c733e40e4752261c38e6a679a91cf2d33b6d2be72180e1f67af01a94a3','qualified passive class')
    runtime=data.read_checked(data.BASE/'PG13378-db-duration-eight-post-recovery-v3/manifest.json','adcb55b80aa70a449e74280aa465f752308310c41c876cf83a5a78c3dda3c882')
    require(all(data.sha(Path(k).read_bytes())==v for k,v in runtime['toolAndDependencyHashes'].items()),'fixed reader SDK')
    stage=runner.step('passive-original-test-crc',[str(runner.TC/'jdk-25.0.4/bin/java'),'-cp',str(reader)+os.pathsep+cp,'WholeSourceCoverageMeasureV1',str(original.SLOT/'jacoco.exec'),str(component),*names,'--metadata='+metadata],SLOT,timeout=120)
    require(stage['actualExit']==0 and not stage['timedOut'],'original Test/Probe CRC identity')
    out=(SLOT/'passive-original-test-crc.stdout').read_text().splitlines()
    crc_rows=[line.split(chr(9)) for line in out if line.startswith('CLASS'+chr(9))]
    require(len(crc_rows)==3 and {r[1] for r in crc_rows}==set(names) and 'METADATA'+chr(9)+metadata in out,'exact three Code/one genuine NoCode')
    verify(p['invocation']);verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir()
    value=dict(actualExit=0,source=SOURCE,invocation=invocation,postSha256=POST[1],originalRawSha256=RAW,tests=7,suites=1,semanticNegativeVectors=len(labels),negativeLabels=labels,independentOracleVectors=7,originalTestSourceSha256=data.sha(text.encode()),independentOracleBasis='LITERAL_PAIR_IDS_DATES_TYPED_NULL_ROWS_BOUNDARIES_UNKNOWN_IDENTITY_AND_OWN_FAKE_COUNTERS',outerUnselectedTestMethods=65,outerLifecycleMethodsAbsent=2,originalTestPhysicalHashes=physical,testCrcIdentityClasses={r[1]:r[2] for r in crc_rows},passiveTestCrcStage=stage,helperSafetyGuardNegativeVectors=6,metadataNegativeVectorsNotProductTests=True,originalProductTestsReexecuted=0,oldSourceTransferred=False,coverageExecUnion=False,actualDatabaseActions=0,actualVmActions=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,effortPercent=None)
    data.write(OUT/'manifest.json',value);print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
