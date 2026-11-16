"""Publish append-only approved detail derived from its actual headers, without copied SSC IDs."""
from pathlib import Path
import copy
import datetime
import hashlib
import json
import re
import subprocess
import sys
import time

r=Path.cwd();w=r.parent/'ssc440-public-namespace-design-20261116'
proof=Path(sys.argv[1]);out=Path(sys.argv[2]);v=json.loads(proof.read_text())
def require(value,message):
    if not value:raise ValueError(message)
def plan(value):
    appends=value['designAppendByPath'];require(isinstance(appends,dict) and len(appends)>=2,'explicit design paths')
    numbers=[]
    for path,append in appends.items():
        require(path.startswith('documents/300_SS/') or path=='documents/900_OTHER/910_台帳/914_詳細設計修正管理台帳.md','design/ledger only')
        require('..' not in Path(path).parts and isinstance(append,str),'canonical append')
        headers=re.findall(r'^## SSC-(\d{3}) (.+)$',append,re.M)
        require(len(headers)==1,'one exact new SSC header in every append')
        numbers.append(headers[0][0])
    require(len(set(numbers))==1,'all design and ledger headers agree')
    return numbers[0]
number=plan(v);marker='## SSC-'+number+' ';negatives=[]
for label,mutate in [
 ('mismatched-header',lambda x:x['designAppendByPath'].__setitem__(next(iter(x['designAppendByPath'])), '\n## SSC-001 wrong\n')),
 ('missing-header',lambda x:x['designAppendByPath'].__setitem__(next(iter(x['designAppendByPath'])), '\nno heading\n')),
 ('multiple-headers',lambda x:x['designAppendByPath'].__setitem__(next(iter(x['designAppendByPath'])), '\n## SSC-001 one\n## SSC-002 two\n')),
 ('implementation-path',lambda x:x['designAppendByPath'].__setitem__('src/Changed.java','\n'+marker+'wrong\n'))]:
    wrong=copy.deepcopy(v);mutate(wrong)
    try:plan(wrong)
    except ValueError:negatives.append(label)
    else:raise ValueError('invalid design plan accepted')
require(v['actualExit']==0 and not out.exists(),'new-only output and approved detail')
require(out.parent==r/'evidence/01_PT/018_NK-OPS-001/evidence','public owned output')
def run(args,cwd=r):
    return subprocess.check_output(args,cwd=cwd,stderr=subprocess.STDOUT,text=True).strip()
run(['git','fetch','origin','main'])
require(run(['git','rev-parse','origin/main'])==v['baseMain'],'current approved base changed; review first')
require(run(['git','status','--porcelain'],w)=='','preserve isolated worktree changes')
paths=list(v['designAppendByPath']);base={name:subprocess.check_output(['git','show','origin/main:'+name],cwd=r,text=True) for name in paths}
require(all(marker not in text for text in base.values()),'new SSC already published; recover original result')
branch='docs/ssc'+number+'-header-bound-20261117'
run(['git','switch','-c',branch,'origin/main'],w)
run(['git','sparse-checkout','set','--no-cone',*['/'+p for p in paths]],w)
for name,append in v['designAppendByPath'].items():(w/name).write_text(base[name]+append)
require(set(run(['git','diff','--name-only','-z'],w).split('\0'))-{''}==set(paths),'only declared documents')
run(['git','diff','--check'],w);run(['git','add','--',*paths],w)
run(['git','commit','-m','docs(ssc'+number+'): publish completed internal detail without implementation'],w)
head=run(['git','rev-parse','HEAD'],w);run(['git','push','-u','origin',branch],w)
private=r.parent/'pgpt-runs/PG379'/out.name.lower();require(not private.exists(),'new body file namespace');private.mkdir(mode=0o700)
body=private/'pr-body.txt';body.write_text('Publish completed SSC'+number+' detail and related ledger append only. '
    'Preserve existing approved document text; no implementation/POM/config/tools/evidence or business/quality/HOLD changes. '
    'The fixed SQL operation representation preserves all SQL bytes/order and independent whole160 tests. '
    'Same-source PG/PT, raw coverage and final acceptance remain separate; SSC449 limited compile results are explicitly partial.\n')
repo='NakajimaMotoharu/schubert_NK_project'
url=run(['gh','pr','create','--repo',repo,'--base','main','--head',branch,
    '--title','docs(ssc'+number+'): 閉SQLの内部詳細を公開','--body-file',str(body)],w)
for _ in range(6):
    review=json.loads(run(['gh','pr','view',url,'--repo',repo,'--json','headRefOid,mergeStateStatus,reviewDecision,statusCheckRollup,files,state'],w))
    if review['mergeStateStatus']!='UNKNOWN':break
    time.sleep(1)
require(review['headRefOid']==head and {x['path'] for x in review['files']}==set(paths),'exact PR head/path')
require(review['mergeStateStatus']=='CLEAN' and review['state']=='OPEN' and not review['statusCheckRollup'],'ordinary merge conditions, no bypass')
run(['gh','pr','merge',url,'--repo',repo,'--merge','--match-head-commit',head],w)
run(['git','fetch','origin','main']);main=run(['git','rev-parse','origin/main'])
run(['git','merge-base','--is-ancestor',head,'origin/main'])
require(all(subprocess.check_output(['git','show',main+':'+name],cwd=r,text=True)==base[name]+append
    for name,append in v['designAppendByPath'].items()),'remote exact published append')
out.mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
result=dict(actualExit=0,ssc='SSC'+number,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    sourceProof=dict(path=str(proof.relative_to(r)),sha256=sha(proof)),headerNegativeChecks=negatives,
    designSource=head,mainCommit=main,pr=url,paths=paths,ordinaryMerge=True,
    implementationIncluded=False,productTestsExecuted=0,formalUpdated=False)
(out/'manifest.json').open('x').write(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
p=r/'documents/900_OTHER/910_台帳/914_詳細設計修正管理台帳.md';text=p.read_text();index=text.index(marker)
p.write_text(text[:index]+text[index:].replace('main反映前','main反映済み '+url+' / '+main,1))
print(json.dumps(dict(actualExit=0,ssc='SSC'+number,pr=url,mainCommit=main,negativeChecks=len(negatives))))
