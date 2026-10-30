"""Independent original RequiredColumn1; SQL exception value contract, no database connection."""
import copy
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

PIN='e26d863768b8659de2840b77421fd2f675d66a5dd9418b91a1796e691853d632'
POST=data.BASE/'PG15309-required-column-one-post-v2'
OUT=data.BASE/'PG15310-required-column-independent-v1'
PREFIX='dev/codex/schubert/nk/api/database/'
COUNTS={"RequiredColumnTest":1}
EXPECTED={"RequiredColumn":[]}
NATURAL=set()
DOC='documents/300_SS/330_データ・ファイル/332_SQL・transaction・lock・削除設計.md'

def require(ok,message):
    if not ok:raise ValueError(message)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only monitoring independent')
    p=data.read_checked(POST/'manifest.json',PIN)
    raw=data.read_checked(data.BASE/'PG15307-required-column-one-pt-v2/manifest.json','caafa8ae9909b8cd0f3ff7a7e2293c8a07260d1cab79505486e6b053f6b4f189')
    registry=data.read_checked(data.BASE/'PG15284-current1748-profile-terminal-registry-v1/manifest.json','7bc09027b74939ddc45fb92d63bb82be1c096f898670f275bed940cbe507435d')
    require(p['actualExit']==raw['actualExit']==registry['actualExit']==0 and p['source']==raw['source']==registry['source']=='6b53efeec87f3ec36a840dd8e7759656cb4aee5c' and p['execSha256']==raw['execSha256'] and p['sessionIdentity']=='PG15307-ORIGINAL-REQUIRED-COLUMN1','genuine same source/own single exec')
    actual=[];suite_names=set()
    for filename,h in p['xmlHashes'].items():
        value=(POST/filename).read_bytes();require(data.sha(value)==h==raw['xmlHashes'][filename],'original whole XML bytes');root=ET.fromstring(value);simple=root.get('name').rsplit('.',1)[-1];suite_names.add(simple)
        require(int(root.get('tests'))==COUNTS[simple] and all(int(root.get(k))==0 for k in ['failures','errors','skipped']),'all original whole16 FES0')
        for c in root.findall('testcase'):
            require(not list(c),'actual PASS');actual.append((c.get('classname'),c.get('name')))
    require(suite_names==COUNTS.keys() and len(actual)==len(set(actual))==1 and set(actual)=={(c['classname'],c['name']) for c in raw['cases']} and not set(actual)&{(c['classname'],c['name']) for c in registry['cases']},'all16/one suite unique new, never prior1367 replay')
    normal=data.read_checked(data.BASE/'PG14216-typed-marker-guard-six-compile-v1/manifest.json','1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3');hashes=normal['begin']['inputHashes']
    declared=set()
    for simple,count in COUNTS.items():
        path='src/schubert-nk-api/src/test/java/'+PREFIX+simple+'.java';text=(data.ROOT/path).read_text();require(data.sha((data.ROOT/path).read_bytes())==hashes[path],'whole original normal Test source pin')
        methods=re.findall(r'void\s+(requiredValuesRetainIdentityAndNullFailsWithSqlState)\s*\(',text);require(len(methods)==count,'all original declared methods');declared.update(('dev.codex.schubert.nk.api.database.'+simple,n) for n in methods)
    require(declared==set(actual),'every declared Test ID corresponds to one original actual XML')
    document=subprocess.check_output(['git','show','origin/main:'+DOC],cwd=data.ROOT);doc_head=subprocess.check_output(['git','rev-parse','origin/main'],cwd=data.ROOT,text=True).strip()
    require('SQL NULLは既存Optional/必須列検査を維持し、値0やepochへ補完しない' in document.decode(),'approved required NULL is failure, no default/epoch')
    test=(data.ROOT/'src/schubert-nk-api/src/test/java'/PREFIX/'RequiredColumnTest.java').read_text()
    require(test.count('@Test')==1 and '@DisplayName("PT-QUALITY-002 required JDBC values retain identity and SQL NULL fails redacted")' in test,'entire single original method and display name')
    require(all(v in test for v in ['assertSame(text, RequiredColumn.requireValue(text))','assertSame(time, RequiredColumn.requireValue(time))','assertSame(bytes, RequiredColumn.requireValue(bytes))','assertThrows(SQLDataException.class, () -> RequiredColumn.requireValue(null))','assertEquals("22004", failure.getSQLState())','assertEquals("required database value is missing", failure.getMessage())','assertNull(failure.getCause())']),'independent literal identity/null/sqlstate/redaction oracle')
    def imports(value):return re.findall(r'^import\s+(java\.sql\.[A-Za-z0-9_.]+)\s*;',value,re.MULTILINE)
    require(imports(test)==['java.sql.SQLDataException'] and not any(v in test for v in ['getConnection(','DriverManager','DataSource','ProcessBuilder','Files.']),'exception type only, not real JDBC or side effects')
    import_negative=[]
    for name in ['java.sql.Connection','java.sql.DriverManager','java.sql.Statement']:
        require(imports('import '+name+';')!=['java.sql.SQLDataException'],'non-exception JDBC import remains refused');import_negative.append(name)
    horizontal={}
    for relative,pin in [('tools/quality/pg15306_required_column_one_pt.py','c5467b116510f86d5a5125e968230e81a963367d0e8bbdbfb1d14990514b1f1c'),('tools/quality/pg15308_required_column_one_post.py','a5aa26607f9873eeda96f3ba7ab47c517ccef537c835511020fef21ddcc84497')]:
        require(data.sha((data.ROOT/relative).read_bytes())==pin,'frozen original failed preflight and duplicate generator');horizontal[relative]=pin
    for simple in ['ApiAdmittedConfigurationTest','ApiReadinessPredicateTest','ApiStopBudgetTest']:
        path=data.ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/bootstrap'/(simple+'.java')
        require(imports(path.read_text())==[] and data.sha(path.read_bytes())==hashes[str(path.relative_to(data.ROOT))],'prior pure suites have no SQL import, unchanged inputs')
    for folder,pin,count in [('PG15152-api-service-binding-sixteen-post-v1','b2f11b43e299cd166e47cff2352781b89983b6eae2a21e8aaa1e6903dd9b63c8',16),('PG15302-api-config-readiness-eleven-post-v1','ff665193ddb62c0ed11afac98a9bc5465167ad5348552b2d1d093951de59b92b',11)]:
        previous=data.read_checked(data.BASE/folder/'manifest.json',pin)
        require(previous['actualExit']==0 and len(previous['cases'])==count and count>=2,'old index1 vectors valid for actual multi-case proofs');verify(previous['invocation'])
    require(p['duplicateVectorInputCases']==1 and p['duplicateVectorRejectedCases']==2 and 'duplicate' in p['negativeLabels'],'single-case duplicate generated and rejected, not IndexError')
    ctor=p['officialPrivateEmptyNoArgConstructorFilter']
    require(ctor['method']=='<init>' and ctor['descriptor']=='()V' and ctor['flags']==2 and ctor['codeLength']==5 and 'EMPTY_PRIVATE_UTILITY_CONSTRUCTOR' in ctor['reason'],'documented unchanged official private empty constructor filter')
    runtime=data.read_checked(data.BASE/'PG13378-db-duration-eight-post-recovery-v3/manifest.json','adcb55b80aa70a449e74280aa465f752308310c41c876cf83a5a78c3dda3c882')
    core=[path for path in runtime['toolAndDependencyHashes'] if 'org.jacoco.core' in path and path.endswith('.jar')]
    require(len(core)==1 and data.sha(Path(core[0]).read_bytes())==runtime['toolAndDependencyHashes'][core[0]],'pinned official analyzer library')
    with zipfile.ZipFile(core[0]) as archive:require('org/jacoco/core/internal/analysis/filter/PrivateEmptyNoArgConstructorFilter.class' in archive.namelist(),'actual official filter present, no manual exclusion added')
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
    require(totals==p['totals']=={'LINE':{'missed':0,'covered':3},'METHOD':{'missed':0,'covered':1},'CLASS':{'missed':0,'covered':1},'BRANCH':{'missed':0,'covered':2}} and p['missedLines']==[],'actual public branch counters, no union')
    require(len(p['owners'])==2,'only one Main/one whole Test owner rows')
    for path,owned in p['owners'].items():
        expected=canonical(path,logical);require(data.sha((data.ROOT/path).read_bytes())==hashes[path]==owned['sha256'] and all(owned[k]==v for k,v in expected.items()),'actual canonical owner identity')
        if '/src/main/java/' in path:require(expected['canonicalOwner']==expected['canonicalCostOwner']=='WBS-P004-05' and expected['ownershipStatus']=='BASELINE_LOGICAL_REFERENCE','Main logical baseline only')
        else:require(expected['canonicalOwner'] is expected['canonicalCostOwner'] is None and expected['ownershipStatus']=='UNKNOWN','Test unknown retained')
    inventory=p['sourcePhysicalInventory'][PREFIX+'RequiredColumn'];methods=inventory['methods']
    require(len(methods)==2 and all(v['hasCode'] for v in methods) and any(v['name']=='<init>' and v['flags']==2 and v['codeLength']==5 for v in methods),'both actual Code methods retained, private ctor never NoCode')
    fixed={k:p[k] for k in ['source','cases','execSha256','sessionIdentity','physicalClasses','completeSourceUnitClosure','sourcePhysicalInventory','fullSourceUnits','totals','owners','fixtureHashes','officialPrivateEmptyNoArgConstructorFilter','duplicateVectorInputCases','duplicateVectorRejectedCases']}
    def contract(v):
        require(all(json.dumps(v[k],sort_keys=True)==json.dumps(value,sort_keys=True) for k,value in fixed.items()),'all actual original proof/owner/fixture immutable')
        require(v['tests']==1 and v['suites']==1 and v['targetUnitFour100'] is True and v['strictFour100GateExit']==0 and v['singleSession'] is True and v['crcMismatch']==0 and v['metadataClasses']==[] and v['manualCounterExclusions']==[],'complete source strict four100 actual')
        require(v['ownChildJvmStandardSdkObserved'] is False and v['forcedGcOrHeapDump'] is False and v['externalVmOrTargetProcessObserved'] is False,'genuine own child SDK measurement never remote/native or forced GC')
        require(v['newAccepted']==v['productTestsReexecutedByPost']==0 and v['formalUpdated'] is v['whole451Accepted'] is v['wholeF03Accepted'] is v['oldCoverageTransferred'] is v['coverageExecUnion'] is False and v['effortPercent'] is None and v['canonicalOwnersRemainCandidateNotAccepted'] is v['helperSourceProgramsNotAcceptedByTheseTargetCounters'] is True,'no helper/old/owner/formal/effort transfer')
    contract(p);negative=[]
    for key,value in [('ownChildJvmStandardSdkObserved',True),('forcedGcOrHeapDump',True),('externalVmOrTargetProcessObserved',True),('source','OLD'),('tests',55),('suites',2),('targetUnitFour100',False),('strictFour100GateExit',1),('singleSession',False),('crcMismatch',1),('metadataClasses',list(names)),('manualCounterExclusions',['AlertLifecycle']),('totals',{}),('fullSourceUnits',{}),('fixtureHashes',{'unknown':'0'*64}),('owners',{}),('newAccepted',1),('productTestsReexecutedByPost',1),('formalUpdated',True),('whole451Accepted',True),('wholeF03Accepted',True),('oldCoverageTransferred',True),('coverageExecUnion',True),('effortPercent',100),('canonicalOwnersRemainCandidateNotAccepted',False),('helperSourceProgramsNotAcceptedByTheseTargetCounters',False),('officialPrivateEmptyNoArgConstructorFilter',{}),('duplicateVectorInputCases',2),('duplicateVectorRejectedCases',1)]:
        bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad)
        except ValueError:negative.append(key)
        else:raise ValueError('false Web-pool-context56 proof accepted '+key)
    for v in [p,registry]:verify(v['invocation'])
    verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=p['source'],invocation=invocation,postSha256=PIN,tests=1,suites=1,newUniqueMethods=1,sourcePrograms=1,physicalClasses=1,four100SourcePrograms=1,naturallyBranchZeroSourcePrograms=0,naturallyBranchZeroPhysicalClasses=0,totals=totals,semanticNegativeVectors=len(negative),negativeLabels=negative,independentSqlState='22004',independentRedactedMessage='required database value is missing',independentValueIdentityTypes=['String','Instant','byte[]'],sqlImportNegativeVectors=len(import_negative),sqlImportNegativeLabels=import_negative,officialPrivateEmptyNoArgConstructorFilter=ctor,horizontalScopeHashes=horizontal,authoritativeDesign=dict(path=DOC,gitRef='origin/main',commit=doc_head,sha256=data.sha(document)),baselineMainOwnerRows=1,unknownTestOwnerRows=1,candidateOwnersNotAccepted=True,originalMethodsReexecuted=0,actualLiveObservation=False,newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
