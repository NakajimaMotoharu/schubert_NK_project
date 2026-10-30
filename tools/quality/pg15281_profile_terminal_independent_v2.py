"""Independent whole Profile/Terminal14; literal oracles, full physical/NoCode and passive own-exec native absence."""
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

PIN='0dde7b7d8ff705d5466522d43072e16f294838a5ec4cbfdc144c7f5e33af79f5'
POST=data.BASE/'PG15278-profile-terminal-fourteen-post-v1'
OUT=data.BASE/'PG15281-profile-terminal-independent-v2'
PREFIX='dev/codex/schubert/nk/bootstrap/'
COUNTS={"FixedNativeCoverageProfileTest":5,"TerminalNativeCoverageProfileTest":4,"FixedNativeCoverageTerminalTest":5}
EXPECTED={"FixedNativeCoverageProfile":["Phase","TerminalRole"],"FixedNativeCoverageTerminal":["Factory"]}
NATURAL=set()
METADATA={PREFIX+'FixedNativeCoverageTerminal$Factory'}
DOC='documents/300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md'

def require(ok,message):
    if not ok:raise ValueError(message)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only monitoring independent')
    p=data.read_checked(POST/'manifest.json',PIN)
    raw=data.read_checked(data.BASE/'PG15276-profile-terminal-fourteen-pt-v1/manifest.json','5904cdcde28f372b55148118f1e28a52ab8e282c1b9b473079d76c07316cfa1d')
    registry=data.read_checked(data.BASE/'PG15266-current1734-fixed-argv-registry-v1/manifest.json','e4a78ab9db65ca49e2f673682e37fe3bf768b031d119e7d5a4ad367f8024952e')
    require(p['actualExit']==raw['actualExit']==registry['actualExit']==0 and p['source']==raw['source']==registry['source']=='6b53efeec87f3ec36a840dd8e7759656cb4aee5c' and p['execSha256']==raw['execSha256'] and p['sessionIdentity']=='PG15276-ORIGINAL-PROFILE-TERMINAL14','genuine same source/own single exec')
    actual=[];suite_names=set()
    for filename,h in p['xmlHashes'].items():
        value=(POST/filename).read_bytes();require(data.sha(value)==h==raw['xmlHashes'][filename],'original whole XML bytes');root=ET.fromstring(value);simple=root.get('name').rsplit('.',1)[-1];suite_names.add(simple)
        require(int(root.get('tests'))==COUNTS[simple] and all(int(root.get(k))==0 for k in ['failures','errors','skipped']),'all original whole16 FES0')
        for c in root.findall('testcase'):
            require(not list(c),'actual PASS');actual.append((c.get('classname'),c.get('name')))
    require(suite_names==COUNTS.keys() and len(actual)==len(set(actual))==14 and set(actual)=={(c['classname'],c['name']) for c in raw['cases']} and not set(actual)&{(c['classname'],c['name']) for c in registry['cases']},'all16/one suite unique new, never prior1367 replay')
    normal=data.read_checked(data.BASE/'PG14216-typed-marker-guard-six-compile-v1/manifest.json','1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3');hashes=normal['begin']['inputHashes']
    declared=set()
    for simple,count in COUNTS.items():
        path='src/schubert-nk-bootstrap/src/test/java/'+PREFIX+simple+'.java';text=(data.ROOT/path).read_text();require(data.sha((data.ROOT/path).read_bytes())==hashes[path],'whole original normal Test source pin')
        methods=re.findall(r'@Test\s+void\s+([A-Za-z0-9_]+)\s*\(',text);require(len(methods)==count,'all original declared methods');declared.update(('dev.codex.schubert.nk.bootstrap.'+simple,n) for n in methods)
    require(declared==set(actual),'every declared Test ID corresponds to one original actual XML')
    fixture='src/schubert-nk-bootstrap/src/test/java/'+PREFIX+'FixedServiceIdentityTest.java'
    require(data.sha((data.ROOT/fixture).read_bytes())==hashes[fixture]==raw['begin']['testSourceHashes'][str(data.ROOT/fixture)] and not any(c.rsplit('.',1)[-1]=='FixedServiceIdentityTest' for c,n in actual),'whole Fixture source compile-only; no fixture Test methods replay')
    document=subprocess.check_output(['git','show','origin/main:'+DOC],cwd=data.ROOT);doc_head=subprocess.check_output(['git','rev-parse','origin/main'],cwd=data.ROOT,text=True).strip()
    require(all(value in document.decode() for value in ['SSC234','TERMINAL→callback/entry/診断帰還→CLOSING/marker→終了','agent無しI/O0','同session累積union0','設計公開は新sourcehost/native/正式の受入ではない']),'approved ordered capture and no-authority/union contract')
    prefix='-javaagent:/opt/pgpt-tools-pg390/jacoco-agent.jar=output=none,append=false,dumponexit=false,sessionid='
    inv='1234567890abcdef1234567890abcdef';golden={}
    for simple in ['FixedNativeCoverageProfileTest','TerminalNativeCoverageProfileTest']:
        text=(data.ROOT/'src/schubert-nk-bootstrap/src/test/java'/PREFIX/(simple+'.java')).read_text()
        literal=''.join(json.loads(v) for v in re.findall(r'"(?:\\.|[^"\\])*"',text.split('private static final String PREFIX =',1)[1].split(';',1)[0]))
        require(literal==prefix and '1234567890abcdef1234567890abcdef' in text,'independent exact literal prefix/invocation not actual native session')
    for service in ['API','WEB']:
        for phase in ['root','ordinary']:golden[service+'-'+phase]=prefix+service+'-'+inv+'-'+phase
    for role in ['INSPECTOR','BOOTSTRAP']:golden[role]=prefix+role+'-'+inv+'-ordinary'
    base=data.ROOT/'src/schubert-nk-bootstrap/src/test/java'/PREFIX
    require('fb5b0036a0899ea97edfa0fc2c7985b55f3f7c5695028163e5e60d4f3cf6075d' in (base/'FixedNativeCoverageProfileTest.java').read_text(),'independent immutable vendor agent pin literal')
    terminal=(base/'FixedNativeCoverageTerminalTest.java').read_text()
    require('List.of('+chr(10)+'            "snapshot", INV + ".terminal.exec", "entry-return", "snapshot", INV + ".closing.exec")' in terminal and 'assertEquals(5, calls.size())' in terminal,'literal independent terminal-entry-return-closing order and no duplicate snapshot')
    require(all(v in terminal for v in ['assertFalse(nativeDefault.terminal())','assertFalse(nativeDefault.closing())','foreign.join(5000)','second.join(5000)','assertThrows(IOException.class, early::closing)'] if v!='assertThrows(IOException.class, early::closing)'),'default inactive/own thread assertions')
    passive=p['passiveNativeBoundaryAbsence'];expected_prefixes=[PREFIX+'NativeCoveragePrivateFile',PREFIX+'FixedNativeCoverageCheckpoint$PublicAgent',PREFIX+'FixedServiceIdentity$NativeQuery']
    require(passive['prefixes']==expected_prefixes and passive['sessionIdentity']==p['sessionIdentity'] and passive['execSha256']==p['execSha256'] and passive['productClassesLoaded'] is passive['productMethodsInvoked'] is False and passive['allPrefixesNormalJarPresent'] is True and passive['toolNegativeExpectedExits']==[1,1],'passive exact own exec no Product invocation')
    require(len(passive['rows'])==3 and {r[1] for r in passive['rows']}==set(expected_prefixes) and all(r[0]=='OWNED_PROFILE_NATIVE_PREFIX_NO_TRUE_PROBES' and r[2:] == ['0','0'] for r in passive['rows']),'all three native boundaries absent, not a native qualification')
    require(data.sha((data.ROOT/passive['readerSourcePath']).read_bytes())==passive['readerSourceSha256'],'fixed reviewed passive reader source')
    slot=data.ROOT.parent/'pgpt-runs/PG379/pg15278-profile-terminal-fourteen-post-v1'
    require(data.sha((slot/'passive-classes/OwnedProfileNativeProbeAbsence.class').read_bytes())==passive['readerClassSha256'],'actual reader compiled class')
    for label,stage,expected in zip(['passive-compile','passive-native-absence','passive-wrong-session','passive-missing-args'],p['stages'][-4:],[0,0,1,1]):
        require(stage['actualExit']==expected and not stage['timedOut'] and data.sha((slot/(label+'.stdout')).read_bytes())==stage['stdoutSha256'] and data.sha((slot/(label+'.stderr')).read_bytes())==stage['stderrSha256'],'actual passive stage outcomes and saved bytes')
    require(raw['begin']['environment']=={'LANG':'C.UTF-8','PATH':'/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin:/usr/bin:/bin'} and len([v for v in raw['stages'][1]['command'] if v.startswith('-javaagent:')])==1 and not any(v.startswith('-javaagent:/opt/pgpt-tools-pg390/') for v in raw['stages'][1]['command']),'own JVM default parse cannot select real reserved native profile')
    closures={PREFIX+n:sorted([PREFIX+n,*[PREFIX+n+'$'+child for child in nested]]) for n,nested in EXPECTED.items()};names=set().union(*(set(v) for v in closures.values()))
    require(p['completeSourceUnitClosure']==closures and set(p['physicalClasses'])==names and set(p['executable'])==names-METADATA and len(names)==5 and set(p['metadataClasses'])==METADATA and not closures.keys()&registry['fullSourceUnits'].keys(),'one entire new Source/oneCode, no helper parent promotion')
    logical={r['path']:r for r in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']};totals={k:dict(missed=0,covered=0) for k in ['LINE','METHOD','CLASS','BRANCH']}
    with zipfile.ZipFile(normal['jars']['bootstrap']['path']) as jar:
        for name,closure in closures.items():
            require({n[:-6] for n in jar.namelist() if n==name+'.class' or n.startswith(name+'$') and n.endswith('.class')}==set(closure),'all actual nested Jar classfiles')
            local={k:{role:sum(p['executable'][n]['counters'][k][role] for n in closure if n not in METADATA) for role in ['missed','covered']} for k in totals};unit=p['fullSourceUnits'][name];natural=name in NATURAL
            require(local==unit['totals'] and unit['four100'] is (not natural) and unit['branchNaturallyZero'] is natural and unit['threeCounter100'] is True and all(local[k]['missed']==0 and local[k]['covered']>0 for k in ['LINE','METHOD','CLASS']) and (local['BRANCH']==dict(missed=0,covered=0) if natural else local['BRANCH']['missed']==0 and local['BRANCH']['covered']>0),'entire Source: one nonempty four100 Source')
            for k in totals:
                for role in totals[k]:totals[k][role]+=local[k][role]
            for n in closure:
                value=jar.read(n+'.class');parsed=code.decode(value,n+'.class');require(data.sha(value)==p['physicalClasses'][n] and parsed['methods']==p['sourcePhysicalInventory'][n]['methods'] and (not any(m['hasCode'] for m in parsed['methods']) if n in METADATA else any(m['hasCode'] for m in parsed['methods'])),'independent actual executable Code, no hidden exclusions')
    counter_expected={'LINE':{'missed':0,'covered':89},'METHOD':{'missed':0,'covered':22},'CLASS':{'missed':0,'covered':4},'BRANCH':{'missed':0,'covered':64}}
    def counter_contract(v):require(json.dumps(v,sort_keys=True)==json.dumps(counter_expected,sort_keys=True),'named four roles and typed values')
    counter_contract(totals);counter_contract(p['totals']);require(p['missedLines']==[],'no missed executable line')
    role_negative=[]
    for role,value in [('LINE',90),('METHOD',23),('CLASS',64),('BRANCH',65),('CLASS',True)]:
        wrong=copy.deepcopy(counter_expected);wrong[role]['covered']=value
        try:counter_contract(wrong)
        except ValueError:role_negative.append(role+'-'+str(value))
        else:raise ValueError('counter role alias accepted')
    require(len(p['owners'])==5,'only one Main/one whole Test owner rows')
    for path,owned in p['owners'].items():
        expected=canonical(path,logical);require(data.sha((data.ROOT/path).read_bytes())==hashes[path]==owned['sha256'] and all(owned[k]==v for k,v in expected.items()),'actual owner identity')
        if '/src/main/java/' in path:require(expected['canonicalOwner']==expected['canonicalCostOwner']=='WBS-P018-08' and expected['ownershipStatus']=='BASELINE_LOGICAL_REFERENCE','Main logical baseline only')
        else:require(expected['canonicalOwner'] is expected['canonicalCostOwner'] is None and expected['ownershipStatus']=='UNKNOWN','Test owner unknown retained')
    require(p['metadataZeroCountersVerified'] is True and p['sourcePhysicalInventory'][next(iter(METADATA))]['flags']==1536 and not any(v['hasCode'] for v in p['sourcePhysicalInventory'][next(iter(METADATA))]['methods']),'genuine NoCode interface not a hidden generated Code')
    fixed={k:p[k] for k in ['source','cases','execSha256','sessionIdentity','physicalClasses','completeSourceUnitClosure','sourcePhysicalInventory','fullSourceUnits','totals','owners','fixtureHashes','passiveNativeBoundaryAbsence','metadataZeroCountersVerified']}
    def contract(v):
        require(all(json.dumps(v[k],sort_keys=True)==json.dumps(value,sort_keys=True) for k,value in fixed.items()),'all actual original proof/owner/fixture immutable')
        require(v['tests']==14 and v['suites']==3 and v['targetUnitFour100'] is True and v['strictFour100GateExit']==0 and v['singleSession'] is True and v['crcMismatch']==0 and set(v['metadataClasses'])==METADATA and v['manualCounterExclusions']==[],'complete source strict four100 actual')
        require(v['ownChildJvmStandardSdkObserved'] is False and v['forcedGcOrHeapDump'] is False and v['externalVmOrTargetProcessObserved'] is False,'genuine own child SDK measurement never remote/native or forced GC')
        require(v['newAccepted']==v['productTestsReexecutedByPost']==0 and v['formalUpdated'] is v['whole451Accepted'] is v['wholeF03Accepted'] is v['oldCoverageTransferred'] is v['coverageExecUnion'] is False and v['effortPercent'] is None and v['canonicalOwnersRemainCandidateNotAccepted'] is v['helperSourceProgramsNotAcceptedByTheseTargetCounters'] is True,'no helper/old/owner/formal/effort transfer')
    contract(p);negative=[]
    for key,value in [('ownChildJvmStandardSdkObserved',True),('forcedGcOrHeapDump',True),('externalVmOrTargetProcessObserved',True),('source','OLD'),('tests',55),('suites',2),('targetUnitFour100',False),('strictFour100GateExit',1),('singleSession',False),('crcMismatch',1),('metadataClasses',[]),('manualCounterExclusions',['AlertLifecycle']),('totals',{}),('fullSourceUnits',{}),('fixtureHashes',{'unknown':'0'*64}),('owners',{}),('newAccepted',1),('productTestsReexecutedByPost',1),('formalUpdated',True),('whole451Accepted',True),('wholeF03Accepted',True),('oldCoverageTransferred',True),('coverageExecUnion',True),('effortPercent',100),('canonicalOwnersRemainCandidateNotAccepted',False),('helperSourceProgramsNotAcceptedByTheseTargetCounters',False),('passiveNativeBoundaryAbsence',{}),('metadataZeroCountersVerified',False)]:
        bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad)
        except ValueError:negative.append(key)
        else:raise ValueError('false Web-pool-context56 proof accepted '+key)
    horizontal={}
    for relative,pin in [('tools/quality/pg15280_profile_terminal_independent.py','0442fab7ad76fc113006ae6ae3f20dcc2cf73ac9717ba22eded4516d0a9b3253'),('tools/quality/pg15262_fixed_service_argv_independent.py','eb9d66670ba4325605db8eab9447e06eb5d8512b0cf6df3087f79d218de72a02'),('tools/quality/pg15245_api_stop_budget_independent_v2.py','ec1b17d2b26b0367b1a77d6a98f2bfefa54b56c84ce5ac22992525232078d3e9')]:
        require(data.sha((data.ROOT/relative).read_bytes())==pin,'frozen readers exact byte');horizontal[relative]=pin
    for folder,pin in [('PG15262-fixed-service-argv-independent-v1','ebe40fe36f407faee91e486ca18901afad67b7c0114fae51e0c223e019a4fbcf'),('PG15245-api-stop-budget-independent-v2','b05a4e1dc4f900e3a0eadc455afdec0f775757f60886d40992a3539a82053f36')]:
        previous=data.read_checked(data.BASE/folder/'manifest.json',pin)
        require(previous['actualExit']==0 and previous['totals']['CLASS']==dict(missed=0,covered=1),'prior scopes have one measured class no64 collision');verify(previous['invocation'])
    for v in [p,registry]:verify(v['invocation'])
    verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=p['source'],invocation=invocation,postSha256=PIN,tests=14,suites=3,newUniqueMethods=14,sourcePrograms=2,physicalClasses=5,four100SourcePrograms=2,naturallyBranchZeroSourcePrograms=0,naturallyBranchZeroPhysicalClasses=0,metadataOnlyPhysical=1,totals=totals,semanticNegativeVectors=len(negative),negativeLabels=negative,independentProfileGoldenVectors=golden,independentTerminalOrder=['snapshot',inv+'.terminal.exec','entry-return','snapshot',inv+'.closing.exec'],passiveNativeBoundaryAbsence=passive,passiveOriginalProductReplay=0,authoritativeDesign=dict(path=DOC,gitRef='origin/main',commit=doc_head,sha256=data.sha(document)),horizontalScopeHashes=horizontal,counterRoleNegativeVectors=len(role_negative),counterRoleNegativeLabels=role_negative,toolBug='BUG-2124',horizontalCheck='YKT-1871',baselineMainOwnerRows=2,unknownTestOwnerRows=3,candidateOwnersNotAccepted=True,originalMethodsReexecuted=0,actualLiveObservation=False,observationScope="PROFILE_STRING_AND_MAP_AGENT_EXPORT_CALLBACKS_ONLY_NO_NATIVE",newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
