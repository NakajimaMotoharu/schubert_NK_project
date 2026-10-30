"""Independent pre-SQL contract matrix and supplemental full-source measurement; no product invocation."""
import copy
import json
import re
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg15678_pre_sql_thirteen_pt as original
import pg15680_pre_sql_thirteen_post as post

PIN='cc5c271d935d29da7f4bf59fc2d9d65e68cb4321b962ca9fe3a2889781655b1b'
OUT=data.BASE/'PG15682-pre-sql-thirteen-independent-v1'
P=original.PREFIX
CLOSURES={P+n:sorted(P+v for v in group) for n,group in original.CLOSURES.items()}
META={P+'persistence/QuestionQueryRepository$RowMapper'}
PHYSICAL=set().union(*map(set,CLOSURES.values()))
EXECUTABLE=PHYSICAL-META
def require(ok,label):
    if not ok:raise ValueError(label)
def assess(p):
    require(p['actualExit']==0 and p['source']==original.SOURCE and p['originalManifestSha256']==post.RAW,'source/raw')
    require((p['tests'],p['suites'],len(p['cases']),len(p['xmlHashes']))==(13,3,13,3),'exact original whole13')
    require(all(type(p[k]) is int and p[k]==0 for k in ['actualExit','failures','errors','skipped','reruns','newAccepted','newTestIds','crcMismatch','actualJdbcMethodsInvoked','actualSqlStatementsPreparedOrExecuted']),'true zero roles')
    require(len({(c['classname'],c['name']) for c in p['cases']})==13 and all(c['result']=='PASS' for c in p['cases']),'all unique passes')
    require(p['singleSession'] is True and p['sessionIdentity']==original.SESSION and p['execSha256']==raw['execSha256'],'one current exec')
    require(p['completeSourceUnitClosure']==CLOSURES and set(p['fullSourceUnits'])==set(CLOSURES) and set(p['physicalClasses'])==set(p['sourcePhysicalInventory'])==PHYSICAL and set(p['executable'])==EXECUTABLE,'complete physical, not partial exclusion')
    require(set(p['metadataClasses'])==META and p['manualCounterExclusions']==[] and p['officialGeneratedFiltersUnchanged'] is True,'trueNoCode not manual exclusion')
    m=p['sourcePhysicalInventory'][next(iter(META))]
    require(m['sha256']=='64041f2bfa092b6440952bd1bfcbc9794ecceca64017d3288df8f04264ae63b9' and m['flags']==1536 and not any(v['hasCode'] for v in m['methods']),'exact abstract RowMapper')
    totals={k:{r:sum(v['counters'][k][r] for v in p['executable'].values()) for r in ['covered','missed']} for k in ['LINE','METHOD','CLASS','BRANCH']}
    require(totals==p['totals']=={k:dict(covered=c,missed=m) for k,c,m in [('LINE',36,381),('METHOD',12,54),('CLASS',3,0),('BRANCH',3,151)]},'independent fresh supplemental sums')
    for name,group in CLOSURES.items():
        counters={k:{r:sum(p['executable'][n]['counters'][k][r] for n in group if n in EXECUTABLE) for r in ['covered','missed']} for k in totals}
        u=p['fullSourceUnits'][name]
        require(u['physical']==group and u['totals']==counters and u['four100'] is False and u['threeCounter100'] is False and u['branchNaturallyZero'] is False,'each whole Source remains incomplete')
    require(p['targetUnitFour100'] is p['allMeasuredApplicableCountersCovered'] is False and p['strictFour100GateExit']==1,'never misreport all-source pass')
    require(p['onlyPreSqlZeroJdbcCallContracts'] is p['sameExecMeasurementSupplementalOnly'] is p['actualJdbcProxyObjectsConstructed'] is True and p['currentSourceQualificationProofsReplaced'] is p['actualJdbcBackendConnected'] is False,'supplement only/Proxy not backend')
    require(p['cryptoOrKeyOperationsInvoked'] is p['publicSyntheticTestKeysUsed'] is p['childLocalJcaRegistryRestorationTested'] is p['actualSecretKeysLoaded'] is p['actualCredentialValuesUsed'] is p['actualAuthenticationOrSessionIssued'] is p['actualFilesOpenedByProduct'] is p['actualPrivateFilesOpened'] is False,'no actual secrets/crypto/files')
    require(p['cryptoOperationKind']=='NONE_IN_REVIEWED_DOMAIN_BODY' and p['forbiddenProductProbeHits']==0 and len(p['passiveNativeBoundaryAbsence']['rows'])==6 and all(r[3]=='0' for r in p['passiveNativeBoundaryAbsence']['rows']),'truthful domain and held/native absences')
    require(all(p[k]==0 for k in ['actualVmActions','actualDatabaseActions','actualServiceActions','actualNetworkActions','actualBrowserActions','actualBoundSockets','actualJmsConnectionsCreated','actualJmsContextsCreated']) and p['actualBrokerOrListenerStarted'] is False,'no real IO')
    require(p['rootMainInvoked'] is p['formalUpdated'] is p['whole451Accepted'] is p['wholeF03Accepted'] is p['oldCoverageTransferred'] is p['priorProductResultsReused'] is False and p['effortPercent'] is None and p['productTestsReexecutedByPost']==0,'no old/formal transfer')
    require(len(p['owners'])==6 and sum(v['ownershipStatus']=='BASELINE_LOGICAL_REFERENCE' for v in p['owners'].values())==3 and sum(v['ownershipStatus']=='UNKNOWN' for v in p['owners'].values())==3,'actual three existing Main owners and three UNKNOWN tests')
    require(all(s['actualExit']==0 and not s['timedOut'] for s in p['stages']),'actual passive terminal')
def main():
    global raw
    invocation=capture(__file__);require(not OUT.exists(),'new only')
    raw=data.read_checked(data.BASE/'PG15678-pre-sql-thirteen-pt-v1/manifest.json',post.RAW)
    p=data.read_checked(post.OUT/'manifest.json',PIN);post.assess(raw);assess(p)
    old=data.read_checked(data.BASE/'PG15668-current1960-request-bindings-registry-v1/manifest.json','90e8c1a53aba7c30f4ff0fded8bbfb2b8f2ba45056cedc42380b8903eea9aeb7')
    require(set(CLOSURES)<=set(old['fullSourceUnits']),'all targets already represented; no new Source')
    previous={n:old['fullSourceUnits'][n] for n in CLOSURES}
    require(all(u['physical']==CLOSURES[n] and u['four100'] is False for n,u in previous.items()),'old incomplete proofs kept separate')
    expected=set();npe={};zero={}
    for name,path in original.TESTS.items():
        text=path.read_text();methods=re.findall(r'(?m)^  void ([A-Za-z0-9_]+)\(',text)
        require(len(methods)==original.COUNTS[name],'whole original method matrix')
        package=re.search(r'package ([A-Za-z0-9_.]+);',text).group(1);expected.update((package+'.'+name,n) for n in methods)
        npe[name]=len(re.findall(r'(?m)^\s+missing\(',text));zero[name]=text.count('port.untouched();')
        require(all(v in text for v in ['Proxy.newProxyInstance(','Connection.class','calls.incrementAndGet();','throw new AssertionError("unexpected JDBC access")','assertEquals(0, calls.get())','assertThrows(NullPointerException.class, operation)']),'zero-JDBC oracle rejects accidental access')
        require(not any(v in text for v in ['DriverManager','getConnection(','DataSource','ProcessBuilder','FingerprintKeyRing','TemporaryInfrastructureException','WebStartupException']),'whole new scope free of held or backend setup')
    require(expected=={(c['classname'],c['name']) for c in p['cases']} and not expected&{(c['classname'],c['name']) for c in old['cases']},'all13 new unique, no old success replay')
    require(npe==dict(LogQueryPreSqlBoundaryTest=3,QuestionQueryPreSqlBoundaryTest=12,UserQueryPreSqlBoundaryTest=8) and sum(npe.values())==23,'literal independent null call matrix')
    require(zero==original.COUNTS and sum(zero.values())==13,'every original has zero-JDBC assertion')
    texts={name:path.read_text() for name,path in original.TESTS.items()}
    require('"x".repeat(257)' in texts['LogQueryPreSqlBoundaryTest'] and all('"x".repeat(65)' in texts[n] for n in ['QuestionQueryPreSqlBoundaryTest','UserQueryPreSqlBoundaryTest']),'independent X256+1 and X64+1 bounds')
    require('ResultCode.FORBIDDEN' in texts['LogQueryPreSqlBoundaryTest'] and 'ResultCode.FORBIDDEN' in texts['UserQueryPreSqlBoundaryTest'] and 'ResultCode.VALIDATION_ERROR' in texts['QuestionQueryPreSqlBoundaryTest'],'closed role/filter error values')
    docs=['documents/200_UI/230_インターフェース/235_メディア・ログ電文仕様.md','documents/200_UI/230_インターフェース/236_管理・質問・通知電文仕様.md']
    documents={name:(data.ROOT/name).read_bytes() for name in docs}
    require(all(v==subprocess.check_output(['git','show','origin/main:'+name],cwd=data.ROOT) for name,v in documents.items()),'approved UI exact main bytes')
    require('| Keyword | 1 | 256 |' in documents[docs[0]].decode() and 'ADMIN以外は共通header認証後に' in documents[docs[0]].decode(),'approved X256 and ADMIN boundary')
    vectors=[('source','source','OLD'),('raw','originalManifestSha256','0'*64),('cases','cases',[]),('tests','tests',14),('suites','suites',4),('physical','physicalClasses',{}),('source-units','fullSourceUnits',{}),('totals','totals',{}),('metadata','metadataClasses',[]),('exclude','manualCounterExclusions',['unknown']),('filter','officialGeneratedFiltersUnchanged',False),('crc','crcMismatch',1),('session','singleSession',False),('four','targetUnitFour100',True),('strict','strictFour100GateExit',0),('replace','currentSourceQualificationProofsReplaced',True),('supplement','sameExecMeasurementSupplementalOnly',False),('jdbc','actualJdbcMethodsInvoked',1),('sql','actualSqlStatementsPreparedOrExecuted',1),('backend','actualJdbcBackendConnected',True),('crypto','cryptoOrKeyOperationsInvoked',True),('keys','actualSecretKeysLoaded',True),('credentials','actualCredentialValuesUsed',True),('auth','actualAuthenticationOrSessionIssued',True),('files','actualFilesOpenedByProduct',True),('root','rootMainInvoked',True),('formal','formalUpdated',True),('whole','whole451Accepted',True),('union','oldCoverageTransferred',True),('accepted','newAccepted',1),('bool-zero','newAccepted',False),('effort','effortPercent',100)]
    require(all(json.dumps(p[k],sort_keys=True)!=json.dumps(v,sort_keys=True) for _,k,v in vectors),'nondegenerate negatives')
    labels=[]
    for label,key,value in vectors:
        bad=copy.deepcopy(p);bad[key]=value
        try:assess(bad)
        except ValueError:labels.append(label)
        else:raise AssertionError('false supplemental qualification '+label)
    verify(raw['begin']['invocation']);verify(p['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,postSha256=PIN,originalManifestSha256=post.RAW,tests=13,suites=3,sourcePrograms=3,newSourcePrograms=0,physicalClasses=4,executablePhysicalClasses=3,metadataPhysicalClasses=1,four100SourcePrograms=0,naturallyBranchZeroSourcePrograms=0,incompleteSourcePrograms=3,baselineMainOwnerRows=3,unknownTestOwnerRows=3,semanticNegativeVectors=len(labels),negativeLabels=labels,independentNpeAssertionCounts=npe,zeroJdbcAssertionCounts=zero,oversizeInputs=[257,65,65],previousSourceProofs=previous,previousProofsNotReplaced=True,approvedDesignHashes={name:data.sha(v) for name,v in documents.items()},sameExecMeasurementSupplementalOnly=True,currentSourceQualificationProofsReplaced=False,onlyPreSqlZeroJdbcCallContracts=True,actualJdbcBackendConnected=False,actualJdbcMethodsInvoked=0,actualSqlStatementsPreparedOrExecuted=0,cryptoOrKeyOperationsInvoked=False,actualSecretKeysLoaded=False,actualCredentialValuesUsed=False,actualAuthenticationOrSessionIssued=False,actualFilesOpenedByProduct=False,productTestsExecutedByIndependent=0,productTestsReexecuted=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(dict(actualExit=0,tests=13,semanticNegativeVectors=len(labels),npeAssertions=23,zeroJdbcAssertions=13)))
if __name__=='__main__':main()
