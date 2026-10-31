"""Independent pre-SQL contract matrix and supplemental full-source measurement; no product invocation."""
import copy
import json
import re
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg15694_media_scenario_pre_sql_twenty_two_pt as original
import pg15697_media_scenario_pre_sql_twenty_two_post as post

PIN='6e5e2307e9d90758fddaf218393b09d69ad4e6480e4f3cf341f303fb9295a73d'
OUT=data.BASE/'PG15698-media-scenario-pre-sql-twenty-two-independent-v1'
P=original.PREFIX
CLOSURES={P+n:sorted(P+v for v in group) for n,group in original.CLOSURES.items()}
META={P+n+'$RowMapper' for n in original.MAIN_PINS}
PHYSICAL=set().union(*map(set,CLOSURES.values()))
EXECUTABLE=PHYSICAL-META
def require(ok,label):
    if not ok:raise ValueError(label)
def assess(p):
    require(p['actualExit']==0 and p['source']==original.SOURCE and p['originalManifestSha256']==post.RAW,'source/raw')
    require((p['tests'],p['suites'],len(p['cases']),len(p['xmlHashes']))==(22,2,22,2),'exact original whole13')
    require(all(type(p[k]) is int and p[k]==0 for k in ['actualExit','failures','errors','skipped','reruns','newAccepted','newTestIds','crcMismatch','actualJdbcMethodsInvoked','actualSqlStatementsPreparedOrExecuted']),'true zero roles')
    require(len({(c['classname'],c['name']) for c in p['cases']})==22 and all(c['result']=='PASS' for c in p['cases']),'all unique passes')
    require(p['singleSession'] is True and p['sessionIdentity']==original.SESSION and p['execSha256']==raw['execSha256'],'one current exec')
    require(p['completeSourceUnitClosure']==CLOSURES and set(p['fullSourceUnits'])==set(CLOSURES) and set(p['physicalClasses'])==set(p['sourcePhysicalInventory'])==PHYSICAL and set(p['executable'])==EXECUTABLE,'complete physical, not partial exclusion')
    require(set(p['metadataClasses'])==META and p['manualCounterExclusions']==[] and p['officialGeneratedFiltersUnchanged'] is True,'trueNoCode not manual exclusion')
    for name in META:
        m=p['sourcePhysicalInventory'][name]
        expected={
          P+'persistence/MediaRepository$RowMapper':('809a1c44426ed71586fbde519b2a70a1cb10f9829ae5e17b45c7e7b3cefef18a','(Ljava/sql/ResultSet;)Ljava/lang/Object;'),
          P+'persistence/ScenarioRepository$RowMapper':('2a4895659e442d7371d798633cd2de0c5be3a1dd804ea3051cc07e408c19fc2c','(Ljava/sql/ResultSet;)Ldev/codex/schubert/nk/protocol/layout/PayloadRecord;')}
        require(m['sha256']==expected[name][0] and m['flags']==1536 and m['methods']==[dict(name='read',descriptor=expected[name][1],flags=1025,hasCode=False,codeLength=0)],'both exact NoCode mapper roles')
    totals={k:{r:sum(v['counters'][k][r] for v in p['executable'].values()) for r in ['covered','missed']} for k in ['LINE','METHOD','CLASS','BRANCH']}
    require(totals==p['totals']=={k:dict(covered=c,missed=m) for k,c,m in [('LINE',78,271),('METHOD',25,40),('CLASS',2,0),('BRANCH',2,108)]},'independent fresh supplemental sums')
    for name,group in CLOSURES.items():
        counters={k:{r:sum(p['executable'][n]['counters'][k][r] for n in group if n in EXECUTABLE) for r in ['covered','missed']} for k in totals}
        u=p['fullSourceUnits'][name]
        require(u['physical']==group and u['totals']==counters and u['four100'] is False and u['threeCounter100'] is False and u['branchNaturallyZero'] is False,'each whole Source remains incomplete')
    require(p['targetUnitFour100'] is p['allMeasuredApplicableCountersCovered'] is False and p['strictFour100GateExit']==1,'never misreport all-source pass')
    require(p['onlyPreSqlZeroJdbcCallContracts'] is p['actualJdbcProxyObjectsConstructed'] is True and p['sameExecMeasurementSupplementalOnly'] is False and p['currentSourceQualificationProofsReplaced'] is p['actualJdbcBackendConnected'] is False,'supplement only/Proxy not backend')
    require(p['cryptoOrKeyOperationsInvoked'] is p['publicSyntheticTestKeysUsed'] is p['childLocalJcaRegistryRestorationTested'] is p['actualSecretKeysLoaded'] is p['actualCredentialValuesUsed'] is p['actualAuthenticationOrSessionIssued'] is p['actualFilesOpenedByProduct'] is p['actualPrivateFilesOpened'] is False,'no actual secrets/crypto/files')
    require(p['cryptoOperationKind']=='NONE_IN_REVIEWED_DOMAIN_BODY' and p['forbiddenProductProbeHits']==0 and len(p['passiveNativeBoundaryAbsence']['rows'])==6 and all(r[3]=='0' for r in p['passiveNativeBoundaryAbsence']['rows']),'truthful domain and held/native absences')
    require(all(p[k]==0 for k in ['actualVmActions','actualDatabaseActions','actualServiceActions','actualNetworkActions','actualBrowserActions','actualBoundSockets','actualJmsConnectionsCreated','actualJmsContextsCreated']) and p['actualBrokerOrListenerStarted'] is False,'no real IO')
    require(p['rootMainInvoked'] is p['formalUpdated'] is p['whole451Accepted'] is p['wholeF03Accepted'] is p['oldCoverageTransferred'] is p['priorProductResultsReused'] is False and p['effortPercent'] is None and p['productTestsReexecutedByPost']==0,'no old/formal transfer')
    require(len(p['owners'])==4 and sum(v['ownershipStatus']=='BASELINE_LOGICAL_REFERENCE' for v in p['owners'].values())==2 and sum(v['ownershipStatus']=='UNKNOWN' for v in p['owners'].values())==3,'actual three existing Main owners and three UNKNOWN tests')
    require(all(s['actualExit']==0 and not s['timedOut'] for s in p['stages']),'actual passive terminal')
def main():
    global raw
    invocation=capture(__file__);require(not OUT.exists(),'new only')
    raw=data.read_checked(data.BASE/'PG15694-media-scenario-pre-sql-twenty-two-pt-v1/manifest.json',post.RAW)
    p=data.read_checked(post.OUT/'manifest.json',PIN);post.assess(raw);assess(p)
    old=data.read_checked(data.BASE/'PG15684-current1973-pre-sql-registry-v1/manifest.json','34ab91df2ee7ec004ae0bf4dc0d7cc4319f5ec859180fa6f7151f2f81312be62')
    require(not set(CLOSURES)&set(old['fullSourceUnits']),'both new whole Source measurements, no requalification')
    expected=set();npe={};zero={}
    for name,path in original.TESTS.items():
        text=path.read_text();methods=re.findall(r'(?m)^  void ([A-Za-z0-9_]+)\(',text)
        require(len(methods)==original.COUNTS[name],'whole original method matrix')
        package=re.search(r'package ([A-Za-z0-9_.]+);',text).group(1);expected.update((package+'.'+name,n) for n in methods)
        calls={helper:len(re.findall(r'(?m)^\s+'+helper+r'\(',text)) for helper in ['boundary','missingRequest','oversize']}
        npe[name]=2*calls['boundary']+calls['missingRequest'];zero[name]=sum(calls.values())
        require(all(v in text for v in ['Proxy.newProxyInstance(','Connection.class','calls.incrementAndGet();','throw new AssertionError("unexpected JDBC access")','assertEquals(0, calls.get())','assertThrows(NullPointerException.class','fixture.untouched();']),'zero-call oracle')
        require(not any(v in text for v in ['DriverManager','getConnection(','DataSource','ProcessBuilder','FingerprintKeyRing','TemporaryInfrastructureException','WebStartupException']),'whole new scope free of held or backend setup')
    require(expected=={(c['classname'],c['name']) for c in p['cases']} and not expected&{(c['classname'],c['name']) for c in old['cases']},'all13 new unique, no old success replay')
    require(npe==dict(MediaPreSqlBoundaryTest=22,ScenarioPreSqlBoundaryTest=17) and zero==dict(MediaPreSqlBoundaryTest=19,ScenarioPreSqlBoundaryTest=14),'39 null and33 zero-call assertions')
    texts={name:path.read_text() for name,path in original.TESTS.items()}
    require(texts['MediaPreSqlBoundaryTest'].count('"x".repeat(65)')==4 and texts['MediaPreSqlBoundaryTest'].count('"x".repeat(129)')==1 and texts['ScenarioPreSqlBoundaryTest'].count('"x".repeat(257)')==2 and texts['ScenarioPreSqlBoundaryTest'].count('"x".repeat(129)')==1,'independent eight byte boundaries')
    docs=['documents/200_UI/230_インターフェース/234_認証・検索・シナリオ電文仕様.md','documents/200_UI/230_インターフェース/235_メディア・ログ電文仕様.md']
    documents={name:(data.ROOT/name).read_bytes() for name in docs}
    require(all(v==subprocess.check_output(['git','show','origin/main:'+name],cwd=data.ROOT) for name,v in documents.items()),'approved exact UI')
    require(all(v in documents[docs[0]].decode() for v in ['| 本文keyword | 1 | 256 |','| Speaker名 | 269 | 128 |','| 章title | 397 | 256 |']) and all(v in documents[docs[1]].decode() for v in ['| Video ID | 1 | 64 |','| Track ID | 1 | 64 |','| Category | 1 | 64 |','| Section | 65 | 128 |']),'approved independent byte limits')
    require(p['suiteMetadataCorrection']['oldPostSha256']=='54747a8f073ae1a8136286374179519548753201ee1084f3e7a0c15c7726aa87' and p['suiteMetadataCorrection']['oldSuites']==3 and p['suiteMetadataCorrection']['effectiveSuites']==2 and len(p['suiteMetadataCorrection']['negativeValuesRejected'])==5,'old incorrect metadata preserved, correction not Product replay')
    vectors=[('source','source','OLD'),('raw','originalManifestSha256','0'*64),('cases','cases',[]),('tests','tests',14),('suites','suites',4),('physical','physicalClasses',{}),('source-units','fullSourceUnits',{}),('totals','totals',{}),('metadata','metadataClasses',[]),('exclude','manualCounterExclusions',['unknown']),('filter','officialGeneratedFiltersUnchanged',False),('crc','crcMismatch',1),('session','singleSession',False),('four','targetUnitFour100',True),('strict','strictFour100GateExit',0),('replace','currentSourceQualificationProofsReplaced',True),('supplement','sameExecMeasurementSupplementalOnly',True),('jdbc','actualJdbcMethodsInvoked',1),('sql','actualSqlStatementsPreparedOrExecuted',1),('backend','actualJdbcBackendConnected',True),('crypto','cryptoOrKeyOperationsInvoked',True),('keys','actualSecretKeysLoaded',True),('credentials','actualCredentialValuesUsed',True),('auth','actualAuthenticationOrSessionIssued',True),('files','actualFilesOpenedByProduct',True),('root','rootMainInvoked',True),('formal','formalUpdated',True),('whole','whole451Accepted',True),('union','oldCoverageTransferred',True),('accepted','newAccepted',1),('bool-zero','newAccepted',False),('effort','effortPercent',100)]
    require(all(json.dumps(p[k],sort_keys=True)!=json.dumps(v,sort_keys=True) for _,k,v in vectors),'nondegenerate negatives')
    labels=[]
    for label,key,value in vectors:
        bad=copy.deepcopy(p);bad[key]=value
        try:assess(bad)
        except ValueError:labels.append(label)
        else:raise AssertionError('false supplemental qualification '+label)
    verify(raw['begin']['invocation']);verify(p['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,postSha256=PIN,originalManifestSha256=post.RAW,tests=22,suites=2,sourcePrograms=2,newSourcePrograms=2,physicalClasses=4,executablePhysicalClasses=2,metadataPhysicalClasses=2,four100SourcePrograms=0,naturallyBranchZeroSourcePrograms=0,incompleteSourcePrograms=2,baselineMainOwnerRows=2,unknownTestOwnerRows=2,semanticNegativeVectors=len(labels),negativeLabels=labels,independentNpeAssertionCounts=npe,zeroJdbcAssertionCounts=zero,oversizeInputs=[65,65,65,65,129,257,129,257],previousProofsNotReplaced=True,approvedDesignHashes={name:data.sha(v) for name,v in documents.items()},sameExecMeasurementSupplementalOnly=False,currentSourceQualificationProofsReplaced=False,onlyPreSqlZeroJdbcCallContracts=True,actualJdbcBackendConnected=False,actualJdbcMethodsInvoked=0,actualSqlStatementsPreparedOrExecuted=0,cryptoOrKeyOperationsInvoked=False,actualSecretKeysLoaded=False,actualCredentialValuesUsed=False,actualAuthenticationOrSessionIssued=False,actualFilesOpenedByProduct=False,productTestsExecutedByIndependent=0,productTestsReexecuted=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(dict(actualExit=0,tests=22,semanticNegativeVectors=len(labels),npeAssertions=39,zeroJdbcAssertions=33)))
if __name__=='__main__':main()
