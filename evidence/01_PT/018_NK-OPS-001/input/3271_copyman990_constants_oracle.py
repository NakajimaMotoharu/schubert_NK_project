"""Declared COPY artifact oracle; prior whole976 reused only for unchanged source proof."""
from pathlib import Path
import re,json,hashlib,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';e=b/'evidence/PG33314-copyman990-source-v1';i=b/'input';load=lambda p:json.loads(p.read_text());ref=lambda p:dict(path=str(p.relative_to(r)),sha256=hashlib.sha256(p.read_bytes()).hexdigest());pf=load(i/'3250_mapverify976_column_profile.json');base='src/schubert-nk-bootstrap/src/';main=base+'main/java/dev/codex/schubert/nk/migration/MigrationMasterCopyManifest.java';test=main.replace('/main/','/test/').replace('.java','Test.java');am=main.replace('MigrationMasterCopyManifest','CurrentMigrationAssembler');at=test.replace('MigrationMasterCopyManifestTest','CurrentMigrationAssemblerTest');ft=test.replace('MigrationMasterCopyManifestTest','MigrationMasterCopyFingerprintTest');old={}
for folder,source,paths in [('main',pf['productionCoreMain'],pf['mainSources']),('test','b5de21c03d2966032d0a89ef41dcf14e19656c2c',[x['path'] for x in pf['testSources']])]:
 for path in paths:
  if path in [am,at,ft]:continue
  h=hashlib.sha256(subprocess.check_output(['git','show',source+':'+path])).hexdigest();assert ref(r/path)['sha256']==h,path;old[path]=h
assert len(old)==93 and sum(len(re.findall(r'@Test\b',(r/p).read_text())) for p in old if '/test/' in p)==934
before=(e/'original-CurrentMigrationAssembler.java.txt').read_text();now=(r/am).read_text();a=now.index('  /** SSC410,');z=now.index('  public CurrentMigrationMappingManifest mappingManifest()',a)
assert now[:a]+now[z:]==before.replace('import java.security.NoSuchAlgorithmException;','import java.io.IOException;\nimport java.security.NoSuchAlgorithmException;')
def methods(s):return {m.group(1):m.group(0).strip() for m in re.finditer(r'  @Test\n  void (\w+)\([^\n]*\)[\s\S]*?(?=\n  @Test|\n  private static)',s)}
a=methods((e/'original-CurrentMigrationAssemblerTest.java.txt').read_text());z=methods((r/at).read_text());assert len(a)==22 and len(z)==24 and all(z[k]==v for k,v in a.items())
assert (r/ft).read_text()==(e/'original-MigrationMasterCopyFingerprintTest.java.txt').read_text().replace('  private static MigrationMasterCopyDataset normal() throws Exception {','  static MigrationMasterCopyDataset normal() throws Exception {')
v=load(e/'independent-golden-vectors.json');t=(r/test).read_text();assert len(re.findall(r'@Test\b',t))==12
for key in ['normal','empty','differentMapping']:assert json.dumps(v[key]['canonical']) in t and json.dumps(v[key]['sha256']) in t
for key,vector in v.items():assert hashlib.sha256(vector['canonical'].encode('ascii')).hexdigest()==vector['sha256'] and hashlib.sha256(vector['mappingCanonical'].encode('ascii')).hexdigest()==vector['mappingSha256'] and len(vector['canonical'])==vector['bytes']
code=(r/main).read_text();assert all(x in code for x in ['new MigrationMasterCopyFingerprint().fingerprint(declared)','return retainedBytes.clone();','Map.of(','counts.get("FILES")','counts.get("ENTRIES")','counts.get("SPEAKERS")','counts.get("AUDIO")'])
m=dict(actualExit=0,newMain=ref(r/main),newTest=ref(r/test),changedAssembler=ref(r/am),changedAssemblerTest=ref(r/at),fixtureVisibilityOnly=ref(r/ft),allOld22AssemblerTestBodiesByteUnchanged=True,allOld20FingerprintTestBodiesByteUnchanged=True,assemblerOnlyCopyFactoryAndImportAdded=True,oldUnchangedSourceHashes=old,independentGoldens=ref(e/'independent-golden-vectors.json'),assemblerMappingGolden=ref(e/'assembler-mapping-golden.json'),newDefinitions=14,newManifestTests=12,newAssemblerTests=2,oldDefinitions=976,wholeExpected=990,allMain=48,allTestSources=50,physicalClasses=68,actualCurrentOrFileOrDbAccess=False,authorityIssued=False,newAcceptance=0,formalAccepted=False)
(e/'part-constants-corrected-manifest.json').open('x').write(json.dumps(m,ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,new=14,whole=990,oldSource=93))
