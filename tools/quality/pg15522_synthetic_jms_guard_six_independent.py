"""Independent SS wire-limit/body/header oracle for original synthetic JMS guard six; no Product rerun."""
import copy
import json
import re
import uuid
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg15518_synthetic_jms_guard_six_pt as original
import pg15520_synthetic_jms_guard_six_post as post

PIN='77b9c0aa0bec563c180c66f3de6e81fc108e9b604c068bbc77f4e49242f2bdcb'
OUT=data.BASE/'PG15522-synthetic-jms-guard-six-independent-v1'
NAME=original.PREFIX+'messaging/guard/JmsMessageGuard'
RECORD=original.PREFIX+'messaging/guard/GuardedJmsMessage'
CLOSURE=[NAME,RECORD]
def require(ok,label):
    if not ok:raise ValueError(label)
def assess(p):
    require(p['actualExit']==0 and p['source']==original.SOURCE and p['originalManifestSha256']==post.RAW,'source/run')
    require((p['tests'],p['suites'],len(p['cases']),len(p['xmlHashes']))==(6,1,6,1) and all(p[k]==0 for k in ['failures','errors','skipped','reruns','newAccepted','newTestIds','crcMismatch']),'exact pass')
    require(len({(c['classname'],c['name']) for c in p['cases']})==6 and all(c['result']=='PASS' for c in p['cases']),'unique/pass')
    require(p['singleSession'] is True and p['sessionIdentity']==original.SESSION and p['execSha256']==raw['execSha256'],'one exec')
    require(p['completeSourceUnitClosure']=={NAME:[NAME],RECORD:[RECORD]} and set(p['physicalClasses'])==set(p['executable'])==set(p['sourcePhysicalInventory'])==set(CLOSURE),'full physical')
    require(p['metadataClasses']==p['manualCounterExclusions']==[] and p['officialGeneratedFiltersUnchanged'] is True,'Code/filter')
    require(all(any(m['hasCode'] for m in p['sourcePhysicalInventory'][n]['methods']) for n in CLOSURE),'actual Code')
    totals={k:{role:sum(p['executable'][n]['counters'][k][role] for n in CLOSURE) for role in ['missed','covered']} for k in ['LINE','METHOD','CLASS','BRANCH']}
    require(totals==p['totals']=={'LINE':{'covered':70,'missed':0},'METHOD':{'covered':13,'missed':0},'CLASS':{'covered':2,'missed':0},'BRANCH':{'covered':40,'missed':0}},'same exec measured gaps')
    require(p['fullSourceUnits'][NAME]['physical']==[NAME] and p['fullSourceUnits'][RECORD]['physical']==[RECORD] and p['targetUnitFour100'] is p['fullSourceUnits'][RECORD]['four100'] is p['fullSourceUnits'][NAME]['branchNaturallyZero'] is False and p['fullSourceUnits'][NAME]['four100'] is p['fullSourceUnits'][RECORD]['branchNaturallyZero'] is p['fullSourceUnits'][RECORD]['threeCounter100'] is True and p['strictFour100GateExit']==1,'no false four100/natural')
    require(p['cryptoOrKeyOperationsInvoked'] is p['actualSecretKeysLoaded'] is p['actualCredentialValuesUsed'] is p['actualAuthenticationOrSessionIssued'] is p['actualFilesOpenedByProduct'] is p['actualPrivateFilesOpened'] is p['immutablePackagedTemplateResourcesRead'] is False,'effect profile')
    require(p['jmsFactoryObjectsConstructed'] is p['onlyCredentialFreeUnconnectedLocators'] is False and p['onlySyntheticJmsProxyMessages'] is p['jmsDestinationValueObjectsConstructed'] is True and p['actualJmsConnectionsCreated']==p['actualJmsContextsCreated']==0 and p['actualBrokerOrListenerStarted'] is False,'unconnected only')
    require(p['forbiddenProductProbeHits']==0 and len(p['passiveNativeBoundaryAbsence']['rows'])==6 and all(r[3]=='0' for r in p['passiveNativeBoundaryAbsence']['rows']),'held/native absences')
    require(p['rootMainInvoked'] is p['formalUpdated'] is p['whole451Accepted'] is p['wholeF03Accepted'] is p['oldCoverageTransferred'] is p['priorProductResultsReused'] is False and p['effortPercent'] is None and p['productTestsReexecutedByPost']==0,'no scope transfer')
    require(all(p[k]==0 for k in ['actualVmActions','actualDatabaseActions','actualNetworkActions','actualServiceActions','actualBrowserActions','actualBoundSockets']),'no external effects')
    owners=p['owners'];require(len(owners)==3,'all owners')
    require(sum(r['ownershipStatus']=='BASELINE_LOGICAL_REFERENCE' and r['canonicalOwner']==r['canonicalCostOwner']=='WBS-P005-03' for r in owners.values())==2 and sum(r['ownershipStatus']=='UNKNOWN' and r['canonicalOwner'] is r['canonicalCostOwner'] is None for r in owners.values())==1,'honest owner gaps')
    require(all(stage['actualExit']==0 and not stage['timedOut'] for stage in p['stages']),'actual stages')
def main():
    global raw
    invocation=capture(__file__);require(not OUT.exists(),'new only')
    raw=data.read_checked(data.BASE/'PG15518-synthetic-jms-guard-six-pt-v1/manifest.json',post.RAW)
    p=data.read_checked(post.OUT/'manifest.json',PIN);post.assess(raw);assess(p)
    text=original.TESTS['JmsMessageGuardTest'].read_text()
    literals=['assertArrayEquals(new byte[] {1, 2, 3}, guarded.body())','providerBody[0] = 9','returned[1] = 9','body=<redacted>','\"nk.sync.request::unapproved.q\"','\"::unapproved.q\"','\"nk.async.work\"','\"JMSXDeliveryCount\", 0','\"NKLayoutID\", \"short\"','\"NKProtocolVersion\", \" \"','EXPIRATION_FIELD, -1L','BODY_LENGTH_FIELD, -1L','BODY_LENGTH_FIELD, 2L','BODY_FIELD, null','Proxy.newProxyInstance(']
    require(all(v in text for v in literals),'independent literal body/null/header/destination matrix')
    require(all(not re.search(r'\b'+v+r'\s*\(',text) for v in ['createConnection','createContext','createConsumer','createProducer','createRetainingUnknown','configureOwned']),'proxy only/no transport acquisition')
    ids=['00000000-0000-0000-0000-000000000001','00000000-0000-0000-0000-000000000002']
    require(all(str(uuid.UUID(v))==v and v in text for v in ids),'public literal UUID shape')
    spec='documents/300_SS/320_メッセージング/321_Artemis物理構成・JMS設定設計.md'
    ss=(data.ROOT/spec).read_text();require(all(v in ss for v in ['最大1,000,000 byte','最大1,000 byte','最大10,000 byte','Bodyは','BytesMessage','NKMessageID','NKLayoutID','NKProtocolVersion','nk.sync.reply.web']),'independent approved wire limits/properties')
    helper_paths=['src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/LayoutDefinition.java','src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/transport/BrokerTopology.java']
    layout,topology=[(data.ROOT/v).read_text() for v in helper_paths]
    require(re.findall(r'public static final int MAXIMUM_BODY_LENGTH = ([0-9_]+);',layout)==['1_000_000'],'original constant-coupled input independently bound to SS1M')
    require(all(v in topology for v in ['SYNC_REQUEST("nk.sync.request", 1_000_000, 5_000)','ASYNC_WORK("nk.async.work", 1_000, 0)','WEB_LOG("nk.web.log", 10_000, 0)']),'all three literal topology maxima')
    labels=[]
    mutations=[
      ('source',lambda v:v.update(source='OLD')),('raw',lambda v:v.update(originalManifestSha256='0'*64)),
      ('tests',lambda v:v.update(tests=7)),('failed',lambda v:v.update(failures=1)),('duplicate',lambda v:v['cases'].append(copy.deepcopy(v['cases'][0]))),
      ('notpass',lambda v:v['cases'][0].update(result='NOT_PASS')),('union',lambda v:v.update(singleSession=False)),('session',lambda v:v.update(sessionIdentity='OTHER')),
      ('crc',lambda v:v.update(crcMismatch=1)),('closure',lambda v:v['completeSourceUnitClosure'][NAME].pop()),
      ('excluded',lambda v:v['manualCounterExclusions'].append(NAME)),('counter',lambda v:v['totals']['LINE'].update(missed=1)),
      ('false100',lambda v:v.update(targetUnitFour100=True)),('natural',lambda v:v['fullSourceUnits'][NAME].update(branchNaturallyZero=True)),
      ('secret',lambda v:v.update(actualSecretKeysLoaded=True)),('crypto',lambda v:v.update(cryptoOrKeyOperationsInvoked=True)),
      ('connected',lambda v:v.update(actualJmsConnectionsCreated=1)),('context',lambda v:v.update(actualJmsContextsCreated=1)),
      ('broker',lambda v:v.update(actualBrokerOrListenerStarted=True)),('native',lambda v:v['passiveNativeBoundaryAbsence']['rows'][0].__setitem__(3,'1')),
      ('held',lambda v:v.update(forbiddenProductProbeHits=1)),('formal',lambda v:v.update(formalUpdated=True)),
      ('owner',lambda v:next(iter(v['owners'].values())).update(canonicalCostOwner='WBS-P018-01')),('timeout',lambda v:v['stages'][0].update(timedOut=True))]
    for label,change in mutations:
        bad=copy.deepcopy(p);change(bad)
        try:assess(bad)
        except ValueError:labels.append(label)
        else:raise AssertionError('false qualification '+label)
    verify(p['invocation']);verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,postSha256=PIN,originalManifestSha256=post.RAW,tests=6,suites=1,sourcePrograms=2,physicalClasses=2,four100SourcePrograms=1,naturallyBranchZeroSourcePrograms=1,incompleteSourcePrograms=0,baselineMainOwnerRows=2,unknownTestOwnerRows=1,semanticNegativeVectors=len(labels),negativeLabels=labels,independentLiteralMatrixChecks=len(literals),independentWireLimit=1000000,originalConstantCouplingIndependentlyChecked=True,approvedSourceHashes={v:data.sha((data.ROOT/v).read_bytes()) for v in [spec,*helper_paths]},cryptoOrKeyOperationsInvoked=False,actualSecretKeysLoaded=False,actualCredentialValuesUsed=False,actualAuthenticationOrSessionIssued=False,actualFilesOpenedByProduct=False,actualPrivateFilesOpened=False,onlyCredentialFreeUnconnectedLocators=False,jmsFactoryObjectsConstructed=False,onlySyntheticJmsProxyMessages=True,jmsDestinationValueObjectsConstructed=True,actualJmsConnectionsCreated=0,actualJmsContextsCreated=0,actualBrokerOrListenerStarted=False,ownFreshJvmProviderStateOnly=True,productTestsExecutedByIndependent=0,productTestsReexecuted=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(dict(actualExit=0,tests=6,semanticNegativeVectors=len(labels))))
if __name__=='__main__':main()
