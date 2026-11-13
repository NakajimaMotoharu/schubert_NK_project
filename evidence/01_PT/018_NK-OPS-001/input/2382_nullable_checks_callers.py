"""SSC340 migration-29 oracle alignment, retaining old golden checks and legacy-28 scenario."""
from pathlib import Path
import datetime,json,hashlib,subprocess,re
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';e=b/'evidence/PG29704-nullable-check-caller-source-alignment-v1';assert not e.exists();e.mkdir();root=r/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();changes=[]
inputs={
'database/DatabaseMigrationTest.java': [('            "migration/V028__retained_success_progress_seals.sql",','            "migration/V028__retained_success_progress_seals.sql",\n            "migration/V029__strict_nullable_compound_checks.sql",')],
'database/StartupSchemaProjectionTest.java': [('"027", "028");','"027", "028", "029");'),('// SSC201: 28 versioned rows plus the unchanged schema-creation row.','// SSC340: 29 versioned rows plus the unchanged schema-creation row.'),('assertEquals(29, rank + 1);','assertEquals(30, rank + 1);')],
'maintenance/InspectionParentBoundaryTest.java': [('"025", "026", "027", "028"),','"025", "026", "027", "028", "029"),'),('027,028",','027,028,029",'),('assertEquals("28", MigrationInventory.COUNT_TEXT);','assertEquals("29", MigrationInventory.COUNT_TEXT);'),('assertEquals(28, files.size());','assertEquals(29, files.size());')],
'maintenance/StepCleanupBoundaryTest.java': [('assertEquals(28, files.size());','assertEquals(29, files.size());'),('"V028__retained_success_progress_seals.sql", files.getLast().getFileName().toString());','"V028__retained_success_progress_seals.sql", files.get(27).getFileName().toString());\n    assertEquals(\n        "V029__strict_nullable_compound_checks.sql", files.getLast().getFileName().toString());'),('"025", "026", "027", "028"),','"025", "026", "027", "028", "029"),'),('"28|1",','"29|1",')]
}
for name,pairs in inputs.items():
 p=root/name;t=p.read_text();(e/(p.name+'.before.txt')).write_text(t);new=t;counts=[]
 for a,z in pairs:
  count=new.count(a);assert count in [1,2],(name,a,count);counts.append(count);new=new.replace(a,z)
 inverse=new
 for a,z in reversed(pairs):inverse=inverse.replace(z,a)
 assert inverse==t
 p.write_text(new);changes.append(dict(path=str(p.relative_to(r)),beforeSha256=hashlib.sha256(t.encode()).hexdigest(),afterSha256=sha(p),replacementCounts=counts,exactInverseEqual=True,reason='Approved SSC340 V029 resource/version count only, old literal checksum assertions unchanged'))
paths=subprocess.check_output(['git','grep','-l','MigrationInventory','--','src',':(exclude,glob)**/RootFailedStartRecoveryTest.java',':(exclude,glob)**/RootFailedStartPairRecoveryTest.java'],text=True).splitlines();assert len(paths)==16
callers=[]
for name in paths:
 p=r/name;callers.append(dict(path=name,sha256=sha(p),disposition=('APPROVED_EXPLICIT_VERSION_29_SOURCE_UPDATED' if name in [x['path'] for x in changes]+[str((root/'database/MigrationInventory.java').relative_to(r))] else 'SHARED_APPROVED_INVENTORY_REFERENCE_SOURCE_UNCHANGED_NO_HARDCODED_CURRENT28_FOUND'),runtimeState='NOT_RUN_DB_HOLD'))
m=dict(actualExit=0,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),SSC='SSC-340',changes=changes,sharedInventoryAndCallers=callers,oldDatabase19OnlyResourceInventoryAddsV029=True,legacyUpgradeTarget28Unchanged=True,oldFrozenChecksumsUnchanged=True,normalCurrentVersion=29,productTestsExecuted=0,coverage=None,formalAcceptanceAdded=0,wholeDbTests='HOLD_NOT_RUN_SOURCE_ALIGNED')
(e/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');print('4 explicit oracle consumers aligned to approved29;16 inventory/consumer paths indexed; old hash goldens and legacy28 unchanged; DB NOT_RUN')
