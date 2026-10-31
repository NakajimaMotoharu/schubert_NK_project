"""Independent fixed twelve-property vectors and original seven; no Product replay."""
import copy
import json
import re
import subprocess
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg16430_maintenance_stop_parser_eight_pt import SOURCE,NAME,ENUM,CLOSURES,FIXTURE,FIXTURE_SHA
POST=('PG16432-maintenance-stop-parser-eight-post-v1','db29d2f25d7947d79da7ec819066cb0a6403041d8f01ad4927b57a9661f24851')
RAW=('PG16430-maintenance-stop-parser-eight-pt-v1','847d6fd8c22428c096c216efda4a7089abf61bdfb50716ccd100c0a15ea3bcaf')
PREV=('PG16420-current2189-process-scope-registry-v1','4346e90455e1497c5317a5388776ef8a8e519fc25262d114b79bec2e0936cbad')
OUT=data.BASE/'PG16434-maintenance-stop-parser-eight-independent-v1'
METHODS=['mstop001FixedNamesAndIndependentTerminalVectors','mstop002MissingDuplicateUnknownAndSeparators','mstop003ByteBoundsNullAndOriginalOwnership','mstop004FixedPlacementAndNonTerminalStates','mstop005InvocationAndUnsignedTimestampDomains','mstop006AbaAndAllFieldChangesStayUnmatched','mstop007IndependentParallelAndNoAmbientAuthorization']
def require(ok,why):
    if not ok:raise ValueError(why)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def strings(value):return [json.loads(v) for v in re.findall(r'"(?:[^"\\]|\\.)*"',value)]
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p,raw,old=[read(v) for v in [POST,RAW,PREV]];require(all(v['actualExit']==0 and v['source']==SOURCE for v in [p,raw,old]),'same source/run')
    original=data.ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/MaintenanceStopSnapshotTest.java';body=original.read_bytes();text=body.decode()
    require(data.sha(body)==raw['begin']['testSourceHashes'][str(original)]=='6b33e77253864cbfafb6327be73022e2216eeaef9a2c3915c274604b950cfd39' and re.findall(r'@Test\s+void\s+(\w+)\(',text)==METHODS,'whole original seven')
    fixture=FIXTURE.read_bytes();require(data.sha(fixture)==raw['begin']['testSourceHashes'][str(FIXTURE)]==FIXTURE_SHA,'new independent fixture fixed bytes')
    new_method='observed001FixedPropertyOrderPreservesColdAndShuffledLiveLiterals';require(re.findall(r'@Test\s+void\s+(\w+)\(',fixture.decode())==[new_method],'one new quality method')
    expected={('dev.codex.schubert.nk.batch.platform.MaintenanceStopSnapshotTest',n) for n in METHODS}|{('dev.codex.schubert.nk.batch.platform.MaintenanceObservedValuesContractTest',new_method)};actual=[];xml_suites=[]
    for file,pin in p['xmlHashes'].items():
        blob=(data.BASE/POST[0]/file).read_bytes();require(data.sha(blob)==pin,'original XML');xml=ET.fromstring(blob);xml_suites.append(xml.get('name'));require(all(xml.get(k)=='0' for k in ['failures','errors','skipped']),'FES0')
        for case in xml.findall('testcase'):require(not list(case),'no nonpass');actual.append((case.get('classname'),case.get('name')))
    require(len(actual)==8 and set(actual)==expected and len(set(xml_suites))==2 and not expected&{(v['classname'],v['name']) for v in old['cases']},'exact original seven/new one and two suites')
    oracles=[
        ['assertEquals(8, MaintenanceUnit.values().length)','"/system.slice/" + NAMES.get(i)','Collections.rotate(lines, 1)'],
        ['"Unknown" + line','"no-equals\\n"','"=empty\\n"','line + "=extra\\n"'],
        ['List.of(0, 13, 127, 128, 255)','assertEquals(2048, longest.length())','"caller retains its original byte ownership"'],
        ['"not-found", "masked", "error"','"4294967296"','assertFalse(parse(replace(entry.getKey(), value)).quiescent())'],
        ['"18446744073709551615"','"18446744073709551616"','"1".repeat(21)'],
        ['replace("StateChangeTimestampMonotonic", "1")','replace("MainPID", "1")','original.matches(null)'],
        ['Executors.newFixedThreadPool(8)','i < 64','pure parsing makes no root/process/startup admission','Thread.currentThread().isInterrupted()']]
    require(all(all(t in text for t in row) for row in oracles),'independent original fixed oracles')
    f=fixture.decode();keys=['Id','LoadState','ActiveState','SubState','Job','MainPID','ControlPID','Slice','Delegate','ControlGroup','InvocationID','StateChangeTimestampMonotonic']
    expected_rows=[['caddy.service','loaded','inactive','dead','','0','0','system.slice','no','','','0'],['caddy.service','loaded','active','running','17','23','7','system.slice','no','/system.slice/caddy.service','0123456789abcdef0123456789abcdef','18446744073709551615']]
    for variable,expected_variable,values in zip(['cold','shuffled'],['expectedCold','expectedLive'],expected_rows):
        match=re.search(r'String '+variable+r'\s*=(.*?);',f,re.S);require(match is not None,'manual input declaration')
        value=''.join(strings(match.group(1)));lines=value.splitlines();pairs=[line.split('=',1) for line in lines]
        require(len(pairs)==len({k for k,v in pairs})==12 and set(k for k,v in pairs)==set(keys),'independent closed twelve fields')
        expected_literal=re.search(r'List<String> '+expected_variable+r'\s*=\s*List.of\((.*?)\);',f,re.S);require(expected_literal is not None,'manual expected declaration')
        require(strings(expected_literal.group(1))==values==[dict(pairs)[key] for key in keys],'independent SS order and unnormalized fields')
    design=list((data.ROOT/'documents/300_SS/340_batch・基盤').glob('343_*.md'));require(len(design)==1,'unique approved SS343');relative=str(design[0].relative_to(data.ROOT));approved=design[0].read_bytes();require(approved==subprocess.check_output(['git','show','origin/main:'+relative],cwd=data.ROOT),'approved same byte')
    counts={n:{k:dict(covered=v,missed=0) for k,v in rows} for n,rows in [(NAME,[('LINE',58),('METHOD',12),('CLASS',1),('BRANCH',56)]),(ENUM,[('LINE',14),('METHOD',4),('CLASS',1),('BRANCH',0)])]}
    def contract(v):
        require(type(v['actualExit']) is int and v['actualExit']==0 and v['source']==SOURCE and v['originalManifestSha256']==RAW[1],'actual current binding')
        require((v['tests'],v['suites'],v['newTestIds'],v['targetSourceUnits'],v['originalOrdinaryMethods'],v['newQualityFixtureMethods'])==(8,2,1,2,7,1),'mixed original7/quality1 domains')
        require(v['completeSourceUnitClosure']==CLOSURES and set(v['physicalClasses'])=={NAME,ENUM} and set(v['fullSourceUnits'])==set(v['executable'])=={NAME,ENUM} and v['metadataClasses']==[],'two full Code keysets')
        require(all(v['fullSourceUnits'][n]['totals']==v['executable'][n]['counters']==rows for n,rows in counts.items()),'actual counters, all miss0')
        require(v['totals']=={k:dict(covered=sum(row[k]['covered'] for row in counts.values()),missed=0) for k in ['LINE','METHOD','CLASS','BRANCH']},'independent whole sums')
        require(v['fullSourceUnits'][NAME]['four100'] is True and v['fullSourceUnits'][ENUM]['branchNaturallyZero'] is v['fullSourceUnits'][ENUM]['threeCounter100'] is True and v['targetUnitFour100'] is False and v['strictFour100GateExit']==1 and v['allMeasuredApplicableCountersCovered'] is True,'natural B0 not fabricated strict four')
        require(v['singleSession'] is True and v['crcMismatch']==0 and v['execSha256']==raw['execSha256'] and v['manualCounterExclusions']==[],'one original exec')
        require(v['syntheticStateFieldsOnly'] is v['mixedOriginalAndNewQualityFixture'] is True and v['normalOrdinaryTestSourceDomain'] is False and v['qualityFixtureSha256']==FIXTURE_SHA,'quality fixture not ordinary declarations')
        require(v['ownThreadCount'] is None and v['declaredOwnWorkerPoolSize']==8 and v['ownTaskCount']==64 and v['productExternalProcessesStarted']==0,'declared own workers only')
        require(all(v[k] is False for k in ['cryptoOrKeyOperationsInvoked','actualSecretKeysLoaded','actualCredentialValuesUsed','actualFilesOpenedByProduct','rootMainInvoked','oldCoverageTransferred','formalUpdated','whole451Accepted']) and v['effortPercent'] is None,'no authority/formal transfer')
    contract(p);labels=[]
    for key,value in [('actualExit',True),('source','OLD'),('originalManifestSha256','0'*64),('tests',7),('suites',1),('newTestIds',0),('targetSourceUnits',1),('originalOrdinaryMethods',8),('newQualityFixtureMethods',0),('completeSourceUnitClosure',{}),('physicalClasses',{}),('fullSourceUnits',{}),('executable',{}),('metadataClasses',[ENUM]),('totals',{}),('targetUnitFour100',True),('strictFour100GateExit',0),('allMeasuredApplicableCountersCovered',False),('singleSession',False),('crcMismatch',1),('manualCounterExclusions',[ENUM]),('syntheticStateFieldsOnly',False),('mixedOriginalAndNewQualityFixture',False),('normalOrdinaryTestSourceDomain',True),('qualityFixtureSha256','0'*64),('ownThreadCount',8),('productExternalProcessesStarted',1),('oldCoverageTransferred',True),('formalUpdated',True),('effortPercent',100)]:
        bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false parser qualification '+key)
    for v in [p,old]:verify(v['invocation'])
    verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir()
    result=dict(actualExit=0,source=SOURCE,invocation=invocation,postSha256=POST[1],rawSha256=RAW[1],tests=8,suites=len(set(xml_suites)),semanticNegativeVectors=len(labels),negativeLabels=labels,independentOracleVectors=9,originalOrdinaryMethods=7,newQualityFixtureMethods=1,newSourcePrograms=1,existingSourceProofsReplaced=1,physicalClasses=2,metadataPhysicalClasses=0,four100SourcePrograms=1,naturallyBranchZeroSourcePrograms=1,wholeSourceIncompleteCount=0,approvedDesignHashes={relative:data.sha(approved)},qualityFixtureSha256=FIXTURE_SHA,postStdoutSuiteErratum=dict(bug='BUG-2177',originalDisplay=1,actualManifestAndXml=2,oldStdoutRetained=True),productTestsReexecuted=0,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None)
    data.write(OUT/'manifest.json',result);print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(dict(actualExit=result['actualExit'],tests=result['tests'],suites=result['suites'])))
if __name__=='__main__':main()
