"""Independent existing ID/disposition/page bindings and full Source gaps; no product execution."""
import copy
import json
import re
import subprocess
import sys
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg15662_request_bindings_ten_pt as original
import pg15664_request_bindings_ten_post as post

PIN='6b5c22e929862e1fef12dca365d8f38015e988668439bea706bb9d53b7ba428a'
OUT=data.BASE/'PG15666-request-bindings-ten-independent-v1'
P=original.PREFIX
CLOSURES={P+n:sorted(P+v for v in values) for n,values in original.CLOSURES.items()}
NAMES=set().union(*[set(v) for v in CLOSURES.values()])
def require(ok,label):
    if not ok:raise ValueError(label)
def assess(p):
    require(p['actualExit']==0 and p['source']==original.SOURCE and p['originalManifestSha256']==post.RAW,'source/run')
    require((p['tests'],p['suites'],len(p['cases']),len(p['xmlHashes']))==(10,3,10,3) and all(p[k]==0 for k in ['failures','errors','skipped','reruns','newAccepted','newTestIds','crcMismatch']),'genuine nine')
    require(len({(c['classname'],c['name']) for c in p['cases']})==10 and all(c['result']=='PASS' for c in p['cases']),'unique/pass')
    require(p['singleSession'] is True and p['sessionIdentity']==original.SESSION and p['execSha256']==raw['execSha256'],'one exec')
    require(p['completeSourceUnitClosure']==CLOSURES and set(p['fullSourceUnits'])==set(CLOSURES) and set(p['physicalClasses'])==set(p['executable'])==set(p['sourcePhysicalInventory'])==NAMES,'whole four Source/seven Code')
    require(p['metadataClasses']==p['manualCounterExclusions']==[] and p['officialGeneratedFiltersUnchanged'] is True,'no exclusion')
    totals={k:{r:sum(p['executable'][n]['counters'][k][r] for n in NAMES) for r in ['missed','covered']} for k in ['LINE','METHOD','CLASS','BRANCH']}
    require(totals==p['totals']=={k:dict(missed=m,covered=c) for k,m,c in [('LINE',99,98),('METHOD',9,12),('CLASS',0,4),('BRANCH',31,34)]},'independent exact sums')
    for name,ns in CLOSURES.items():
        u=p['fullSourceUnits'][name];values={k:{r:sum(p['executable'][n]['counters'][k][r] for n in ns) for r in ['missed','covered']} for k in ['LINE','METHOD','CLASS','BRANCH']}
        require(u['physical']==ns and u['totals']==values and u['four100'] is all(v['missed']==0 and v['covered']>0 for v in values.values()) and u['branchNaturallyZero'] is (values['BRANCH']==dict(missed=0,covered=0)) and u['threeCounter100'] is all(values[k]['missed']==0 and values[k]['covered']>0 for k in ['LINE','METHOD','CLASS']),'actual per Source categories')
    require(p['targetUnitFour100'] is False and p['strictFour100GateExit']==1 and p['allMeasuredApplicableCountersCovered'] is False and sum(u['four100'] for u in p['fullSourceUnits'].values())==0,'two branchless not fake four100')
    require(p['cryptoOrKeyOperationsInvoked'] is True and p['cryptoOperationKind']=='UUID_V4_PUBLIC_REQUEST_IDENTIFIERS_ONLY' and p['publicSyntheticTestKeysUsed'] is p['childLocalJcaRegistryRestorationTested'] is p['ownFreshJvmProviderStateOnly'] is False and p['ownedJcaProviderOrderRestored'] is None and p['publicRequestIdentifiersGenerated'] is True and p['generatedPublicIdentifiersPersisted'] is False,'truthful SHA comparison only')
    require(p['actualSecretKeysLoaded'] is p['actualCredentialValuesUsed'] is p['actualAuthenticationOrSessionIssued'] is p['actualFilesOpenedByProduct'] is p['actualPrivateFilesOpened'] is p['jmsFactoryObjectsConstructed'] is p['onlySyntheticJmsProxyMessages'] is False,'no live/private IO')
    require(p['actualJmsConnectionsCreated']==p['actualJmsContextsCreated']==0 and p['actualBrokerOrListenerStarted'] is False,'no broker')
    require(p['forbiddenProductProbeHits']==0 and len(p['passiveNativeBoundaryAbsence']['rows'])==6 and all(r[3]=='0' for r in p['passiveNativeBoundaryAbsence']['rows']),'held/native absence')
    require(p['rootMainInvoked'] is p['formalUpdated'] is p['whole451Accepted'] is p['wholeF03Accepted'] is p['oldCoverageTransferred'] is p['priorProductResultsReused'] is False and p['effortPercent'] is None and p['productTestsReexecutedByPost']==0,'no transfer/acceptance')
    require(all(p[k]==0 for k in ['actualVmActions','actualDatabaseActions','actualNetworkActions','actualServiceActions','actualBrowserActions','actualBoundSockets']),'no external effects')
    require(len(p['owners'])==5 and sum(r['ownershipStatus']=='BASELINE_LOGICAL_REFERENCE' and r['canonicalOwner']==r['canonicalCostOwner'] for r in p['owners'].values())==2 and sum(r['ownershipStatus']=='UNKNOWN' and r['canonicalOwner'] is r['canonicalCostOwner'] is None for r in p['owners'].values())==3,'actual owners')
    require(all(v['actualExit']==0 and not v['timedOut'] for v in p['stages']),'actual stage terminal')
def main():
    global raw
    invocation=capture(__file__);require(not OUT.exists(),'new only')
    raw=data.read_checked(data.BASE/'PG15662-request-bindings-ten-pt-v1/manifest.json',post.RAW)
    p=data.read_checked(post.OUT/'manifest.json',PIN);post.assess(raw);assess(p)
    old=data.read_checked(data.BASE/'PG15652-current1950-lgs-reply-registry-v1/manifest.json','a7f69e546495618e04fb9df177da6fd70e6571262d3920f4b93186c47373dd2c')
    require(not set(CLOSURES)&set(old['fullSourceUnits']),'new four Source, no old helper reacceptance')
    texts={k:path.read_text() for k,path in original.TESTS.items()};expected=set()
    for key,text in texts.items():
        names=re.findall(r'(?m)^  void ([A-Za-z0-9_]+)\(',text);require(len(names)==original.COUNTS[key],'whole original counts')
        package=re.search(r'package ([A-Za-z0-9_.]+);',text).group(1);expected.update((package+'.'+key,n) for n in names)
    require(expected=={(c['classname'],c['name']) for c in p['cases']},'every whole original once')
    media=texts['MediaRequestDescriptorBindingTest'];scenario=texts['ScenarioScriptFileBindingTest'];question=texts['QuestionQueryResponseBindingTest']
    require(all(v in media for v in ['"700"','"music-0"','"opening"','999_999_999_999L','MUSIC_DISPOSITION_OFFSET = 64','ContentDisposition.values()','request.descriptor(null)','audio("701", disposition)','music("other", disposition)','video("other", ContentDisposition.INLINE)','ContentDisposition.ATTACHMENT','request.descriptor(sameLayout).isEmpty()']),'independent media identity/disposition/null')
    ids=['000000000001','000000000030','999999999999']
    require([int(v) for v in ids]==[1,30,10**12-1] and all(v in scenario for v in ids) and all(v in scenario for v in ['Arrays.fill(input, (byte) 0)','assertEquals(2, other.scriptFileId().orElseThrow())','request.scriptFileId().isEmpty()']),'independent N12/ownership')
    require(all(v in question for v in ['999_999_999_999L','999_999_999_998L','QUESTION_PAGE_OFFSET = 366','NOTIFICATION_PAGE_OFFSET = 46','"000001", "000002", "999999"','new PagedResponseData(1, 50, 0, 1, 0, 0)','new PagedResponseData(2, 50, 0, 1, 0, 0)','question(OTHER_ID)','notification(OTHER_ID)']),'independent question/notification identity/family/page')
    pages=[1,2,999999];require([min(v,1) for v in pages]==[1,1,1],'empty page independently clamps to one')
    helpers={str((original.ROOT/(name+'.java')).relative_to(data.ROOT)):pin for name,pin in original.HELPER_PINS.items()}
    require(all(data.sha((data.ROOT/path).read_bytes())==pin and raw['begin']['testSourceHashes'][str(data.ROOT/path)]==pin for path,pin in helpers.items()),'whole unchanged compiled helpers')
    helper=(original.ROOT/'application/question/QuestionQueryRequestTest.java').read_text()
    helper_body=helper.split('  static WireMessage<FixedPayload> message(',1)[1].split('  static void lp(',1)[0]
    require('new FingerprintKeyRing' not in helper_body and 'Mac.getInstance' not in helper_body and 'getConnection(' not in helper_body and 'new CommonHeader(' in helper_body,'only existing static data/message/put helper')
    require(all(c['classname']!='dev.codex.schubert.nk.api.application.question.QuestionQueryRequestTest' for c in p['cases']) and 'QuestionQueryRequestTest' not in raw['begin']['selectedSuites'],'held helper2 JUnit not selected/executed')
    fixture_texts=[(original.ROOT/(name+'.java')).read_text() for name in original.HELPER_PINS if name.endswith('RequestFixture')]
    require(len(fixture_texts)==2 and all('UUID.randomUUID()' in text and 'System.out' not in text and 'System.err' not in text for text in fixture_texts),'public request UUID randomness/no printing')
    qname=P+'application/question/QuestionQueryRequest';previous=old['fullSourceUnits'][qname]
    require(previous['post']=='PG14762-question-sql-joint-eighteen-post-v1' and previous['four100'] is True and previous['counters']=={k:dict(missed=0,covered=v) for k,v in [('LINE',102),('METHOD',16),('CLASS',1),('BRANCH',32)]} and qname not in CLOSURES,'old helper full qualification kept')
    docs=['documents/200_UI/230_インターフェース/234_認証・検索・シナリオ電文仕様.md','documents/200_UI/230_インターフェース/235_メディア・ログ電文仕様.md','documents/200_UI/230_インターフェース/236_管理・質問・通知電文仕様.md']
    documents={v:(data.ROOT/v).read_bytes() for v in docs}
    require(all(value==subprocess.check_output(['git','show','origin/main:'+v],cwd=data.ROOT) for v,value in documents.items()),'approved main UI bytes')
    require('0件でも1' in documents[docs[0]].decode() and '要求IDのcanonical値' in documents[docs[1]].decode() and (chr(96)+'I'+chr(96)+' inline、'+chr(96)+'A'+chr(96)+' attachment') in documents[docs[1]].decode(),'approved empty page/media identity/disposition')
    design=documents[docs[2]].decode()
    require('| Page | 367 | 6 |' in design and '| Page | 47 | 6 |' in design and 'QSDREQ01' in design and 'NTDREQ01' in design,'independent page offsets/detail layouts')
    vectors=[('source','source','OLD'),('raw','originalManifestSha256','0'*64),('cases','cases',[]),('totals','totals',{}),('physical','physicalClasses',{}),('sources','fullSourceUnits',{}),('tests','tests',11),('suites','suites',4),('four','targetUnitFour100',True),('strict','strictFour100GateExit',0),('session','singleSession',False),('crc','crcMismatch',1),('metadata','metadataClasses',['unknown']),('excluded','manualCounterExclusions',['unknown']),('crypto','cryptoOrKeyOperationsInvoked',False),('public-random','publicRequestIdentifiersGenerated',False),('random-persist','generatedPublicIdentifiersPersisted',True),('synthetic-key','publicSyntheticTestKeysUsed',True),('jca','childLocalJcaRegistryRestorationTested',True),('secret','actualSecretKeysLoaded',True),('credentials','actualCredentialValuesUsed',True),('auth','actualAuthenticationOrSessionIssued',True),('formal','formalUpdated',True),('whole','whole451Accepted',True),('old','oldCoverageTransferred',True),('file','actualFilesOpenedByProduct',True),('root','rootMainInvoked',True),('accepted','newAccepted',1),('post-replay','productTestsReexecutedByPost',1),('effort','effortPercent',100)]
    require(all(json.dumps(p[key],sort_keys=True)!=json.dumps(value,sort_keys=True) for _,key,value in vectors),'every negative differs from genuine metadata')
    labels=[]
    for label,key,value in vectors:
        bad=copy.deepcopy(p);bad[key]=value
        try:assess(bad)
        except ValueError:labels.append(label)
        else:raise AssertionError('false qualification '+label)
    verify(raw['begin']['invocation']);verify(p['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,postSha256=PIN,originalManifestSha256=post.RAW,tests=10,suites=3,sourcePrograms=2,physicalClasses=4,four100SourcePrograms=0,naturallyBranchZeroSourcePrograms=0,incompleteSourcePrograms=2,baselineMainOwnerRows=2,unknownTestOwnerRows=3,semanticNegativeVectors=len(labels),negativeLabels=labels,independentDetailIds=ids,independentEmptyPageValues=[min(v,1) for v in pages],wholeCompiledHelperSourceHashes=helpers,helperStaticBodySha256=data.sha(helper_body.encode()),helperJUnitMethodsSelected=0,previousQuestionMainProof=previous,nondegenerateNegativeVectors=len(vectors),publicRequestIdentifiersGenerated=True,generatedPublicIdentifiersPersisted=False,pythonVersion=sys.version,approvedDesignHashes={v:data.sha(b) for v,b in documents.items()},cryptoOrKeyOperationsInvoked=True,cryptoOperationKind=p['cryptoOperationKind'],publicSyntheticTestKeysUsed=False,childLocalJcaRegistryRestorationTested=False,ownFreshJvmProviderStateOnly=False,actualSecretKeysLoaded=False,actualCredentialValuesUsed=False,actualAuthenticationOrSessionIssued=False,actualFilesOpenedByProduct=False,actualPrivateFilesOpened=False,actualJmsConnectionsCreated=0,actualJmsContextsCreated=0,actualBrokerOrListenerStarted=False,previousHelpersNotReaccepted=True,productTestsExecutedByIndependent=0,productTestsReexecuted=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(dict(actualExit=0,tests=10,semanticNegativeVectors=len(labels))))
if __name__=='__main__':main()
