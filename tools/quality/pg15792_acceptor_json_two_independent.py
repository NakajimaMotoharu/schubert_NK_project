"""Independent original Acceptor JSON2, whole-source counters and literal SS port oracle."""
import copy
import json
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg15790_acceptor_json_two_post as post
import pg15788_acceptor_json_two_pt as original

PIN='ed61d0f65858cab957822702701c5f8a0b77f3cd962f78a5b7cb01052af29f06'
OUT=data.BASE/'PG15792-acceptor-json-two-independent-v1'
PREFIX='dev/codex/schubert/nk/batch/mq/'
CLOSURES={'ArtemisAcceptorReadinessClient':['ArtemisAcceptorReadinessClient','ArtemisAcceptorReadinessClient$Reader'],'ArtemisManagementReadinessException':['ArtemisManagementReadinessException']}
META={'ArtemisAcceptorReadinessClient$Reader':(1536,'read','(Lorg/apache/activemq/artemis/api/core/client/ClientSession;)Ljava/lang/Object;',1025)}
EXPECTED_TOTALS={'LINE':dict(covered=41,missed=8),'METHOD':dict(covered=5,missed=2),'CLASS':dict(covered=2,missed=0),'BRANCH':dict(covered=19,missed=15)}
def require(ok,message):
    if not ok:raise ValueError(message)
def wire(v):return json.dumps(v,sort_keys=True)
def assess(p):
    require(p['actualExit']==0 and p['source']==original.SOURCE and p['originalManifestSha256']==post.RAW,'genuine source/raw')
    require(type(p['tests']) is int and p['tests']==2 and type(p['suites']) is int and p['suites']==1 and all(p[k]==0 and type(p[k]) is int for k in ['failures','errors','skipped','reruns','newAccepted']),'all original2, no not-run pass')
    require(p['singleSession'] is True and p['crcMismatch']==0 and p['sessionIdentity']=='PG15788-ACCEPTOR-JSON-WHOLE2','one original session')
    expected={PREFIX+n:sorted(PREFIX+c for c in v) for n,v in CLOSURES.items()}
    require(p['completeSourceUnitClosure']==expected and set(p['fullSourceUnits'])==set(expected) and len(p['physicalClasses'])==3,'whole two Source/three physical')
    require(set(p['metadataClasses'])=={PREFIX+n for n in META} and len(p['metadataClasses'])==1 and p['manualCounterExclusions']==[] and p['officialGeneratedFiltersUnchanged'] is True,'one true NoCode, no manual exclusion')
    require(set(p['sourcePhysicalInventory'])=={n for v in expected.values() for n in v},'exact inventory keys before any entry lookup')
    for name,(flags,method,descriptor,method_flags) in META.items():
        v=p['sourcePhysicalInventory'][PREFIX+name]
        require(v['flags']==flags and v['methods']==[dict(name=method,descriptor=descriptor,flags=method_flags,hasCode=False,codeLength=0)],'exact interface visibility and method Code absence')
    require(set(p['executable'])==set(p['physicalClasses'])-set(p['metadataClasses']) and len(p['executable'])==2,'all two Code classes included')
    require(p['unexecutedCodeClasses']==[] and p['unexecutedCodeIncludedInAllDenominators'] is True,'unexecuted outer Code never NoCode/excluded')
    for n,v in p['executable'].items():
        require(set(v['counters'])=={'LINE','METHOD','CLASS','BRANCH'} and all(type(x) is int for counter in v['counters'].values() for x in counter.values()),'typed real counters')
    total={k:{role:sum(row['counters'][k][role] for row in p['executable'].values()) for role in ['covered','missed']} for k in EXPECTED_TOTALS}
    require(wire(total)==wire(p['totals'])==wire(EXPECTED_TOTALS),'whole counters retain real missed')
    for name,u in p['fullSourceUnits'].items():
        require(u['physical']==expected[name] and u['four100'] is u['metadataOnly'] is False and u['branchNaturallyZero'] is name.endswith('Exception') and u['threeCounter100'] is name.endswith('Exception'),'one incomplete source/one natural-zero branch source')
        require(u['totals']=={k:{role:sum(p['executable'][n]['counters'][k][role] for n in u['physical'] if n in p['executable']) for role in ['covered','missed']} for k in total},'independent per-source sums')
    require(p['strictFour100GateExit']==1 and p['targetUnitFour100'] is p['allMeasuredApplicableCountersCovered'] is False,'missed gate is not PASS')
    require(p['onlyInjectedArtemisReaders'] is p['unusedCoreSessionProxyConstructed'] is True and p['outerStartupObservationInvoked'] is False,'original full injected-reader contract')
    require(all(type(p[k]) is int and p[k]==0 for k in ['actualBorrowedCoreSessionMethodsInvoked','actualManagementOperationsInvoked','actualParentDeadlineOperationsInvoked','actualVmActions','actualDatabaseActions','actualServiceActions','actualNetworkActions','actualJmsConnectionsCreated','actualJmsContextsCreated','actualBoundSockets']),'no deployed/parent operations')
    require(all(p[k] is False for k in ['cryptoOrKeyOperationsInvoked','actualSecretKeysLoaded','actualCredentialValuesUsed','actualAuthenticationOrSessionIssued','actualFilesOpenedByProduct','rootMainInvoked','formalUpdated','whole451Accepted','wholeF03Accepted','priorProductResultsReused','oldCoverageTransferred']) and p['effortPercent'] is None,'no crypto/authority/IO/formal transfer')
    require(p['forbiddenProductProbeHits']==0 and len(p['passiveNativeBoundaryAbsence']['rows'])==6 and all(r[3]=='0' for r in p['passiveNativeBoundaryAbsence']['rows']) and all(s['actualExit']==0 and not s['timedOut'] for s in p['stages']),'actual passive stage terminal')
    require(len(p['owners'])==3 and sum(v['ownershipStatus']=='BASELINE_LOGICAL_REFERENCE' for v in p['owners'].values())==2 and sum(v['ownershipStatus']=='UNKNOWN' for v in p['owners'].values())==1,'real two baseline/one unknown roles')
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p=data.read_checked(post.OUT/'manifest.json',PIN)
    raw=data.read_checked(data.BASE/'PG15788-acceptor-json-two-pt-v1/manifest.json',post.RAW)
    post.assess(raw);assess(p)
    require(p['cases']==raw['cases'] and len({(v['classname'],v['name']) for v in p['cases']})==2,'original cases unchanged')
    text=original.TESTS['AcceptorObjectBoundaryTest'].read_text()
    required=['opsMqObj001RejectsEachNonObjectExtraPropsBeforeStartedRead','opsMqObj002RejectsEachNonObjectParamsBeforeStartedRead','List.of("null", "[]", "\\\"public-fixture\\\"", "7", "true")','Map.of(','"127.0.0.1"','"61616"','"CORE"','org.apache.activemq.artemis.core.remoting.impl.netty.NettyAcceptorFactory','assertEquals(1, started.get())','assertEquals(0, uses.get())','assertEquals(0, reads.get())','assertEquals(0, failure.getSuppressed().length)','assertNull(failure.getCause())']
    require(all(v in text for v in required) and text.count('@Test')==2,'original independent literal/ten nonobject fixtures/order/zero-session assertions')
    require(all(not isinstance(json.loads(v),dict) for v in ['null','[]','"public-fixture"','7','true']),'independent JSON type five-vector classification')
    path='documents/300_SS/320_メッセージング/321_Artemis物理構成・JMS設定設計.md'
    spec=subprocess.check_output(['git','show','origin/main:'+path],cwd=data.ROOT)
    require(data.sha(spec)=='2fbf317dcc6d2048abb3c8ecdc9747e7b3d46cdba4753bec6bbc9e3ace5d5d1c','approved SS321 source hash')
    require('| Bind | Core/JMS '+chr(96)+'tcp://127.0.0.1:61616?protocols=CORE'+chr(96) in spec.decode(),'approved literal loopback/core/port, not live listener')
    vectors=[('source','source','OLD'),('raw','originalManifestSha256','0'*64),('tests','tests',3),('suites','suites',2),('failed','failures',1),('bool-tests','tests',True),('physical','physicalClasses',{}),('closure','completeSourceUnitClosure',{}),('units','fullSourceUnits',{}),('inventory','sourcePhysicalInventory',{}),('meta','metadataClasses',[]),('executable','executable',{}),('totals','totals',{}),('unexecuted','unexecutedCodeClasses',['X']),('exclusion','manualCounterExclusions',['X']),('filters','officialGeneratedFiltersUnchanged',False),('strict','strictFour100GateExit',0),('four','targetUnitFour100',True),('all','allMeasuredApplicableCountersCovered',True),('session','singleSession',False),('crc','crcMismatch',1),('readers','onlyInjectedArtemisReaders',False),('proxy','unusedCoreSessionProxyConstructed',False),('outer','outerStartupObservationInvoked',True),('core','actualBorrowedCoreSessionMethodsInvoked',1),('management','actualManagementOperationsInvoked',1),('parent','actualParentDeadlineOperationsInvoked',1),('crypto','cryptoOrKeyOperationsInvoked',True),('keys','actualSecretKeysLoaded',True),('credentials','actualCredentialValuesUsed',True),('auth','actualAuthenticationOrSessionIssued',True),('file','actualFilesOpenedByProduct',True),('root','rootMainInvoked',True),('formal','formalUpdated',True),('whole','whole451Accepted',True),('prior','priorProductResultsReused',True),('oldcoverage','oldCoverageTransferred',True),('accepted','newAccepted',1),('bool-accepted','newAccepted',False),('effort','effortPercent',100),('owners','owners',{})]
    labels=[]
    for label,key,value in vectors:
        require(wire(p[key])!=wire(value),'nondegenerate '+label);bad=copy.deepcopy(p);bad[key]=value
        try:assess(bad)
        except ValueError:labels.append(label)
        else:raise ValueError('false original values proof '+label)
    bad=copy.deepcopy(p);bad['sourcePhysicalInventory'][PREFIX+'ArtemisAcceptorReadinessClient$Reader']['flags']=1537
    try:assess(bad)
    except ValueError:labels.append('reader-interface-visibility')
    else:raise ValueError('exact Reader metadata visibility regression not detected')
    for v in [raw['begin'],p]:
        verify(v['invocation'])
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,postSha256=PIN,originalManifestSha256=post.RAW,tests=2,suites=1,sourcePrograms=2,newSourcePrograms=2,physicalClasses=3,executablePhysicalClasses=2,metadataPhysicalClasses=1,four100SourcePrograms=0,naturallyBranchZeroSourcePrograms=1,incompleteSourcePrograms=1,baselineMainOwnerRows=2,unknownTestOwnerRows=1,semanticNegativeVectors=len(labels),negativeLabels=labels,approvedSpecPath=path,approvedSpecSha256=data.sha(spec),independentJsonTypeVectors=5,onlyInjectedArtemisReaders=True,unusedCoreSessionProxyConstructed=True,actualBorrowedCoreSessionMethodsInvoked=0,actualManagementOperationsInvoked=0,actualParentDeadlineOperationsInvoked=0,outerStartupObservationInvoked=False,cryptoOrKeyOperationsInvoked=False,actualSecretKeysLoaded=False,actualCredentialValuesUsed=False,actualAuthenticationOrSessionIssued=False,actualFilesOpenedByProduct=False,productTestsExecutedByIndependent=0,productTestsReexecuted=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(dict(actualExit=0,semanticNegativeVectors=len(labels),tests=2,newSourcePrograms=2,incomplete=1)))
if __name__=='__main__':main()
