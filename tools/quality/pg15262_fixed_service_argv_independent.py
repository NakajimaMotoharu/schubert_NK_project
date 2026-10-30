"""Independent pure argv original5; retain generated synthetic Code, official filters unchanged."""
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

PIN='330db5435a282e0f6d4c72af0f536871871f2ad20f7fc0760b91bbeebba9a6c8'
POST=data.BASE/'PG15261-fixed-service-argv-five-post-v2'
OUT=data.BASE/'PG15262-fixed-service-argv-independent-v1'
PREFIX='dev/codex/schubert/nk/bootstrap/'
COUNTS={"FixedServiceExecArgumentsTest":5}
EXPECTED={"FixedServiceExecArguments":["1"]}
NATURAL=set()
DOC='documents/300_SS/340_batch・基盤/342_Caddy・systemd・PostgreSQL・Java設定設計.md'

def require(ok,message):
    if not ok:raise ValueError(message)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only monitoring independent')
    p=data.read_checked(POST/'manifest.json',PIN)
    raw=data.read_checked(data.BASE/'PG15259-fixed-service-argv-five-pt-v2/manifest.json','65384096840e6402df1ad4eb1c6590beadca1f917a3a11d44de7a7ad85ca6820')
    registry=data.read_checked(data.BASE/'PG15248-current1729-stop-budget-registry-v1/manifest.json','64e5758fc7b382c109741c9f97d291b746046b6446e6befc4beb07c6c662c8bd')
    require(p['actualExit']==raw['actualExit']==registry['actualExit']==0 and p['source']==raw['source']==registry['source']=='6b53efeec87f3ec36a840dd8e7759656cb4aee5c' and p['execSha256']==raw['execSha256'] and p['sessionIdentity']=='PG15259-ORIGINAL-FIXED-SERVICE-ARGV5','genuine same source/own single exec')
    actual=[];suite_names=set()
    for filename,h in p['xmlHashes'].items():
        value=(POST/filename).read_bytes();require(data.sha(value)==h==raw['xmlHashes'][filename],'original whole XML bytes');root=ET.fromstring(value);simple=root.get('name').rsplit('.',1)[-1];suite_names.add(simple)
        require(int(root.get('tests'))==COUNTS[simple] and all(int(root.get(k))==0 for k in ['failures','errors','skipped']),'all original whole16 FES0')
        for c in root.findall('testcase'):
            require(not list(c),'actual PASS');actual.append((c.get('classname'),c.get('name')))
    require(suite_names==COUNTS.keys() and len(actual)==len(set(actual))==5 and set(actual)=={(c['classname'],c['name']) for c in raw['cases']} and not set(actual)&{(c['classname'],c['name']) for c in registry['cases']},'all16/one suite unique new, never prior1367 replay')
    normal=data.read_checked(data.BASE/'PG14216-typed-marker-guard-six-compile-v1/manifest.json','1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3');hashes=normal['begin']['inputHashes']
    declared=set()
    for simple,count in COUNTS.items():
        path='src/schubert-nk-bootstrap/src/test/java/'+PREFIX+simple+'.java';text=(data.ROOT/path).read_text();require(data.sha((data.ROOT/path).read_bytes())==hashes[path],'whole original normal Test source pin')
        methods=re.findall(r'@Test\s+void\s+([A-Za-z0-9_]+)\s*\(',text);require(len(methods)==count,'all original declared methods');declared.update(('dev.codex.schubert.nk.bootstrap.'+simple,n) for n in methods)
    require(declared==set(actual),'every declared Test ID corresponds to one original actual XML')
    document=subprocess.check_output(['git','show','origin/main:'+DOC],cwd=data.ROOT);doc_head=subprocess.check_output(['git','rev-parse','origin/main'],cwd=data.ROOT,text=True).strip()
    require(all(value in document.decode() for value in ['/usr/bin/setpriv','/usr/bin/java','--reuid/--regid/--groups','init-groups/任意account/任意commandは禁止','NoNewPrivileges']),'approved literal vector/sandbox contract')
    text=(data.ROOT/'src/schubert-nk-bootstrap/src/test/java'/PREFIX/'FixedServiceExecArgumentsTest.java').read_text()
    golden={}
    for role,method,uid,gid,groups,direct,meta,initial,maximum in [('web','rexec001',998,980,'980,982,986','128m','192m','384m','768m'),('api','rexec002',999,981,'980,981,982,986','256m','256m','512m','1024m')]:
        block=text.split('void '+method,1)[1].split('assertEquals(',1)[1].split('actual);',1)[0]
        actual_literals=[json.loads(v) for v in re.findall(r'"(?:\\.|[^"\\])*"',block)]
        expected=['/usr/bin/setpriv','--reuid='+str(uid),'--regid='+str(gid),'--groups='+groups,'--inh-caps=-all','--ambient-caps=-all','--bounding-set=-all','--no-new-privs','/usr/bin/java','--enable-native-access=ALL-UNNAMED','-Dfile.encoding=UTF-8','-Duser.timezone=UTC','-XX:+ExitOnOutOfMemoryError','-XX:MaxDirectMemorySize='+direct,'-XX:MaxMetaspaceSize='+meta,'-XX:ReservedCodeCacheSize=128m','-Xms'+initial,'-Xmx'+maximum,'-Xlog:gc*=info:stdout:time,uptime,level,tags','-cp','/opt/schubert-nk/current/'+role+'/'+role+'.jar:/opt/schubert-nk/current/'+role+'/lib/*','dev.codex.schubert.nk.'+role+'.bootstrap.'+role.title()+'ProcessMain']
        require(actual_literals==expected,'independent complete argv literal vector never production expected')
        golden[role]=expected
    files_call=re.compile(r'(?<![A-Za-z0-9_])Files\s*\.')
    require(not files_call.search(text) and not files_call.search('ServiceConfigFiles.Service.API'),'safe enum not actual file I/O')
    files_negative=[]
    for value in ['Files.readString(x)','java.nio.file.Files.readString(x)','Files.delete(x)']:
        require(files_call.search(value) is not None,'actual Files token remains rejected');files_negative.append(value)
    horizontal={}
    for relative,pin in [('tools/quality/pg15258_fixed_service_argv_five_pt.py','46eff1b10c386b333f23819d2ed0ea2c315de911e36c28d30105d2380f77cca5'),('tools/quality/pg15260_fixed_service_argv_five_post.py','c93a3897c5c8ae1faf04a8c9eab120893ef1076cfba64e614a94b6f3175098a6'),('tools/quality/pg15240_api_stop_budget_eighteen_pt.py','7dbad79917bf23dd9a6791fe0f9c790a03a3405a4112e5ad91a7564ac8edae87'),('tools/quality/pg15222_nonsecret_config_fourteen_pt.py','77a912cdd3db28b096250a985a7bf0512f23b513ee995bdfdf1fed3b156a8d26')]:
        require(data.sha((data.ROOT/relative).read_bytes())==pin,'frozen old and prior scope inputs');horizontal[relative]=pin
    require('Files.' not in (data.ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/bootstrap/ApiStopBudgetTest.java').read_text(),'prior clock suite unaffected by enum alias')
    require('templates(normal)' in (data.ROOT/'tools/quality/pg15222_nonsecret_config_fourteen_pt.py').read_text(),'prior config suite uses explicit public snapshot pin, not this token guard')
    for folder,pin in [('PG15242-api-stop-budget-eighteen-post-v1','242a987a6b39aa0365fa0b479e41ffe12b6b5d01cfc9e49c4f6e3a7945da1001'),('PG15224-nonsecret-config-fourteen-post-v1','5d714d963f1183844fb41f46e41ebd2e3ecece0a37d3c6d7700ca18f9a218c53')]:
        prior=data.read_checked(data.BASE/folder/'manifest.json',pin)
        require(all('$1' not in n for n in prior['physicalClasses']),'prior target inventories have no enum switchmap')
        with zipfile.ZipFile(normal['jars']['bootstrap' if '15224' in folder else 'api']['path']) as jar:
            for name,closure in prior['completeSourceUnitClosure'].items():require({v[:-6] for v in jar.namelist() if v==name+'.class' or v.startswith(name+'$') and v.endswith('.class')}==set(closure),'prior actual Jar closures remain complete')
        verify(prior['invocation'])
    closures={PREFIX+n:sorted([PREFIX+n,*[PREFIX+n+'$'+child for child in nested]]) for n,nested in EXPECTED.items()};names=set().union(*(set(v) for v in closures.values()))
    require(p['completeSourceUnitClosure']==closures and set(p['physicalClasses'])==set(p['executable'])==names and len(names)==2 and p['metadataClasses']==[] and not closures.keys()&registry['fullSourceUnits'].keys(),'one entire new Source/oneCode, no helper parent promotion')
    logical={r['path']:r for r in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']};totals={k:dict(missed=0,covered=0) for k in ['LINE','METHOD','CLASS','BRANCH']}
    with zipfile.ZipFile(normal['jars']['bootstrap']['path']) as jar:
        for name,closure in closures.items():
            require({n[:-6] for n in jar.namelist() if n==name+'.class' or n.startswith(name+'$') and n.endswith('.class')}==set(closure),'all actual nested Jar classfiles')
            local={k:{role:sum(p['executable'][n]['counters'][k][role] for n in closure) for role in ['missed','covered']} for k in totals};unit=p['fullSourceUnits'][name];natural=name in NATURAL
            require(local==unit['totals'] and unit['four100'] is (not natural) and unit['branchNaturallyZero'] is natural and unit['threeCounter100'] is True and all(local[k]['missed']==0 and local[k]['covered']>0 for k in ['LINE','METHOD','CLASS']) and (local['BRANCH']==dict(missed=0,covered=0) if natural else local['BRANCH']['missed']==0 and local['BRANCH']['covered']>0),'entire Source: one nonempty four100 Source')
            for k in totals:
                for role in totals[k]:totals[k][role]+=local[k][role]
            for n in closure:
                value=jar.read(n+'.class');parsed=code.decode(value,n+'.class');require(data.sha(value)==p['physicalClasses'][n] and parsed['methods']==p['sourcePhysicalInventory'][n]['methods'] and any(m['hasCode'] for m in parsed['methods']),'independent actual executable Code, no hidden exclusions')
    require(totals==p['totals']==dict(LINE=dict(missed=0,covered=27),METHOD=dict(missed=0,covered=6),CLASS=dict(missed=0,covered=1),BRANCH=dict(missed=0,covered=8)) and p['missedLines']==[],'actual one-class counters, not union')
    require(len(p['owners'])==2,'only one Main/one whole Test owner rows')
    for path,owned in p['owners'].items():
        expected=canonical(path,logical);require(data.sha((data.ROOT/path).read_bytes())==hashes[path]==owned['sha256'] and all(owned[k]==v for k,v in expected.items()),'actual owner identity')
        if '/src/main/java/' in path:require(expected['canonicalOwner']==expected['canonicalCostOwner']=='WBS-P018-04' and expected['ownershipStatus']=='BASELINE_LOGICAL_REFERENCE','Main logical baseline not current runtime proof')
        else:require(expected['canonicalOwner'] is expected['canonicalCostOwner'] is None and expected['ownershipStatus']=='UNKNOWN','Test UNKNOWN preserved')
    generated=PREFIX+'FixedServiceExecArguments$1'
    require(p['generatedFilteredClasses']==[generated] and p['generatedCrcQualified'] is False,'one generated official-filter scope no measured exec CRC invented')
    value=zipfile.ZipFile(normal['jars']['bootstrap']['path']).read(generated+'.class');parsed=code.decode(value,generated+'.class')
    require(parsed['flags'] & 4096 and len(parsed['methods'])==1 and parsed['methods'][0]['name']=='<clinit>' and parsed['methods'][0]['hasCode'] and b'$SwitchMap$dev$codex$schubert$nk$storage$ServiceConfigFiles$Service' in value,'actual synthetic compiler Code never NoCode')
    require(p['executable'][generated]['crc64'] is None and p['executable'][generated]['bytecodeHasCode'] is True and all(v==dict(missed=0,covered=0) for v in p['executable'][generated]['counters'].values()),'official Analyzer zero counters, not manually excluded executable lines')
    fixed={k:p[k] for k in ['source','cases','execSha256','sessionIdentity','physicalClasses','completeSourceUnitClosure','sourcePhysicalInventory','fullSourceUnits','totals','owners','fixtureHashes','generatedFilteredClasses','generatedCrcQualified','generatedFilterReason']}
    def contract(v):
        require(all(json.dumps(v[k],sort_keys=True)==json.dumps(value,sort_keys=True) for k,value in fixed.items()),'all actual original proof/owner/fixture immutable')
        require(v['tests']==5 and v['suites']==1 and v['targetUnitFour100'] is True and v['strictFour100GateExit']==0 and v['singleSession'] is True and v['crcMismatch']==0 and v['metadataClasses']==[] and v['manualCounterExclusions']==[],'complete source strict four100 actual')
        require(v['ownChildJvmStandardSdkObserved'] is False and v['forcedGcOrHeapDump'] is False and v['externalVmOrTargetProcessObserved'] is False,'genuine own child SDK measurement never remote/native or forced GC')
        require(v['newAccepted']==v['productTestsReexecutedByPost']==0 and v['formalUpdated'] is v['whole451Accepted'] is v['wholeF03Accepted'] is v['oldCoverageTransferred'] is v['coverageExecUnion'] is False and v['effortPercent'] is None and v['canonicalOwnersRemainCandidateNotAccepted'] is v['helperSourceProgramsNotAcceptedByTheseTargetCounters'] is True,'no helper/old/owner/formal/effort transfer')
    contract(p);negative=[]
    for key,value in [('ownChildJvmStandardSdkObserved',True),('forcedGcOrHeapDump',True),('externalVmOrTargetProcessObserved',True),('source','OLD'),('tests',55),('suites',2),('targetUnitFour100',False),('strictFour100GateExit',1),('singleSession',False),('crcMismatch',1),('metadataClasses',list(names)),('manualCounterExclusions',['AlertLifecycle']),('totals',{}),('fullSourceUnits',{}),('fixtureHashes',{'unknown':'0'*64}),('owners',{}),('newAccepted',1),('productTestsReexecutedByPost',1),('formalUpdated',True),('whole451Accepted',True),('wholeF03Accepted',True),('oldCoverageTransferred',True),('coverageExecUnion',True),('effortPercent',100),('canonicalOwnersRemainCandidateNotAccepted',False),('helperSourceProgramsNotAcceptedByTheseTargetCounters',False),('generatedFilteredClasses',[]),('generatedCrcQualified',True),('generatedFilterReason','')]:
        bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad)
        except ValueError:negative.append(key)
        else:raise ValueError('false Web-pool-context56 proof accepted '+key)
    for v in [p,registry]:verify(v['invocation'])
    verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=p['source'],invocation=invocation,postSha256=PIN,tests=5,suites=1,newUniqueMethods=5,sourcePrograms=1,physicalClasses=2,four100SourcePrograms=1,naturallyBranchZeroSourcePrograms=0,naturallyBranchZeroPhysicalClasses=0,totals=totals,semanticNegativeVectors=len(negative),negativeLabels=negative,independentArgvVectors=golden,filesTokenNegativeVectors=len(files_negative),horizontalScopeHashes=horizontal,generatedFilteredClasses=p['generatedFilteredClasses'],generatedHasCodeNotNoCode=True,generatedExecCrcUnmeasured=True,authoritativeDesign=dict(path=DOC,gitRef='origin/main',commit=doc_head,sha256=data.sha(document)),baselineMainOwnerRows=1,unknownTestOwnerRows=1,candidateOwnersNotAccepted=True,originalMethodsReexecuted=0,actualLiveObservation=False,observationScope="STRING_VECTOR_ENUM_VALUE_ONLY_NO_EXEC",newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
