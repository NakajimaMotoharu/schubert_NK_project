"""Independent public synthetic ASCII SHA256/current ContextHash3; truthful crypto/JCA-local flags."""
import copy
import hashlib
import json
import re
from pathlib import Path
import subprocess
import zipfile
import xml.etree.ElementTree as ET
import classfile_code_metadata as code
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical

POST=('PG15420-context-hash-three-post-v1','4012b66d2bae7a216495e1b73a23ea8a89c2aa5eb86766f36308d6242ccfe15e')
RAW=('PG15419-context-hash-three-pt-v2','af16a93a8ddf54157ca3c4b679c3867d9eebac10b7de7b2e2eed4ec3f13a5915')
REG=('PG15408-current1800-exact12-owner-registry-v3','75c239f0250f38bb7ed4f6d9cf812eaaf8dd6766f38e93d917f81be0ae287640')
OUT=data.BASE/'PG15422-context-hash-three-independent-v1'
NAME='dev/codex/schubert/nk/api/security/ContextHash';TEST=NAME+'Test'
TOTALS={'LINE':dict(missed=0,covered=11),'METHOD':dict(missed=0,covered=2),'CLASS':dict(missed=0,covered=1),'BRANCH':dict(missed=0,covered=0)}
DOC='documents/300_SS/310_アプリケーション/314_認証・認可・session・CSRF実装設計.md'
def require(ok,message):
    if not ok:raise ValueError(message)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def wire(v):return json.dumps(v,sort_keys=True)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p,raw,reg=read(POST),read(RAW),read(REG)
    require(p['actualExit']==raw['actualExit']==reg['actualExit']==0 and p['source']==raw['source']==reg['source']=='6b53efeec87f3ec36a840dd8e7759656cb4aee5c' and p['execSha256']==raw['execSha256'] and p['sessionIdentity']=='PG15419-CONTEXT-HASH-CURRENT-WHOLE3','genuine new source/current original session')
    actual=[];expected={'bug036CallerMonitorCannotBlockSharedDigest','asciiVectorsAndConcurrentCallsDoNotShareDigestState','unavailableMandatoryDigestPreventsStartupAndRestoresProviders'}
    for filename,pin in p['xmlHashes'].items():
        b=(data.BASE/POST[0]/filename).read_bytes();require(data.sha(b)==pin==raw['xmlHashes'][filename],'original XML')
        root=ET.fromstring(b);require(root.get('name')==TEST.replace('/','.') and int(root.get('tests'))==3 and all(int(root.get(k))==0 for k in ['failures','errors','skipped']),'whole3 FES0')
        for c in root.findall('testcase'):
            require(not list(c),'actual PASS');actual.append((c.get('classname'),c.get('name')))
    require(len(actual)==len(set(actual))==3 and {n for c,n in actual}==expected and not set(actual)&{(c['classname'],c['name']) for c in reg['cases']},'new current source qualification, not old0061 replay/transfer')
    normal=read(('PG14216-typed-marker-guard-six-compile-v1','1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'));hashes=normal['begin']['inputHashes']
    path='src/schubert-nk-api/src/test/java/'+TEST+'.java';test=(data.ROOT/path).read_text()
    require(data.sha((data.ROOT/path).read_bytes())==hashes[path]=='eafd2eb1a16ac85b8d8eb40f1d75cdcf49c0c894c9d08c883d546b233e62b353' and set(re.findall(r'@Test\s+void\s+(\w+)\s*\(',test))==expected,'whole original declared Test source')
    vectors=[('a','ffe054fe7ae0cb6dc65c3af9b61d5209f439851db43d0ba5997337df154668eb'),('b','a0fab1377f49a759b57f63318262ebe89fabfc990e8e93ceac2984561482b9d4')]
    for value,oracle in vectors:
        require(hashlib.sha256((value*64).encode('ascii')).hexdigest()==oracle and oracle in test and hashlib.sha256(bytes.fromhex(value*64)).hexdigest()!=oracle,'independent ASCII64 not hex-decoded32 SHA256')
    clauses=['@Isolated(','synchronized (hashes)','Executors.newVirtualThreadPerTaskExecutor()','.get(5, java.util.concurrent.TimeUnit.SECONDS)','i < 100','hashes.calculate(null)','Provider[] original = Security.getProviders()','Security.removeProvider(provider.getName())','assertThrows(NoSuchAlgorithmException.class, ContextHash::new)','finally {','Security.insertProviderAt(original[index], index + 1)','assertArrayEquals(original, Security.getProviders())']
    require(all(v in test for v in clauses) and not any(v in test for v in ['@BeforeAll','ProcessBuilder','Files.','getConnection(','TemporaryInfrastructureException','System.getenv(']),'whole child-only registry/thread/null/mandatory-failure restoration asserts')
    doc=subprocess.check_output(['git','show','origin/main:'+DOC],cwd=data.ROOT)
    require('SHA-256(raw ASCII bytes)' in doc.decode(),'approved lookup hash byte semantics')
    main_path='src/schubert-nk-api/src/main/java/'+NAME+'.java';require(data.sha((data.ROOT/main_path).read_bytes())==hashes[main_path]=='9b0714ec9dc88f3f15e11341d71d873250fee8436ebad03b3fb1079060392581','unchanged Main source')
    require(p['completeSourceUnitClosure']=={NAME:[NAME]} and set(p['physicalClasses'])==set(p['executable'])=={NAME} and NAME not in reg['fullSourceUnits'],'one complete new Source')
    with zipfile.ZipFile(normal['jars']['api']['path']) as jar:
        require({n[:-6] for n in jar.namelist() if n==NAME+'.class' or n.startswith(NAME+'$') and n.endswith('.class')}=={NAME},'whole Jar closure')
        b=jar.read(NAME+'.class');parsed=code.decode(b,NAME+'.class')
        require(data.sha(b)==p['physicalClasses'][NAME] and parsed['methods']==p['sourcePhysicalInventory'][NAME]['methods'] and {m['name'] for m in parsed['methods'] if m['hasCode']}=={'<init>','calculate'},'all actual Code methods, no artificial exclusion')
    require(p['executable'][NAME]['counters']==p['totals']==p['fullSourceUnits'][NAME]['totals']==TOTALS,'all original 11L2M1C missed0/B0')
    logical={r['path']:r for r in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    for path,row in p['owners'].items():require(row['sha256']==hashes[path]==data.sha((data.ROOT/path).read_bytes()) and all(row[k]==v for k,v in canonical(path,logical).items()),'baseline Main/UNKNOWN Test')
    require(len(p['owners'])==2 and p['owners'][main_path]['canonicalOwner']=='WBS-P007-03','actual canonical baseline')
    for stage in p['stages']:
        slot=Path(stage['cwd']);require(slot==data.ROOT.parent/'pgpt-runs/PG379/pg15420-context-hash-three-post-v1','fixed own passive tool slot')
        label='session-identity' if 'CoverageSessionIdentity' in stage['command'] else 'coverage-audit'
        require(stage['actualExit']==0 and stage['timedOut'] is False and data.sha((slot/(label+'.stdout')).read_bytes())==stage['stdoutSha256'] and data.sha((slot/(label+'.stderr')).read_bytes())==stage['stderrSha256'],'actual passive session/audit command receipts/output hashes')
    require(data.sha((data.ROOT/'tools/quality/pg15418_context_hash_three_pt.py').read_bytes())=='31d3cf55f9865833dfce5cc39c15e6e0415ec21073cbba0f3ac7639e65e59117','unexecuted first lint draft retained, not repaired/replayed')
    fixed={k:p[k] for k in ['source','cases','execSha256','sessionIdentity','physicalClasses','completeSourceUnitClosure','sourcePhysicalInventory','fullSourceUnits','totals','owners','reportedEnvironment']}
    def contract(v):
        require(all(wire(v[k])==wire(x) for k,x in fixed.items()),'all actual source/run/counter/owner/env semantics')
        require(v['tests']==3 and v['suites']==1 and v['targetUnitFour100'] is False and v['strictFour100GateExit']==1 and v['singleSession'] is True and v['crcMismatch']==0 and v['metadataClasses']==[] and v['manualCounterExclusions']==[] and v['naturalZeroBranch'] is True and v['branchPercent'] is None,'natural B0 never false four100')
        require(v['allMeasuredApplicableCountersCovered'] is True and v['fullSourceUnits'][NAME]['threeCounter100'] is True and v['fullSourceUnits'][NAME]['branchNaturallyZero'] is True,'all applicable LMC closed')
        require(v['cryptoOrKeyOperationsInvoked'] is True and v['cryptoOperationKind']=='SHA256_PUBLIC_FIXED_ASCII64_NO_KEYS' and v['onlyReviewedPureValueSuites'] is False and v['ownFreshJvmProviderStateOnly'] is v['childLocalJcaRegistryRestorationTested'] is True,'truthful crypto execution and child-only provider assertions')
        require(v['actualSecretKeysLoaded'] is v['actualCredentialValuesUsed'] is v['actualAuthenticationOrSessionIssued'] is v['formalUpdated'] is v['whole451Accepted'] is v['wholeF03Accepted'] is v['oldCoverageTransferred'] is v['actualFilesOpenedByProduct'] is v['rootMainInvoked'] is False and v['newAccepted']==v['productTestsReexecutedByPost']==0 and v['effortPercent'] is None,'no secret/actualauth/IO/old/formal/effort credit')
    contract(p);labels=[]
    for key,value in [('source','OLD'),('tests',4),('suites',2),('cases',[]),('totals',{}),('fullSourceUnits',{}),('physicalClasses',{}),('owners',{}),('targetUnitFour100',True),('strictFour100GateExit',0),('singleSession',False),('crcMismatch',1),('metadataClasses',[NAME]),('manualCounterExclusions',['calculate']),('naturalZeroBranch',False),('branchPercent',100),('allMeasuredApplicableCountersCovered',False),('cryptoOrKeyOperationsInvoked',False),('cryptoOperationKind','KEYS'),('onlyReviewedPureValueSuites',True),('ownFreshJvmProviderStateOnly',False),('childLocalJcaRegistryRestorationTested',False),('actualSecretKeysLoaded',True),('actualCredentialValuesUsed',True),('actualAuthenticationOrSessionIssued',True),('newAccepted',1),('productTestsReexecutedByPost',1),('formalUpdated',True),('whole451Accepted',True),('wholeF03Accepted',True),('oldCoverageTransferred',True),('actualFilesOpenedByProduct',True),('rootMainInvoked',True),('effortPercent',100)]:
        bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false fixed SHA256 proof accepted')
    for v in [p,reg]:verify(v['invocation'])
    verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=p['source'],invocation=invocation,postSha256=POST[1],tests=3,suites=1,newUniqueMethods=3,sourcePrograms=1,physicalClasses=1,four100SourcePrograms=0,naturallyBranchZeroSourcePrograms=1,incompleteSourcePrograms=0,totals=TOTALS,semanticNegativeVectors=len(labels),negativeLabels=labels,independentPublicAscii64Sha256=[dict(publicRepeatedCharacter=v,sha256=h) for v,h in vectors],wholeChildProviderRestorationAssertions=clauses,cryptoOrKeyOperationsInvoked=True,actualSecretKeysLoaded=False,actualCredentialValuesUsed=False,ownFreshJvmProviderStateOnly=True,authoritativeDesign=dict(path=DOC,gitRef='origin/main',commit=subprocess.check_output(['git','rev-parse','origin/main'],cwd=data.ROOT,text=True).strip(),sha256=data.sha(doc)),baselineMainOwnerRows=1,unknownTestOwnerRows=1,candidateOwnersNotAccepted=True,originalMethodsReexecuted=0,actualLiveObservation=False,newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
