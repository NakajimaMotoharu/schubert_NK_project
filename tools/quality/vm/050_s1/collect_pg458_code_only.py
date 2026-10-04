"""Sanitized code-only provisioning witnesses, never native parent/formal acceptance."""
import datetime,hashlib,json,pathlib,re,subprocess
ROOT=pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
WORK=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
OUT=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG458-code-only-v1'
assert not OUT.exists();OUT.mkdir(mode=0o750)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
jobs=[];files=[]
for name,expected in [('pg458-stage-v1.log','PG458_STAGE '),('pg458-code-verify-v1.log','PG458_CODE_ONLY_VERIFIED '),('pg458-code-activate-v1.log','PG458_CODE_ONLY_ACTIVATED '),('pg458-watch-stage-v2.log','PG458_WATCH_STAGE_V2 '),('pg458-code-tool-test-v1.log','PG458_CODE_ONLY_TOOL_PASS ')]:
 raw=WORK/name;lines=[line for line in raw.read_text().splitlines() if re.fullmatch(r'PG(?:456|458)[A-Za-z0-9_.$:= /,-]+',line)]
 assert any(line.startswith(expected) for line in lines)
 p=OUT/'logs'/name.replace('.log','.txt');p.parent.mkdir(exist_ok=True);p.write_text('\n'.join(lines)+'\n')
 jobs.append({'privateLog':name,'privateLogSha256':sha(raw),'exitCode':0,'exitBasis':'actual tool session returned0; success flags are additional postconditions','safePath':str(p.relative_to(OUT))})
 files.append({'path':str(p.relative_to(OUT)),'sha256':sha(p)})
proof=json.loads((WORK/'pg458-runtime-proof-v3.json').read_text());assert set(proof)=={'protocol','storage','bootstrap','api','web','batch'}
assert all(p['allOriginalRuntimeJarBytesEqual'] and p['originalMainJarEqual'] and p['allInternalSharedMainJarsEqual'] and p['originalGavEqual'] for p in proof.values())
p=OUT/'runtime-proof.json';p.write_text(json.dumps(proof,indent=2)+'\n');files.append({'path':p.name,'sha256':sha(p)})
sourceFiles={str(p.relative_to(ROOT)):sha(p) for n in ('Pg458CodeOnlyDeployment.java','Pg458CodeOnlyDeploymentTest.java','pg458_stage_v1.py','pg458_stage_watch_v2.py','pg458_watch_parent.py','pg457_stable_actor.py') for p in [ROOT/'tools/quality/vm/050_s1'/n]}
manifest={'id':'PG458-code-only-v1','collectedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'branch':'dev-foundation',
 'hostHeadAtCollection':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'toolSourcesDirtyAtCollection':True,
 'productionSourceCommit':'ea1c13aa6a1b0fca2c2f4de1769a7c5afd70244a','previousSignedSource':'559bf7eacb401d6d07037dbdd295b32f174976a0',
 'signedRelease':'0.1.0-PG458','signedManifestSha256':'d0413fc29171dc69363ec173e1d37dcc8bf3d25da2f26cc474ca80b7b316d6b2',
 'environment':{'host':'Linux/JDK25.0.4/Maven3.9.12/Node24.19.0','guest':'Ubuntu26.04/PostgreSQL18.6/JDK25.0.4/Artemis2.56.0'},
 'commands':['javac -Xlint:all -Werror against actual guest16-class closed base; Pg458CodeOnlyDeploymentTest',
   'python3 pg458_stage_v1.py d0413fc29171dc69363ec173e1d37dcc8bf3d25da2f26cc474ca80b7b316d6b2',
   'guest sudo java Pg458CodeOnlyDeployment ea1c13aa6a1b0fca2c2f4de1769a7c5afd70244a d0413fc29171dc69363ec173e1d37dcc8bf3d25da2f26cc474ca80b7b316d6b2 verify|activate',
   'python3 pg458_stage_watch_v2.py'],
 'toolSourcesSha256':sourceFiles,'nativeToolClassSha256':'506331e0d414edf7ce449eafa3818da9a79b750eb5660111ac2a4972f141a1dd',
 'jobs':jobs,'testIds':['CODE458001','CODE458002','CODE458003'],'independentToolAssertions':42,'productionPtAdded':0,
 'expected':'literal signed027/current boot/old INVALID exact5, genuine M/A/DB, full261x14/all23business/originalPending/Backup20/Transfer preservation, all9 stopped, DDL/start/permit0; normal owned callback return only',
 'actual':'verify0 and activate0; signed current/approvalPG458/fresh INVALID; signed Unit delta0; all complete preservation/kernel/ownedclose flags confirmed',
 'hostFullRun':'PG458-caddy-timeout-full','hostFullManifestSha256':'9357f776614877674b9ac64e7791bdd385b8befbe35598ff04233e0ce77db8fd',
 'hostFullStartedAt':'2026-10-05T00:04:17+09:00','hostFullCompletedAt':'2026-10-05T00:21:40+09:00','hostFullExitCode':0,'hostFullTests':3254,'hostFullSuites':480,
 'hostCoverage100':False,'formal':False,'nativeParentAccepted':False,'bugs':['BUG-678','BUG-679'],'ykt':['YKT-483','YKT-484'],'ssc':['SSC-178','SSC-179'],
 'limitations':['Tool/native execution start/end timestamps were not recorded by original commands; collection time is not execution time',
 'Full host byte/source was frozen before runtime follow-up; standalone stale jars and partial fixture remain private; original PT is not rerun or combined with other source',
 'External parent started once, current execution pending; observer Root/ordinary/TLS/DONE/whole closure and native coverage/CHR/formal remain unaccepted',
 'Tool assertions42 cover arguments/namespace only, not production PT/coverage100; observer20 is separate'],
 'redaction':'Only fixed stage/postcondition flags, public source/hash and sanitized dependency proof. No original, DB dump, owner/permit, cookie/session/token/password/signing key.',
 'files':files}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'id':manifest['id'],'manifestSha256':sha(OUT/'manifest.json'),'formal':False,'nativeParentAccepted':False}))
