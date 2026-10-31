"""Independent original policy/legacy oracles and all forty physical classes; no Product replay."""
import copy
import re
import subprocess
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import jacoco_readonly_exec_subset as decoder
from pg16403_legacy_policy_original_eight_post_v3 import MAINS,CLOSURES,GENUINE_NO_CODE,OFFICIAL_FILTERED,UNEXECUTED

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
POST=('PG16403-legacy-policy-original-eight-post-v3','cfef910bf1c7f8ba95970e36f9eb2893892dda25e54903cf52a7183aab189fdd')
RAW=('PG16398-legacy-policy-original-eight-pt-v1','bac7abe8a29857fd3cd5a926fa94f2dfa76bf4ad54cd018fe9a456e5ff95ff89')
PREV=('PG16334-current2174-observation-registry-v1','4692639392b626eaecd51bf435d54399ada80d7ba95b680e839b378484806215')
OUT=data.BASE/'PG16405-legacy-policy-original-eight-independent-v2'
P='dev/codex/schubert/nk/batch/platform/'
TEST_PINS={
  "LegacyReceiptValueTest": "7be453b987c5e50dca3d2697115087dbb52b85b1f4d761239dcba38428da09f8",
  "MaintenanceUnitStopPolicyTest": "b9804b33eb028770bac620fabe176883ad8a627aa92fdc0f2282264ae43114f4",
  "InspectorUnitProbeFixture": "75b62aea8f3e4fbc558ec24698c7ff7d1faf4f477f34addb17e5e58f1283da2b",
  "InspectorUnitSnapshotTest": "edf0ce67d649d340e2e61907cc8228cd9c44fe08a21a9f011d81cdcbef4d1a63"
}
METHODS={'LegacyReceiptValueTest':['retdata001LegacyZeroDoesNotManufactureTypedOrStoppedReceipt'],
'MaintenanceUnitStopPolicyTest':['mpol001AllEightFixedPolicyAndOrderIndependent','mpol002MissingDuplicateUnknownAndLineStructure','mpol003ByteAndNullBounds','mpol004WrongIdLoadKillAndAutomaticSigkillRefused','mpol005FixedNativeQueryAndAllProcessOwners','mpol006KnownUnknownNullAndInterrupts','mpol007IndependentParallelAndNoStopAuthority']}

def require(ok,why):
    if not ok:raise ValueError(why)

def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])

def filter_contract(outer,matcher):
    require(all(v in outer for v in ['getSuperClassName','IFilterOutput.ignore','<init>','()V']) and all(v in matcher for v in ['firstIsALoad0','nextIsInvoke','nextIs']),'official filter class/method witness')

def normalized_closures(value):
    require(type(value) is dict and set(value)==set(CLOSURES),'exact Source closure keys')
    require(all(type(v) is list and all(type(n) is str for n in v) and len(v)==len(set(v)) for v in value.values()),'no duplicate physical names')
    return {k:sorted(v) for k,v in value.items()}

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p,raw,old=[read(v) for v in [POST,RAW,PREV]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [p,raw,old]),'genuine chain')
    bodies={}
    for name,pin in TEST_PINS.items():
        path=data.ROOT/('src/schubert-nk-batch/src/test/java/'+P+name+'.java');blob=path.read_bytes()
        require(data.sha(blob)==raw['begin']['testSourceHashes'][str(path)]==pin,'whole unchanged original/compile-only helper')
        bodies[name]=blob.decode()
    expected={(('dev.codex.schubert.nk.batch.platform.'+c),m) for c,methods in METHODS.items() for m in methods}
    for name,methods in METHODS.items():require(re.findall(r'@Test\s+void\s+(\w+)\(',bodies[name])==methods,'whole original method set')
    actual=[]
    for name,pin in p['xmlHashes'].items():
        blob=(data.BASE/POST[0]/name).read_bytes();require(data.sha(blob)==pin,'original XML')
        xml=ET.fromstring(blob);require(all(xml.get(k)=='0' for k in ['failures','errors','skipped']),'actual nonpass zero')
        for case in xml.findall('testcase'):require(not list(case),'no child nonpass');actual.append((case.get('classname'),case.get('name')))
    require(len(actual)==8 and set(actual)==expected and not expected&{(v['classname'],v['name']) for v in old['cases']},'exact fresh current eight')
    legacy=bodies['LegacyReceiptValueTest'];policy=bodies['MaintenanceUnitStopPolicyTest']
    oracles=[
        ('legacy-data-only',all(v in legacy for v in ['new boolean[] {false, true}','data-only test must not capture an actual receipt','typed receipt unavailable','stopped Backup receipt unavailable','assertEquals(1, queries.get())','zero ? Optional.of(MorningBackupUnitCycle.Outcome.SUCCESS) : Optional.empty()'])),
        ('fixed-eight-unit-table',re.findall(r'"([a-z][a-z-]*\.service)"',policy[:policy.index('private static byte[] policy')])==['caddy.service','schubert-nk-web.service','schubert-nk-api.service','schubert-nk-cleanup.service','schubert-nk-inbox-inspector.service','schubert-nk-expiry-cleanup.service','schubert-nk-backup.service','artemis.service']),
        ('malformed-wipe',all(v in policy for v in ['StopGateFailure.MALFORMED_STATE','assertArrayEquals(new byte[value.length], value)','good.substring(0, good.length() - 1)','KillMode=='])),
        ('byte-null-boundary',all(v in policy for v in ['new byte[0]','new byte[512]','new byte[513]','new byte[] {0, 13, 31, 127, (byte) 0x80}','new MaintenanceUnitStopPolicy(null)','new MaintenanceUnitStopPolicy.NativeSource(null)'])),
        ('fixed-policy-refusal',all(v in policy for v in ['LoadState=not-found','LoadState=masked','KillMode=process','KillMode=mixed','SendSIGKILL=yes'])),
        ('existing-fake-query',all(v in policy for v in ['new InspectorUnitProbeFixture.Child','"/usr/bin/systemctl"','"--property=Id,LoadState,KillMode,SendSIGKILL"','child.allClosed()','child.wiped()']) and 'class Child extends Process' in bodies['InspectorUnitProbeFixture']),
        ('irq-identity',all(v in policy for v in ['assertEquals(0, calls[0])','StopGateFailure.INTERRUPTED','Thread.currentThread().isInterrupted()','assertSame(','known,','unknown,'])),
        ('own-parallel-fixed-oracle',all(v in policy for v in ['Executors.newFixedThreadPool(8)','i < 64','Arrays.equals(input, new byte[input.length])','assertTrue(result.get())','"Id,LoadState,KillMode,SendSIGKILL"']))]
    require(all(ok for _,ok in oracles),'independent original literal oracle')
    design_hashes={}
    # Resolve exact approved document names by the numeric program design identity.
    for number in ['341','342','343']:
        choices=list((data.ROOT/'documents/300_SS/340_batch・基盤').glob(number+'_*.md'));require(len(choices)==1,'one approved SS by ID')
        path=choices[0];relative=str(path.relative_to(data.ROOT));blob=path.read_bytes()
        require(blob==subprocess.check_output(['git','show','origin/main:'+relative],cwd=data.ROOT),'approved same byte')
        design_hashes[relative]=data.sha(blob)
    slot=data.ROOT.parent/'pgpt-runs/PG379/pg16403-legacy-policy-original-eight-post-v3'
    outer=(slot/'official-filter.stdout').read_text();matcher=(slot/'official-filter-matcher.stdout').read_text();filter_contract(outer,matcher)
    filter_labels=[]
    for label,a,b in [('swapped',matcher,outer),('wrong-helper',outer,matcher.replace('firstIsALoad0','nextIsVar')),('missing-super',outer.replace('getSuperClassName','unknown'),matcher),('empty','',matcher)]:
        try:filter_contract(a,b)
        except ValueError:filter_labels.append(label)
        else:raise ValueError('false official filter witness')
    exec_blob=(data.ROOT.parent/'pgpt-runs/PG379/pg16398-legacy-policy-original-eight-pt-v1/jacoco.exec').read_bytes()
    require(data.sha(exec_blob)==p['execSha256']==raw['execSha256'],'one immutable actual exec')
    base=decoder.decode(exec_blob,set());require(len(base['sessions'])==1 and base['sessions'][0]['labelBytesHex']==p['sessionIdentity'].encode().hex(),'one structurally validated session')
    for name,row in p['executable'].items():
        if name in UNEXECUTED:
            try:decoder.decode(exec_blob,{name})
            except ValueError as error:require(error.args==('one session and all exact target records required',),'only genuine missing record allowed after full structural validation')
            else:raise ValueError('observed claimed absent')
        else:
            observed=decoder.decode(exec_blob,{name})['classes'][name]
            require(observed['crc64']==row['crc64'] and len(observed['hitProbeIds'])>0,'actual observed same CRC')
    def contract(v):
        require(type(v['actualExit']) is int and v['actualExit']==0 and v['source']==SOURCE and v['originalManifestSha256']==RAW[1],'same source/run')
        require((v['tests'],v['suites'],v['targetSourceUnits'],v['newTestIds'])==(8,2,6,0) and v['cases']==raw['cases'],'eight whole originals')
        physical=set().union(*map(set,CLOSURES.values()));code=physical-GENUINE_NO_CODE-OFFICIAL_FILTERED
        require(normalized_closures(v['completeSourceUnitClosure'])==normalized_closures(CLOSURES) and set(v['physicalClasses'])==set(v['sourcePhysicalInventory'])==physical and set(v['fullSourceUnits'])==set(MAINS) and set(v['executable'])==code,'all physical and executable exact keysets')
        require(set(v['metadataClasses'])==GENUINE_NO_CODE|OFFICIAL_FILTERED and set(v['genuineNoCodeClasses'])==GENUINE_NO_CODE and set(v['officialGeneratedNoCounterClasses'])==OFFICIAL_FILTERED and (v['rawClassfileCodePhysical'],v['jacocoExecutablePhysical'],v['genuineNoCodePhysical'],v['officialGeneratedNoCounterPhysical'])==(19,18,21,1),'raw Code versus official zero counter')
        require(set(v['unexecutedCodeClasses'])==UNEXECUTED and len(UNEXECUTED)==8 and v['unexecutedCodeIncludedInAllDenominators'] is True,'actual unobserved eight, not initialized Inspector')
        for name in GENUINE_NO_CODE:require(not any(m['hasCode'] for m in v['sourcePhysicalInventory'][name]['methods']),'genuine no Code')
        for name in OFFICIAL_FILTERED:require(any(m['hasCode'] for m in v['sourcePhysicalInventory'][name]['methods']),'filtered Code not genuine no Code')
        totals={k:{r:sum(c['counters'][k][r] for c in v['executable'].values()) for r in ['covered','missed']} for k in ['LINE','METHOD','CLASS','BRANCH']}
        require(totals==v['totals']=={k:dict(covered=c,missed=m) for k,c,m in [('LINE',127,464),('METHOD',39,97),('CLASS',10,8),('BRANCH',39,149)]},'independent physical counter sums, miss retained')
        require(all(c['covered']==0 for n in UNEXECUTED for c in v['executable'][n]['counters'].values()),'unobserved zero coverage')
        require(v['singleSession'] is True and v['crcMismatch']==0 and v['strictFour100GateExit']==1 and v['targetUnitFour100'] is False and v['manualCounterExclusions']==[] and v['officialGeneratedFiltersUnchanged'] is True,'no artificial whole100/filter')
        require(v['existingFakeProcessFixtureUsed'] is True and v['productExternalProcessesStarted']==0 and v['defaultNativeCallbackInvoked'] is False and v['ownThreadCount'] is None and v['declaredOwnWorkerPoolSize']==8 and v['ownTaskCount']==64,'declared versus measured effects')
        require(all(v[k] is False for k in ['actualPermitIssueSignPublishOrRetire','actualSecretKeysLoaded','actualCredentialValuesUsed','actualAuthenticationOrSessionIssued','actualFilesOpenedByProduct','rootMainInvoked','oldCoverageTransferred','formalUpdated','whole451Accepted']) and v['effortPercent'] is None,'no authority/acceptance transfer')
    contract(p);labels=[]
    ordered=copy.deepcopy(p);ordered['completeSourceUnitClosure']={k:list(reversed(v)) for k,v in CLOSURES.items()};contract(ordered)
    for label,change in [('closure-duplicate',lambda v:v['completeSourceUnitClosure'][P+'MaintenanceUnit'].append(P+'MaintenanceUnit')),('closure-missing',lambda v:v['completeSourceUnitClosure'][P+'MaintenanceUnit'].clear()),('closure-extra',lambda v:v['completeSourceUnitClosure'][P+'MaintenanceUnit'].append(P+'Unknown'))]:
        bad=copy.deepcopy(p);change(bad)
        try:contract(bad)
        except ValueError:labels.append(label)
        else:raise ValueError('false closure shape '+label)
    for key,value in [('actualExit',True),('source','OLD'),('originalManifestSha256','0'*64),('tests',9),('suites',3),('targetSourceUnits',5),('newTestIds',1),('cases',[]),('completeSourceUnitClosure',{}),('physicalClasses',{}),('sourcePhysicalInventory',{}),('fullSourceUnits',{}),('executable',{}),('metadataClasses',[]),('genuineNoCodeClasses',p['metadataClasses']),('officialGeneratedNoCounterClasses',[]),('rawClassfileCodePhysical',18),('jacocoExecutablePhysical',19),('unexecutedCodeClasses',list(UNEXECUTED)+[P+'InspectorUnitProbe']),('totals',{}),('singleSession',False),('crcMismatch',1),('strictFour100GateExit',0),('targetUnitFour100',True),('manualCounterExclusions',['Unresolved']),('existingFakeProcessFixtureUsed',False),('productExternalProcessesStarted',1),('defaultNativeCallbackInvoked',True),('ownThreadCount',8),('formalUpdated',True),('effortPercent',100)]:
        bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false whole source qualification '+key)
    for v in [p,old]:verify(v['invocation'])
    verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,postSha256=POST[1],rawSha256=RAW[1],tests=8,suites=2,semanticNegativeVectors=len(labels),negativeLabels=labels,officialFilterNegativeVectors=len(filter_labels),officialFilterNegativeLabels=filter_labels,independentOracleVectors=len(oracles),oracleLabels=[n for n,_ in oracles],newSourcePrograms=6,newPhysicalClasses=40,metadataPhysicalClasses=22,genuineNoCodePhysicalClasses=21,officialGeneratedOnlyZeroCounterClasses=1,wholeSourceIncompleteCount=sum(not(v['four100'] or v['branchNaturallyZero'] and v['threeCounter100']) for v in p['fullSourceUnits'].values()),approvedDesignHashes=design_hashes,productTestsReexecuted=0,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
