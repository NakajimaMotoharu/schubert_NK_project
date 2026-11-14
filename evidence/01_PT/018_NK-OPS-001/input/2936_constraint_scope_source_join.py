"""SSC383: verify final source delta and independent full-DDL scope, never actual DB execution."""
from pathlib import Path
import json,hashlib,re,subprocess,datetime
import pgpt_closed_host_profile as policy
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';e=b/'evidence/PG32232-constraint-trigger-scope-source-repair-v1';i=b/'input';oldunit='0cb9d3fde00cab9ca8e63d3f7f3f389efa1c8650';core='73e983a3549d60b72bd3ccfb1f4e4ff6723f2b38';mp='src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/migration/';tp='src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/migration/';paths=subprocess.check_output(['git','ls-tree','-r','--name-only',oldunit,'--',mp,tp],text=True).splitlines()
for p in paths:policy.relative_name(p)
changed=[];unchanged={};olddefs=newdefs=0
for p in paths:
 before=subprocess.check_output(['git','show',oldunit+':'+p]);after=(r/p).read_bytes()
 if before!=after:changed.append(p)
 else:unchanged[p]=hashlib.sha256(after).hexdigest()
 if p.startswith(tp):olddefs+=before.count(b'@Test');newdefs+=after.count(b'@Test')
assert set(changed)=={mp+'MigrationMasterConstraintVerifier.java',tp+'MigrationMasterConstraintVerifierTest.java',tp+'MigrationMasterTargetPublisherTest.java'} and olddefs==newdefs==705
q=json.loads((i/'2937_constraint_scope_independent_oracle.json').read_text());original=json.loads((i/'2928_constraint_independent_oracle.json').read_text());assert q['tables']==original['tables'] and q['sourceDdl']==original['sourceDdl'] and q['rows']==75 and len(q['sourceDdlConstraintTriggers'])==1
main=r/mp/'MigrationMasterConstraintVerifier.java';test=r/tp/'MigrationMasterConstraintVerifierTest.java';target=r/tp/'MigrationMasterTargetPublisherTest.java';strings=lambda s:[json.loads(v) for v in re.findall(r'"(?:[^"\\]|\\.)*"',s)];ms=main.read_text();ts=test.read_text();expected=ms[ms.index('  private static final List<List<String>> EXPECTED'):ms.index('  public void verify(')];assert strings(expected)==['\t'.join(row) for table in q['tables'].values() for row in table];block=ts[ts.index('  private static final List<List<String>> DATA'):ts.index('  @Test')];assert strings(block)==['\t'.join([str(j+1)]+row) for table in q['tables'].values() for j,row in enumerate(table)]
for p,count in [(main,1),(test,7),(target,12)]:assert p.read_text().count("k.contype NOT IN ('n','t')")==count and "k.contype<>'n'" not in p.read_text()
assert subprocess.check_output(['git','show',core+':'+str(main.relative_to(r))])==main.read_bytes();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));oldpost=b/'evidence/PG32218-constraint-target641-unit-v1/manifest.json';j=json.loads(oldpost.read_text());assert (j['actualExit'],j['tests'],j['failures'],j['errors'],j['skipped'])==(0,641,0,0,0)
out=dict(actualExit=0,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),productionCoreMain=core,previousUnit=oldunit,changed=changed,unchangedSourceHashes=unchanged,allMigrationMain=34,oldTestDefinitions=705,newTestDefinitions=705,newDefinitionsInCorrection=0,wholeScopeTests=641,original75MatrixAndDdlUnchanged=True,sourceDdlConstraintTriggers=q['sourceDdlConstraintTriggers'],knownNandTTypesSeparated=True,unknownTypesNotSuppressed=True,original641SourceQualified=False,oldRawRun=ref(oldpost),earlierManufactureSourceProof=ref(b/'evidence/PG32208-constraint-target641-source-v1/manifest.json'),scopeCorrection=ref(e/'scope-correction.json'),oracle=ref(i/'2937_constraint_scope_independent_oracle.json'),actualDatabaseOrNativeOperations=0,newAcceptance=0,whole451Accepted=False)
(e/'manifest.json').open('x').write(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,changedSources=len(changed),allDefinitions=705,old641Qualification=False,original75Unchanged=True))
