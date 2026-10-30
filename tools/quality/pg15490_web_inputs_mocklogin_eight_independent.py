"""Independent original Web input4/mockLogin4 with immutable public template, no live service."""
import copy
import json
from pathlib import Path
import re
import subprocess
import zipfile
import xml.etree.ElementTree as ET
import classfile_code_metadata as code
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical

POST=('PG15488-web-inputs-mocklogin-eight-post-v1','ce8e46e58d76ed4125ef31505ca9b1fb72e633f3321931ae9e863739ca0ff8a3')
RAW=('PG15487-web-inputs-mocklogin-eight-pt-v2','c839f67e2addf939d531dc12a1e238a0de7130ab8832f2e334a0d669119c5eb1')
REG=('PG15478-current1831-disclosure-registry-v1','1f43f440ac2346b0a6d85fd615902197408fbeceba6a7cf7e79a2bca6d083c59')
OUT=data.BASE/'PG15490-web-inputs-mocklogin-eight-independent-v1'
PREFIX='dev/codex/schubert/nk/web/'
MAINS={"controller/LoginController":"ef9bbc81c79799528840f70f65f55056d08fd1ea0f9fd1a93d8212b946f4e630","bootstrap/WebStartupInputs":"aacdcad0881ad85dee12ca67a92396bcfa4f0aefd91e24c033d7e46d1f840042"}
TESTS={"controller/LoginControllerTest":["5255b728adf851b400649c9f0e9e107d9b8059df4e7a656cbbc6470c01e80a4d",4],"bootstrap/WebStartupInputsTest":["4994569f2e6c1dd29ceff084562a25818294e11be3c41bec23cb938422d84d18",4]}
EXPECTED={'bootstrap/WebStartupInputsTest':{'opsWebInput001CombinesIndependentFixedInputs','opsWebInput002MissingPrivateLocationStopsBeforeSourceRead','opsWebInput003SourceFailureAndConfigAdmissionStayDistinct','opsWebInput004NullContracts'},'controller/LoginControllerTest':{'scr105ApprovedBrandAndPostCsrf','scr106InputsAndNoLeakedCredentials','scr107OnlyMatchingCurrentMessagesAppear','scr108ClosedViewAndControllerBoundary'}}
ROWS={'bootstrap/WebStartupInputs':[(2,7),(1,2),(0,1),(0,0)],'bootstrap/WebStartupInputs$Values':[(0,4),(0,1),(0,1),(0,0)],'controller/LoginController':[(0,2),(0,2),(0,1),(0,0)]}
KINDS=['LINE','METHOD','CLASS','BRANCH']
DOCS=['documents/200_UI/220_画面・認証/222_画面共通・レイアウト設計.md','documents/200_UI/220_画面・認証/226_認証・認可・セッション設計.md','documents/200_UI/260_引継ぎ・監査/264_現行互換性Characterization Test仕様.md','documents/300_SS/310_アプリケーション/313_画面template・controller・form設計.md','documents/300_SS/340_batch・基盤/343_設定file・directory・初期data・migration・切戻し設計.md']
def require(ok,message):
    if not ok:raise ValueError(message)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def wire(v):return json.dumps(v,sort_keys=True)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p,raw,reg=map(read,[POST,RAW,REG])
    require(p['actualExit']==raw['actualExit']==reg['actualExit']==0 and p['source']==raw['source']==reg['source']=='6b53efeec87f3ec36a840dd8e7759656cb4aee5c' and p['execSha256']==raw['execSha256'] and p['sessionIdentity']=='PG15487-WEB-INPUTS-MOCKLOGIN-CURRENT-WHOLE8','genuine original source/run')
    actual=set()
    for filename,pin in p['xmlHashes'].items():
        b=(data.BASE/POST[0]/filename).read_bytes();require(data.sha(b)==pin==raw['xmlHashes'][filename],'original XML')
        root=ET.fromstring(b);name=root.get('name');short=name.replace('.','/').removeprefix(PREFIX)
        require(short in EXPECTED and int(root.get('tests'))==4 and all(int(root.get(k))==0 for k in ['failures','errors','skipped']),'whole4+4/FES0')
        cases=[(c.get('classname'),c.get('name')) for c in root.findall('testcase') if not list(c)]
        require(len(cases)==len(set(cases))==4 and {n for c,n in cases}==EXPECTED[short] and not set(cases)&actual,'all actual original Test IDs');actual|=set(cases)
    require(len(actual)==8 and not actual&{(c['classname'],c['name']) for c in reg['cases']},'new current eight, no old success replay')
    normal=read(('PG14216-typed-marker-guard-six-compile-v1','1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'));hashes=normal['begin']['inputHashes'];texts={}
    for short,(pin,count) in TESTS.items():
        path='src/schubert-nk-web/src/test/java/'+PREFIX+short+'.java';text=(data.ROOT/path).read_text();texts[short]=text
        require(data.sha(text.encode())==hashes[path]==pin and count==4 and set(re.findall(r'(?m)^  void (\w+)\(',text))==EXPECTED[short],'whole declared source')
    login=texts['controller/LoginControllerTest'];inputs=texts['bootstrap/WebStartupInputsTest']
    clauses=['new MockServletContext()','context.register(WebMvcConfiguration.class)','MockMvcBuilders.webAppContextSetup(context)','new DefaultCsrfToken(','"safe-fixture-csrf"','assertEquals(200, response.getStatus())','assertEquals("UTF-8", response.getCharacterEncoding())','assertEquals("schubert NK - ログイン", document.title())','assertEquals("schubert NK", document.selectFirst("h1").text())','form[method=post][action=/login]','form input[name=_csrf][type=hidden]','List.of("error", "locked", "logout", "unknown")','assertNull(resolver.resolveViewName(name, Locale.JAPAN))','assertEquals(405, response.getStatus())','assertEquals("", document.selectFirst(PASSWORD_INPUT_SELECTOR).val())']
    require(all(v in login for v in clauses) and all(v in inputs for v in ['ServiceConfigFiles.Service.WEB','"8080"','"DEBUG"','assertEquals(1, reads.get())','assertEquals(0, reads.get())','new WebStartupInputs(null, ENV)','new WebStartupInputs.Values(null, credentials)','new WebStartupInputs.Values(config, null)']),'independent HTTP/DOM/Map/null/order literals')
    require(not any(v in inputs+login for v in ['.production(','new WebProcessMain(','getConnection(','TemporaryInfrastructureException','WebStartupException','ProcessBuilder','HttpClient']),'no live startup/auth/DB/network/held path')
    boundary=re.compile(r'(?<![A-Za-z0-9_$])Files\s*\.')
    require(not boundary.search(inputs+login) and not boundary.search('ServiceConfigFiles.Contents') and not boundary.search('ServiceConfigFiles.Service.WEB') and all(boundary.search(v) for v in ['Files.readString(path)','java.nio.file.Files.readAllBytes(path)','Files \n .readString(path)']),'Files identifier semantics, not type-name substring')
    old=(data.ROOT/'tools/quality/pg15486_web_inputs_mocklogin_eight_pt.py').read_text()
    require(data.sha(old.encode())=='4b7d6ea44f05d324836c38870b933aac5d93124de878ba22658777dab2e0cc6a' and "'DriverManager','Files.','System.getenv('" in old,'old failed preflight source retained')
    require(r'(?<![A-Za-z0-9_])Files\s*\.' in (data.ROOT/'tools/quality/pg15340_api_startup_inputs_four_pt.py').read_text(),'YKT old API boundary nonapplicable')
    valueproof=read(('PG15462-public-value-eighteen-independent-v1','c5277dc239be507ed1562d039e9ae3c94fd880a10e133566d33033c18a69cc9d'))
    require(valueproof['actualExit']==0 and valueproof['tests']==18 and valueproof['semanticNegativeVectors']==36,'YKT old successful public-output proof not replayed')
    for short in ['maintenance/InspectorSettingsTest','logging/RequestLogDetailsTest','application/question/QuestionReceiptIdTest','application/question/StubAnswerProviderTest']:
        path='src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/'+short+'.java';b=(data.ROOT/path).read_bytes()
        require(data.sha(b)==hashes[path] and 'ServiceConfigFiles.' not in b.decode(),'YKT previous four actual bodies nonapplicable')
    closure={};full={}
    with zipfile.ZipFile(normal['jars']['web']['path']) as jar:
        for short,pin in MAINS.items():
            name=PREFIX+short;path='src/schubert-nk-web/src/main/java/'+name+'.java'
            require(data.sha((data.ROOT/path).read_bytes())==hashes[path]==pin and name not in reg['fullSourceUnits'],'new unchanged target Source')
            group={n[:-6] for n in jar.namelist() if n==name+'.class' or n.startswith(name+'$') and n.endswith('.class')}
            require(group==({name,name+'$Values'} if short=='bootstrap/WebStartupInputs' else {name}),'full actual Jar closure');closure[name]=sorted(group)
            for n in group:
                b=jar.read(n+'.class');parsed=code.decode(b,n+'.class')
                require(data.sha(b)==p['physicalClasses'][n] and parsed['methods']==p['sourcePhysicalInventory'][n]['methods'] and any(m['hasCode'] for m in parsed['methods']),'all Code/Values not NoCode')
                values={k:dict(missed=a,covered=b) for k,(a,b) in zip(KINDS,ROWS[n.removeprefix(PREFIX)])}
                require(p['executable'][n]['counters']==values,'exact independent physical counters')
            totals={k:dict(missed=sum(ROWS[n.removeprefix(PREFIX)][i][0] for n in group),covered=sum(ROWS[n.removeprefix(PREFIX)][i][1] for n in group)) for i,k in enumerate(KINDS)}
            full[name]=dict(physical=sorted(group),totals=totals,four100=False,metadataOnly=False,branchNaturallyZero=True,threeCounter100=short=='controller/LoginController')
        resource='src/schubert-nk-web/src/main/resources/templates/login.html';html=(data.ROOT/resource).read_bytes()
        require(jar.read('templates/login.html')==html and data.sha(html)==hashes[resource]=='ba814efffec4be98d17338cacd63927d50aa552958188ba3fb7db0b77171443a' and p['packagedResourceHashes']=={resource:hashes[resource]},'fixed public template in normal Jar')
        for text in ['<html lang="ja"','<title>schubert NK - ログイン</title>','th:if="'+chr(36)+'{param.error}"','th:if="'+chr(36)+'{param.locked}"','th:if="'+chr(36)+'{param.logout}"','method="post"','type="password"','autocomplete="current-password"']:require(text in html.decode(),'static template contract')
    require(p['completeSourceUnitClosure']==closure and wire(p['fullSourceUnits'])==wire(full) and set(p['physicalClasses'])==set(p['executable'])==set(p['sourcePhysicalInventory'])=={PREFIX+n for n in ROWS},'whole two Source/three Code')
    total={k:dict(missed=sum(v[i][0] for v in ROWS.values()),covered=sum(v[i][1] for v in ROWS.values())) for i,k in enumerate(KINDS)}
    require(p['totals']==total and total=={'LINE':dict(missed=2,covered=13),'METHOD':dict(missed=1,covered=5),'CLASS':dict(missed=0,covered=3),'BRANCH':dict(missed=0,covered=0)},'complete measured gap retained')
    require('config.validateEnvironment();' in (data.ROOT/'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/bootstrap/WebStartupInputs.java').read_text() and not re.search(r'\.validateEnvironment\s*\(',inputs),'uncalled wrapper not excluded')
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    for path,row in p['owners'].items():require(row['sha256']==hashes[path]==data.sha((data.ROOT/path).read_bytes()) and all(row[k]==v for k,v in canonical(path,logical).items()),'two baseline/two UNKNOWN, no inference')
    require(len(p['owners'])==4 and sum(v['ownershipStatus']=='BASELINE_LOGICAL_REFERENCE' for v in p['owners'].values())==2,'actual owner partition')
    missed=[]
    for stage in p['stages']:
        slot=Path(stage['cwd']);require(slot==data.ROOT.parent/'pgpt-runs/PG379/pg15488-web-inputs-mocklogin-eight-post-v1','own passive slot')
        label='passive-held-probe-audit' if 'ReviewedProjectionHeldProbeAudit' in stage['command'] else ('session-identity' if 'CoverageSessionIdentity' in stage['command'] else 'coverage-audit')
        require(stage['actualExit']==0 and stage['timedOut'] is False and data.sha((slot/(label+'.stdout')).read_bytes())==stage['stdoutSha256'] and data.sha((slot/(label+'.stderr')).read_bytes())==stage['stderrSha256'],'genuine passive stage/outputs')
        if label=='coverage-audit':
            require(stage['command'][-3:]==sorted(p['physicalClasses']),'three exact reader names');missed=[line.split('\t')[1:] for line in (slot/(label+'.stdout')).read_text().splitlines() if line.startswith('MISSED_LINE\t')]
        if label=='passive-held-probe-audit':require((slot/(label+'.stdout')).read_text().strip()=='FORBIDDEN_PROBE_HITS=0','four fixed held types absent, not all HOLD解除')
    require(len(missed)==2 and all(v[0]==PREFIX+'bootstrap/WebStartupInputs' and v[2:]==['0','0'] for v in missed),'two wrapper missed lines retained')
    designs={}
    for path in DOCS:
        b=subprocess.check_output(['git','show','origin/main:'+path],cwd=data.ROOT);designs[path]=dict(gitRef='origin/main',sha256=data.sha(b))
        if '/222_' in path or '/226_' in path:require('QA-045/UIC-005' in b.decode() and 'schubert NK - ログイン' in b.decode(),'approved brand, no new approval')
        if '/264_' in path:require('DIF-001' in b.decode() and 'CHR-A01' in b.decode(),'approved difference, not CHR execution')
    fixed={k:p[k] for k in ['source','cases','execSha256','sessionIdentity','physicalClasses','completeSourceUnitClosure','sourcePhysicalInventory','fullSourceUnits','owners','reportedEnvironment','totals','packagedResourceHashes']}
    def contract(v):
        require(all(wire(v[k])==wire(x) for k,x in fixed.items()),'actual source/run/counters/template/owner')
        require(v['tests']==8 and v['suites']==2 and v['targetUnitFour100'] is False and v['strictFour100GateExit']==1 and v['allMeasuredApplicableCountersCovered'] is False and v['singleSession'] is True and v['crcMismatch']==0 and v['metadataClasses']==[] and v['manualCounterExclusions']==[] and v['naturalZeroBranch'] is True and v['branchPercent'] is None,'one natural closed and one source gap, no false four100')
        require(v['cryptoOrKeyOperationsInvoked'] is v['publicNonSecretCanonicalConfigDigestOnly'] is v['ownFreshJvmProviderStateOnly'] is v['actualFilesOpenedByProduct'] is v['immutablePackagedTemplateResourcesRead'] is v['mockMvcOnly'] is True and v['cryptoOperationKind']=='SHA256_PUBLIC_NONSECRET_CANONICAL_CONFIG_NO_KEYS','truthful digest/resource/MockMvc effects')
        require(all(v[k] is False for k in ['actualPrivateFilesOpened','testOwnNewSlotPublicEvidenceWrites','childLocalJcaRegistryRestorationTested','onlyReviewedPureValueSuites','actualSecretKeysLoaded','actualCredentialValuesUsed','actualAuthenticationOrSessionIssued','formalUpdated','whole451Accepted','wholeF03Accepted','oldCoverageTransferred','rootMainInvoked','characterizationAccepted']) and v['forbiddenProductProbeHits']==v['actualBoundSockets']==v['actualBrowserActions']==v['newAccepted']==v['productTestsReexecutedByPost']==0 and v['effortPercent'] is None,'no private/live/native/CHR/credit')
    contract(p);negative=[]
    vectors=[('source','OLD'),('cases',[]),('totals',{}),('fullSourceUnits',{}),('physicalClasses',{}),('owners',{}),('packagedResourceHashes',{}),('tests',9),('suites',3),('targetUnitFour100',True),('strictFour100GateExit',0),('allMeasuredApplicableCountersCovered',True),('singleSession',False),('crcMismatch',1),('metadataClasses',['Values']),('manualCounterExclusions',['validateEnvironment']),('naturalZeroBranch',False),('branchPercent',100),('cryptoOrKeyOperationsInvoked',False),('publicNonSecretCanonicalConfigDigestOnly',False),('actualFilesOpenedByProduct',False),('immutablePackagedTemplateResourcesRead',False),('mockMvcOnly',False),('actualPrivateFilesOpened',True),('testOwnNewSlotPublicEvidenceWrites',True),('actualSecretKeysLoaded',True),('actualCredentialValuesUsed',True),('actualAuthenticationOrSessionIssued',True),('formalUpdated',True),('whole451Accepted',True),('wholeF03Accepted',True),('oldCoverageTransferred',True),('rootMainInvoked',True),('characterizationAccepted',True),('forbiddenProductProbeHits',1),('actualBoundSockets',1),('actualBrowserActions',1),('newAccepted',1),('productTestsReexecutedByPost',1),('effortPercent',100)]
    for key,value in vectors:
        bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad)
        except ValueError:negative.append(key)
        else:raise ValueError('false Web qualification')
    for value in [p,reg,valueproof]:verify(value['invocation'])
    verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=p['source'],invocation=invocation,postSha256=POST[1],tests=8,suites=2,newUniqueMethods=8,sourcePrograms=2,physicalClasses=3,four100SourcePrograms=0,naturallyBranchZeroSourcePrograms=1,incompleteSourcePrograms=1,incompletePhysical=2,totals=total,missedLines=missed,semanticNegativeVectors=len(negative),negativeLabels=negative,httpDomEvidenceBasis='ORIGINAL_LITERAL_ASSERTIONS_AND_GENUINE_PASS_XML_NO_CAPTURED_HTML_SNAPSHOT',originalHttpDomClauses=clauses,publicMockCsrfFixtureOnly=True,packagedResourceHashes=p['packagedResourceHashes'],cryptoOrKeyOperationsInvoked=True,publicNonSecretCanonicalConfigDigestOnly=True,actualSecretKeysLoaded=False,actualCredentialValuesUsed=False,ownFreshJvmProviderStateOnly=True,actualFilesOpenedByProduct=True,immutablePackagedTemplateResourcesRead=True,actualPrivateFilesOpened=False,mockMvcOnly=True,actualBoundSockets=0,actualBrowserActions=0,characterizationAccepted=False,forbiddenProductProbeHits=0,baselineMainOwnerRows=2,unknownTestOwnerRows=2,authoritativeDesigns=designs,oldToolPreflightFailedBeforeProduct=True,relatedBug='BUG-2131',relatedYkt='YKT-1878',originalMethodsReexecuted=0,actualLiveObservation=False,newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(dict(actualExit=0,tests=8,semanticNegativeVectors=len(negative),incompleteSourcePrograms=1,naturallyBranchZeroSourcePrograms=1)))
if __name__=='__main__':main()
