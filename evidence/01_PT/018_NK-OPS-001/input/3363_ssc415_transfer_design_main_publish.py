"""Publish only approved internal SS supplement and its ledger using ordinary PR rules."""
from pathlib import Path
import datetime,hashlib,json,subprocess,time
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';patchfile=b/'evidence/PG33624-ssc415-current-transfer-design-only-v1/design-only-main-patch.json';v=json.loads(patchfile.read_text());w=r.parent/'ssc415-current-transfer-design-20261115';private=r.parent/'pgpt-runs/PG379/pg33626-ssc415-design';e=b/'evidence/PG33626-ssc415-design-main-publication-v1';assert not (e/'manifest.json').exists();private.mkdir(mode=0o700,exist_ok=True);e.mkdir(exist_ok=True)
def run(args,cwd=r):return subprocess.check_output(args,cwd=cwd,stderr=subprocess.STDOUT,text=True).strip()
assert hashlib.sha256(v['patch'].encode()).hexdigest()==v['patchUtf8Sha256'];assert run(['git','rev-parse','origin/main'])==v['baseMain']
branch='docs/ssc415-current-transfer-20261115'
if not w.exists():
 run(['git','worktree','add','-b',branch,str(w),'origin/main'])
 f=private/'design.patch';f.write_text(v['patch']);run(['git','apply','--check',str(f)],w);run(['git','apply',str(f)],w)
else:
 assert run(['git','branch','--show-current'],w)==branch and run(['git','rev-parse','HEAD'],w)==v['baseMain']
 assert run(['git','diff','--cached','--name-only'],w)==''
 saved=private/'design.patch';assert saved.read_text()==v['patch']
 run(['git','apply','--reverse','--check',str(saved)],w)
names=[x for x in run(['git','diff','--name-only','-z'],w).split('\0') if x];assert set(names)==set(v['paths']);run(['git','diff','--check'],w);run(['git','add','--',*v['paths']],w);run(['git','commit','-m','docs(ssc415): specify borrowed Current-to-target assembly and COPY path'],w);head=run(['git','rev-parse','HEAD'],w);run(['git','push','-u','origin',branch],w)
body=private/'pr-body.txt';body.write_text('SSC415: join five Current readers, same immutable assembler mapping/dataset and existing borrowed target sixCOPY coordinator. New20/full1030 planned, typed counts and boundary/fail-stop/golden/finite64 contracts; original50Main and1010 Test bodies preserved. No actual DB/driver/snapshot/authority/native/Root/HOLD admission. Internal supplement only SS311/343/914, code/config/tools/evidence excluded. Validation exact design-only diff and independent source-to-target literal/SHA expectations. Additional3/9/9.9cap10, original fees and formal acceptance unchanged.\n')
url=run(['gh','pr','create','--repo','NakajimaMotoharu/schubert_NK_project','--base','main','--head',branch,'--title','docs(ssc415): Current読取から六COPYへの一経路','--body-file',str(body)],w)
for attempt in range(6):
 review=json.loads(run(['gh','pr','view',url,'--json','headRefOid,mergeStateStatus,reviewDecision,statusCheckRollup,files'],w))
 if review['mergeStateStatus']!='UNKNOWN':break
 time.sleep(1)
assert review['headRefOid']==head and {x['path'] for x in review['files']}==set(v['paths']) and review['mergeStateStatus']=='CLEAN'
assert all(x.get('conclusion') in [None,'SUCCESS','SKIPPED','NEUTRAL'] and x.get('state') not in ['FAILURE','ERROR','PENDING'] for x in review['statusCheckRollup'])
run(['gh','pr','merge',url,'--merge','--match-head-commit',head],w);run(['git','fetch','origin','main']);main=run(['git','rev-parse','origin/main']);assert run(['git','merge-base','--is-ancestor',head,'origin/main'])==''
for name in v['paths']:assert run(['git','show','origin/main:'+name])==run(['git','show',head+':'+name])
ledger=r/'documents/900_OTHER/910_台帳/914_詳細設計修正管理台帳.md';t=ledger.read_text();at=t.index('## SSC-415');t=t[:at]+t[at:].replace('main公開待ち','main公開済み（'+url+'、'+main+'）',1);ledger.write_text(t)
result=dict(actualExit=0,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),ssc='SSC415',baseMain=v['baseMain'],designSource=head,mainCommit=main,pr=url,paths=v['paths'],ordinaryMerge=True,implementationIncluded=False,formalAccepted=False);(e/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False))
