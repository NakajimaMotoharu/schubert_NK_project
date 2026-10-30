"""Independent DLQ property/health truth table/HTTP lease value oracles; no product invocation."""
import copy
import json
import re
import subprocess
import sys
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg15614_dlq_web_health_nine_pt as original
import pg15616_dlq_web_health_nine_post as post

PIN='43bc3610124c113a4f85186fa7689a0e70fa9e26e674a0749a2b50aa932f90b2'
OUT=data.BASE/'PG15619-dlq-web-health-nine-independent-v2'
P=original.PREFIX
CLOSURES={P+n:sorted(P+v for v in values) for n,values in original.CLOSURES.items()}
NAMES=set().union(*[set(v) for v in CLOSURES.values()])
def require(ok,label):
    if not ok:raise ValueError(label)
def assess(p):
    require(p['actualExit']==0 and p['source']==original.SOURCE and p['originalManifestSha256']==post.RAW,'source/run')
    require((p['tests'],p['suites'],len(p['cases']),len(p['xmlHashes']))==(9,3,9,3) and all(p[k]==0 for k in ['failures','errors','skipped','reruns','newAccepted','newTestIds','crcMismatch']),'genuine nine')
    require(len({(c['classname'],c['name']) for c in p['cases']})==9 and all(c['result']=='PASS' for c in p['cases']),'unique/pass')
    require(p['singleSession'] is True and p['sessionIdentity']==original.SESSION and p['execSha256']==raw['execSha256'],'one exec')
    require(p['completeSourceUnitClosure']==CLOSURES and set(p['fullSourceUnits'])==set(CLOSURES) and set(p['physicalClasses'])==set(p['executable'])==set(p['sourcePhysicalInventory'])==NAMES,'whole four Source/seven Code')
    require(p['metadataClasses']==p['manualCounterExclusions']==[] and p['officialGeneratedFiltersUnchanged'] is True,'no exclusion')
    totals={k:{r:sum(p['executable'][n]['counters'][k][r] for n in NAMES) for r in ['missed','covered']} for k in ['LINE','METHOD','CLASS','BRANCH']}
    require(totals==p['totals']=={k:dict(missed=m,covered=c) for k,m,c in [('LINE',17,103),('METHOD',3,22),('CLASS',0,7),('BRANCH',16,58)]},'independent exact sums')
    for name,ns in CLOSURES.items():
        u=p['fullSourceUnits'][name];values={k:{r:sum(p['executable'][n]['counters'][k][r] for n in ns) for r in ['missed','covered']} for k in ['LINE','METHOD','CLASS','BRANCH']}
        require(u['physical']==ns and u['totals']==values and u['four100'] is all(v['missed']==0 and v['covered']>0 for v in values.values()) and u['branchNaturallyZero'] is (values['BRANCH']==dict(missed=0,covered=0)) and u['threeCounter100'] is all(values[k]['missed']==0 and values[k]['covered']>0 for k in ['LINE','METHOD','CLASS']),'actual per Source categories')
    require(p['targetUnitFour100'] is False and p['strictFour100GateExit']==1 and p['allMeasuredApplicableCountersCovered'] is False and sum(u['four100'] for u in p['fullSourceUnits'].values())==3,'two branchless not fake four100')
    require(p['cryptoOrKeyOperationsInvoked'] is False and p['cryptoOperationKind']=='NONE_IN_REVIEWED_DOMAIN_BODY' and p['publicSyntheticTestKeysUsed'] is p['childLocalJcaRegistryRestorationTested'] is p['ownFreshJvmProviderStateOnly'] is False and p['ownedJcaProviderOrderRestored'] is None,'truthful SHA comparison only')
    require(p['actualSecretKeysLoaded'] is p['actualCredentialValuesUsed'] is p['actualAuthenticationOrSessionIssued'] is p['actualFilesOpenedByProduct'] is p['actualPrivateFilesOpened'] is p['jmsFactoryObjectsConstructed'] is False,'no live/private IO')
    require(p['actualJmsConnectionsCreated']==p['actualJmsContextsCreated']==0 and p['actualBrokerOrListenerStarted'] is False and p['onlySyntheticJmsProxyMessages'] is p['onlyUnstartedTomcatRequestResponseObjects'] is True,'no broker/server; proxy and unstarted objects only')
    require(p['forbiddenProductProbeHits']==0 and len(p['passiveNativeBoundaryAbsence']['rows'])==6 and all(r[3]=='0' for r in p['passiveNativeBoundaryAbsence']['rows']),'held/native absence')
    require(p['rootMainInvoked'] is p['formalUpdated'] is p['whole451Accepted'] is p['wholeF03Accepted'] is p['oldCoverageTransferred'] is p['priorProductResultsReused'] is False and p['effortPercent'] is None and p['productTestsReexecutedByPost']==0,'no transfer/acceptance')
    require(all(p[k]==0 for k in ['actualVmActions','actualDatabaseActions','actualNetworkActions','actualServiceActions','actualBrowserActions','actualBoundSockets']),'no external effects')
    require(len(p['owners'])==8 and sum(r['ownershipStatus']=='BASELINE_LOGICAL_REFERENCE' and r['canonicalOwner']==r['canonicalCostOwner'] for r in p['owners'].values())==5 and sum(r['ownershipStatus']=='UNKNOWN' and r['canonicalOwner'] is r['canonicalCostOwner'] is None for r in p['owners'].values())==3,'actual owners')
    require(all(v['actualExit']==0 and not v['timedOut'] for v in p['stages']),'actual stage terminal')
def main():
    global raw
    invocation=capture(__file__);require(not OUT.exists(),'new only')
    raw=data.read_checked(data.BASE/'PG15614-dlq-web-health-nine-pt-v1/manifest.json',post.RAW)
    p=data.read_checked(post.OUT/'manifest.json',PIN);post.assess(raw);assess(p)
    old=data.read_checked(data.BASE/'PG15604-current1903-checksum-capacity-registry-v1/manifest.json','eb3aa009a2892cffbac916a23e6dbd5c4d59b1a98476007dcbe2046e98088d72')
    require(not set(CLOSURES)&set(old['fullSourceUnits']),'new four Source, no old helper reacceptance')
    texts={k:path.read_text() for k,path in original.TESTS.items()};expected=set()
    for key,text in texts.items():
        names=re.findall(r'(?m)^  void ([A-Za-z0-9_]+)\(',text);require(len(names)==original.COUNTS[key],'whole original counts')
        package=re.search(r'package ([A-Za-z0-9_.]+);',text).group(1);expected.update((package+'.'+key,n) for n in names)
    require(expected=={(c['classname'],c['name']) for c in p['cases']},'every whole original once')
    dlq=texts['FatalDlqMessageWriterTest'];health=texts['WebRuntimeHealthTest'];valve=texts['WebHttpAdmissionValveTest']
    properties=['_AMQ_ORIG_ADDRESS','_AMQ_ORIG_QUEUE','NKOriginalTransportID','NKMessageID','NKCorrelationID','NKLayoutID','NKDeliveryCount','NKErrorCode','NKDetectedBy','NKDetectedAt']
    require(len(properties)==len(set(properties))==10 and all('"'+v+'"' in dlq for v in properties),'independent exact ten property names')
    require(all(v in dlq for v in ['new byte[] {1, 2, 3}','sourceBody[0] = 9','"nk.sync.request.q"','"ID:provider-1"','Map.of("NKDeliveryCount", 4)','"A".repeat(129)','"A".repeat(33)','"ID:\\n1"','"ID:\\u00e9"','containsKey("Password")','containsKey("BodyHash")']),'independent body/property/bounds/redaction literals')
    calls=['owner','stop','terminal','reply','log','retry']
    expected_calls=[calls[:1],calls[:2],calls[:3],calls[:3],calls[:3],calls[:3],calls[:3],calls[:4],calls[:5],calls]
    for rejected,expected_order in enumerate(expected_calls):
        actual=[]
        for i,call in enumerate(calls[:3]):
            actual.append(call)
            if rejected==i:break
        else:
            if rejected not in [3,4,5,6]:
                for i,call in enumerate(calls[3:],7):
                    actual.append(call)
                    if rejected==i:break
        require(actual==expected_order,'independent ten condition short circuit order')
    require(all(v in health for v in ['rejected < 10','case 2, 3, 4, 5, 6','index == 3 ? null','index == 4 ? null','index == 5 ? null','index == 6 ? null','position + 1','assertSame(','later notification must not run','provider must not run']),'original truth matrix/identity/order')
    require(all(v in valve for v in ['assertEquals(503, response.getStatus())','assertEquals("no-store", response.getHeader("Cache-Control"))','assertEquals(2, calls.get())','gate.drain(Duration.ZERO)','valve.log(request, null, 0)','valve.log(request, response, 0)','assertSame(fatal','new LinkageError("synthetic fatal")','".lease", "invalid"']),'independent terminal lease/HTTP literal oracle')
    require(not any(v in text for text in texts.values() for v in ['.start(','new Server(','createConnection(','createContext(','TemporaryInfrastructureException','WebStartupException']),'whole scope no service/held graph')
    docs=['documents/300_SS/320_メッセージング/321_Artemis物理構成・JMS設定設計.md']
    documents={v:(data.ROOT/v).read_bytes() for v in docs}
    require(all(b==subprocess.check_output(['git','show','origin/main:'+v],cwd=data.ROOT) for v,b in documents.items()),'approved main design bytes')
    design=documents[docs[0]].decode().split('## 11. DLQ metadata',1)[1].split('## ',1)[0]
    require(all(v in design for v in properties) and 'bodyを改変せず' in design and 'body hashを追加propertyへ複製しない' in design,'independent SS321 metadata allowlist/unchanged body')
    vectors=[('source','source','OLD'),('raw','originalManifestSha256','0'*64),('cases','cases',[]),('totals','totals',{}),('physical','physicalClasses',{}),('sources','fullSourceUnits',{}),('tests','tests',10),('suites','suites',4),('four','targetUnitFour100',True),('strict','strictFour100GateExit',0),('session','singleSession',False),('crc','crcMismatch',1),('metadata','metadataClasses',['unknown']),('excluded','manualCounterExclusions',['unknown']),('crypto','cryptoOrKeyOperationsInvoked',True),('synthetic-key','publicSyntheticTestKeysUsed',True),('jca','childLocalJcaRegistryRestorationTested',True),('secret','actualSecretKeysLoaded',True),('credentials','actualCredentialValuesUsed',True),('auth','actualAuthenticationOrSessionIssued',True),('formal','formalUpdated',True),('whole','whole451Accepted',True),('old','oldCoverageTransferred',True),('file','actualFilesOpenedByProduct',True),('root','rootMainInvoked',True),('accepted','newAccepted',1),('post-replay','productTestsReexecutedByPost',1),('effort','effortPercent',100)]
    frozen=data.ROOT/'tools/quality/pg15618_dlq_web_health_nine_independent.py'
    require(data.sha(frozen.read_bytes())=='6aac9cdcee5c893a3872cb3759442f8b3f0004eb617a3d2bb92d844509e8af20' and "('suites','suites',3)" in frozen.read_text(),'frozen old tool/degenerate negative preserved')
    require(p['suites']==3 and json.dumps(p['suites'])==json.dumps(3) and json.dumps(p['suites'])!=json.dumps(4),'old degeneracy/new distinct suite vector')
    require(all(json.dumps(p[key],sort_keys=True)!=json.dumps(value,sort_keys=True) for _,key,value in vectors),'every negative vector non-equivalent to genuine input')
    labels=[]
    for label,key,value in vectors:
        bad=copy.deepcopy(p);bad[key]=value
        try:assess(bad)
        except ValueError:labels.append(label)
        else:raise AssertionError('false qualification '+label)
    verify(raw['begin']['invocation']);verify(p['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,postSha256=PIN,originalManifestSha256=post.RAW,tests=9,suites=3,sourcePrograms=5,physicalClasses=7,four100SourcePrograms=3,naturallyBranchZeroSourcePrograms=0,incompleteSourcePrograms=2,baselineMainOwnerRows=5,unknownTestOwnerRows=3,semanticNegativeVectors=len(labels),negativeLabels=labels,nondegenerateNegativeVectors=len(vectors),oldToolSha256='6aac9cdcee5c893a3872cb3759442f8b3f0004eb617a3d2bb92d844509e8af20',oldToolObservedBodyExit=1,oldFailureConvertedToPass=False,independentDlqPropertyNames=properties,independentHealthCalls=expected_calls,onlySyntheticJmsProxyMessages=True,onlyUnstartedTomcatRequestResponseObjects=True,pythonVersion=sys.version,approvedDesignHashes={v:data.sha(b) for v,b in documents.items()},cryptoOrKeyOperationsInvoked=False,cryptoOperationKind=p['cryptoOperationKind'],publicSyntheticTestKeysUsed=False,childLocalJcaRegistryRestorationTested=False,ownFreshJvmProviderStateOnly=False,actualSecretKeysLoaded=False,actualCredentialValuesUsed=False,actualAuthenticationOrSessionIssued=False,actualFilesOpenedByProduct=False,actualPrivateFilesOpened=False,actualJmsConnectionsCreated=0,actualJmsContextsCreated=0,actualBrokerOrListenerStarted=False,previousHelpersNotReaccepted=True,productTestsExecutedByIndependent=0,productTestsReexecuted=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(dict(actualExit=0,tests=9,semanticNegativeVectors=len(labels))))
if __name__=='__main__':main()
