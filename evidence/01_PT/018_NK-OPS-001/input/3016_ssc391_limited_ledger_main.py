"""Publish only SSC391's evidenced limited status; preserve upstream ledger prefix and ordinary PR checks."""
from pathlib import Path
import datetime,difflib,hashlib,json,subprocess,time
r=Path.cwd();w=r.parent/'ssc391-file-read-design-20261115';b=r/'evidence/01_PT/018_NK-OPS-001';e=b/'evidence/PG32460-ssc391-limited-ledger-main-v1';private=r.parent/'pgpt-runs/PG379/pg32460-ssc391-ledger';assert not e.exists() and not private.exists();e.mkdir();private.mkdir(mode=0o700)
def run(args,cwd=r):return subprocess.check_output(args,cwd=cwd,stderr=subprocess.STDOUT,text=True).strip()
path='documents/900_OTHER/910_台帳/914_詳細設計修正管理台帳.md';base=run(['git','rev-parse','origin/main']);old=subprocess.check_output(['git','show',base+':'+path],cwd=r,text=True);local=(r/path).read_text();marker='## SSC-391 ';assert old.count(marker)==local.count(marker)==1
section=local[local.index(marker):].replace('mainへ当台帳限定反映予定','mainへ当台帳限定反映');new=old[:old.index(marker)]+section;assert new!=old
patch=''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/'+path,tofile='b/'+path));(e/'design-only-main-patch.json').write_text(json.dumps(dict(baseMain=base,paths=[path],patchUtf8Sha256=hashlib.sha256(patch.encode()).hexdigest(),patch=patch),ensure_ascii=False,indent=2)+'\n')
assert run(['git','status','--porcelain'],w)=='';branch='docs/ssc391-limited-qualification-20261115';run(['git','switch','-c',branch,'origin/main'],w);p=private/'ledger.patch';p.write_text(patch);run(['git','apply','--check',str(p)],w);run(['git','apply',str(p)],w)
assert subprocess.check_output(['git','diff','--name-only','-z'],cwd=w)==(path+'\0').encode();run(['git','diff','--check'],w);run(['git','add','--',path],w);run(['git','commit','-m','docs(ssc391): record Current file20 raw9 qualification'],w);head=run(['git','rev-parse','HEAD'],w);run(['git','push','-u','origin',branch],w)
body=private/'pr-body.txt';body.write_text('SSC391のCurrent script_files八列borrowed readonly reader限定実績を914だけへ反映。PG32452新20FES0、1CRC-init、既定/無filter9Code四counter100%、SQLNULL/保存path/全JDBC位置fault/cleanup/有限64を確認。source hash-sizeは未信頼metadata、実asset検査/DB/target file対応/全移行/Rootnative/global451/HOLDは未受入。\n\nValidation: exact914 path, upstream prefix preserved, diff --check; Core82454cec/Unitd6470537, PG32452/454/456/458. Implementation/config/tool/evidence excluded.\n')
repo='NakajimaMotoharu/schubert_NK_project';url=run(['gh','pr','create','--repo',repo,'--base','main','--head',branch,'--title','docs(ssc391): Current file読取り20試験の限定実績','--body-file',str(body)],w)
for attempt in range(6):
 review=json.loads(run(['gh','pr','view',url,'--repo',repo,'--json','headRefOid,mergeStateStatus,reviewDecision,statusCheckRollup,files,state'],w))
 if review['mergeStateStatus']!='UNKNOWN':break
 time.sleep(1)
assert review['headRefOid']==head and [x['path'] for x in review['files']]==[path] and review['mergeStateStatus']=='CLEAN' and review['state']=='OPEN' and not review['statusCheckRollup']
run(['gh','pr','merge',url,'--repo',repo,'--merge','--match-head-commit',head],w);run(['git','fetch','origin','main']);main=run(['git','rev-parse','origin/main']);run(['git','merge-base','--is-ancestor',head,'origin/main']);assert subprocess.check_output(['git','show','origin/main:'+path],cwd=r,text=True)==new
# The execution tree's historical prefix is intentionally independent; update its last SSC391 section only.
p=r/path;p.write_text(local[:local.index(marker)]+section)
(e/'manifest.json').write_text(json.dumps(dict(actualExit=0,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),ssc='SSC391',baseMain=base,designSource=head,mainCommit=main,pr=url,paths=[path],ordinaryMerge=True,upstreamPrefixPreserved=True,implementationIncluded=False,formalAccepted=False),ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,pr=url,mainCommit=main,designSource=head,implementationIncluded=False)))
