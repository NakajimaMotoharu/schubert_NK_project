"""Independent18 whole suites/six Sources; only own public evidence and identifier entropy."""
import copy
from collections import Counter
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

POST=('PG15460-public-value-eighteen-post-v1','b316e19d53bb71007e4442a6d835feedfae2a55201197fe89e4478796427e5b8')
RAW=('PG15458-public-value-eighteen-pt-v1','40f71060cfd3baf4ab456250e4062654f5e58a7667133caf8dd45c645f875a28')
REG=('PG15442-current1810-auth-context-codec-registry-v1','e94941427a78ea47d0b82eabbcffd19400909efb16b939c3216a30cc6aed897c')
OUT=data.BASE/'PG15462-public-value-eighteen-independent-v1'
PREFIX='dev/codex/schubert/nk/api/'
MAIN_PINS={"maintenance/InspectorSettings":"5fe7308a07bd1647aea4981749e348c44913e1f5df73159865f502be98bc24ae","logging/RequestLogDetails":"96467f5d3475d8e2fe5fe02124ce7d8571403f9141527a87ea880c9640117aa1","application/question/QuestionReceiptId":"32e2d84c19a05c4655c6911e0b27374c13fb6b4d3ef09ead40e60877305d5d2f","application/question/QuestionReceiptIdGenerator":"a4cb4c03f5dbdb225632d6abf4c2465fbb414ce09b0894f0b6649c83c7bc145d","application/question/StubAnswerProvider":"719addcd16754a2179b04a31ec7a17130c912fef362adbcbcc347ec523f4816f","application/question/AnswerResult":"bfa7c5a2827d5c97579a030df72997f928f5817b6d68ea9b0d918d88aef3fae6"}
TEST_PINS={"maintenance/InspectorSettingsTest":["0184124b8740a45322de685b4b9be4ff6705818dd259a5c15db78ef47de6faff",3],"logging/RequestLogDetailsTest":["c266b46400912485549e57220b73e94cae7ef4304d13871afeee7f7f5248e184",2],"application/question/QuestionReceiptIdTest":["95ecae1fb73ba439d3150b37083f087fde857f49dfa7a1c0e67f5bf4ac69e1c3",8],"application/question/StubAnswerProviderTest":["ac4d482aeaa66f017973eddcff1858990a7ef4d3f07ca03138c1a1ebf6f2dceb",5]}
ROWS={'maintenance/InspectorSettings':(19,4,1,12),'logging/RequestLogDetails':(47,4,1,23),'application/question/QuestionReceiptId':(7,3,1,2),'application/question/QuestionReceiptIdGenerator':(14,3,1,6),'application/question/StubAnswerProvider':(5,2,1,0),'application/question/AnswerResult':(5,2,1,0)}
EXPECTED={
'maintenance/InspectorSettingsTest':{'validSnapshot','invalidSettings','sharedValidation'},
'logging/RequestLogDetailsTest':{'allowedScalarsAndRolesMatchLiteralJson','unsafeMalformedDuplicateAndWrongTypesAreRejected'},
'application/question/QuestionReceiptIdTest':{'exactAlphabet','lengthBoundaries','characterBoundaries','independentRandomVector','randomFailure','nullAndFactory','concurrentCalls','equalityAndPublicEvidence'},
'application/question/StubAnswerProviderTest':{'emptyAnswerAndClock','nullContracts','clockFailures','resultValueAndRedaction','concurrentCallsAndEvidence'}}
OUTPUTS={
'target/question-receipt-traces/PT-QST-RID008.txt':'forward=0123456789ABCDEFGHJKMNPQRS\nreverse=ZYXWVTSRQPNMKJHGFEDCBA9876\nlength=26\nalphabetSize=32\nrandomDrawsPerId=26\nownerOrTimeInput=false\n',
'target/question-stub-traces/PT-ASY-STB005.txt':'provider=STUB\nanswerLength=0\nclockReadsPerCall=1\nconcurrentCalls=64\nuniqueClockValues=64\nexternalCalls=0\nrawBodySaved=false\n'}
DOCS=['documents/300_SS/310_アプリケーション/312_処理sequence・method・例外・transaction設計.md','documents/300_SS/330_データ・ファイル/331_DB物理・DDL・index・権限設計.md','documents/300_SS/350_運用・品質/351_Log・metric・alert・error code設計.md','documents/300_SS/340_batch・基盤/343_設定file・directory・初期data・migration・切戻し設計.md']
def require(ok,message):
    if not ok:raise ValueError(message)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def wire(v):return json.dumps(v,sort_keys=True)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p,raw,reg=read(POST),read(RAW),read(REG)
    require(p['actualExit']==raw['actualExit']==reg['actualExit']==0 and p['source']==raw['source']==reg['source']=='6b53efeec87f3ec36a840dd8e7759656cb4aee5c' and p['execSha256']==raw['execSha256'] and p['sessionIdentity']=='PG15458-PUBLIC-VALUE-CURRENT-WHOLE18','true original current source/session')
    cases=set()
    for filename,pin in p['xmlHashes'].items():
        b=(data.BASE/POST[0]/filename).read_bytes();require(data.sha(b)==pin==raw['xmlHashes'][filename],'actual XML')
        root=ET.fromstring(b);short=root.get('name').replace('.','/').removeprefix(PREFIX)
        require(short in EXPECTED and int(root.get('tests'))==len(EXPECTED[short]) and all(int(root.get(k))==0 for k in ['failures','errors','skipped']),'whole original suites/FES0')
        actual=[]
        for c in root.findall('testcase'):
            require(not list(c),'PASS only');actual.append((c.get('classname'),c.get('name')))
        require(len(actual)==len(set(actual))==len(EXPECTED[short]) and {n for c,n in actual}==EXPECTED[short] and not set(actual)&cases,'whole declared actual Test IDs');cases|=set(actual)
    require(len(cases)==18 and not cases&{(c['classname'],c['name']) for c in reg['cases']},'distinct new current source methods')
    normal=read(('PG14216-typed-marker-guard-six-compile-v1','1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'));hashes=normal['begin']['inputHashes'];texts={}
    for short,(pin,count) in TEST_PINS.items():
        path='src/schubert-nk-api/src/test/java/'+PREFIX+short+'.java';text=(data.ROOT/path).read_text();texts[short]=text
        require(data.sha(text.encode())==hashes[path]==pin and text.count('@Test')==count==len(EXPECTED[short]) and set(re.findall(r'(?m)^  void (\w+)\(',text))==EXPECTED[short],'all original whole source, including DisplayName methods')
    alphabet='0123456789ABCDEFGHJKMNPQRSTVWXYZ'
    cycles=[''.join(alphabet[(i*26+j)%32] for j in range(26)) for i in range(16)]
    receipt=texts['application/question/QuestionReceiptIdTest']
    require(len(set(alphabet))==32 and 26*5==130 and len(set(cycles))==16 and all('"'+v+'"' in receipt for v in cycles) and Counter(cycles*4)=={v:4 for v in cycles} and 64*26==1664,'independent alphabet/random-cycle mathematics, not production generator')
    forward=alphabet[:26];reverse=''.join(alphabet[57-i] for i in range(26,52))
    require(forward=='0123456789ABCDEFGHJKMNPQRS' and reverse=='ZYXWVTSRQPNMKJHGFEDCBA9876' and len([c for c in range(128) if chr(c) not in alphabet])+5==101 and 101*26==2626,'independent forward/reverse/forbidden-character matrix')
    require(all(v in receipt for v in ['i < 64','failureAt = position','bound ->','assertEquals(32, bound)','synchronized (generator)','assertEquals(1664, calls.get())','QuestionReceiptIdGenerator.create()']),'original independent RNG/null/private-monitor/64call assertions')
    settings=texts['maintenance/InspectorSettingsTest']
    require(all(v in settings for v in ['new int[] {1, 65535}','new InspectorSettings(ROOT, URL, input)','input.clear()','InspectorDatabaseConnections.databaseName','failure.getSuppressed().length']) and 'new InspectorDatabaseConnections(' not in settings and '.open(' not in settings,'pure typed-settings string helper only, no DB construction/open')
    stub=texts['application/question/StubAnswerProviderTest']
    require(all(v in stub for v in ['2026-09-20T00:00:00.123456789Z','1582-10-10T00:00:00Z','assertEquals("", answer.body())','assertEquals(0, calls.get())','assertEquals(expected, actual)','assertEquals(64, calls.get())','clock(() -> null)']),'literal clock/empty/negative/concurrent oracle')
    log=texts['logging/RequestLogDetailsTest']
    require(all(v in log for v in ['999999999999','1000000000000','repeat(1022)','repeat(1023)','repeat(342)','UserRole.USER','UserRole.ADMIN','"REQUEST log details violate the safe projection contract"']),'literal JSON/UTF8/N12/role/negative oracle')
    def unique(pairs):
        result={}
        for k,v in pairs:
            if k in result:raise ValueError('duplicate')
            result[k]=v
        return result
    def safe_json(text):
        require(len(text.encode('utf8'))<=1024,'bytes')
        value=json.loads(text,object_pairs_hook=unique)
        require(type(value) is dict,'root')
        for k,v in value.items():
            if k=='responseBytes':require(type(v) is int and 0<=v<=999999999999,'N12')
            elif k=='userAgentFamily':require(type(v) is str and re.fullmatch(r'[A-Za-z0-9 ._-]{1,32}',v) is not None,'family')
            elif k=='truncated':require(type(v) is bool,'boolean')
            elif k=='projectionStatus':require(type(v) is str and v in {'PENDING','FAILED'},'status')
            else:raise ValueError('unknown wire key')
        return json.dumps(value,separators=(',',':'),ensure_ascii=False)
    golden=['{}','{"responseBytes":999999999999,"userAgentFamily":"'+'A'*32+'","truncated":true,"projectionStatus":"PENDING"}','{"responseBytes":0,"userAgentFamily":"A","truncated":false,"projectionStatus":"FAILED"}','{"userAgentFamily":"Browser 1.0_x-y"}']
    require(all(safe_json(v)==v for v in golden) and safe_json(' '*1022+'{}')=='{}','independent stdlib literal JSON oracle')
    invalid=['[]','null','{} {}','{"truncated":true,"truncated":false}','{"actorRole":"ADMIN"}','{"responseBytes":true}','{"responseBytes":1.0}','{"responseBytes":1000000000000}','{"userAgentFamily":null}','{"projectionStatus":"SENT"}',' '*1023+'{}']
    for v in invalid:
        try:safe_json(v)
        except ValueError:pass
        else:raise ValueError('invalid independent JSON vector')
    closure={};full={}
    with zipfile.ZipFile(normal['jars']['api']['path']) as jar:
        for short,pin in MAIN_PINS.items():
            name=PREFIX+short;path='src/schubert-nk-api/src/main/java/'+name+'.java'
            require(data.sha((data.ROOT/path).read_bytes())==hashes[path]==pin and name not in reg['fullSourceUnits'],'new unchanged target Source')
            group={n[:-6] for n in jar.namelist() if n==name+'.class' or n.startswith(name+'$') and n.endswith('.class')}
            require(group=={name},'whole one physical Source');closure[name]=[name]
            b=jar.read(name+'.class');decoded=code.decode(b,name+'.class')
            require(data.sha(b)==p['physicalClasses'][name] and decoded['methods']==p['sourcePhysicalInventory'][name]['methods'] and any(m['hasCode'] for m in decoded['methods']),'all actual Code')
            values={k:dict(missed=0,covered=v) for k,v in zip(['LINE','METHOD','CLASS','BRANCH'],ROWS[short])}
            require(p['executable'][name]['counters']==values,'independent exact per-role counters')
            full[name]=dict(physical=[name],totals=values,four100=all(v['covered']>0 for v in values.values()),metadataOnly=False,branchNaturallyZero=values['BRANCH']['covered']==0,threeCounter100=True)
            if short=='logging/RequestLogDetails':
                require(any(m['name']=='<init>' and m['hasCode'] for m in decoded['methods']) and 'private RequestLogDetails() {}' in (data.ROOT/path).read_text(),'actual empty private ctor Code retained; official filter unchanged, not manual exclusion')
    require(set(p['physicalClasses'])==set(p['executable'])==set(p['sourcePhysicalInventory'])==set(closure) and p['completeSourceUnitClosure']==closure and wire(p['fullSourceUnits'])==wire(full),'six complete physical and source units')
    total={k:dict(missed=0,covered=sum(v[i] for v in ROWS.values())) for i,k in enumerate(['LINE','METHOD','CLASS','BRANCH'])}
    require(p['totals']==total,'independent total97L18M6C43B')
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    for path,row in p['owners'].items():require(row['sha256']==hashes[path]==data.sha((data.ROOT/path).read_bytes()) and all(row[k]==v for k,v in canonical(path,logical).items()),'actual canonical role/cost')
    require(len(p['owners'])==10 and sum(v['ownershipStatus']=='BASELINE_LOGICAL_REFERENCE' for v in p['owners'].values())==6 and sum(v['ownershipStatus']=='UNKNOWN' for v in p['owners'].values())==4,'sixbaseline/fourUNKNOWN')
    for relative,expected in OUTPUTS.items():
        row=p['publicTestOutputs'][relative];require((data.ROOT/row['copy']).read_bytes()==expected.encode('ascii') and data.sha(expected.encode('ascii'))==row['sha256'] and row['bytes']==len(expected.encode('ascii')) and row['publicFixtureOnly'] is True,'independent fixed own-public evidence output/hash')
    require(set(p['publicTestOutputs'])==set(OUTPUTS),'no third IO path')
    for stage in p['stages']:
        slot=Path(stage['cwd']);require(slot==data.ROOT.parent/'pgpt-runs/PG379/pg15460-public-value-eighteen-post-v1','own passive slot')
        label='passive-held-probe-audit' if 'ReviewedProjectionHeldProbeAudit' in stage['command'] else ('session-identity' if 'CoverageSessionIdentity' in stage['command'] else 'coverage-audit')
        require(stage['actualExit']==0 and stage['timedOut'] is False and data.sha((slot/(label+'.stdout')).read_bytes())==stage['stdoutSha256'] and data.sha((slot/(label+'.stderr')).read_bytes())==stage['stderrSha256'],'actual passive command receipts')
        if label=='coverage-audit':require(stage['command'][-6:]==sorted(closure),'six exact reader names, no package prefix')
        if label=='passive-held-probe-audit':require((slot/(label+'.stdout')).read_text().strip()=='FORBIDDEN_PROBE_HITS=0','four fixed held prefixes no true probes, not all HOLD解除')
    designs={}
    for path in DOCS:
        b=subprocess.check_output(['git','show','origin/main:'+path],cwd=data.ROOT);designs[path]=dict(gitRef='origin/main',sha256=data.sha(b))
        anchor={'312_':'STUBは空文字と現在時刻','331_':'^[0-9A-HJKMNP-TV-Z]{26}$','351_':'整数0～999999999999','343_':'ここはenv/file parserではなく'}[next(k for k in ['312_','331_','351_','343_'] if k in path)]
        require(anchor in b.decode(),'approved target-specific design')
    fixed={k:p[k] for k in ['source','cases','execSha256','sessionIdentity','physicalClasses','completeSourceUnitClosure','sourcePhysicalInventory','fullSourceUnits','owners','reportedEnvironment','totals','publicTestOutputs']}
    def contract(v):
        require(all(wire(v[k])==wire(x) for k,x in fixed.items()),'actual source/run/oracle-output/counters')
        require(v['tests']==18 and v['suites']==4 and v['targetUnitFour100'] is False and v['strictFour100GateExit']==1 and v['allMeasuredApplicableCountersCovered'] is True and v['singleSession'] is True and v['crcMismatch']==0 and v['metadataClasses']==[] and v['manualCounterExclusions']==[],'four four100/two naturalB0, no fake global four100')
        require(v['cryptoOrKeyOperationsInvoked'] is v['publicReceiptIdentifierRandomnessOnly'] is v['ownFreshJvmProviderStateOnly'] is v['testOwnNewSlotPublicEvidenceWrites'] is True and v['cryptoOperationKind']=='CSPRNG_PUBLIC_RECEIPT_IDENTIFIER_ONLY_NO_KEYS' and v['childLocalJcaRegistryRestorationTested'] is v['onlyReviewedPureValueSuites'] is False,'truthful public entropy/own test IO/provider-no-mutation')
        require(all(v[k] is False for k in ['actualSecretKeysLoaded','actualCredentialValuesUsed','actualAuthenticationOrSessionIssued','formalUpdated','whole451Accepted','wholeF03Accepted','oldCoverageTransferred','actualFilesOpenedByProduct','rootMainInvoked']) and v['forbiddenProductProbeHits']==v['newAccepted']==v['productTestsReexecutedByPost']==0 and v['effortPercent'] is None,'no secret/live/Graph/formal/effort credit')
    contract(p);negative=[]
    for key,value in [('source','OLD'),('cases',[]),('totals',{}),('fullSourceUnits',{}),('owners',{}),('physicalClasses',{}),('publicTestOutputs',{}),('tests',19),('suites',5),('targetUnitFour100',True),('strictFour100GateExit',0),('allMeasuredApplicableCountersCovered',False),('singleSession',False),('crcMismatch',1),('metadataClasses',['X']),('manualCounterExclusions',['normalize']),('cryptoOrKeyOperationsInvoked',False),('publicReceiptIdentifierRandomnessOnly',False),('ownFreshJvmProviderStateOnly',False),('testOwnNewSlotPublicEvidenceWrites',False),('cryptoOperationKind','NO_CRYPTO'),('childLocalJcaRegistryRestorationTested',True),('onlyReviewedPureValueSuites',True),('actualSecretKeysLoaded',True),('actualCredentialValuesUsed',True),('actualAuthenticationOrSessionIssued',True),('formalUpdated',True),('whole451Accepted',True),('wholeF03Accepted',True),('oldCoverageTransferred',True),('actualFilesOpenedByProduct',True),('rootMainInvoked',True),('forbiddenProductProbeHits',1),('newAccepted',1),('productTestsReexecutedByPost',1),('effortPercent',100)]:
        bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad)
        except ValueError:negative.append(key)
        else:raise ValueError('false public-value qualification')
    for v in [p,reg]:verify(v['invocation'])
    verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=p['source'],invocation=invocation,postSha256=POST[1],tests=18,suites=4,newUniqueMethods=18,sourcePrograms=6,physicalClasses=6,four100SourcePrograms=4,naturallyBranchZeroSourcePrograms=2,incompleteSourcePrograms=0,totals=total,semanticNegativeVectors=len(negative),negativeLabels=negative,independentReceiptOracle=dict(alphabet=alphabet,forward=forward,reverse=reverse,cycles=cycles,cycleCopies=4,totalDraws=1664,forbiddenPositionVectors=2626,identifierBits=130),independentJsonGolden=golden,independentJsonNegativeVectors=len(invalid),publicTestOutputs=p['publicTestOutputs'],cryptoOrKeyOperationsInvoked=True,publicReceiptIdentifierRandomnessOnly=True,actualSecretKeysLoaded=False,actualCredentialValuesUsed=False,ownFreshJvmProviderStateOnly=True,testOwnNewSlotPublicEvidenceWrites=True,forbiddenProductProbeHits=0,baselineMainOwnerRows=6,unknownTestOwnerRows=4,candidateOwnersNotAccepted=True,authoritativeDesigns=designs,originalMethodsReexecuted=0,actualLiveObservation=False,newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(dict(actualExit=0,tests=18,semanticNegativeVectors=len(negative),forbiddenProductProbeHits=0)))
if __name__=='__main__':main()
