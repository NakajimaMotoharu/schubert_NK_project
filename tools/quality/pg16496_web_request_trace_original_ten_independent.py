"""Independent route/identity/null/thread oracles and full four Source current qualification."""
import copy
import json
import re
import subprocess
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg16492_web_request_trace_original_ten_pt as original
POST=('PG16494-web-request-trace-original-ten-post-v1','3ae5aaf2ebec865b7c3cfad02f18622c12ef7f385484bf658b787a941149a9d6')
RAW=('PG16492-web-request-trace-original-ten-pt-v1','0153e773f3f58add52e391e34fa1bea11285f28a9211bb4b7e10571d686ad909')
PREV=('PG16482-current2226-batch-enum-registry-v1','71620afa247589ff1dc183dc822d7d0ab562eac1f47794b540a44cc37fcfa8f1')
OUT=data.BASE/'PG16496-web-request-trace-original-ten-independent-v1'
ROUTES=['/','/login','/logout','/error','/search','/logs','/scenarios','/scenarios/{id:[0-9]{1,12}}','/scenarios/{game:NUKITASHI[12]}','/scenarios/{game:NUKITASHI[12]}/{prefix:[0-9]{2}}','/animation','/animation/main','/animation/ova','/animation/opening','/animation/videos/{id}','/animation/media/{id}','/music','/music/{category}','/music/{category}/{section}','/music/media/{id}','/music/download/{id}','/audio/{id}','/audio/{id}/download','/admin/users','/admin/users/new','/admin/users/{id:[0-9]{1,12}}','/questions','/questions/new','/questions/accepted/{receiptId}','/questions/{id:[0-9]{1,12}}','/notifications','/notifications/{id:[0-9]{1,12}}','/css/**','/js/**']
def require(ok,why):
    if not ok:raise ValueError(why)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p,raw,old=[read(v) for v in [POST,RAW,PREV]]
    require(all(v['actualExit']==0 and v['source']==original.SOURCE for v in [p,raw,old]),'same actual source')
    name='dev.codex.schubert.nk.web.logging.WebRequestTraceTest';path=original.TESTS['WebRequestTraceTest'];body=path.read_bytes();text=body.decode()
    require(data.sha(body)==original.TEST_PINS['WebRequestTraceTest']==raw['begin']['testSourceHashes'][str(path)],'unchanged whole test')
    methods=re.findall(r'@Test\s+void\s+(\w+)\(',text);require(len(methods)==10,'whole original ten')
    expected={(name,m) for m in methods};decl=old['currentOrdinaryTestDeclarationReference'];catalog=read(('PG15950-g13-current-test-declaration-inventory-v1',decl['inventoryManifestSha256']))
    bindings=data.read_checked(data.BASE/'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json',catalog['files']['exact-ordinary-bindings.json'])
    require(expected=={(v['className'],v['method']) for v in bindings if v['className']==name} and not expected&{(v['classname'],v['name']) for v in old['cases']},'new closed normal declarations')
    actual=[]
    for file,pin in p['xmlHashes'].items():
        blob=(data.BASE/POST[0]/file).read_bytes();require(data.sha(blob)==pin,'original XML');root=ET.fromstring(blob)
        require(all(root.get(k)=='0' for k in ['failures','errors','skipped']),'FES0')
        for case in root.findall('testcase'):require(not list(case),'PASS');actual.append((case.get('classname'),case.get('name')))
    require(len(actual)==len(set(actual))==10 and set(actual)==expected,'whole ten actual methods')
    region=text.split('private static final Set<String> ROUTES =',1)[1].split(');',1)[0]
    test_routes=set(json.loads(v) for v in re.findall(r'"(?:[^"\\]|\\.)*"',region));test_routes|={'/login','/error'}
    require(test_routes==set(ROUTES) and len(ROUTES)==34,'independent hand-listed 34 route patterns')
    annotation_values=[]
    for relative,pin in original.PUBLIC_READS.items():
        blob=(original.COMPILE/'snapshot'/relative).read_bytes();require(data.sha(blob)==pin,'normal public Source original read identity')
        if '/controller/' in relative:annotation_values+=re.findall(r'@(Get|Post|Request)Mapping\("([^"]+)"\)',blob.decode())
    require(len(annotation_values)==37 and {v[1] for v in annotation_values}==set(ROUTES)-{'/css/**','/js/**'},'independent original public 37 annotations and 32 mappings')
    vectors=[
      ['new UUID(0, 3)','new UUID(1, 3)','assertEquals(trace.eventId(), trace.correlationId())'],
      ['"équipe"','"TopBarViewModel[REDACTED]"','assertTrue(trace.claimCompletion())','assertFalse(trace.claimCompletion())'],
      ['for (int i = 1; i <= 100; i++)','new UUID(2, owner)','new UUID(0, owner)','get(5, TimeUnit.SECONDS)'],
      ['ExecutionException.class','outer.close()','"request audit scope order mismatch"','same ? new UUID(2, 91) : new UUID(1, 90)'],
      ['"web request context is unavailable"','assertNull(contextFailure.getCause())','contextFailure.getSuppressed().length'],
      ['FIXTURE_REQUEST_ID_ATTRIBUTE_SUFFIX, "bad-type"','"not-context"','"not-trace"'],
      ['"request audit metadata is unavailable"','for (boolean set : List.of(false, true))','for (boolean state : List.of(false, true))'],
      ['DispatcherType.ERROR','DispatcherType.ASYNC','new RequestLogMvcConfiguration()','configuration.addInterceptors(null)']]
    require(all(all(v in text for v in group) for group in vectors),'independent literal and partition oracles')
    counts={k:dict(missed=0,covered=c) for k,c in [('LINE',123),('METHOD',33),('CLASS',5),('BRANCH',40)]}
    physical=set(n for values in original.CLOSURES.values() for n in values)
    def contract(v):
        require(type(v['actualExit']) is int and v['actualExit']==0 and v['source']==original.SOURCE and v['originalManifestSha256']==RAW[1],'actual source/run')
        require((v['tests'],v['suites'],v['targetSourceUnits'],v['newTestIds'])==(10,1,4,0) and v['cases']==raw['cases'],'whole ten four Sources')
        require(v['completeSourceUnitClosure']==original.CLOSURES and set(v['physicalClasses'])==set(v['executable'])==physical and v['metadataClasses']==[] and v['unexecutedCodeClasses']==[],'all five complete Code')
        require(v['totals']==counts and all(c['missed']==0 for r in v['executable'].values() for c in r['counters'].values()),'all actual applicable counters covered')
        require(v['strictFour100GateExit']==1 and v['targetUnitFour100'] is False and v['allMeasuredApplicableCountersCovered'] is True,'branch0 Source not false four100')
        require(sum(u['four100'] for u in v['fullSourceUnits'].values())==3 and sum(u['branchNaturallyZero'] and u['threeCounter100'] for u in v['fullSourceUnits'].values())==1,'three four100 and one naturalzero')
        require(v['singleSession'] is True and v['crcMismatch']==0 and v['manualCounterExclusions']==[],'single actual exec no exclusions')
        require(v['publicSourceReadHashes']==original.PUBLIC_READS==raw['stages'][1]['publicSourceReadHashes'] and v['testPublicSourceRead'] is True and v['testOwnScalarTraceWritten'] is False,'public read, no invented scalar writes')
        require(v['syntheticAuthenticationContextValueUsed'] is True and v['actualAuthenticationOrSessionIssued'] is False and v['cryptoOrKeyOperationsInvoked'] is v['actualSecretKeysLoaded'] is False,'synthetic display value not credentials/session/crypto')
        require(v['ownThreadCount'] is None and v['declaredOwnExecutorInstances']==2 and v['declaredOwnTaskCount']==101,'declared own threads not measured count')
        require(len(v['rootRecoveryProbeAudit'])==27 and all(not r['recordPresent'] and r['trueProbeHits']==0 for r in v['rootRecoveryProbeAudit'].values()),'no Root recovery execution')
        require(all(v[k] is False for k in ['actualFilesOpenedByProduct','rootMainInvoked','actualPermitIssueSignPublishOrRetire','formalUpdated','whole451Accepted','oldCoverageTransferred']) and v['effortPercent'] is None,'no authority/formal transfer')
    contract(p);labels=[]
    for key,value in [('actualExit',True),('source','OLD'),('originalManifestSha256','0'*64),('tests',11),('suites',2),('targetSourceUnits',5),('newTestIds',1),('cases',[]),('completeSourceUnitClosure',{}),('physicalClasses',{}),('executable',{}),('metadataClasses',['missing']),('totals',{}),('strictFour100GateExit',0),('targetUnitFour100',True),('allMeasuredApplicableCountersCovered',False),('manualCounterExclusions',['hidden']),('singleSession',False),('crcMismatch',1),('publicSourceReadHashes',{}),('testPublicSourceRead',False),('testOwnScalarTraceWritten',True),('syntheticAuthenticationContextValueUsed',False),('actualAuthenticationOrSessionIssued',True),('cryptoOrKeyOperationsInvoked',True),('actualSecretKeysLoaded',True),('ownThreadCount',101),('declaredOwnTaskCount',0),('rootRecoveryProbeAudit',{}),('formalUpdated',True),('effortPercent',100)]:
        require(p[key]!=value,'nondegenerate '+key);bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false trace qualification '+key)
    designs={}
    for number in ['312','314','351']:
        matches=list((data.ROOT/'documents/300_SS').glob('*/'+number+'_*.md'));require(len(matches)==1,'unique approved SS')
        path=matches[0];relative=str(path.relative_to(data.ROOT));blob=path.read_bytes()
        require(blob==subprocess.check_output(['git','show','origin/main:'+relative],cwd=data.ROOT),'approved design bytes');designs[relative]=data.sha(blob)
    for v in [p,old]:verify(v['invocation'])
    verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,postSha256=POST[1],rawSha256=RAW[1],tests=10,suites=1,semanticNegativeVectors=len(labels),negativeLabels=labels,independentOracleVectors=len(vectors),manualRoutePatterns=34,publicMappingAnnotations=37,approvedDesignHashes=designs,productTestsReexecuted=0,newSourcePrograms=3,newPhysicalClasses=4,replacedExistingPartialSources=1,metadataPhysicalClasses=0,four100SourcePrograms=3,naturalZeroBranchSourcePrograms=1,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
