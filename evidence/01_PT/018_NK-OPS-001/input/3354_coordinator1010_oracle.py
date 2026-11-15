"""Exact original990 preservation plus declared same-target sequencing/independent wire vectors."""
from pathlib import Path
import json,hashlib,re,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';e=b/'evidence/PG33604-copy-coordinator1010-source-v1';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));pf=load(b/'input/3272_copyman990_constants_profile.json');base='src/schubert-nk-bootstrap/src/';main=base+'main/java/dev/codex/schubert/nk/migration/MigrationMasterCopyCoordinator.java';port=main.replace('MigrationMasterCopyCoordinator','MigrationCopyPort');test=main.replace('/main/','/test/').replace('.java','Test.java');parent=test.replace('MigrationMasterCopyCoordinatorTest','MigrationMasterTargetPublisherTest');maps=test.replace('MigrationMasterCopyCoordinatorTest','MigrationMasterCopyManifestTest');finger=test.replace('MigrationMasterCopyCoordinatorTest','MigrationMasterCopyFingerprintTest');old={}
for folder,source,paths in [('main',pf['productionCoreMain'],pf['mainSources']),('test','a8c52a44dc978db766e77beb92477319899d896f',[x['path'] for x in pf['testSources']])]:
 for path in paths:
  if path in [parent,maps,finger]:continue
  h=hashlib.sha256(subprocess.check_output(['git','show',source+':'+path])).hexdigest();assert sha(r/path)==h,path;old[path]=h
assert len(old)==95
# Preserve every whole prior Test body, including the three intentionally shared test-only fixtures.
def methods(s):return {m.group(1):m.group(0).strip() for m in re.finditer(r'  @Test\n  void (\w+)\([^\n]*\)[\s\S]*?(?=\n  @Test|\n  (?:private )?static)',s)}
counts={}
for path,expected in [(parent,38),(maps,12),(finger,20)]:
 a=methods((e/('original-'+Path(path).name+'.txt')).read_text());z=methods((r/path).read_text());assert len(a)==len(z)==expected and all(z[k]==v for k,v in a.items()),path;counts[Path(path).name]=expected
assert len(re.findall(r'@Test\b',(r/test).read_text()))==20
code=(r/main).read_text();assert all(s in code for s in ['target.getAutoCommit() || target.isReadOnly()','new MigrationMasterCopyManifest(mappings, declared)','publisher.prepare(target);','copy.copy(target, TABLES.get(index), rows.get(index))','publisher.transferAndFinalize(target, declared);'])
assert code.index('new MigrationMasterCopyManifest')<code.index('publisher.prepare')<code.index('copy.copy')<code.index('publisher.transferAndFinalize')
assert all(s not in code for s in ['.commit(','.rollback(','.close(','.setReadOnly(','.setAutoCommit(','catch ('])
p=(r/port).read_text();assert '@FunctionalInterface' in p and 'public interface MigrationCopyPort' in p and 'long copy(' in p and 'throws SQLException, IOException;' in p and 'default ' not in p and 'static ' not in p
v=load(b/'evidence/PG33314-copyman990-source-v1/independent-golden-vectors.json');t=(r/test).read_text();assert json.dumps(v['normal']['sha256']) in t and json.dumps(v['empty']['sha256']) in t
m=dict(actualExit=0,newCoordinator=ref(r/main),newPort=ref(r/port),newTest=ref(r/test),oldUnchangedSourceHashes=old,oldSharedWholeTestBodiesUnchanged=counts,modifiedTestFixtures=[ref(r/x) for x in [parent,maps,finger]],oldDefinitions990Preserved=True,independentCopyManifestGoldens=ref(b/'evidence/PG33314-copyman990-source-v1/independent-golden-vectors.json'),independentSixWireMetadata='MigrationMasterCopyFingerprintTest literal NORMAL_METADATA, not production expected generator',sameTargetPrepareCopyFinalizeSourceOrder=True,callerTxAndConnectionNeverOwned=True,fixedSixTables=True,abstractInterfaceNoCodeExpectedNeedsCompiledProof=True,newDefinitions=20,wholeExpected=1010,allMain=50,allTestSources=51,physicalClasses=70,actualDriverOrDbCurrentAssetNativeOrAuthority=0,newAcceptance=0,formalAccepted=False)
(e/'manifest.json').open('x').write(json.dumps(m,ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,new=20,whole=1010,oldSources=95,oldBodyCounts=counts))
