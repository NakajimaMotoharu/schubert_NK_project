"""Independent full-source and original literal oracle qualification of Artemis values3."""
import copy
import json
import struct
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg15775_artemis_detailed_values_three_post as post
import pg15772_artemis_detailed_values_three_pt as original

PIN='e7d6e740d7f2199d21a4df8e7ea83e7b7ad003a1f2e141649f4695e98d6bb38b'
OUT=data.BASE/'PG15776-artemis-detailed-values-three-independent-v1'
PREFIX='dev/codex/schubert/nk/batch/mq/'
CLOSURES={
 'ArtemisStartupObservation':['ArtemisStartupObservation','ArtemisStartupObservation$Evidence'],
 'ArtemisManagementReadinessClient':['ArtemisManagementReadinessClient','ArtemisManagementReadinessClient$Exchange','ArtemisManagementReadinessClient$MessageWriter','ArtemisManagementReadinessClient$OperationEncoder','ArtemisManagementReadinessClient$OwnedOperation','ArtemisManagementReadinessClient$Reader'],
 'ArtemisQueuePressureClient':['ArtemisQueuePressureClient','ArtemisQueuePressureClient$Limits','ArtemisQueuePressureClient$Pressure','ArtemisQueuePressureClient$Reader','ArtemisQueuePressureClient$Value']}
META={
 'ArtemisManagementReadinessClient$Reader':(1536,'read','(Lorg/apache/activemq/artemis/api/core/client/ClientSession;Ljava/lang/String;)Ljava/lang/Object;',1025),
 'ArtemisManagementReadinessClient$OperationEncoder':(1536,'encode','(Lorg/apache/activemq/artemis/api/core/client/ClientMessage;Ljava/lang/String;Ljava/lang/String;[Ljava/lang/Object;)V',1153),
 'ArtemisManagementReadinessClient$OwnedOperation':(1537,'execute','()Ljava/lang/Object;',1025),
 'ArtemisManagementReadinessClient$MessageWriter':(1536,'write','(Lorg/apache/activemq/artemis/api/core/client/ClientMessage;)V',1025),
 'ArtemisManagementReadinessClient$Exchange':(1536,'query','(Lorg/apache/activemq/artemis/api/core/client/ClientSession;Ljava/lang/String;)Ljava/lang/Object;',1025),
 'ArtemisQueuePressureClient$Reader':(1536,'read','(Lorg/apache/activemq/artemis/api/core/client/ClientSession;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/Object;',1025)}
EXPECTED_TOTALS={'LINE':dict(covered=107,missed=141),'METHOD':dict(covered=23,missed=46),'CLASS':dict(covered=6,missed=1),'BRANCH':dict(covered=44,missed=52)}
def require(ok,message):
    if not ok:raise ValueError(message)
def wire(v):return json.dumps(v,sort_keys=True)
def assess(p):
    require(p['actualExit']==0 and p['source']==original.SOURCE and p['originalManifestSha256']==post.RAW,'genuine source/raw')
    require(type(p['tests']) is int and p['tests']==3 and type(p['suites']) is int and p['suites']==1 and all(p[k]==0 and type(p[k]) is int for k in ['failures','errors','skipped','reruns','newAccepted']),'all original3, no not-run pass')
    require(p['singleSession'] is True and p['crcMismatch']==0 and p['sessionIdentity']=='PG15772-ARTEMIS-DETAILED-VALUES-WHOLE3','one original session')
    expected={PREFIX+n:sorted(PREFIX+c for c in v) for n,v in CLOSURES.items()}
    require(p['completeSourceUnitClosure']==expected and set(p['fullSourceUnits'])==set(expected) and len(p['physicalClasses'])==13,'whole three Source/13 physical')
    require(set(p['metadataClasses'])=={PREFIX+n for n in META} and len(p['metadataClasses'])==6 and p['manualCounterExclusions']==[] and p['officialGeneratedFiltersUnchanged'] is True,'six true NoCode, no manual exclusion')
    for name,(flags,method,descriptor,method_flags) in META.items():
        v=p['sourcePhysicalInventory'][PREFIX+name]
        require(v['flags']==flags and v['methods']==[dict(name=method,descriptor=descriptor,flags=method_flags,hasCode=False,codeLength=0)],'exact interface visibility and method Code absence')
    require(set(p['executable'])==set(p['physicalClasses'])-set(p['metadataClasses']) and len(p['executable'])==7,'all seven Code classes included')
    require(p['unexecutedCodeClasses']==[PREFIX+'ArtemisStartupObservation'] and p['unexecutedCodeIncludedInAllDenominators'] is True,'unexecuted outer Code never NoCode/excluded')
    for n,v in p['executable'].items():
        require(set(v['counters'])=={'LINE','METHOD','CLASS','BRANCH'} and all(type(x) is int for counter in v['counters'].values() for x in counter.values()),'typed real counters')
        if n==PREFIX+'ArtemisStartupObservation':
            require(v['counters']=={k:dict(covered=0,missed=m) for k,m in [('LINE',51),('METHOD',9),('CLASS',1),('BRANCH',10)]},'outer startup not invoked')
    total={k:{role:sum(row['counters'][k][role] for row in p['executable'].values()) for role in ['covered','missed']} for k in EXPECTED_TOTALS}
    require(wire(total)==wire(p['totals'])==wire(EXPECTED_TOTALS),'whole counters retain real missed')
    for name,u in p['fullSourceUnits'].items():
        require(u['physical']==expected[name] and u['four100'] is u['metadataOnly'] is u['branchNaturallyZero'] is u['threeCounter100'] is False,'three incomplete source qualifications')
        require(u['totals']=={k:{role:sum(p['executable'][n]['counters'][k][role] for n in u['physical'] if n in p['executable']) for role in ['covered','missed']} for k in total},'independent per-source sums')
    require(p['strictFour100GateExit']==1 and p['targetUnitFour100'] is p['allMeasuredApplicableCountersCovered'] is False,'missed gate is not PASS')
    require(p['onlyInjectedArtemisReaders'] is p['unusedCoreSessionProxyConstructed'] is True and p['outerStartupObservationInvoked'] is False,'original full injected-reader contract')
    require(all(type(p[k]) is int and p[k]==0 for k in ['actualBorrowedCoreSessionMethodsInvoked','actualManagementOperationsInvoked','actualParentDeadlineOperationsInvoked','actualVmActions','actualDatabaseActions','actualServiceActions','actualNetworkActions','actualJmsConnectionsCreated','actualJmsContextsCreated','actualBoundSockets']),'no deployed/parent operations')
    require(all(p[k] is False for k in ['cryptoOrKeyOperationsInvoked','actualSecretKeysLoaded','actualCredentialValuesUsed','actualAuthenticationOrSessionIssued','actualFilesOpenedByProduct','rootMainInvoked','formalUpdated','whole451Accepted','wholeF03Accepted','priorProductResultsReused','oldCoverageTransferred']) and p['effortPercent'] is None,'no crypto/authority/IO/formal transfer')
    require(p['forbiddenProductProbeHits']==0 and len(p['passiveNativeBoundaryAbsence']['rows'])==6 and all(r[3]=='0' for r in p['passiveNativeBoundaryAbsence']['rows']) and all(s['actualExit']==0 and not s['timedOut'] for s in p['stages']),'actual passive stage terminal')
    require(len(p['owners'])==4 and sum(v['ownershipStatus']=='BASELINE_LOGICAL_REFERENCE' for v in p['owners'].values())==3 and sum(v['ownershipStatus']=='UNKNOWN' for v in p['owners'].values())==1,'real three baseline/one unknown roles')
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p=data.read_checked(post.OUT/'manifest.json',PIN)
    raw=data.read_checked(data.BASE/'PG15772-artemis-detailed-values-three-pt-v1/manifest.json',post.RAW)
    post.assess(raw);assess(p)
    require(p['cases']==raw['cases'] and len({(v['classname'],v['name']) for v in p['cases']})==3,'original cases unchanged')
    text=original.TESTS['ArtemisDetailedValuesTest'].read_text()
    required=['assertEquals(11, reads.size())','assertEquals(11, new HashSet<>(reads).size())','assertEquals(1, diskCalls.get())','assertEquals(12, queries.size())','assertEquals(12, new HashSet<>(queries).size())','return 0.125','Map.entry("diskStoreUsage", "3fc0000000000000")','ArtemisQueuePressureClient.Value(5200, 10, ArtemisQueuePressureClient.Pressure.WARNING)','assertEquals(5200, actual.get("nk.async.work").count())','observed.clear()','counts.clear()','fields.clear()','roles.clear()','pressure.clear()','NullPointerException.class','UnsupportedOperationException.class','borrowed session not needed by fixed reader fixture']
    require(all(v in text for v in required) and text.count('@Test')==3,'original independent fixed assertions/aliases/query cardinality/null')
    require(struct.pack('>d',0.125).hex()=='3fc0000000000000' and 5000<=5200<9000 and 10<70*1024**3/100,'independent IEEE754/SS threshold arithmetic')
    path='documents/300_SS/320_メッセージング/321_Artemis物理構成・JMS設定設計.md'
    spec=subprocess.check_output(['git','show','origin/main:'+path],cwd=data.ROOT)
    require(data.sha(spec)=='2fbf317dcc6d2048abb3c8ecdc9747e7b3d46cdba4753bec6bbc9e3ace5d5d1c','approved SS321 source hash')
    require(all(v in spec.decode() for v in ['| Broker name | '+chr(96)+'schubert-nk-broker'+chr(96)+' |','| '+chr(96)+'journal-file-size'+chr(96)+' | 10MiB |','| '+chr(96)+'nk.async.work'+chr(96)+' | 1GiB | 10,000 | PAGE→上限FAIL | 5,000/9,000件、70/90% |']),'independent approved SS fixed values')
    vectors=[('source','source','OLD'),('raw','originalManifestSha256','0'*64),('tests','tests',4),('suites','suites',2),('failed','failures',1),('bool-tests','tests',True),('physical','physicalClasses',{}),('closure','completeSourceUnitClosure',{}),('units','fullSourceUnits',{}),('inventory','sourcePhysicalInventory',{}),('meta','metadataClasses',[]),('executable','executable',{}),('totals','totals',{}),('unexecuted','unexecutedCodeClasses',[]),('exclusion','manualCounterExclusions',['X']),('filters','officialGeneratedFiltersUnchanged',False),('strict','strictFour100GateExit',0),('four','targetUnitFour100',True),('all','allMeasuredApplicableCountersCovered',True),('session','singleSession',False),('crc','crcMismatch',1),('readers','onlyInjectedArtemisReaders',False),('proxy','unusedCoreSessionProxyConstructed',False),('outer','outerStartupObservationInvoked',True),('core','actualBorrowedCoreSessionMethodsInvoked',1),('management','actualManagementOperationsInvoked',1),('parent','actualParentDeadlineOperationsInvoked',1),('crypto','cryptoOrKeyOperationsInvoked',True),('keys','actualSecretKeysLoaded',True),('credentials','actualCredentialValuesUsed',True),('auth','actualAuthenticationOrSessionIssued',True),('file','actualFilesOpenedByProduct',True),('root','rootMainInvoked',True),('formal','formalUpdated',True),('whole','whole451Accepted',True),('prior','priorProductResultsReused',True),('oldcoverage','oldCoverageTransferred',True),('accepted','newAccepted',1),('bool-accepted','newAccepted',False),('effort','effortPercent',100),('owners','owners',{})]
    labels=[]
    for label,key,value in vectors:
        require(wire(p[key])!=wire(value),'nondegenerate '+label);bad=copy.deepcopy(p);bad[key]=value
        try:assess(bad)
        except ValueError:labels.append(label)
        else:raise ValueError('false original values proof '+label)
    bad=copy.deepcopy(p);bad['sourcePhysicalInventory'][PREFIX+'ArtemisManagementReadinessClient$OwnedOperation']['flags']=1536
    try:assess(bad)
    except ValueError:labels.append('public-interface-visibility')
    else:raise ValueError('BUG2147 regression not detected')
    for v in [raw['begin'],p]:
        verify(v['invocation'])
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,postSha256=PIN,originalManifestSha256=post.RAW,tests=3,suites=1,sourcePrograms=3,newSourcePrograms=3,physicalClasses=13,executablePhysicalClasses=7,metadataPhysicalClasses=6,four100SourcePrograms=0,naturallyBranchZeroSourcePrograms=0,incompleteSourcePrograms=3,baselineMainOwnerRows=3,unknownTestOwnerRows=1,semanticNegativeVectors=len(labels),negativeLabels=labels,approvedSpecPath=path,approvedSpecSha256=data.sha(spec),independentIeee754Hex='3fc0000000000000',onlyInjectedArtemisReaders=True,unusedCoreSessionProxyConstructed=True,actualBorrowedCoreSessionMethodsInvoked=0,actualManagementOperationsInvoked=0,actualParentDeadlineOperationsInvoked=0,outerStartupObservationInvoked=False,cryptoOrKeyOperationsInvoked=False,actualSecretKeysLoaded=False,actualCredentialValuesUsed=False,actualAuthenticationOrSessionIssued=False,actualFilesOpenedByProduct=False,productTestsExecutedByIndependent=0,productTestsReexecuted=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(dict(actualExit=0,semanticNegativeVectors=len(labels),tests=3,newSourcePrograms=3,incomplete=3)))
if __name__=='__main__':main()
