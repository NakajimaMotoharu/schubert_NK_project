"""Independent original API input4 oracle/full Source gap; no native/IO or Product replay."""
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

POST=('PG15342-api-startup-inputs-four-post-v2','22f14eebdb3284e51c67d9b05b4ee8eaf4b01784006a76cae6d73b071c98bcb3')
RAW=('PG15340-api-startup-inputs-four-pt-v1','40ecce1446324f21b6c9f260aa102dcf6d57409a0479c0e7f38c50c6054a9fc7')
REG=('PG15331-current1760-exact11-owner-registry-v3','cfb7c63e1b0761397371bf5fef625b7014aff588b992c35619c99b633374bd9f')
OUT=data.BASE/'PG15344-api-startup-inputs-independent-v1'
NAME='dev/codex/schubert/nk/api/bootstrap/ApiStartupInputs'
DOC='documents/300_SS/340_batch・基盤/343_設定file・directory・初期data・migration・切戻し設計.md'
TOTALS={'LINE':dict(missed=2,covered=11),'METHOD':dict(missed=1,covered=3),'CLASS':dict(missed=0,covered=2),'BRANCH':dict(missed=0,covered=0)}
def require(ok,message):
    if not ok:raise ValueError(message)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def wire(v):return json.dumps(v,sort_keys=True)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p,raw,registry=read(POST),read(RAW),read(REG)
    require(p['actualExit']==raw['actualExit']==registry['actualExit']==0 and p['source']==raw['source']==registry['source']=='6b53efeec87f3ec36a840dd8e7759656cb4aee5c' and p['execSha256']==raw['execSha256'] and p['sessionIdentity']=='PG15340-ORIGINAL-API-INPUTS4','genuine source/execution')
    actual=[]
    for filename,pin in p['xmlHashes'].items():
        xml=(data.BASE/POST[0]/filename).read_bytes();require(data.sha(xml)==pin==raw['xmlHashes'][filename],'original XML identity');suite=ET.fromstring(xml)
        require(suite.get('name')=='dev.codex.schubert.nk.api.bootstrap.ApiStartupInputsTest' and int(suite.get('tests'))==4 and all(int(suite.get(k))==0 for k in ['failures','errors','skipped']),'whole4 FES0')
        for case in suite.findall('testcase'):
            require(not list(case),'actual PASS');actual.append((case.get('classname'),case.get('name')))
    expected={'opsApiInput001CombinesIndependentFixedInputs','opsApiInput002MissingPrivateLocationStopsBeforeSourceRead','opsApiInput003SourceFailureAndConfigAdmissionStayDistinct','opsApiInput004NullContracts'}
    require(len(actual)==len(set(actual))==4 and {n for c,n in actual}==expected and not set(actual)&{(c['classname'],c['name']) for c in registry['cases']},'new distinct whole4, no prior replay')
    normal=read(('PG14216-typed-marker-guard-six-compile-v1','1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'));hashes=normal['begin']['inputHashes']
    path='src/schubert-nk-api/src/test/java/'+NAME+'Test.java';test=(data.ROOT/path).read_text()
    require(data.sha((data.ROOT/path).read_bytes())==hashes[path]=='3cecaf9d04173e9b973683a95f94a566ac47506654cad33170134814a54be3d5' and set(re.findall(r'@Test\s+void\s+(\w+)\s*\(',test))==expected,'full original source/TestID')
    tokens=['Map.of("SCHUBERT_NK_CONFIG_DIR", "/etc/schubert-nk", "CREDENTIALS_DIRECTORY", ROOT)','assertEquals(ServiceConfigFiles.Service.API, service)','reads.incrementAndGet();','"nk.monitoring.mode: DEBUG\\n", "nk.db.pool.api.max: \'8\'\\n"','assertEquals("DEBUG", result.config().value("nk.monitoring.mode"))','assertEquals("8", result.config().value("nk.db.pool.api.max"))','assertEquals(Path.of(ROOT), result.credentials().directory())','assertEquals(1, reads.get())','"service credential location unavailable"','assertEquals(0, reads.get())','assertSame(','StorageIoException.class','"API non-secret environment unavailable"','new ApiStartupInputs(null, ENV)','new ApiStartupInputs(service -> null, null)','new ApiStartupInputs.Values(null, credentials)','new ApiStartupInputs.Values(config, null)']
    require(all(v in test for v in tokens),'independent 072 literal values/order/null/original assertions')
    doc=subprocess.check_output(['git','show','origin/main:'+DOC],cwd=data.ROOT)
    require(all(v in doc.decode() for v in ['SCHUBERT_NK_CONFIG_DIR=/etc/schubert-nk','未知key','systemd credential/config tree','YAML2層の保持inode読取とcredentialのprivate LoadCredentialは別境界']),'approved env location/unknown rejection/secret separation')
    source_path='src/schubert-nk-api/src/main/java/'+NAME+'.java';main_text=(data.ROOT/source_path).read_text()
    require(data.sha((data.ROOT/source_path).read_bytes())==hashes[source_path]=='e6d69bfa6580bba22f2558c37d0ab43799ee5cc515e00a8d64370168333648e6','actual Main pin')
    require('config.validateEnvironment();' in main_text and not re.search(r'\.validateEnvironment\s*\(',test),'uncalled wrapper not hidden')
    closure=[NAME,NAME+'$Values'];logical={r['path']:r for r in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    require(p['completeSourceUnitClosure']=={NAME:closure} and set(p['physicalClasses'])==set(p['executable'])==set(closure) and NAME not in registry['fullSourceUnits'],'full new Source and both Code classes')
    with zipfile.ZipFile(normal['jars']['api']['path']) as jar:
        require({n[:-6] for n in jar.namelist() if n==NAME+'.class' or n.startswith(NAME+'$') and n.endswith('.class')}==set(closure),'actual Jar closure')
        for name in closure:
            b=jar.read(name+'.class');parsed=code.decode(b,name+'.class')
            require(data.sha(b)==p['physicalClasses'][name] and parsed['methods']==p['sourcePhysicalInventory'][name]['methods'] and any(m['hasCode'] for m in parsed['methods']),'actual executable Code not metadata/excluded')
    computed={k:{role:sum(p['executable'][n]['counters'][k][role] for n in closure) for role in ['missed','covered']} for k in TOTALS}
    require(computed==p['totals']==TOTALS and p['fullSourceUnits'][NAME]['totals']==TOTALS,'independent complete Source sum, no CRC union')
    require(p['missedLines']==[[NAME,'33','0','0'],[NAME,'34','0','0']],'exact two wrapper missed lines')
    require(len(p['owners'])==2,'one Main/one whole Test')
    for path,row in p['owners'].items():
        require(row['sha256']==hashes[path] and all(row[k]==v for k,v in canonical(path,logical).items()),'actual canonical row')
    require(p['owners'][source_path]['canonicalOwner']=='WBS-P018-05' and p['owners'][source_path]['ownershipStatus']=='BASELINE_LOGICAL_REFERENCE' and p['owners']['src/schubert-nk-api/src/test/java/'+NAME+'Test.java']['ownershipStatus']=='UNKNOWN','baseline Main/UNKNOWN Test retained')
    fixed={k:p[k] for k in ['source','cases','execSha256','sessionIdentity','physicalClasses','completeSourceUnitClosure','sourcePhysicalInventory','fullSourceUnits','totals','owners','missedLines','profile']}
    def contract(v):
        require(all(wire(v[k])==wire(x) for k,x in fixed.items()),'exact independent original semantics')
        require(v['tests']==4 and v['suites']==1 and v['targetUnitFour100'] is False and v['strictFour100GateExit']==1 and v['singleSession'] is True and v['crcMismatch']==0 and v['metadataClasses']==[] and v['manualCounterExclusions']==[],'measured incomplete Source, no false strict pass')
        u=v['fullSourceUnits'][NAME];require(u['branchNaturallyZero'] is True and u['threeCounter100'] is False and u['four100'] is False,'B0 alone never LMC pass')
        require(v['profile']['originalTestsAlreadyCounted'] is False and v['productTestsReexecutedByPost']==v['newAccepted']==0 and v['formalUpdated'] is v['whole451Accepted'] is v['wholeF03Accepted'] is v['oldCoverageTransferred'] is v['actualFilesOpenedByProduct'] is v['rootMainInvoked'] is False and v['effortPercent'] is None,'no Product IO/old transfer/accepted count')
    contract(p);labels=[]
    for key,value in [('source','OLD'),('tests',5),('suites',2),('cases',[]),('totals',{}),('fullSourceUnits',{}),('missedLines',[]),('physicalClasses',{}),('owners',{}),('targetUnitFour100',True),('strictFour100GateExit',0),('singleSession',False),('crcMismatch',1),('metadataClasses',[NAME+'$Values']),('manualCounterExclusions',['validateEnvironment']),('newAccepted',1),('productTestsReexecutedByPost',1),('formalUpdated',True),('whole451Accepted',True),('wholeF03Accepted',True),('oldCoverageTransferred',True),('actualFilesOpenedByProduct',True),('rootMainInvoked',True),('effortPercent',50)]:
        bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false original inputs proof accepted '+key)
    for v in [p,registry]:verify(v['invocation'])
    verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=p['source'],invocation=invocation,postSha256=POST[1],tests=4,suites=1,newUniqueMethods=4,sourcePrograms=1,physicalClasses=2,four100SourcePrograms=0,naturallyBranchZeroSourcePrograms=0,incompleteSourcePrograms=1,totals=TOTALS,semanticNegativeVectors=len(labels),negativeLabels=labels,independentOracleTokens=tokens,authoritativeDesign=dict(path=DOC,gitRef='origin/main',commit=subprocess.check_output(['git','rev-parse','origin/main'],cwd=data.ROOT,text=True).strip(),sha256=data.sha(doc)),baselineMainOwnerRows=1,unknownTestOwnerRows=1,candidateOwnersNotAccepted=True,originalMethodsReexecuted=0,actualLiveObservation=False,newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
