"""Publish only approved internal SS supplement and its ledger using ordinary PR rules."""
from pathlib import Path
import datetime,hashlib,json,subprocess,time
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';patchfile=b/'evidence/PG34740-ssc435-aad-cleanup-design-only-v1/design-only-main-patch.json';v=json.loads(patchfile.read_text());w=r.parent/'ssc435-aad-acquire-design-20261116';private=r.parent/'pgpt-runs/PG379/pg34742-ssc435-design';e=b/'evidence/PG34742-ssc435-design-main-publication-v1';assert not (e/'manifest.json').exists();private.mkdir(mode=0o700,exist_ok=True);e.mkdir(exist_ok=True)
def run(args,cwd=r):return subprocess.check_output(args,cwd=cwd,stderr=subprocess.STDOUT,text=True).strip()
assert hashlib.sha256(v['patch'].encode()).hexdigest()==v['patchUtf8Sha256'];assert run(['git','rev-parse','origin/main'])==v['baseMain']
branch='docs/ssc435-aad-acquire-20261116'
if not w.exists():
 run(['git','worktree','add','-b',branch,str(w),'origin/main'])
 f=private/'design.patch';f.write_text(v['patch']);run(['git','apply','--check',str(f)],w);run(['git','apply',str(f)],w)
else:
 assert run(['git','branch','--show-current'],w)==branch and run(['git','rev-parse','HEAD'],w)==v['baseMain']
 assert run(['git','diff','--cached','--name-only'],w)==''
 saved=private/'design.patch';assert saved.read_text()==v['patch']
 run(['git','apply','--reverse','--check',str(saved)],w)
names=[x for x in run(['git','diff','--name-only','-z'],w).split('\0') if x];assert set(names)==set(v['paths']);run(['git','diff','--check'],w);run(['git','add','--',*v['paths']],w);run(['git','commit','-m','docs(ssc435): specify protected AAD field acquisition and original value contracts'],w);head=run(['git','rev-parse','HEAD'],w);run(['git','push','-u','origin',branch],w)
body=private/'pr-body.txt';body.write_text('SSC435 closes ownedAAD acquisition outside cleanup: create only six empty slots before try, assign original6 expressions in exact original order inside try, then same length/BE/return and finallyeraseFields once. Thus original nullversion failure erases acquired metadata; same normal113byteAAD/publicAPI/exceptiontype/QA050. Original5/source expectations byteexact, freshMain5Root/static/current182CRC-init/XML/rawsix mandatoryfour. Prior SSC434 LINE1 remains OPEN until newsourceproof; no OOM/reflection/exclusion/oldexecunion/actualDB-key-JMS-retry/Root2Actual4/VM/native/aru/HOLD. SS311331352914 only, no implementation/evidence/formal.\n')
url=run(['gh','pr','create','--repo','NakajimaMotoharu/schubert_NK_project','--base','main','--head',branch,'--title','docs(ssc435): Revocation AAD所有field取得をcleanup領域へ移す','--body-file',str(body)],w)
for attempt in range(6):
 review=json.loads(run(['gh','pr','view',url,'--json','headRefOid,mergeStateStatus,reviewDecision,statusCheckRollup,files'],w))
 if review['mergeStateStatus']!='UNKNOWN':break
 time.sleep(1)
assert review['headRefOid']==head and {x['path'] for x in review['files']}==set(v['paths']) and review['mergeStateStatus']=='CLEAN'
assert all(x.get('conclusion') in [None,'SUCCESS','SKIPPED','NEUTRAL'] and x.get('state') not in ['FAILURE','ERROR','PENDING'] for x in review['statusCheckRollup'])
run(['gh','pr','merge',url,'--merge','--match-head-commit',head],w);run(['git','fetch','origin','main']);main=run(['git','rev-parse','origin/main']);assert run(['git','merge-base','--is-ancestor',head,'origin/main'])==''
for name in v['paths']:assert run(['git','show','origin/main:'+name])==run(['git','show',head+':'+name])
ledger=r/'documents/900_OTHER/910_台帳/914_詳細設計修正管理台帳.md';t=ledger.read_text();at=t.index('## SSC-430');t=t[:at]+t[at:].replace('main反映前','main反映済み（'+url+'、'+main+'）',1);ledger.write_text(t)
result=dict(actualExit=0,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),ssc='SSC435',baseMain=v['baseMain'],designSource=head,mainCommit=main,pr=url,paths=v['paths'],ordinaryMerge=True,implementationIncluded=False,formalAccepted=False);(e/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False))
