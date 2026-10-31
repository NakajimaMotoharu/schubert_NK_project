"""Independent unchanged original enum oracles and passive whole Source qualification."""
import ast
import copy
import re
import subprocess
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg16477_batch_enum_catalog_original_two_pt as original

POST=('PG16478-batch-enum-catalog-original-two-post-v1','d45441e00a12dcdc7070430d30b528a6d48625b026367af7ce311f6dadf8cc4d')
RAW=('PG16477-batch-enum-catalog-original-two-pt-v1','c4dd384d53a32ec054ba794e17234c0587711a08f0fd0d5e6099d16f38095801')
PREV=('PG16466-current2224-inspector-snapshot-registry-v1','1461c4715e3c1fd53ade29bae01ba03e64d44fecb93cff4f115814d2ecab1d94')
OUT=data.BASE/'PG16480-batch-enum-catalog-original-two-independent-v1'
def require(ok,why):
    if not ok:raise ValueError(why)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def has_entry(text):
    tree=ast.parse(text)
    return any(isinstance(n,ast.If) and isinstance(n.test,ast.Compare) and ast.dump(n.test)==ast.dump(ast.parse("__name__=='__main__'",mode='eval').body) and any(isinstance(v,ast.Expr) and isinstance(v.value,ast.Call) and isinstance(v.value.func,ast.Name) and v.value.func.id=='main' and not v.value.args and not v.value.keywords for v in n.body) for n in tree.body)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p,raw,old=[read(v) for v in [POST,RAW,PREV]]
    require(all(v['actualExit']==0 and v['source']==original.SOURCE for v in [p,raw,old]),'actual same source')
    decl=old['currentOrdinaryTestDeclarationReference'];catalog=read(('PG15950-g13-current-test-declaration-inventory-v1',decl['inventoryManifestSha256']))
    bindings=data.read_checked(data.BASE/'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json',catalog['files']['exact-ordinary-bindings.json'])
    expected=set();texts={}
    for name,path in original.TESTS.items():
        body=path.read_bytes();require(data.sha(body)==original.TEST_PINS[name]==raw['begin']['testSourceHashes'][str(path)],'whole unchanged original Test')
        methods=re.findall(r'@Test\s+void\s+(\w+)\(',body.decode());require(len(methods)==1,'whole original one')
        expected|={(name,methods[0])};texts[name]=body.decode()
    ordinary={(v['className'],v['method']) for v in bindings}
    require(expected<=ordinary and not expected&{(v['classname'],v['name']) for v in old['cases']},'new current original only')
    actual=[]
    for file,pin in p['xmlHashes'].items():
        blob=(data.BASE/POST[0]/file).read_bytes();require(data.sha(blob)==pin,'exact original XML')
        root=ET.fromstring(blob);require(all(root.get(k)=='0' for k in ['failures','errors','skipped']),'FES0')
        for case in root.findall('testcase'):require(not list(case),'all PASS');actual.append((case.get('classname'),case.get('name')))
    require(len(actual)==len(set(actual))==2 and set(actual)==expected,'both FQN classes, never simple-name collapse')
    repository=texts['dev.codex.schubert.nk.batch.repository.EnumValueCatalogCompatibilityTest']
    platform=texts['dev.codex.schubert.nk.batch.platform.EnumValueCatalogCompatibilityTest']
    vectors=[
      (repository,['"BACKUP_DB"','"BACKUP_CONFIG"','List.of(true, true, false, false, false, false, false, false, false, false)']),
      (repository,['"schubert.maintenance_cleanup_web_receipt_references"','"schubert.maintenance_cleanup_log_progress"','List.of(1000, 1000, 1000, 1000, 10000, 1000, 1000, 1000, 1000)']),
      (repository,['List.of("SUCCESS", "WARNING")','List.of(0, 10)','getSerialVersionUID()']),
      (platform,['"/system.slice/" + name','"/run/schubert-nk/backup-request"','"broker-start.intent"']),
      (platform,['target.ownedBy(null)','target == BackupUnitStartClient.Target.INSPECTOR','service == RootStartupContext.Service.CLEANUP','service == RootStartupContext.Service.MORNING'])]
    require(all(all(v in body for v in values) for body,values in vectors),'independently reviewed literal tables and null/all-service relation')
    old_entry=(data.ROOT/'tools/quality/pg16476_batch_enum_catalog_original_two_pt.py').read_text()
    new_entry=(data.ROOT/'tools/quality/pg16477_batch_enum_catalog_original_two_pt.py').read_text()
    require(not has_entry(old_entry) and has_entry(new_entry),'BUG2178 old rejected/new actual entry present')
    require(not has_entry(new_entry.replace("if __name__=='__main__':main()","")),'missing-entry regression negative')
    require("run.main()" in (data.ROOT/'tools/quality/pg16460_inspector_snapshot_original_twentythree_pt.py').read_text(),'old explicit caller nonapplicable')
    require(has_entry((data.ROOT/'tools/quality/pg16446_config_source_original_four_pt.py').read_text()),'old standalone nonapplicable')
    counts={k:dict(missed=m,covered=c) for k,m,c in [('LINE',760,109),('METHOD',150,31),('CLASS',12,8),('BRANCH',590,10)]}
    closures={n:sorted(row['physical']) for n,row in original.MAIN_UNITS.items()}
    code={n for row in original.MAIN_UNITS.values() for n,v in row['physical'].items() if v['code']}
    meta={n for row in original.MAIN_UNITS.values() for n,v in row['physical'].items() if not v['code']}
    def contract(v):
        require(type(v['actualExit']) is int and v['actualExit']==0 and v['source']==original.SOURCE and v['originalManifestSha256']==RAW[1],'same actual source/run')
        require((v['tests'],v['suites'],v['targetSourceUnits'],v['newTestIds'])==(2,2,8,0) and v['cases']==raw['cases'],'two unchanged whole tests')
        require(v['completeSourceUnitClosure']==closures and set(v['physicalClasses'])==code|meta and set(v['executable'])==code and set(v['metadataClasses'])==meta,'all eight Source physical closure, no cherry picking')
        require(len(code)==20 and len(meta)==8 and len(v['unexecutedCodeClasses'])==12 and all(v['executable'][n]['counters']['CLASS']['covered']==0 for n in v['unexecutedCodeClasses']),'outer unexecuted not hidden')
        require(v['totals']==counts and v['strictFour100GateExit']==1 and v['targetUnitFour100'] is v['allMeasuredApplicableCountersCovered'] is False,'partial coverage honest')
        require(v['manualCounterExclusions']==[] and v['singleSession'] is True and v['crcMismatch']==0,'single actual exec CRC/no exclusions')
        require(v['publicEnumLabelsAndSerializationSchemaOnly'] is True and v['cryptoOrKeyOperationsInvoked'] is v['actualSecretKeysLoaded'] is False,'enum-only effects')
        require(v['actualRootRecoveryOperations']==v['actualFailedCohortCollectionOperations']==v['ownThreadCount']==0 and len(v['rootRecoveryProbeAudit'])==27 and all(not r['recordPresent'] and r['trueProbeHits']==0 for r in v['rootRecoveryProbeAudit'].values()),'no Root/cohort effects')
        require(all(v[k] is False for k in ['actualFilesOpenedByProduct','rootMainInvoked','actualPermitIssueSignPublishOrRetire','formalUpdated','whole451Accepted','oldCoverageTransferred']) and v['effortPercent'] is None,'no authority or formal transfer')
    contract(p);labels=[]
    for key,value in [('actualExit',True),('source','OLD'),('originalManifestSha256','0'*64),('tests',3),('suites',1),('targetSourceUnits',1),('newTestIds',1),('cases',[]),('completeSourceUnitClosure',{}),('physicalClasses',{}),('executable',{}),('metadataClasses',[]),('unexecutedCodeClasses',[]),('totals',{}),('strictFour100GateExit',0),('targetUnitFour100',True),('allMeasuredApplicableCountersCovered',True),('manualCounterExclusions',['enum']),('singleSession',False),('crcMismatch',1),('publicEnumLabelsAndSerializationSchemaOnly',False),('cryptoOrKeyOperationsInvoked',True),('actualSecretKeysLoaded',True),('actualRootRecoveryOperations',1),('rootRecoveryProbeAudit',{}),('formalUpdated',True),('effortPercent',100)]:
        require(p[key]!=value,'nondegenerate '+key);bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false partial enum qualification '+key)
    designs={}
    for folder,number in [('330_DB・処理','331'),('340_batch・基盤','341'),('340_batch・基盤','343')]:
        # Unique document selection by number, with Git origin/main byte equality.
        matches=list((data.ROOT/'documents/300_SS').glob('*/'+number+'_*.md'));require(len(matches)==1,'unique approved SS')
        path=matches[0];relative=str(path.relative_to(data.ROOT));body=path.read_bytes()
        require(body==subprocess.check_output(['git','show','origin/main:'+relative],cwd=data.ROOT),'approved SS byte')
        designs[relative]=data.sha(body)
    for v in [p,old]:verify(v['invocation'])
    verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,postSha256=POST[1],rawSha256=RAW[1],tests=2,suites=2,semanticNegativeVectors=len(labels),negativeLabels=labels,independentOracleVectors=5,entryRegressionChecks=5,approvedDesignHashes=designs,productTestsReexecuted=0,newSourcePrograms=3,newPhysicalClasses=21,metadataPhysicalClasses=8,retainedPreviouslyQualifiedSourcePrograms=5,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()

