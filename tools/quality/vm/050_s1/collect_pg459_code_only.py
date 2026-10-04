"""Fixed allowlisted code-only evidence; private payloads never copied."""
import datetime, hashlib, json, pathlib, re, subprocess
ROOT=pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
WORK=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
OUT=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG459-code-only-v1'
assert not OUT.exists();OUT.mkdir(mode=0o750)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
jobs=[];files=[]
for name,flag in [('pg459-assemble-v1.log','migrationsSqlCount=27'),('pg459-stage-v1.log','PG459_STAGE '),('pg459-code-tool-test-v1.log','PG459_CODE_ONLY_TOOL_PASS '),('pg459-code-verify-v1.log','PG459_CODE_ONLY_VERIFIED '),('pg459-code-activate-v1.log','PG459_CODE_ONLY_ACTIVATED ')]:
 raw=WORK/name
 lines=[l for l in raw.read_text().splitlines() if re.fullmatch(r'[A-Za-z0-9_.$:= /,-]+',l) and (l.startswith('PG459') or 'migrationsSqlCount=' in l)]
 assert any(flag in l for l in lines),name
 p=OUT/'logs'/name.replace('.log','.txt');p.parent.mkdir(exist_ok=True);p.write_text('\n'.join(lines)+'\n')
 jobs.append({'testId':'CODE459-'+name,'privateLog':name,'privateSha256':sha(raw),'actualExitCode':0,'safePath':str(p.relative_to(OUT)),'timestamps':'execution timestamps not recorded in original command; not inferred from collection time'})
 files.append({'path':str(p.relative_to(OUT)),'sha256':sha(p)})
src=ROOT/'tools/quality/vm/050_s1'
sources={str(p.relative_to(ROOT)):sha(p) for n in ['Pg459CodeOnlyDeployment.java','Pg459CodeOnlyDeploymentTest.java','pg459_stage_v1.py','pg459_watch_parent.py','pg459_external_start_once.py','pg457_stable_actor.py'] for p in [src/n]}
full=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG459-caddy-cold-full/manifest.json'
m={'id':'PG459-code-only-v1','collectedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'branch':'dev-foundation','hostHeadAtCollection':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'toolSourcesDirtyAtCollection':True,
 'productionSourceCommit':'8e97eb9138828010926cd47fd10868d8a2d54f11','previousSource':'ea1c13aa6a1b0fca2c2f4de1769a7c5afd70244a','signedRelease':'0.1.0-PG459','schema':'027','manifestSha256':'88a6504f93782c65e2328bd719db4133bdc2b3457d0495c9e5887d084fd38311',
 'environment':{'host':'Linux/JDK25.0.4/Maven3.9.12/Node24.19.0','guest':'Ubuntu26.04/PostgreSQL18.6/JDK25.0.4/Artemis2.56.0'},'toolSourcesSha256':sources,'nativeToolClassSha256':sha(WORK/'pg459-code-tools-v1/Pg459CodeOnlyDeployment.class'),
 'commands':['javac -Xlint:all -Werror; Pg459CodeOnlyDeploymentTest (46 independent argument/namespace assertions)','AssembleReleaseFixture <repo> pg459-release-v1 8e97eb9138828010926cd47fd10868d8a2d54f11 0.1.0-PG459 <effective-profile> <public-recipient>','python3 pg459_stage_v1.py <signed manifest digest>','guest sudo java --enable-native-access=ALL-UNNAMED -cp <new singleton + preserved16 + signed runtime> Pg459CodeOnlyDeployment <source> <digest> verify|activate'],
 'expected':'literal signed027/27SQL/old INVALID9 current boot; genuine M/A/DB; all271x14/all23business/originalPending/Backup/Transfer/old8record preservation; all9kernel empty; DDL/start/permit0; all owned scopes return normally',
 'actual':'assembly/stage/verify/activate0; full185BOM independently checked; freshINVALID and approval/currentPG459; unchanged signed27SQL/config/all Units; all preservation/terminal/normal owned return flags verified',
 'independentToolAssertions':46,'productionPtAdded':0,'jobs':jobs,'files':files,'hostFullRun':json.loads(full.read_text())['id'],'hostFullManifestSha256':sha(full),'hostFullTests':3257,'hostFullSuites':480,'hostFullExitCode':0,
 'hostCoverage100':False,'formal':False,'nativeParentAccepted':False,'bugs':['BUG-683','BUG-684'],'ykt':['YKT-488','YKT-489'],'ssc':['SSC-180'],'limitations':['Native parent is independently running and not accepted by code-only evidence','Tool assertions do not qualify production coverage','Private original/DB/owner/permit/credentials remain outside Git'],'redaction':'Fixed flags and public source/hash only; no token, cookie, session ID, password, key, DB dump or originals.'}
(OUT/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'id':m['id'],'manifestSha256':sha(OUT/'manifest.json'),'formal':False,'nativeParentAccepted':False}))
