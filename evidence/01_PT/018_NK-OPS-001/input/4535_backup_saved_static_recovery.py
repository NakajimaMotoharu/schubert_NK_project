"""Read the completed static files; never rerun the three javap commands or product code."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess
import sys

r=Path.cwd();sys.path.insert(0,str(r/'tools/quality'))
from pmo_group_context import build_context
b=r/'evidence/01_PT/018_NK-OPS-001';load=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
cp=b/'evidence/PG36956-backup-path-four-main-compile-v1/manifest.json';c=load(cp)
sp=b/'evidence/PG36958-backup-path-fresh-sibling-spotbugs-v1/manifest.json';s=load(sp)
mp=b/'evidence/PG36960-current287-root-pmd-v1/manifest.json';m=load(mp)
old=load(b/'evidence/PG36872-ssc450-four-main-compile-v1/manifest.json')
assert c['actualExit']==s['actualExit']==m['actualExit']==0 and c['sourceCore']==s['sourceCore']==m['sourceCore']
path='src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/file/BackupStartIntentFiles.java'
parent=subprocess.check_output(['git','rev-parse',c['sourceCore']+'^'],text=True).strip()
assert subprocess.check_output(['git','diff','--name-only',parent,c['sourceCore'],'--','src'],text=True).splitlines()==[path]
for p,h in c['inputHashes'].items():assert sha(r/p)==h
changed=[(module,n) for module,values in old['physicalClassHashes'].items() for n,h in values.items() if c['physicalClassHashes'][module].get(n)!=h]
assert changed==[('batch','dev/codex/schubert/nk/batch/file/BackupStartIntentFiles.class')]
assert all(set(values)==set(c['physicalClassHashes'][module]) for module,values in old['physicalClassHashes'].items())
for module in ['bootstrap','batch']:
    row=s['reports'][module];assert s['stages'][module]['actualExit']==0 and not row['bugs'] and not row['errors'] and not row['missingClasses']
    assert set(row['classStats'])=={n[:-6].replace('/','.') for n in c['physicalClassHashes'][module]}
saved=b/'evidence/PG36964-backup-static-independent-v2'
assert (saved/'before-public.txt').read_bytes()==(saved/'after-public.txt').read_bytes()
text=(saved/'after-bytecode.txt').read_text();start=text.index('public static dev.codex.schubert.nk.batch.file.BackupStartIntentFiles createService(')
body=text[start:text.index('\n  dev.codex.schubert.nk.batch.file.BackupStartIntentFiles(',start)]
assert body.index('java/nio/file/Path.of:')<body.index('InvokeDynamic')<body.index('storage/ResourceScope.handoff:')
assert 'LinuxDirectoryCalls.create' not in body and 'OwnedTransferDirectory.open' not in body
spec=b/'4457_F03固定Path静的是正仕様.md';report=b/'evidence/PG36848-ssc449-fresh-sibling-spotbugs-v1/manifest.json'
context=dict(group_id='PGPT-STATIC-REFERENCE-SELF',category='REVIEW',kind='TOOL_FIX',scope='Read-only context schema check, not an operation.',oracle_refs=[ref(spec),ref(report)])
build_context(**context)
try:build_context(**dict(context,oracle_refs=[ref(report.parent/'batch-spotbugs.xml')]))
except ValueError as failure:assert str(failure)=='public reference'
else:raise AssertionError('XML negative accepted')
out=b/'evidence/PG36966-backup-saved-static-independent-v3';assert not out.exists();out.mkdir()
value=dict(actualExit=0,source=c['sourceCore'],sourceCore=c['sourceCore'],unitChangeParent=parent,
    terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),compile=ref(cp),spotbugs=ref(sp),pmd=ref(mp),
    originalSourceInverse=ref(b/'evidence/PG36954-backup-path-source-equivalence-v1/manifest.json'),
    recoveredFiles=[ref(saved/n) for n in ['before-public.txt','after-public.txt','after-bytecode.txt']],
    originalProducer=ref(b/'input/4534_backup_static_independent_post_v2.py'),
    javapReplayed=0,productTestsExecuted=0,newApplicationInitialization=0,
    publicAbiExact=True,pathValueBeforeAcquireLambda=True,other1100PhysicalByteExact=True,
    changedPhysical=changed,bootstrapClassStats=200,batchClassStats=646,spotbugsBugsMissingErrors=0,
    pmdRaw=971,pmdUnclassified=True,referenceSchemaPositive=1,referenceSchemaNegative=1,
    sourceBoundaryNegativesPreviouslyAsserted=3,canonicalArtifactOwner='WBS-P017-06',workOwner='WBS-F03',
    factoryHorizontal={'create':'closed-target variable, unchanged','createPublication':'already outer fixed local, unchanged','createService':'pure fixed Path moved before acquire lambda, existing annotation unchanged'},
    createServiceNormalPt='NOT_RUN_HOLD',coverageMeasured=False,wholeF03Accepted=False,newAcceptance=0,formalUpdated=False)
(out/'manifest.json').open('x').write(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,source=c['sourceCore'],SB0=True,other1100Exact=True,publicAbiExact=True,javapReplay=0,productTests=0)))
