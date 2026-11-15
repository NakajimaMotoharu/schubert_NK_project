"""Publish only SSC432's evidenced limited status; preserve upstream ledger prefix and ordinary PR checks."""
from pathlib import Path
import datetime,difflib,hashlib,json,re,subprocess,time
r=Path.cwd();w=r.parent/'ssc432-provider-cleanup-design-20261116';b=r/'evidence/01_PT/018_NK-OPS-001';e=b/'evidence/PG34590-ssc432-limited-ledger-main-v1';private=r.parent/'pgpt-runs/PG379/pg34590-ssc432-ledger';assert not e.exists() and not private.exists();e.mkdir();private.mkdir(mode=0o700)
def run(args,cwd=r):return subprocess.check_output(args,cwd=cwd,stderr=subprocess.STDOUT,text=True).strip()
path='documents/900_OTHER/910_台帳/914_詳細設計修正管理台帳.md';base=run(['git','rev-parse','origin/main']);old=subprocess.check_output(['git','show',base+':'+path],cwd=r,text=True);local=(r/path).read_text();marker='## SSC-432 ';assert old.count(marker)==local.count(marker)==1;assert max(map(int,re.findall(r'^## SSC-(\d+)',old,re.M)))==max(map(int,re.findall(r'^## SSC-(\d+)',local,re.M)))==432
first='## SSC-431 ';second='## SSC-432 ';assert old.count(first)==local.count(first)==1 and old.index(first)<old.index(second)
summary=json.loads((b/'evidence/PG34588-ssc432-cleanup18-component-join-v1/manifest.json').read_text())['summary']
firstsection=local[local.index(first):local.index(second)].rstrip()+'\n\n2026-11-16 SSC431局所実施記録（SS432補足sourceで連続確認）: '+summary+'\nProbe既七分類fatal保全/新graph1及び閉failure1は現在whole18で確認、全WBS/451/終了依存は未完。\n\n'
lastsection=local[local.index(second):].rstrip()+'\n\n2026-11-16 SSC432限定実施: '+summary+'\n当914だけmain反映、未受入code/config/tools/evidenceは含めない。\n'
new=old[:old.index(first)]+firstsection+lastsection;assert new!=old

patch=''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/'+path,tofile='b/'+path));(e/'design-only-main-patch.json').write_text(json.dumps(dict(baseMain=base,paths=[path],patchUtf8Sha256=hashlib.sha256(patch.encode()).hexdigest(),patch=patch),ensure_ascii=False,indent=2)+'\n')
assert run(['git','status','--porcelain'],w)=='';branch='docs/ssc432-login18-cleanup-status-20261116';run(['git','switch','-c',branch,'origin/main'],w);p=private/'ledger.patch';p.write_text(patch);run(['git','apply','--check',str(p)],w);run(['git','apply',str(p)],w)
assert subprocess.check_output(['git','diff','--name-only','-z'],cwd=w)==(path+'\0').encode();run(['git','diff','--check'],w);run(['git','add','--',path],w);run(['git','commit','-m','docs(ssc431432): record login eighteen and single credential cleanup qualification'],w);head=run(['git','rev-parse','HEAD'],w);run(['git','push','-u','origin',branch],w)
body=private/'pr-body.txt';body.write_text('SSC431/432 limited source3cb3f31e/Unitbd64d6e9/PG34580 all18 FES0, original4Testclasses byte exact. Existing Probe fatal graph guard and single private credentialconsume helper preserving two cleanupguards order/nullability/auth/API/failure precedence. Main18 freshRoot/static/current197CRC62/init/XML and exactJDKSQLgetter binding; GJF-CS-SB0/PMD31 concrete sites applicability0. Sameexec raw three sources/four classes99LINE20METHOD4CLASS48BRANCH519I miss0; previousSource raw2 retained without exclusion/unreachable/reflection/execunion. PG34586 knownLogin6 source evidence checked, widerYKT2556/2431/2554 remainopen. Only914 status of both changes, no code/config/tools/evidence/wholeWBS451/formal/JMSDBauth/CHR/native/HOLD promotion.\n')
repo='NakajimaMotoharu/schubert_NK_project';url=run(['gh','pr','create','--repo',repo,'--base','main','--head',branch,'--title','docs(ssc432): Login通常十八・Probe保全と単一資格消費の限定資格を記録','--body-file',str(body)],w)
for attempt in range(6):
 review=json.loads(run(['gh','pr','view',url,'--repo',repo,'--json','headRefOid,mergeStateStatus,reviewDecision,statusCheckRollup,files,state'],w))
 if review['mergeStateStatus']!='UNKNOWN':break
 time.sleep(1)
assert review['headRefOid']==head and [x['path'] for x in review['files']]==[path] and review['mergeStateStatus']=='CLEAN' and review['state']=='OPEN' and not review['statusCheckRollup']
run(['gh','pr','merge',url,'--repo',repo,'--merge','--match-head-commit',head],w);run(['git','fetch','origin','main']);main=run(['git','rev-parse','origin/main']);run(['git','merge-base','--is-ancestor',head,'origin/main']);assert subprocess.check_output(['git','show','origin/main:'+path],cwd=r,text=True)==new
# The execution tree's historical prefix is intentionally independent; update its last SSC432 section only.
p=r/path;p.write_text(local[:local.index(first)]+firstsection+lastsection)
(e/'manifest.json').write_text(json.dumps(dict(actualExit=0,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),ssc='SSC432',baseMain=base,designSource=head,mainCommit=main,pr=url,paths=[path],ordinaryMerge=True,upstreamPrefixPreserved=True,implementationIncluded=False,formalAccepted=False),ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,pr=url,mainCommit=main,designSource=head,implementationIncluded=False)))
