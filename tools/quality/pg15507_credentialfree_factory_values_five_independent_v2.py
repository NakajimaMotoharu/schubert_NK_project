"""Independent literal contracts and passive current-source provider measurement; no Product rerun."""
import ast
import copy
import json
from pathlib import Path
import re
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg15502_credentialfree_factory_values_five_pt as original
import pg15505_credentialfree_factory_values_five_post_v2 as post

PIN='85428d8b3fb10300500a0349a1aa05696f04ab1006c5327138188ceceb81d07f'
OUT=data.BASE/'PG15507-credentialfree-factory-values-five-independent-v2'
NAME=original.PREFIX+'messaging/config/ArtemisConnectionFactoryProvider'
CLOSURE=[NAME,NAME+'$ConsumerProfile']
def require(ok,label):
    if not ok:raise ValueError(label)
def assess(p):
    require(p['actualExit']==0 and p['source']==original.SOURCE and p['originalManifestSha256']==post.RAW,'source/run')
    require((p['tests'],p['suites'],len(p['cases']),len(p['xmlHashes']))==(5,3,5,3) and all(p[k]==0 for k in ['failures','errors','skipped','reruns','newAccepted','newTestIds','crcMismatch']),'exact pass')
    require(len({(c['classname'],c['name']) for c in p['cases']})==5 and all(c['result']=='PASS' for c in p['cases']),'unique/pass')
    require(p['singleSession'] is True and p['sessionIdentity']==original.SESSION and p['execSha256']==raw['execSha256'],'one exec')
    require(p['completeSourceUnitClosure']=={NAME:CLOSURE} and set(p['physicalClasses'])==set(p['executable'])==set(p['sourcePhysicalInventory'])==set(CLOSURE),'full physical')
    require(p['metadataClasses']==p['manualCounterExclusions']==[] and p['officialGeneratedFiltersUnchanged'] is True,'Code/filter')
    require(all(any(m['hasCode'] for m in p['sourcePhysicalInventory'][n]['methods']) for n in CLOSURE),'actual Code')
    totals={k:{role:sum(p['executable'][n]['counters'][k][role] for n in CLOSURE) for role in ['missed','covered']} for k in ['LINE','METHOD','CLASS','BRANCH']}
    require(totals==p['totals']==p['fullSourceUnits'][NAME]['totals']=={'LINE':{'covered':47,'missed':12},'METHOD':{'covered':9,'missed':3},'CLASS':{'covered':2,'missed':0},'BRANCH':{'covered':5,'missed':5}},'same exec measured gaps')
    require(p['fullSourceUnits'][NAME]['physical']==CLOSURE and p['targetUnitFour100'] is p['fullSourceUnits'][NAME]['four100'] is p['fullSourceUnits'][NAME]['branchNaturallyZero'] is False and p['strictFour100GateExit']==1,'no false four100/natural')
    require(p['cryptoOrKeyOperationsInvoked'] is p['actualSecretKeysLoaded'] is p['actualCredentialValuesUsed'] is p['actualAuthenticationOrSessionIssued'] is p['actualFilesOpenedByProduct'] is p['actualPrivateFilesOpened'] is p['immutablePackagedTemplateResourcesRead'] is False,'effect profile')
    require(p['jmsFactoryObjectsConstructed'] is p['onlyCredentialFreeUnconnectedLocators'] is True and p['actualJmsConnectionsCreated']==p['actualJmsContextsCreated']==0 and p['actualBrokerOrListenerStarted'] is False,'unconnected only')
    require(p['forbiddenProductProbeHits']==0 and len(p['passiveNativeBoundaryAbsence']['rows'])==6 and all(r[3]=='0' for r in p['passiveNativeBoundaryAbsence']['rows']),'held/native absences')
    require(p['rootMainInvoked'] is p['formalUpdated'] is p['whole451Accepted'] is p['wholeF03Accepted'] is p['oldCoverageTransferred'] is p['priorProductResultsReused'] is False and p['effortPercent'] is None and p['productTestsReexecutedByPost']==0,'no scope transfer')
    require(all(p[k]==0 for k in ['actualVmActions','actualDatabaseActions','actualNetworkActions','actualServiceActions','actualBrowserActions','actualBoundSockets']),'no external effects')
    owners=p['owners'];require(len(owners)==4,'all owners')
    require(sum(r['ownershipStatus']=='BASELINE_LOGICAL_REFERENCE' and r['canonicalOwner']==r['canonicalCostOwner']=='WBS-P005-04' for r in owners.values())==1 and sum(r['ownershipStatus']=='UNKNOWN' and r['canonicalOwner'] is r['canonicalCostOwner'] is None for r in owners.values())==3,'honest owner gaps')
    require(all(stage['actualExit']==0 and not stage['timedOut'] for stage in p['stages']),'actual stages')
def main():
    global raw
    invocation=capture(__file__);require(not OUT.exists(),'new only')
    raw=data.read_checked(data.BASE/'PG15502-credentialfree-factory-values-five-pt-v1/manifest.json',post.RAW)
    p=data.read_checked(post.OUT/'manifest.json',PIN);post.assess(raw);assess(p)
    old_path=data.ROOT/'tools/quality/pg15504_credentialfree_factory_values_five_post.py'
    old=old_path.read_text();require(data.sha(old_path.read_bytes())=='165e27a387fe7a90b4cb8f359cf19c171e576fb6d54f64358942ab39e2c2ec02','frozen failure')
    fixed=old.replace('pg15502_credentialfree_factory_values_five_pt_v2','pg15502_credentialfree_factory_values_five_pt').replace('PG15504-credentialfree-factory-values-five-post-v1','PG15505-credentialfree-factory-values-five-post-v2').replace('pg15504-credentialfree-factory-values-five-post-v1','pg15505-credentialfree-factory-values-five-post-v2')
    require(fixed.rstrip(chr(10))==Path(post.__file__).read_text().rstrip(chr(10)) and ast.dump(ast.parse(fixed))==ast.dump(ast.parse(Path(post.__file__).read_text())),'only import/output repair')
    def equivalent(a,b):return a.rstrip(chr(10))==b.rstrip(chr(10)) and ast.dump(ast.parse(a))==ast.dump(ast.parse(b))
    require(equivalent(fixed,fixed+chr(10)) and equivalent(fixed,fixed.rstrip(chr(10))) and not equivalent(fixed,fixed.replace('TOTAL=5','TOTAL=6')) and not equivalent(fixed,fixed.replace('RAW=', 'ALTERED_RAW=')),'LF-only guard vectors')
    require(not (data.BASE/'PG15504-credentialfree-factory-values-five-post-v1').exists() and not (data.ROOT.parent/'pgpt-runs/PG379/pg15504-credentialfree-factory-values-five-post-v1').exists(),'old failed before outputs')
    module_checks={}
    for path in [Path(post.__file__),data.ROOT/'tools/quality/pg15488_web_inputs_mocklogin_eight_post.py']:
        tree=ast.parse(path.read_text());module=next(n.module for n in tree.body if isinstance(n,ast.ImportFrom) and any(a.asname=='original' for a in n.names))
        target=path.parent/(module+'.py');require(target.is_file(),'real original module');module_checks[str(path.relative_to(data.ROOT))]=dict(module=module,targetSha256=data.sha(target.read_bytes()))
    texts={k:path.read_text() for k,path in original.TESTS.items()}
    effective=texts['ArtemisConnectionFactoryProviderTest']
    literal_settings=['assertEquals(2_000L, factory.getCallTimeout())','assertEquals(10_000L, factory.getClientFailureCheckPeriod())','assertEquals(30_000L, factory.getConnectionTTL())','assertEquals(3, factory.getInitialConnectAttempts())','assertEquals(-1, factory.getReconnectAttempts())','assertEquals(1_000L, factory.getRetryInterval())','assertEquals(2.0, factory.getRetryIntervalMultiplier())','assertEquals(30_000L, factory.getMaxRetryInterval())','assertTrue(factory.isBlockOnDurableSend())','assertFalse(factory.isPreAcknowledge())','assertFalse(factory.isUseTopologyForLoadBalancing())']
    require(all(v in effective for v in literal_settings),'independent literal effective settings')
    require(all(v in effective for v in ['1_048_576','65_536','new int[] {1, 61616, 65535}','assertNull(factory.getUser())','assertNull(factory.getPassword())','\"connect-timeout-millis\", 3_000']),'windows/ports/credential absence')
    require(all(not re.search(r'\b'+v+r'\s*\(',text) for text in texts.values() for v in ['createConnection','createContext','createRetainingUnknown','configureOwned']),'no connected/fault calls')
    enums=texts['EnumValueCatalogCompatibilityTest'];exc=texts['ExceptionValueContractTest']
    require(all(v in enums for v in ['List.of(\"SYNC\", \"ASYNC\", \"WEB_LOG\")','List.of(\"ASYNC_WORK\", \"DLQ\")','List.of(\"nk.async.work\", \"nk.dead.letter\")','List.of(5, 10)','descriptor.getFields().length','descriptor.getSerialVersionUID()']),'enum independent closed lists')
    require(all(v in exc for v in ['ResultCode.FORBIDDEN || code == ResultCode.NOT_FOUND','\"authentication context cryptography failed\"','\"operation is not available\"','assertNull(failure.getCause())']),'shallow value exceptions only')
    spec='documents/300_SS/320_メッセージング/321_Artemis物理構成・JMS設定設計.md';ss=(data.ROOT/spec).read_text()
    require(all(v in ss for v in ['call timeout 2秒','consumer window 1MiB','consumer window 0','consumer window 64KiB','connect timeout 3秒','initial connect attempts 3','reconnect attempts unlimited','retry interval 1秒','retry multiplier 2','max retry 30秒','client failure check 10秒','connection TTL 30秒']),'approved SS literal oracle')
    labels=[]
    mutations=[
      ('source',lambda v:v.update(source='OLD')),('raw',lambda v:v.update(originalManifestSha256='0'*64)),
      ('tests',lambda v:v.update(tests=6)),('failed',lambda v:v.update(failures=1)),('duplicate',lambda v:v['cases'].append(copy.deepcopy(v['cases'][0]))),
      ('notpass',lambda v:v['cases'][0].update(result='NOT_PASS')),('union',lambda v:v.update(singleSession=False)),('session',lambda v:v.update(sessionIdentity='OTHER')),
      ('crc',lambda v:v.update(crcMismatch=1)),('closure',lambda v:v['completeSourceUnitClosure'][NAME].pop()),
      ('excluded',lambda v:v['manualCounterExclusions'].append(NAME)),('counter',lambda v:v['totals']['LINE'].update(missed=0)),
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
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,postSha256=PIN,originalManifestSha256=post.RAW,tests=5,suites=3,sourcePrograms=1,physicalClasses=2,four100SourcePrograms=0,naturallyBranchZeroSourcePrograms=0,incompleteSourcePrograms=1,baselineMainOwnerRows=1,unknownTestOwnerRows=3,semanticNegativeVectors=len(labels),negativeLabels=labels,originalModulePathChecks=module_checks,repairOnlyImportOutput=True,independentLiteralSettingCount=len(literal_settings),approvedSourceHashes={spec:data.sha((data.ROOT/spec).read_bytes())},cryptoOrKeyOperationsInvoked=False,actualSecretKeysLoaded=False,actualCredentialValuesUsed=False,actualAuthenticationOrSessionIssued=False,actualFilesOpenedByProduct=False,actualPrivateFilesOpened=False,onlyCredentialFreeUnconnectedLocators=True,jmsFactoryObjectsConstructed=True,actualJmsConnectionsCreated=0,actualJmsContextsCreated=0,actualBrokerOrListenerStarted=False,ownFreshJvmProviderStateOnly=True,productTestsExecutedByIndependent=0,productTestsReexecuted=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(dict(actualExit=0,tests=5,semanticNegativeVectors=len(labels))))
if __name__=='__main__':main()

