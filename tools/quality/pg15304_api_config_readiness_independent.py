"""Independent original API data-only11/whole physical Main; preserve native coverage gaps."""
import copy
import json
import re
import subprocess
import zipfile
import xml.etree.ElementTree as ET
import classfile_code_metadata as code
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical

PIN='ff665193ddb62c0ed11afac98a9bc5465167ad5348552b2d1d093951de59b92b'
POST=data.BASE/'PG15302-api-config-readiness-eleven-post-v1'
OUT=data.BASE/'PG15304-api-config-readiness-independent-v1'
PREFIX='dev/codex/schubert/nk/api/bootstrap/'
COUNTS={"ApiAdmittedConfigurationTest":8,"ApiReadinessPredicateTest":3}
EXPECTED={"ApiProcessMain":["ConfigurationLoad","Startup"]}
NATURAL=set()
METADATA={PREFIX+'ApiProcessMain$ConfigurationLoad',PREFIX+'ApiProcessMain$Startup'}
DOC='documents/300_SS/340_batch・基盤/343_設定file・directory・初期data・migration・切戻し設計.md'

def require(ok,message):
    if not ok:raise ValueError(message)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only monitoring independent')
    p=data.read_checked(POST/'manifest.json',PIN)
    raw=data.read_checked(data.BASE/'PG15300-api-config-readiness-eleven-pt-v1/manifest.json','de9cb79a296838fd5112450d14ac6531dbb510eed64860853a807108fdbd58d4')
    registry=data.read_checked(data.BASE/'PG15284-current1748-profile-terminal-registry-v1/manifest.json','7bc09027b74939ddc45fb92d63bb82be1c096f898670f275bed940cbe507435d')
    require(p['actualExit']==raw['actualExit']==registry['actualExit']==0 and p['source']==raw['source']==registry['source']=='6b53efeec87f3ec36a840dd8e7759656cb4aee5c' and p['execSha256']==raw['execSha256'] and p['sessionIdentity']=='PG15300-ORIGINAL-API-CONFIG-READINESS11','genuine same source/own single exec')
    actual=[];suite_names=set()
    for filename,h in p['xmlHashes'].items():
        value=(POST/filename).read_bytes();require(data.sha(value)==h==raw['xmlHashes'][filename],'original whole XML bytes');root=ET.fromstring(value);simple=root.get('name').rsplit('.',1)[-1];suite_names.add(simple)
        require(int(root.get('tests'))==COUNTS[simple] and all(int(root.get(k))==0 for k in ['failures','errors','skipped']),'all original whole16 FES0')
        for c in root.findall('testcase'):
            require(not list(c),'actual PASS');actual.append((c.get('classname'),c.get('name')))
    require(suite_names==COUNTS.keys() and len(actual)==len(set(actual))==11 and set(actual)=={(c['classname'],c['name']) for c in raw['cases']} and not set(actual)&{(c['classname'],c['name']) for c in registry['cases']},'all16/one suite unique new, never prior1367 replay')
    normal=data.read_checked(data.BASE/'PG14216-typed-marker-guard-six-compile-v1/manifest.json','1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3');hashes=normal['begin']['inputHashes']
    declared=set()
    for simple,count in COUNTS.items():
        path='src/schubert-nk-api/src/test/java/'+PREFIX+simple+'.java';text=(data.ROOT/path).read_text();require(data.sha((data.ROOT/path).read_bytes())==hashes[path],'whole original normal Test source pin')
        methods=re.findall(r'@Test\s+void\s+([A-Za-z0-9_]+)\s*\(',text);require(len(methods)==count,'all original declared methods');declared.update(('dev.codex.schubert.nk.api.bootstrap.'+simple,n) for n in methods)
    require(declared==set(actual),'every declared Test ID corresponds to one original actual XML')
    document=subprocess.check_output(['git','show','origin/main:'+DOC],cwd=data.ROOT);doc_head=subprocess.check_output(['git','rev-parse','origin/main'],cwd=data.ROOT,text=True).strip()
    require(all(v in document.decode() for v in ['SSC301','ConfigurationLoad','failureCode=70','non-secret configuration unavailable','IOExceptionは同一objectを伝搬']),'approved static config-port failure/identity contract')
    testbase=data.ROOT/'src/schubert-nk-api/src/test/java'/PREFIX
    config=(testbase/'ApiAdmittedConfigurationTest.java').read_text();readiness=(testbase/'ApiReadinessPredicateTest.java').read_text()
    prior_oracle=data.read_checked(data.BASE/'PG15226-nonsecret-config-independent-v1/manifest.json','7fad8f7566a946e3fdf76353f56fdf9e0f896647db5c7cd0fa172269626634f3')
    golden='afec3045ebed78de9d1fab75daf34d7ca4e2bd990b110f3c6afac97def435796'
    require(prior_oracle['independentGoldenSha256']['ApiNonSecretConfigTest']==golden and golden in config,'independent fixed SS343 23-key canonical SHA, not current Production expected')
    require(all(v in config for v in ['assertSame(input, result.value())','assertEquals(50, status[0])','assertEquals(70, status[0])','assertNull(failure.getCause())','assertEquals(0, failure.getSuppressed().length)','assertSame(','new int[0]','new int[] {50, 50}','assertEquals(0, calls.get())']),'independent value/slot50-70/IO-fatal identity/null-before-callback oracle')
    def boolean_rows(declaration):
        rows=[]
        for literal in re.findall(r'\{([^{}]+)\}',declaration):
            values=[v.strip() for v in literal.split(',')];require(all(v in ['true','false'] for v in values),'literal boolean row only');rows.append([v=='true' for v in values])
        return rows
    management=[[False,False,False,False],[False,False,True,False],[False,True,False,False],[False,True,True,False],[True,False,False,False],[True,False,True,True],[True,True,False,False],[True,True,True,False]]
    runtime=[[False,False,False],[False,True,False],[True,False,False],[True,True,True]]
    require(boolean_rows(readiness.split('boolean[][] management = {',1)[1].split('};',1)[0])==management and boolean_rows(readiness.split('boolean[][] runtime = {',1)[1].split('};',1)[0])==runtime,'all independent8/4 truth rows, no production-derived expected')
    steps={'CONSUMER_GROUPS_STEP':'groups','STOP_STEP':'stop','OUTBOX_STEP':'outbox','CONSUMERS_STEP':'consumers'}
    def orders(declaration):return [[steps[v.strip()] for v in row.split(',')] for row in re.findall(r'List.of\(([^()]*)\)',declaration)]
    management_order=[['groups'],['groups'],['groups'],['groups'],['groups','stop','outbox'],['groups','stop','outbox'],['groups','stop'],['groups','stop']]
    runtime_order=[['consumers'],['consumers'],['consumers','outbox'],['consumers','outbox']]
    require(orders(readiness.split('List<List<String>> order =',1)[1].split('for (int i',1)[0])==management_order and orders(readiness.split('List<List<String>> runtimeOrder =',1)[1].split('for (int i',1)[0])==runtime_order,'independent short-circuit sequence and no factory sample')
    require('assertEquals(List.of(), calls' in readiness and 'assertSame(' in readiness and all('new ApiProcessMain(' not in v and '.main(' not in v and '.run(' not in v for v in [config,readiness]),'only original static data ports, not public Main or excluded original Main Test')
    passive=p['passiveNativeBoundaryAbsence'];expected_prefixes=['dev/codex/schubert/nk/bootstrap/ServiceStartupAdmission$NativeGate','dev/codex/schubert/nk/bootstrap/ServiceStartupAdmission$NativeObservation','dev/codex/schubert/nk/bootstrap/ChildStartupContext$NativeIo','dev/codex/schubert/nk/api/bootstrap/ApiProcessLifetime','dev/codex/schubert/nk/api/file/ServiceProcessResources','dev/codex/schubert/nk/storage/ServiceConfigFiles$NioIo']
    require(passive['prefixes']==expected_prefixes and passive['sessionIdentity']==p['sessionIdentity'] and passive['execSha256']==p['execSha256'] and passive['productClassesLoaded'] is passive['productMethodsInvoked'] is False and passive['allPrefixesNormalJarPresent'] is True and passive['toolNegativeExpectedExits']==[1,1],'passive same original exec, no product invocation')
    require(len(passive['rows'])==6 and {r[1] for r in passive['rows']}==set(expected_prefixes) and all(r[0]=='OWNED_API_PORT_NATIVE_PREFIX_NO_TRUE_PROBES' and r[2:]==['0','0'] for r in passive['rows']),'all six unsafe/native/resource prefixes absent, not native acceptance')
    require(data.sha((data.ROOT/passive['readerSourcePath']).read_bytes())==passive['readerSourceSha256'],'passive fixed reader source')
    slot=data.ROOT.parent/'pgpt-runs/PG379/pg15302-api-config-readiness-eleven-post-v1'
    require(data.sha((slot/'passive-classes/OwnedApiPortBoundaryProbeAbsence.class').read_bytes())==passive['readerClassSha256'],'passive actual compiled reader')
    for label,stage,expected in zip(['passive-compile','passive-native-absence','passive-wrong-session','passive-missing-args'],p['stages'][-4:],[0,0,1,1]):
        require(stage['actualExit']==expected and not stage['timedOut'] and data.sha((slot/(label+'.stdout')).read_bytes())==stage['stdoutSha256'] and data.sha((slot/(label+'.stderr')).read_bytes())==stage['stderrSha256'],'passive stage terminal/hash provenance')
    verify(prior_oracle['invocation'])
    closures={PREFIX+n:sorted([PREFIX+n,*[PREFIX+n+'$'+child for child in nested]]) for n,nested in EXPECTED.items()};names=set().union(*(set(v) for v in closures.values()))
    require(p['completeSourceUnitClosure']==closures and set(p['physicalClasses'])==names and set(p['executable'])==names-METADATA and len(names)==3 and set(p['metadataClasses'])==METADATA and not closures.keys()&registry['fullSourceUnits'].keys(),'one entire new Source/oneCode, no helper parent promotion')
    logical={r['path']:r for r in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']};totals={k:dict(missed=0,covered=0) for k in ['LINE','METHOD','CLASS','BRANCH']}
    with zipfile.ZipFile(normal['jars']['api']['path']) as jar:
        for name,closure in closures.items():
            require({n[:-6] for n in jar.namelist() if n==name+'.class' or n.startswith(name+'$') and n.endswith('.class')}==set(closure),'all actual nested Jar classfiles')
            local={k:{role:sum(p['executable'][n]['counters'][k][role] for n in closure if n not in METADATA) for role in ['missed','covered']} for k in totals};unit=p['fullSourceUnits'][name];natural=name in NATURAL
            require(local==unit['totals'] and unit['four100'] is False and unit['branchNaturallyZero'] is False and unit['threeCounter100'] is False and local['LINE']['missed']==159 and local['METHOD']['missed']==29 and local['BRANCH']['missed']==6,'whole Main remains coverage incomplete; eleven successful tests not a native/Main acceptance')
            for k in totals:
                for role in totals[k]:totals[k][role]+=local[k][role]
            for n in closure:
                value=jar.read(n+'.class');parsed=code.decode(value,n+'.class');require(data.sha(value)==p['physicalClasses'][n] and parsed['methods']==p['sourcePhysicalInventory'][n]['methods'] and (not any(m['hasCode'] for m in parsed['methods']) if n in METADATA else any(m['hasCode'] for m in parsed['methods'])),'independent actual executable Code, no hidden exclusions')
    require(totals==p['totals']=={'LINE':{'missed':159,'covered':17},'METHOD':{'missed':29,'covered':5},'CLASS':{'missed':0,'covered':1},'BRANCH':{'missed':6,'covered':12}} and len(p['missedLines'])>0,'actual full Main counter gaps preserved, no filter or success conversion')
    require(len(p['owners'])==3,'only one Main/one whole Test owner rows')
    for path,owned in p['owners'].items():
        expected=canonical(path,logical);require(data.sha((data.ROOT/path).read_bytes())==hashes[path]==owned['sha256'] and all(owned[k]==v for k,v in expected.items()),'exact canonical owner identity')
        if '/src/main/java/' in path:require(expected['canonicalOwner']==expected['canonicalCostOwner']=='WBS-P018-05' and expected['ownershipStatus']=='BASELINE_LOGICAL_REFERENCE','Main baseline not runtime proof')
        else:require(expected['canonicalOwner'] is expected['canonicalCostOwner'] is None and expected['ownershipStatus']=='UNKNOWN','Test unknown not inferred')
    require(p['metadataZeroCountersVerified'] is True and all(p['sourcePhysicalInventory'][n]['flags']==1536 and not any(v['hasCode'] for v in p['sourcePhysicalInventory'][n]['methods']) for n in METADATA),'two real NoCode interfaces, no executable exclusion')
    fixed={k:p[k] for k in ['source','cases','execSha256','sessionIdentity','physicalClasses','completeSourceUnitClosure','sourcePhysicalInventory','fullSourceUnits','totals','owners','fixtureHashes','passiveNativeBoundaryAbsence','metadataZeroCountersVerified','missedLines']}
    def contract(v):
        require(all(json.dumps(v[k],sort_keys=True)==json.dumps(value,sort_keys=True) for k,value in fixed.items()),'all actual original proof/owner/fixture immutable')
        require(v['tests']==11 and v['suites']==2 and v['targetUnitFour100'] is False and v['strictFour100GateExit']==1 and v['singleSession'] is True and v['crcMismatch']==0 and set(v['metadataClasses'])==METADATA and v['manualCounterExclusions']==[],'complete source strict four100 actual')
        require(v['ownChildJvmStandardSdkObserved'] is False and v['forcedGcOrHeapDump'] is False and v['externalVmOrTargetProcessObserved'] is False,'genuine own child SDK measurement never remote/native or forced GC')
        require(v['newAccepted']==v['productTestsReexecutedByPost']==0 and v['formalUpdated'] is v['whole451Accepted'] is v['wholeF03Accepted'] is v['oldCoverageTransferred'] is v['coverageExecUnion'] is False and v['effortPercent'] is None and v['canonicalOwnersRemainCandidateNotAccepted'] is v['helperSourceProgramsNotAcceptedByTheseTargetCounters'] is True,'no helper/old/owner/formal/effort transfer')
    contract(p);negative=[]
    for key,value in [('ownChildJvmStandardSdkObserved',True),('forcedGcOrHeapDump',True),('externalVmOrTargetProcessObserved',True),('source','OLD'),('tests',55),('suites',3),('targetUnitFour100',True),('strictFour100GateExit',0),('singleSession',False),('crcMismatch',1),('metadataClasses',[]),('manualCounterExclusions',['AlertLifecycle']),('totals',{}),('fullSourceUnits',{}),('fixtureHashes',{'unknown':'0'*64}),('owners',{}),('newAccepted',1),('productTestsReexecutedByPost',1),('formalUpdated',True),('whole451Accepted',True),('wholeF03Accepted',True),('oldCoverageTransferred',True),('coverageExecUnion',True),('effortPercent',100),('canonicalOwnersRemainCandidateNotAccepted',False),('helperSourceProgramsNotAcceptedByTheseTargetCounters',False),('passiveNativeBoundaryAbsence',{}),('metadataZeroCountersVerified',False),('missedLines',[])]:
        bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad)
        except ValueError:negative.append(key)
        else:raise ValueError('false Web-pool-context56 proof accepted '+key)
    for v in [p,registry]:verify(v['invocation'])
    verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=p['source'],invocation=invocation,postSha256=PIN,tests=11,suites=2,newUniqueMethods=11,sourcePrograms=1,physicalClasses=3,four100SourcePrograms=0,incompleteSourcePrograms=1,incompletePhysicalClasses=3,naturallyBranchZeroSourcePrograms=0,naturallyBranchZeroPhysicalClasses=0,metadataOnlyPhysical=2,totals=totals,semanticNegativeVectors=len(negative),negativeLabels=negative,independentConfigGoldenSha256=golden,independentManagementTruth=management,independentRuntimeTruth=runtime,independentManagementOrder=management_order,independentRuntimeOrder=runtime_order,passiveNativeBoundaryAbsence=passive,passiveOriginalProductReplay=0,authoritativeDesign=dict(path=DOC,gitRef='origin/main',commit=doc_head,sha256=data.sha(document)),baselineMainOwnerRows=1,unknownTestOwnerRows=2,candidateOwnersNotAccepted=True,originalMethodsReexecuted=0,actualLiveObservation=False,observationScope="STATIC_CONFIG_VALUES_AND_BOOLEAN_SUPPLIERS_ONLY_NO_NATIVE",newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
