"""Independent clock-only original18/one API Source; no actual stop or native operation."""
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

PIN='242a987a6b39aa0365fa0b479e41ffe12b6b5d01cfc9e49c4f6e3a7945da1001'
POST=data.BASE/'PG15242-api-stop-budget-eighteen-post-v1'
OUT=data.BASE/'PG15245-api-stop-budget-independent-v2'
PREFIX='dev/codex/schubert/nk/api/bootstrap/'
COUNTS={"ApiStopBudgetTest":18}
EXPECTED={"ApiStopBudget":[]}
NATURAL=set()
DOC='documents/300_SS/340_batch・基盤/342_Caddy・systemd・PostgreSQL・Java設定設計.md'

def require(ok,message):
    if not ok:raise ValueError(message)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only monitoring independent')
    p=data.read_checked(POST/'manifest.json',PIN)
    raw=data.read_checked(data.BASE/'PG15240-api-stop-budget-eighteen-pt-v1/manifest.json','b5e2c1a74401b7d9342865e06bdaa9b72ceb36f4380f0b76b65e35c32d8b2019')
    registry=data.read_checked(data.BASE/'PG15230-current1711-config-registry-v1/manifest.json','9ffe1d9a2d535571f5bf94e4bab1353afb88b7b9a71820afa31c5534247c9a21')
    require(p['actualExit']==raw['actualExit']==registry['actualExit']==0 and p['source']==raw['source']==registry['source']=='6b53efeec87f3ec36a840dd8e7759656cb4aee5c' and p['execSha256']==raw['execSha256'] and p['sessionIdentity']=='PG15240-ORIGINAL-API-STOP-BUDGET18','genuine same source/own single exec')
    actual=[];suite_names=set()
    for filename,h in p['xmlHashes'].items():
        value=(POST/filename).read_bytes();require(data.sha(value)==h==raw['xmlHashes'][filename],'original whole XML bytes');root=ET.fromstring(value);simple=root.get('name').rsplit('.',1)[-1];suite_names.add(simple)
        require(int(root.get('tests'))==COUNTS[simple] and all(int(root.get(k))==0 for k in ['failures','errors','skipped']),'all original whole16 FES0')
        for c in root.findall('testcase'):
            require(not list(c),'actual PASS');actual.append((c.get('classname'),c.get('name')))
    require(suite_names==COUNTS.keys() and len(actual)==len(set(actual))==18 and set(actual)=={(c['classname'],c['name']) for c in raw['cases']} and not set(actual)&{(c['classname'],c['name']) for c in registry['cases']},'all16/one suite unique new, never prior1367 replay')
    normal=data.read_checked(data.BASE/'PG14216-typed-marker-guard-six-compile-v1/manifest.json','1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3');hashes=normal['begin']['inputHashes']
    declared=set()
    for simple,count in COUNTS.items():
        path='src/schubert-nk-api/src/test/java/'+PREFIX+simple+'.java';text=(data.ROOT/path).read_text();require(data.sha((data.ROOT/path).read_bytes())==hashes[path],'whole original normal Test source pin')
        methods=re.findall(r'@Test\s+void\s+([A-Za-z0-9_]+)\s*\(',text);require(len(methods)==count,'all original declared methods');declared.update(('dev.codex.schubert.nk.api.bootstrap.'+simple,n) for n in methods)
    require(declared==set(actual),'every declared Test ID corresponds to one original actual XML')
    document=subprocess.check_output(['git','show','origin/main:'+DOC],cwd=data.ROOT);doc_head=subprocess.check_output(['git','rev-parse','origin/main'],cwd=data.ROOT,text=True).strip()
    require('| '+chr(96)+'TimeoutStopSec'+chr(96)+' | Web 30s/API 60s |' in document.decode(),'approved API stop upper bound60 seconds')
    test=(data.ROOT/'src/schubert-nk-api/src/test/java'/PREFIX/'ApiStopBudgetTest.java').read_text()
    vector_declaration=test.split('long[][] vectors = {',1)[1].split('};',1)[0]
    def read_vectors(declaration):
        result=[]
        for line in declaration.splitlines():
            line=line.strip()
            if not line:continue
            match=re.fullmatch(r'\{\s*([0-9][0-9_]*L?)\s*,\s*([0-9][0-9_]*L?)\s*\},?',line)
            require(match is not None,'one complete two-long Java vector line')
            result.append([int(v.removesuffix('L').replace('_','')) for v in match.groups()])
        return result
    vectors=read_vectors(vector_declaration)
    expected_vectors=[[0,60000000000],[1,59999999999],[1000000000,59000000000],[59999999999,1]]
    require(vectors==expected_vectors,'independent finite vector literals, not Production results')
    require('59_999_999_980L' in test and 'Long.MIN_VALUE + 9' in test and 'Long.MAX_VALUE - 10' in test and 'must not read after expiry' in test,'twenty-ns wrap and irreversible expiry original assertions')
    require(all(v in test for v in ['f.budget::begin','f.budget::remainingNanos','CountDownLatch(1)','assertEquals(1, f.reads.get())','assertThrows(NullPointerException.class','assertSame(primary','assertSame(fatal']),'null, clock-fault identity, one claim and own concurrency assertions')
    oracle_negative=[]
    for label,values in [('off-by-one',[[0,60000000001],*expected_vectors[1:]]),('missing-boundary',expected_vectors[:-1]),('reverse-boundary',list(reversed(expected_vectors)))]:
        try:require(values==expected_vectors,'literal mismatch')
        except ValueError:oracle_negative.append(label)
        else:raise ValueError('false arithmetic oracle '+label)
    require(read_vectors('{0, 60_000_000_000L},')==read_vectors('{0, 60_000_000_000},')==[[0,60000000000]],'optional long suffix numeric equivalence')
    syntax_negative=[]
    for label,text in [('bad-suffix','{0, 60_000_000_000X},'),('missing-value','{0},'),('extra-value','{0,1,2},')]:
        try:read_vectors(text)
        except ValueError:syntax_negative.append(label)
        else:raise ValueError('false Java numeric vector '+label)
    horizontal_hashes={}
    for relative,pin in [('tools/quality/pg15244_api_stop_budget_independent.py','3a27c40ea2bb707bb114e094623ae3b8d33cf421415644c9857e61be7830eb7f'),('tools/quality/pg15226_nonsecret_config_independent.py','68a671eb4be5d094bc94b633c24aa46691f1839680f16f00dea3d11e54df1588')]:
        require(data.sha((data.ROOT/relative).read_bytes())==pin,'frozen old reader and prior string-only independent source')
        horizontal_hashes[relative]=pin
    require('json.loads(v)' in (data.ROOT/'tools/quality/pg15226_nonsecret_config_independent.py').read_text() and 'long[][]' not in (data.ROOT/'tools/quality/pg15226_nonsecret_config_independent.py').read_text(),'prior string reader no numeric suffix parsing')
    closures={PREFIX+n:sorted([PREFIX+n,*[PREFIX+n+'$'+child for child in nested]]) for n,nested in EXPECTED.items()};names=set().union(*(set(v) for v in closures.values()))
    require(p['completeSourceUnitClosure']==closures and set(p['physicalClasses'])==set(p['executable'])==names and len(names)==1 and p['metadataClasses']==[] and not closures.keys()&registry['fullSourceUnits'].keys(),'one entire new Source/oneCode, no helper parent promotion')
    logical={r['path']:r for r in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']};totals={k:dict(missed=0,covered=0) for k in ['LINE','METHOD','CLASS','BRANCH']}
    with zipfile.ZipFile(normal['jars']['api']['path']) as jar:
        for name,closure in closures.items():
            require({n[:-6] for n in jar.namelist() if n==name+'.class' or n.startswith(name+'$') and n.endswith('.class')}==set(closure),'all actual nested Jar classfiles')
            local={k:{role:sum(p['executable'][n]['counters'][k][role] for n in closure) for role in ['missed','covered']} for k in totals};unit=p['fullSourceUnits'][name];natural=name in NATURAL
            require(local==unit['totals'] and unit['four100'] is (not natural) and unit['branchNaturallyZero'] is natural and unit['threeCounter100'] is True and all(local[k]['missed']==0 and local[k]['covered']>0 for k in ['LINE','METHOD','CLASS']) and (local['BRANCH']==dict(missed=0,covered=0) if natural else local['BRANCH']['missed']==0 and local['BRANCH']['covered']>0),'entire Source: one nonempty four100 Source')
            for k in totals:
                for role in totals[k]:totals[k][role]+=local[k][role]
            for n in closure:
                value=jar.read(n+'.class');parsed=code.decode(value,n+'.class');require(data.sha(value)==p['physicalClasses'][n] and parsed['methods']==p['sourcePhysicalInventory'][n]['methods'] and any(m['hasCode'] for m in parsed['methods']),'independent actual executable Code, no hidden exclusions')
    require(totals==p['totals']==dict(LINE=dict(missed=0,covered=24),METHOD=dict(missed=0,covered=5),CLASS=dict(missed=0,covered=1),BRANCH=dict(missed=0,covered=12)) and p['missedLines']==[],'actual one-class counters, not union')
    require(len(p['owners'])==2,'only one Main/one whole Test owner rows')
    for path,owned in p['owners'].items():
        expected=canonical(path,logical);require(data.sha((data.ROOT/path).read_bytes())==hashes[path]==owned['sha256'] and all(owned[k]==v for k,v in expected.items()) and expected['canonicalOwner'] is expected['canonicalCostOwner'] is None and expected['ownershipStatus']=='UNKNOWN','current approved-rule candidate ownership never baseline/accepted')
    fixed={k:p[k] for k in ['source','cases','execSha256','sessionIdentity','physicalClasses','completeSourceUnitClosure','sourcePhysicalInventory','fullSourceUnits','totals','owners','fixtureHashes']}
    def contract(v):
        require(all(v[k]==value for k,value in fixed.items()),'all actual original proof/owner/fixture immutable')
        require(v['tests']==18 and v['suites']==1 and v['targetUnitFour100'] is True and v['strictFour100GateExit']==0 and v['singleSession'] is True and v['crcMismatch']==0 and v['metadataClasses']==[] and v['manualCounterExclusions']==[],'complete source strict four100 actual')
        require(v['ownChildJvmStandardSdkObserved'] is False and v['forcedGcOrHeapDump'] is False and v['externalVmOrTargetProcessObserved'] is False,'genuine own child SDK measurement never remote/native or forced GC')
        require(v['newAccepted']==v['productTestsReexecutedByPost']==0 and v['formalUpdated'] is v['whole451Accepted'] is v['wholeF03Accepted'] is v['oldCoverageTransferred'] is v['coverageExecUnion'] is False and v['effortPercent'] is None and v['canonicalOwnersRemainCandidateNotAccepted'] is v['helperSourceProgramsNotAcceptedByTheseTargetCounters'] is True,'no helper/old/owner/formal/effort transfer')
    contract(p);negative=[]
    for key,value in [('ownChildJvmStandardSdkObserved',True),('forcedGcOrHeapDump',True),('externalVmOrTargetProcessObserved',True),('source','OLD'),('tests',55),('suites',2),('targetUnitFour100',False),('strictFour100GateExit',1),('singleSession',False),('crcMismatch',1),('metadataClasses',list(names)),('manualCounterExclusions',['AlertLifecycle']),('totals',{}),('fullSourceUnits',{}),('fixtureHashes',{'unknown':'0'*64}),('owners',{}),('newAccepted',1),('productTestsReexecutedByPost',1),('formalUpdated',True),('whole451Accepted',True),('wholeF03Accepted',True),('oldCoverageTransferred',True),('coverageExecUnion',True),('effortPercent',100),('canonicalOwnersRemainCandidateNotAccepted',False),('helperSourceProgramsNotAcceptedByTheseTargetCounters',False)]:
        bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad)
        except ValueError:negative.append(key)
        else:raise ValueError('false Web-pool-context56 proof accepted '+key)
    for v in [p,registry]:verify(v['invocation'])
    verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=p['source'],invocation=invocation,postSha256=PIN,tests=18,suites=1,newUniqueMethods=18,sourcePrograms=1,physicalClasses=1,four100SourcePrograms=1,naturallyBranchZeroSourcePrograms=0,naturallyBranchZeroPhysicalClasses=0,totals=totals,semanticNegativeVectors=len(negative),negativeLabels=negative,independentClockVectors=expected_vectors,clockOracleNegativeVectors=len(oracle_negative),clockOracleNegativeLabels=oracle_negative,javaLiteralSyntaxNegativeVectors=len(syntax_negative),javaLiteralSyntaxNegativeLabels=syntax_negative,horizontalScopeHashes=horizontal_hashes,toolBug='BUG-2121',horizontalCheck='YKT-1868',authoritativeDesign=dict(path=DOC,gitRef='origin/main',commit=doc_head,sha256=data.sha(document)),unknownOwnerRows=2,candidateOwnersNotAccepted=True,originalMethodsReexecuted=0,actualLiveObservation=False,observationScope="FINITE_FAKE_CLOCK_AND_OWN_THREADS_NO_SIGNAL",forcedGcOrHeapDump=False,externalVmOrTargetProcessObserved=False,newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
