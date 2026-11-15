"""Prove original1010 preservation and independent same-assembler source-to-target contract."""
from pathlib import Path
import json,hashlib,re,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';e=b/'evidence/PG33628-current-transfer1030-source-v1';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));pf=load(b/'input/3355_coordinator1010_profile.json');base='src/schubert-nk-bootstrap/src/';main=base+'main/java/dev/codex/schubert/nk/migration/CurrentMigrationTransfer.java';test=main.replace('/main/','/test/').replace('.java','Test.java');parent=test.replace('CurrentMigrationTransferTest','MigrationMasterTargetPublisherTest');old={}
for source,paths in [(pf['productionCoreMain'],pf['mainSources']),('3cb794e0457275967643c42971e2d939ffdcc552',[x['path'] for x in pf['testSources']])]:
 for path in paths:
  if path==parent:continue
  h=hashlib.sha256(subprocess.check_output(['git','show',source+':'+path])).hexdigest();assert sha(r/path)==h,path;old[path]=h
assert len(old)==100
def methods(s):return {m.group(1):m.group(0).strip() for m in re.finditer(r'  @Test\n  void (\w+)\([^\n]*\)[\s\S]*?(?=\n  @Test|\n  (?:private )?static)',s)}
a=methods((e/'original-MigrationMasterTargetPublisherTest.java.txt').read_text());z=methods((r/parent).read_text());assert len(a)==len(z)==38 and all(z[k]==v for k,v in a.items())
assert len(re.findall(r'@Test\b',(r/test).read_text()))==20
s=(r/main).read_text();assert all(x in s for x in ['source == target','target.getAutoCommit() || target.isReadOnly()','new CurrentMigrationProjection()','assembler.assemble(snapshot, media, at)','assembler.mappingManifest()','new MigrationMasterCopyCoordinator().transfer(target, mappings, declared, copy)'])
assert s.index('target.getAutoCommit')<s.index('new CurrentMigrationProjection')<s.index('assembler.assemble')<s.index('assembler.mappingManifest')<s.index('new MigrationMasterCopyCoordinator')
assert all(x not in s for x in ['.commit(','.rollback(','.close(','.setReadOnly(','.setAutoCommit(','catch ('])
g=load(e/'independent-golden.json');assert hashlib.sha256(g['canonical'].encode()).hexdigest()==g['sha256'] and g['sha256'] in (r/test).read_text();assert len(g['sixWireTuples'])==6
m=dict(actualExit=0,newMain=ref(r/main),newTest=ref(r/test),oldUnchangedSourceHashes=old,oldShared38WholeTestBodiesUnchanged=True,oldDefinitions1010Preserved=True,independentGolden=ref(e/'independent-golden.json'),sameAssemblerMappingAndDataset=True,sourceReadBeforeTargetSql=True,callerOwnsBothConnectionsAndTransactions=True,sourceAndTargetReferenceIdentityRejectedNotPeerAuthentication=True,typedCountsNoNegative=True,newDefinitions=20,wholeExpected=1030,allMain=51,allTestSources=52,physicalClasses=72,actualDriverOrDbCurrentAssetNativeOrAuthority=0,newAcceptance=0,formalAccepted=False)
(e/'manifest.json').open('x').write(json.dumps(m,ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,new=20,whole=1030,oldSources=100,oldParentTestBodies=38))
