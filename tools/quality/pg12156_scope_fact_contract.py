"""Independent pure-metadata vectors and one pinned actual dataset; no Product execution."""
import copy
import hashlib
from pathlib import Path
import platform
import subprocess
import sys
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from frozen_selected_scope import derive_facts,require_classpath
SOURCE='8a229695c0ea503ebac8761993665242eeba0107'
OUT=data.BASE/'PG12156-scope-facts-contract-v1'
ROLES=('api','batch','bootstrap','protocol','storage','web')
FAKE_SOURCE='1'*40
PATH='src/schubert-nk-batch/src/test/java/example/ProbeTest.java'
def fixture():
    plan=dict(sourceChanges=[dict(path=PATH,sha256='2'*64,beforeSha256='3'*64)])
    normal=dict(source=FAKE_SOURCE,actualExit=0,testsExecuted=0,begin=dict(inputHashes={PATH:'2'*64}),jars={r:dict(path='/fixture/'+r+'.jar',sha256='4'*64) for r in ROLES})
    return plan,normal
def main():
    invocation=capture(__file__);assert not OUT.exists()
    lint=[sys.executable,'-B','-m','pyflakes','tools/quality/frozen_selected_scope.py','tools/quality/pg12156_scope_fact_contract.py'];result=subprocess.run(lint,cwd=data.ROOT,check=False,capture_output=True)
    assert result.returncode==0 and not result.stdout and not result.stderr
    positives=[];negatives=[]
    p,n=fixture();original_p,original_n=copy.deepcopy(p),copy.deepcopy(n);facts=derive_facts(p,n,FAKE_SOURCE)
    assert facts['sources']=={PATH:'2'*64} and facts['modules']==['batch'] and facts['javaPackagePrefixes'] is None and facts['metadataOnly'] is True and facts['executionPermission'] is False
    assert facts['mainJarPaths']==['/fixture/'+r+'.jar' for r in ROLES] and facts['requiredModuleJars']=={'batch':dict(path='/fixture/batch.jar',sha256='4'*64)};positives.append('SINGLE_MODULE_EXACT_FACTS')
    assert require_classpath(facts,['/fixture/reader',*facts['mainJarPaths'],'/fixture/sdk.jar'])==tuple(['/fixture/reader',*['/fixture/'+r+'.jar' for r in ROLES],'/fixture/sdk.jar']);positives.append('REQUIRED_JARS_PLUS_EXPLICIT_EXTRA_ENTRIES')
    facts['sources'][PATH]='f'*64;facts['allMainJars']['batch']['path']='/fixture/changed.jar';assert p==original_p and n==original_n;positives.append('OUTPUT_MUTATION_DOES_NOT_CHANGE_INPUTS')
    p,n=fixture();other='src/schubert-nk-web/src/test/java/example/ProbeTest.java';p['sourceChanges'].append(dict(path=other,sha256='5'*64));n['begin']['inputHashes'][other]='5'*64;facts=derive_facts(p,n,FAKE_SOURCE);assert facts['sources']=={PATH:'2'*64,other:'5'*64} and facts['modules']==['batch','web'];positives.append('SAME_STEM_DIFFERENT_MODULES_STAY_EXPLICIT')
    p,n=fixture();boot='src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/api/ProbeTest.java';p['sourceChanges']=[dict(path=boot,sha256='6'*64)];n['begin']['inputHashes']={boot:'6'*64};facts=derive_facts(p,n,FAKE_SOURCE);assert facts['modules']==['bootstrap'] and facts['javaPackagePrefixes'] is None;positives.append('BOOTSTRAP_DOES_NOT_IMPLY_JAVA_PACKAGE')
    mutations=[
      ('BUILD_FAILED',lambda p,n:n.update(actualExit=1)),('BOOL_IS_NOT_EXIT_CODE',lambda p,n:n.update(actualExit=False)),('BUILD_RAN_TESTS',lambda p,n:n.update(testsExecuted=1)),('BOOL_IS_NOT_PT_COUNT',lambda p,n:n.update(testsExecuted=False)),('SOURCE_MISMATCH',lambda p,n:n.update(source='0'*40)),
      ('NULL_BEGIN',lambda p,n:n.update(begin=None)),('NULL_INPUTS',lambda p,n:n['begin'].update(inputHashes=None)),('NULL_CHANGES',lambda p,n:p.update(sourceChanges=None)),('EMPTY_CHANGES',lambda p,n:p.update(sourceChanges=[])),('NULL_ROW',lambda p,n:p.update(sourceChanges=[None])),
      ('NULL_PATH',lambda p,n:p['sourceChanges'][0].update(path=None)),('PARENT_TRAVERSAL',lambda p,n:p['sourceChanges'][0].update(path=PATH.replace('/example/','/../'))),('EMPTY_SEGMENT',lambda p,n:p['sourceChanges'][0].update(path=PATH.replace('/example/','//example/'))),('MAIN_IS_NOT_SELECTED_TEST',lambda p,n:p['sourceChanges'][0].update(path=PATH.replace('/test/','/main/'))),('UNKNOWN_MODULE',lambda p,n:p['sourceChanges'][0].update(path=PATH.replace('nk-batch','nk-other'))),
      ('NULL_HASH',lambda p,n:p['sourceChanges'][0].update(sha256=None)),('NON_HEX_HASH',lambda p,n:p['sourceChanges'][0].update(sha256='z'*64)),('CURRENT_INPUT_MISMATCH',lambda p,n:n['begin']['inputHashes'].update({PATH:'7'*64})),('DUPLICATE_PATH',lambda p,n:p['sourceChanges'].append(dict(p['sourceChanges'][0]))),
      ('MISSING_MODULE_JAR',lambda p,n:n['jars'].pop('batch')),('NULL_JAR_PATH',lambda p,n:n['jars']['batch'].update(path=None)),('ALIASED_MODULE_JAR',lambda p,n:n['jars']['batch'].update(path=n['jars']['api']['path'])),('NULL_JAR_HASH',lambda p,n:n['jars']['batch'].update(sha256=None)),('UNKNOWN_JAR_FIELD',lambda p,n:n['jars']['batch'].update(extra='not-a-declared-fact'))]
    def rejected(label,call):
        try:call()
        except ValueError:negatives.append(label)
        else:raise AssertionError('invalid metadata was accepted: '+label)
    for name,mutation in mutations:
        p,n=fixture();mutation(p,n);rejected(name,lambda:derive_facts(p,n,FAKE_SOURCE))
    p,n=fixture();rejected('NULL_PLAN',lambda:derive_facts(None,n,FAKE_SOURCE));rejected('NULL_NORMAL',lambda:derive_facts(p,None,FAKE_SOURCE));rejected('NULL_EXPECTED_SOURCE',lambda:derive_facts(p,n,None))
    facts=derive_facts(p,n,FAKE_SOURCE);entries=['/fixture/'+r+'.jar' for r in ROLES]
    for name,value in [('NULL_CP',None),('EMPTY_CP',[]),('NULL_CP_ELEMENT',[*entries,None]),('DUPLICATE_CP',[*entries,entries[0]]),('MISSING_TARGET_MODULE_CP',[p for p in entries if p!='/fixture/batch.jar'])]:rejected(name,lambda value=value:require_classpath(facts,value))
    rejected('NULL_FACTS',lambda:require_classpath(None,entries));bad=copy.deepcopy(facts);bad['executionPermission']=True;rejected('METADATA_IS_NOT_EXECUTION_PERMISSION',lambda:require_classpath(bad,entries))
    assert len(set(negatives))==len(negatives)==len(mutations)+10 and len(positives)==5
    normal=data.read_checked(data.BASE/'PG12134-batch-value-fixture-six-compile-v1/manifest.json','6894ef3e885fbe1d4995e5809fd82dc16fa88b0a3ccb02613c120370fdf56bb9');plan=data.read_checked(data.BASE/'PG12130-batch-value-fixture-plan-v1/manifest.json','e605ba4aa54692bb840093735ea245f6088f93bd9d702213dbe407101820098b');real=derive_facts(plan,normal,SOURCE)
    paths=['src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/EnumValueCatalogCompatibilityTest.java','src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/mq/ArtemisDetailedValuesTest.java'];expected={p:hashlib.sha256((data.ROOT/p).read_bytes()).hexdigest() for p in paths}
    assert real['sources']==expected and real['modules']==['batch'] and real['mainJarPaths']==[normal['jars'][r]['path'] for r in ROLES]
    assert require_classpath(real,real['mainJarPaths'])==tuple(normal['jars'][r]['path'] for r in ROLES)
    verify(invocation);OUT.mkdir();data.write(OUT/'facts.json',real);data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,hostOs=platform.platform(),pythonVersion=platform.python_version(),lintCommand=lint,lintExit=result.returncode,helperSha256=data.sha((data.ROOT/'tools/quality/frozen_selected_scope.py').read_bytes()),factsSha256=data.sha((OUT/'facts.json').read_bytes()),syntheticPositiveVectors=positives,syntheticNegativeVectors=negatives,allDeclaredVectorsExecuted=True,actualPinnedDatasetCases=1,actualSourcePathsCheckedAgainstCurrentTree=2,normalManifestSha256='6894ef3e885fbe1d4995e5809fd82dc16fa88b0a3ccb02613c120370fdf56bb9',planManifestSha256='e605ba4aa54692bb840093735ea245f6088f93bd9d702213dbe407101820098b',moduleDoesNotImplyJavaPackage=True,metadataIsNotExecutionPermission=True,productTestsExecuted=0,targetExternalActions=0,coverage=None,newAccepted=0,formalUpdated=False,whole451Accepted=False,effortPercent=None));print(dict(actualExit=0,positiveVectors=len(positives),negativeVectors=len(negatives),actualDatasets=1,manifestSha256=data.sha((OUT/'manifest.json').read_bytes())))
if __name__=='__main__':main()
