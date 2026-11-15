"""Publish only approved internal SS supplement and its ledger using ordinary PR rules."""
from pathlib import Path
import datetime,hashlib,json,subprocess,time
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';patchfile=b/'evidence/PG35500-ssc440-public-namespace-design-only-v1/design-only-main-patch.json';v=json.loads(patchfile.read_text());w=r.parent/'ssc440-public-namespace-design-20261116';private=r.parent/'pgpt-runs/PG379/pg35502-ssc440-design';e=b/'evidence/PG35502-ssc440-design-main-publication-v1';assert not (e/'manifest.json').exists();private.mkdir(mode=0o700,exist_ok=True);e.mkdir(exist_ok=True)
def run(args,cwd=r):return subprocess.check_output(args,cwd=cwd,stderr=subprocess.STDOUT,text=True).strip()
assert hashlib.sha256(v['patch'].encode()).hexdigest()==v['patchUtf8Sha256'];assert run(['git','rev-parse','origin/main'])==v['baseMain']
branch='docs/ssc440-public-namespace-20261116'
if not w.exists():
 run(['git','worktree','add','--no-checkout','-b',branch,str(w),'origin/main'])
 run(['git','sparse-checkout','set','--no-cone',*['/'+n for n in v['paths']]],w)
 run(['git','read-tree','-mu','HEAD'],w)
 assert not (w/'src').exists() and not (w/'tools').exists() and not (w/'evidence').exists()
 assert run(['git','status','--porcelain'],w)==''
 f=private/'design.patch';f.write_text(v['patch']);run(['git','apply','--check',str(f)],w);run(['git','apply',str(f)],w)
else:
 assert run(['git','branch','--show-current'],w)==branch and run(['git','rev-parse','HEAD'],w)==v['baseMain']
 assert run(['git','diff','--cached','--name-only'],w)==''
 saved=private/'design.patch';assert saved.read_text()==v['patch']
 run(['git','apply','--reverse','--check',str(saved)],w)
names=[x for x in run(['git','diff','--name-only','-z'],w).split('\0') if x];assert set(names)==set(v['paths']);run(['git','diff','--check'],w);run(['git','add','--',*v['paths']],w);run(['git','commit','-m','docs(ssc440): retain public utility contracts as stateless namespaces'],w);head=run(['git','rev-parse','HEAD'],w);run(['git','push','-u','origin',branch],w)
body=private/'pr-body.txt';body.write_text('SSC440: three public utilities become static-only interfaces. Existing method/nested-interface/MAXIMUM_BYTES visibility, signatures, normal/null/error contracts and exact old36 tests remain. Private Pattern/int definitions move into requireValid final locals; no private state exposed, same literal regex/order/guards. Allocation timing/performance remains an IT limitation; fatalError not normalized. All74 Main reference sources/owners recorded, wholecaller freshbinary mandatory before release. OriginalResource26/Env10 plus dependencyStorage2/BatchRun1 require freshRoot5/static/39/current10 CRC-initXML/raw sixCode100/four naturalCode0. Only SS333343354914, no implementation/evidence or operational/Root2Actual4/VM/DB/key/aru/HOLD acceptance. Sparse docs-only worktree materializes no src/tools/evidence.\n')
url=run(['gh','pr','create','--repo','NakajimaMotoharu/schubert_NK_project','--base','main','--head',branch,'--title','docs(ssc440): public utilityの非instance責務と局所pattern','--body-file',str(body)],w)
for attempt in range(6):
 review=json.loads(run(['gh','pr','view',url,'--json','headRefOid,mergeStateStatus,reviewDecision,statusCheckRollup,files'],w))
 if review['mergeStateStatus']!='UNKNOWN':break
 time.sleep(1)
assert review['headRefOid']==head and {x['path'] for x in review['files']}==set(v['paths']) and review['mergeStateStatus']=='CLEAN'
assert all(x.get('conclusion') in [None,'SUCCESS','SKIPPED','NEUTRAL'] and x.get('state') not in ['FAILURE','ERROR','PENDING'] for x in review['statusCheckRollup'])
run(['gh','pr','merge',url,'--merge','--match-head-commit',head],w);run(['git','fetch','origin','main']);main=run(['git','rev-parse','origin/main']);assert run(['git','merge-base','--is-ancestor',head,'origin/main'])==''
for name in v['paths']:assert run(['git','show','origin/main:'+name])==run(['git','show',head+':'+name])
ledger=r/'documents/900_OTHER/910_台帳/914_詳細設計修正管理台帳.md';t=ledger.read_text();at=t.index('## SSC-440');t=t[:at]+t[at:].replace('main反映前','main反映済み（'+url+'、'+main+'）',1);ledger.write_text(t)
result=dict(actualExit=0,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),ssc='SSC440',baseMain=v['baseMain'],designSource=head,mainCommit=main,pr=url,paths=v['paths'],ordinaryMerge=True,implementationIncluded=False,formalAccepted=False,sparseDocsOnly=True,sourceOrToolsOrEvidenceMaterialized=False);(e/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False))
