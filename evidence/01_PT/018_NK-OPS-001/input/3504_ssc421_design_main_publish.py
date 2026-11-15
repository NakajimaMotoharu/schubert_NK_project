"""Publish only approved internal SS supplement and its ledger using ordinary PR rules."""
from pathlib import Path
import datetime,hashlib,json,subprocess,time
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';patchfile=b/'evidence/PG33800-ssc421-auth-context-design-only-v1/design-only-main-patch.json';v=json.loads(patchfile.read_text());w=r.parent/'ssc421-auth-context-design-20261115';private=r.parent/'pgpt-runs/PG379/pg33802-ssc421-design';e=b/'evidence/PG33802-ssc421-design-main-publication-v1';assert not (e/'manifest.json').exists();private.mkdir(mode=0o700,exist_ok=True);e.mkdir(exist_ok=True)
def run(args,cwd=r):return subprocess.check_output(args,cwd=cwd,stderr=subprocess.STDOUT,text=True).strip()
assert hashlib.sha256(v['patch'].encode()).hexdigest()==v['patchUtf8Sha256'];assert run(['git','rev-parse','origin/main'])==v['baseMain']
branch='docs/ssc421-auth-context-20261115'
if not w.exists():
 run(['git','worktree','add','-b',branch,str(w),'origin/main'])
 f=private/'design.patch';f.write_text(v['patch']);run(['git','apply','--check',str(f)],w);run(['git','apply',str(f)],w)
else:
 assert run(['git','branch','--show-current'],w)==branch and run(['git','rev-parse','HEAD'],w)==v['baseMain']
 assert run(['git','diff','--cached','--name-only'],w)==''
 saved=private/'design.patch';assert saved.read_text()==v['patch']
 run(['git','apply','--reverse','--check',str(saved)],w)
names=[x for x in run(['git','diff','--name-only','-z'],w).split('\0') if x];assert set(names)==set(v['paths']);run(['git','diff','--check'],w);run(['git','add','--',*v['paths']],w);run(['git','commit','-m','docs(ssc421): specify protect API context acquisition and bound fixture workers'],w);head=run(['git','rev-parse','HEAD'],w);run(['git','push','-u','origin',branch],w)
body=private/'pr-body.txt';body.write_text('SSC421 API AuthContextCodec encrypt/decrypt owned buffer acquisition moves inside existing cleanup region, preserving NKENC1/AES256GCM/nonce/AAD/keys/API/errors. Original7 business assertions and independent DataOutput/JCA vectors retained; old2 fixture pools get bounded Future and termination-first close; new public deterministic nonce Error then other-worker normal golden case gives whole8. Fresh Main5/current Protocol exactbyte/static/sameexec mandatoryfour CRC qualification required. Supplement instruction misses preserved and no fullscope/actualprivate key/DB/RootActual4/VM/native/SDK/aru admission. Only SS311314352914 to main, no implementation/config/tools/evidence or formal acceptance.\n')
url=run(['gh','pr','create','--repo','NakajimaMotoharu/schubert_NK_project','--base','main','--head',branch,'--title','docs(ssc421): API認証context取得保護と有限単体fixture','--body-file',str(body)],w)
for attempt in range(6):
 review=json.loads(run(['gh','pr','view',url,'--json','headRefOid,mergeStateStatus,reviewDecision,statusCheckRollup,files'],w))
 if review['mergeStateStatus']!='UNKNOWN':break
 time.sleep(1)
assert review['headRefOid']==head and {x['path'] for x in review['files']}==set(v['paths']) and review['mergeStateStatus']=='CLEAN'
assert all(x.get('conclusion') in [None,'SUCCESS','SKIPPED','NEUTRAL'] and x.get('state') not in ['FAILURE','ERROR','PENDING'] for x in review['statusCheckRollup'])
run(['gh','pr','merge',url,'--merge','--match-head-commit',head],w);run(['git','fetch','origin','main']);main=run(['git','rev-parse','origin/main']);assert run(['git','merge-base','--is-ancestor',head,'origin/main'])==''
for name in v['paths']:assert run(['git','show','origin/main:'+name])==run(['git','show',head+':'+name])
ledger=r/'documents/900_OTHER/910_台帳/914_詳細設計修正管理台帳.md';t=ledger.read_text();at=t.index('## SSC-421');t=t[:at]+t[at:].replace('main反映前','main反映済み（'+url+'、'+main+'）',1);ledger.write_text(t)
result=dict(actualExit=0,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),ssc='SSC421',baseMain=v['baseMain'],designSource=head,mainCommit=main,pr=url,paths=v['paths'],ordinaryMerge=True,implementationIncluded=False,formalAccepted=False);(e/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False))
